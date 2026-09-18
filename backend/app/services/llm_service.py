import os
import re
from typing import Dict, Any, List, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.app.config import get_settings


class LLMService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
        self.model_name = model or settings.GROQ_MODEL
        self._llm = None

    def get_llm(self) -> ChatGroq:
        if not self._llm:
            if not self.api_key or not self.api_key.strip():
                raise RuntimeError(
                    "GROQ_API_KEY is missing or empty. Please set GROQ_API_KEY in your .env file "
                    "or environment variables."
                )
            self._llm = ChatGroq(
                model=self.model_name,
                temperature=0.1,
                api_key=self.api_key.strip(),
            )
        return self._llm

    # Chains
    def synthesize_research(self, topic: str, search_snippets: str, scraped_sources: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a Senior Intelligence Analyst. Synthesize web search results and deep "
                "scraped text into structured, dense research notes. Highlight key facts, metrics, "
                "competing viewpoints, and primary source quotes.",
            ),
            (
                "human",
                """Topic: {topic}

Search Summaries:
{search_snippets}

Deep Scraped Sources:
{scraped_sources}

Create structured research notes organized by core themes. List specific technical details, statistics, and citations where available.""",
            ),
        ])
        chain = prompt | self.get_llm() | StrOutputParser()
        return chain.invoke({
            "topic": topic,
            "search_snippets": search_snippets[:3000],
            "scraped_sources": scraped_sources[:8000],
        })

    def write_report(
        self,
        topic: str,
        research_content: str,
        depth: str = "Standard",
        tone: str = "Formal",
    ) -> str:
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert research scientist and technical author. Produce polished, "
                "authoritative, structured research reports with inline citations referencing the gathered sources.",
            ),
            (
                "human",
                """Write a {depth} research report on the topic below in a {tone} tone.

Topic: {topic}

Gathered Research & Synthesis:
{research_content}

Structure the report with the following Markdown headers:
# Executive Summary
## Introduction & Background
## Core Analysis & Findings
(Provide at least 3-4 detailed analytical points with evidence and citations where applicable)
## Strategic Implications & Challenges
## Conclusion & Outlook
## References & Sources
(List all URLs and source domains cited in the text)

Depth Guidelines:
- Quick: ~350 - 500 words, direct, concise, high-impact key findings.
- Standard: ~750 - 1000 words, robust depth, nuance, and structural context.
- Deep: 1300+ words, exhaustive analysis, comprehensive breakdown, data points, and forward-looking risks.

Tone Guidelines:
- Formal: Objective, scholarly, authoritative.
- Conversational: Engaging, accessible, clear without compromising technical accuracy.
- Technical: Architecture-focused, specific, precise, data-dense.
- Executive: High-level strategic briefing, bottom-line upfront, actionable takeaways.

Do not include conversational conversational greetings or conversational filler outside the report. Output purely the Markdown report.""",
            ),
        ])
        chain = prompt | self.get_llm() | StrOutputParser()
        return chain.invoke({
            "topic": topic,
            "research_content": research_content,
            "depth": depth,
            "tone": tone,
        })

    def critique_report(self, report: str, depth: str = "Standard") -> str:
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a rigorous, uncompromising Chief Research Editor. Evaluate the research report "
                "on factual depth, structural coherence, citation grounding, clarity, and depth suitability. "
                "Give an exact score between 1 and 10.",
            ),
            (
                "human",
                """Evaluate this research report:

{report}

Depth setting: {depth}

You MUST follow this exact response template:

Score: X/10

Strengths:
- [Point 1]
- [Point 2]
- [Point 3]

Areas to Improve:
- [Specific point 1]
- [Specific point 2]
- [Specific point 3]

One line verdict:
[Brief assessment]""",
            ),
        ])
        chain = prompt | self.get_llm() | StrOutputParser()
        return chain.invoke({"report": report, "depth": depth})

    def revise_report(self, report: str, feedback: str, depth: str = "Standard", tone: str = "Formal") -> str:
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert research editor and technical reviser. Rewrite and elevate the report "
                "addressing every single critique and weakness pointed out by the editor. Maintain strict factual "
                "integrity and preserve the Markdown structure.",
            ),
            (
                "human",
                """Original Report:
{report}

Critic Feedback:
{feedback}

Settings: Depth = {depth}, Tone = {tone}

Revise and improve the report. Fix all identified weaknesses, deepen shallow explanations, improve transitions, and ensure references are comprehensive.
Output ONLY the revised Markdown report.""",
            ),
        ])
        chain = prompt | self.get_llm() | StrOutputParser()
        return chain.invoke({
            "report": report,
            "feedback": feedback,
            "depth": depth,
            "tone": tone,
        })

    def answer_question(self, report: str, research_notes: str, question: str) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an AI Research Assistant. You MUST answer the user's question STRICTLY and ONLY "
                "using the provided Research Report and Research Notes. "
                "If the information is not present or cannot be directly inferred from the research, you MUST "
                "explicitly and clearly state that the current research does not contain enough information to answer the question.",
            ),
            (
                "human",
                """Research Report:
{report}

Research Notes & Sources:
{research_notes}

User Question:
{question}

Answer with precision. Ground every point in the report/notes. If unknown from the source material, state that explicitly.""",
            ),
        ])
        chain = prompt | self.get_llm() | StrOutputParser()
        answer = chain.invoke({
            "report": report,
            "research_notes": research_notes[:4000],
            "question": question,
        })

        # Check grounding disclaimer heuristic
        lower_ans = answer.lower()
        not_covered_indicators = [
            "does not contain",
            "not mentioned",
            "not provided",
            "not enough information",
            "cannot be answered",
            "not covered",
        ]
        is_grounded = not any(ind in lower_ans for ind in not_covered_indicators)

        return {
            "answer": answer,
            "is_grounded": is_grounded,
        }

    @staticmethod
    def extract_score(critique_text: str) -> int:
        match = re.search(r"Score:\s*(\d+)\s*/\s*10", critique_text, re.IGNORECASE)
        if match:
            try:
                score = int(match.group(1))
                return max(1, min(10, score))
            except ValueError:
                pass
        # Alternative pattern: "Score: 8" or "8/10"
        match2 = re.search(r"\b([1-9]|10)\s*/\s*10\b", critique_text)
        if match2:
            return int(match2.group(1))
        return 7
