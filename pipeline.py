"""
pipeline.py
Orchestrates the multi-agent research pipeline:

    Search Agent -> Scraping Agent -> Writer Chain -> Critic Chain -> (optional) Reviser Chain

Exposed as execute_research_pipeline(...) so it can be driven from a CLI (see __main__)
or a UI such as app.py without any Streamlit import here.
"""

import re
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_not_exception_type

from agents import (
    web_search_agent,
    web_scraping_agent,
    reportChain,
    feedbackChain,
    revisionChain,
    ensure_groq_key,
)
from tools import ensure_tavily_key

# Groq's own auth error type, imported defensively: if the groq package's public
# API ever changes shape, we still fall back to a safe stand-in class instead of
# crashing at import time.
try:
    from groq import AuthenticationError as GroqAuthError
except ImportError:  # pragma: no cover
    class GroqAuthError(Exception):
        pass

# Exceptions that mean "this will never succeed on retry" - config/auth problems,
# not flaky network blips. Retrying these just wastes 3x the time before the
# user sees the real error, wrapped in an opaque RetryError.
NON_RETRYABLE = (RuntimeError, ValueError, GroqAuthError)

DEFAULT_QUALITY_BAR = 7  # minimum acceptable critic score out of 10


def _log_step(step_number: int, label: str) -> None:
    print("\n" + "=" * 50)
    print(f"step {step_number} - {label}")
    print("=" * 50)


def _friendly_error(e: Exception) -> RuntimeError:
    """Turns raw SDK exceptions into a message a user can actually act on."""
    msg = str(e).lower()
    if isinstance(e, GroqAuthError) or "authentication" in msg or "401" in msg or "invalid api key" in msg:
        return RuntimeError(
            "Groq rejected the API key (authentication failed). Check that GROQ_API_KEY "
            "in your .env file (or Streamlit secrets) is correct, active, and has no "
            "extra spaces/quotes around it."
        )
    if "tavily" in msg and ("key" in msg or "unauthorized" in msg or "401" in msg):
        return RuntimeError(
            "Tavily rejected the API key. Check TAVILY_API_KEY in your .env file "
            "(or Streamlit secrets)."
        )
    return RuntimeError(f"Pipeline step failed: {e}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_not_exception_type(NON_RETRYABLE),
    reraise=True,
)
def _invoke_chain(chain, inputs: dict):
    """Wraps any LCEL chain invoke with the same friendly-error / no-pointless-retry
    behavior as the agents below. This is what was missing before: reportChain,
    feedbackChain and revisionChain were calling .invoke(...) directly, so a bad
    API key surfaced as a raw 401 JSON blob instead of a clear message."""
    try:
        return chain.invoke(inputs)
    except NON_RETRYABLE:
        raise
    except Exception as e:
        raise _friendly_error(e) from e


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_not_exception_type(NON_RETRYABLE),
    reraise=True,
)
def _run_search_agent(topic: str) -> str:
    try:
        agent = web_search_agent()
        result = agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        return result["messages"][-1].content
    except NON_RETRYABLE:
        raise
    except Exception as e:
        raise _friendly_error(e) from e


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_not_exception_type(NON_RETRYABLE),
    reraise=True,
)
def _run_scraping_agent(topic: str, search_results: str) -> str:
    try:
        agent = web_scraping_agent()
        result = agent.invoke({
            "messages": [(
                "user",
                f"Based on the following search results about '{topic}', identify the "
                f"2-3 most relevant and diverse URLs and scrape each of them for deeper "
                f"content. Combine what you find into one coherent set of notes.\n\n"
                f"Search Results:\n{search_results[:1200]}"
            )]
        })
        return result["messages"][-1].content
    except NON_RETRYABLE:
        raise
    except Exception as e:
        raise _friendly_error(e) from e


def _extract_score(feedback_text: str) -> int:
    """Pulls the numeric score (out of 10) out of the critic's feedback text.
    Defaults to 10 if not found, so a parsing miss never triggers an unwanted extra LLM call."""
    match = re.search(r"Score:\s*(\d+)\s*/\s*10", feedback_text)
    return int(match.group(1)) if match else 10


def _extract_sources(text: str) -> list:
    return sorted(set(re.findall(r"https?://[^\s\)\]\"'>,]+", text)))


