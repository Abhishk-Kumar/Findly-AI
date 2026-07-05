"""
agents.py
Defines the two tool-using agents (search, scraping) and the three LLM chains
(report writer, critic, reviser) used by the research pipeline.
"""

from tools import web_search, scrape_url
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)


def ensure_groq_key() -> None:
    """Fails fast with a clear message instead of letting a missing/blank key
    surface later as a cryptic AuthenticationError buried inside a RetryError."""
    key = os.getenv("GROQ_API_KEY")
    if not key or not key.strip():
        raise RuntimeError(
            "GROQ_API_KEY is missing or empty. Add it to your .env file (see .env.example), "
            "or, if deployed on Streamlit Community Cloud, add it under "
            "App settings -> Secrets."
        )


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------


def web_search_agent():
    """Agent responsible for discovering relevant, recent sources on the web."""
    return create_agent(model=llm, tools=[web_search])


def web_scraping_agent():
    """Agent responsible for extracting deeper content from a chosen URL."""
    return create_agent(model=llm, tools=[scrape_url])


# ---------------------------------------------------------------------------
# Chains
# ---------------------------------------------------------------------------

report_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a {depth} research report on the topic below, in a {tone} tone.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points; more for deeper reports)
- Conclusion
- Sources (list all URLs found in the research)

Depth guide:
- Quick: concise, roughly 250-400 words total, only the most essential points.
- Standard: roughly 600-900 words, solid detail in every section.
- Deep: 1200+ words, thorough analysis, more findings, nuance and caveats.

Be factual and well-organized."""),
])

reportChain = report_prompt | llm | StrOutputParser()

feedback_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

feedbackChain = feedback_prompt | llm | StrOutputParser()

# Used only when the critic's score is below the quality bar (see pipeline.py),
# to auto-revise the report once based on the critic's own feedback.
revision_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research editor. Improve reports based on critic feedback "
               "without losing factual accuracy."),
    ("human", """Revise the report below using the critic's feedback. Keep the same section
structure (Introduction, Key Findings, Conclusion, Sources) but address every point raised.

Original Report:
{report}

Critic Feedback:
{feedback}

Return only the improved report."""),
])

revisionChain = revision_prompt | llm | StrOutputParser()