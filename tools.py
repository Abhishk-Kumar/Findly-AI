"""
tools.py
Search and scraping tools used by the agents in agents.py.

- web_search: uses Tavily to find recent, reliable sources for a query.
- scrape_url:  fetches a URL and extracts its main readable text.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

_tavily_client = None


def ensure_tavily_key() -> None:
    """Fails fast with a clear message instead of a cryptic error deep inside an agent call."""
    key = os.getenv("TAVILY_API_KEY")
    if not key or not key.strip():
        raise RuntimeError(
            "TAVILY_API_KEY is missing or empty. Add it to your .env file (see .env.example), "
            "or, if deployed on Streamlit Community Cloud, add it under "
            "App settings -> Secrets."
        )


def _get_tavily_client() -> TavilyClient:
    global _tavily_client
    if _tavily_client is None:
        ensure_tavily_key()
        _tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    return _tavily_client


@tool
def web_search(query: str) -> str:
    """Search the web for recent, reliable information on a given query.
    Returns a formatted list of results, each with a title, URL and short snippet.
    """
    try:
        client = _get_tavily_client()
        response = client.search(query=query, search_depth="advanced", max_results=6)
        results = response.get("results", [])

        if not results:
            return f"No search results found for query: {query}"

        formatted = []
        for i, r in enumerate(results, start=1):
            formatted.append(
                f"{i}. {r.get('title', 'Untitled')}\n"
                f"   URL: {r.get('url', 'N/A')}\n"
                f"   Snippet: {r.get('content', '')[:400]}\n"
            )
        return "\n".join(formatted)

    except Exception as e:
        return f"Web search failed: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """Scrape the main textual content of a given URL.
    If a full sentence is passed instead of a raw URL, the first URL found inside it is used.
    """
    match = re.search(r"https?://[^\s\)\]\"']+", url)
    target_url = match.group(0) if match else url.strip()

    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"}
        resp = requests.get(target_url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()

        text = " ".join(soup.stripped_strings)
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return f"Could not extract readable content from {target_url}"

        return text[:6000]

    except Exception as e:
        return f"Scraping failed for {target_url}: {str(e)}"