def execute_research_pipeline(
    topic: str,
    progress_callback=None,
    depth: str = "Standard",
    tone: str = "Formal",
    quality_bar: int = DEFAULT_QUALITY_BAR,
) -> dict:
    """
    Runs the full multi-agent research pipeline for a topic.

    progress_callback: optional callable(step: int, total: int, label: str) -> None
        Lets a UI (e.g. Streamlit) show live progress without importing Streamlit here.
    depth: "Quick" | "Standard" | "Deep" - controls report length/detail.
    tone:  "Formal" | "Conversational" - controls report voice.
    quality_bar: critic score (out of 10) below which the report is auto-revised once.
    """
    # Fail fast with clear messages instead of a cryptic RetryError deep in an agent call.
    ensure_groq_key()
    ensure_tavily_key()

    start_time = time.time()
    state = {"topic": topic, "depth": depth, "tone": tone}
    total_steps = 4
    step_timings = {}

    def notify(step, label):
        if progress_callback:
            progress_callback(step, total_steps, label)

    def timed(label, fn, *args):
        t0 = time.time()
        result = fn(*args)
        step_timings[label] = round(time.time() - t0, 2)
        return result

    # Step 1 - search agent
    _log_step(1, "search agent is working ...")
    notify(1, "Searching the web")
    state["search_results"] = timed("search", _run_search_agent, topic)
    print("\nSearch result:\n", state["search_results"])

    # Step 2 - scraping agent
    _log_step(2, "scraping agent is working ...")
    notify(2, "Scraping the most relevant sources")
    state["scraped_content"] = timed("scrape", _run_scraping_agent, topic, state["search_results"])
    print("\nScraped content:\n", state["scraped_content"])

    # Step 3 - report writer
    _log_step(3, "writer is drafting the report ...")
    notify(3, "Drafting the report")
    complete_research_content = (
        f"Search results:\n{state['search_results']}\n\n"
        f"Scraped content:\n{state['scraped_content']}\n\n"
    )
    t0 = time.time()
    state["report"] = _invoke_chain(reportChain, {
        "topic": topic,
        "research": complete_research_content,
        "depth": depth,
        "tone": tone,
    })
    step_timings["write"] = round(time.time() - t0, 2)
    print(f"\nFinal report is:\n{state['report']}\n")

    # Step 4 - critic
    _log_step(4, "critic is reviewing the report")
    notify(4, "Getting critic feedback")
    t0 = time.time()
    state["feedback"] = _invoke_chain(feedbackChain, {"report": state["report"]})
    step_timings["critique"] = round(time.time() - t0, 2)
    print(f"\nFeedback of report is:\n{state['feedback']}\n")

    # Optional auto-revision loop: if the critic's score is below the quality bar,
    # send the report back through an editor chain once, then re-score it.
    score = _extract_score(state["feedback"])
    state["initial_score"] = score
    state["initial_feedback"] = state["feedback"]
    state["revised"] = False
    state["original_report"] = None

    if score < quality_bar:
        _log_step(5, f"critic score {score}/10 is below bar ({quality_bar}) - auto-revising once ...")
        notify(4, "Revising report based on feedback")
        state["original_report"] = state["report"]
        t0 = time.time()
        state["report"] = _invoke_chain(revisionChain, {
            "report": state["report"],
            "feedback": state["feedback"],
        })
        step_timings["revise"] = round(time.time() - t0, 2)
        state["feedback"] = _invoke_chain(feedbackChain, {"report": state["report"]})
        state["revised"] = True
        score = _extract_score(state["feedback"])
        print(f"\nRevised report score: {score}/10\n")

    state["final_score"] = score
    state["quality_bar"] = quality_bar
    state["sources"] = _extract_sources(state["search_results"] + state["scraped_content"])
    state["step_timings"] = step_timings
    state["elapsed_seconds"] = round(time.time() - start_time, 2)

    return state


if __name__ == "__main__":
    """Pipeline in execution phase now"""
    topic = input("\nKindly enter the topic to research:\n")
    result = execute_research_pipeline(topic)
    print("\n" + "=" * 50)
    print(f"Done in {result['elapsed_seconds']}s | Final score: {result['final_score']}/10 | Revised: {result['revised']}")
    print("=" * 50)