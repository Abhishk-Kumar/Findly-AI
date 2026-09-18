import pytest
from unittest.mock import patch, MagicMock
from backend.app.graph.state import ResearchState
from backend.app.graph.nodes import (
    search_node,
    source_selection_node,
    scrape_node,
    synthesize_node,
    write_node,
    critique_node,
    should_revise_router,
    revision_node,
    finalize_node,
)


def test_should_revise_router_decision_logic():
    # Scenario 1: Score is below quality bar and revisions remain -> Revise
    state_need_rev: ResearchState = {
        "final_score": 5,
        "quality_bar": 7,
        "revision_count": 0,
        "max_revisions": 3,
    }
    assert should_revise_router(state_need_rev) == "revise"

    # Scenario 2: Score meets or exceeds quality bar -> Finalize
    state_good_score: ResearchState = {
        "final_score": 8,
        "quality_bar": 7,
        "revision_count": 0,
        "max_revisions": 3,
    }
    assert should_revise_router(state_good_score) == "finalize"

    # Scenario 3: Score is below bar, but max revisions reached -> Finalize (Hard Cap)
    state_max_revisions: ResearchState = {
        "final_score": 6,
        "quality_bar": 7,
        "revision_count": 3,
        "max_revisions": 3,
    }
    assert should_revise_router(state_max_revisions) == "finalize"


def test_source_selection_and_failed_source_resilience():
    # Provide 4 discovered sources, one of which fails scraping
    mock_search_results = [
        {"url": "https://example.com/source1", "title": "Source 1", "snippet": "Snippet 1", "relevance_score": 0.95},
        {"url": "https://example.com/source2", "title": "Source 2", "snippet": "Snippet 2", "relevance_score": 0.90},
        {"url": "http://127.0.0.1/blocked", "title": "Blocked SSRF", "snippet": "Bad snippet", "relevance_score": 0.85},
    ]

    state: ResearchState = {
        "topic": "Quantum Computing",
        "search_results": mock_search_results,
        "step_timings": {},
    }

    # Node: source selection
    sel_res = source_selection_node(state)
    assert len(sel_res["selected_sources"]) == 3
    state.update(sel_res)

    # Node: scrape node (one source is blocked by SSRF)
    scrape_res = scrape_node(state)
    assert len(scrape_res["scraped_content"]) == 3

    # Verify that the blocked source failed gracefully without raising an unhandled exception
    blocked_src = next(s for s in scrape_res["scraped_content"] if "127.0.0.1" in s["url"])
    assert blocked_src["status"] == "failed"
    assert "Security restriction" in blocked_src["error_reason"]

    # Verify progress state
    assert scrape_res["progress_pct"] == 55
    assert scrape_res["status"] == "scraping"


def test_finalize_node_calculates_word_count():
    state: ResearchState = {
        "final_report": "# Executive Summary\nQuantum error correction is advancing rapidly with cat qubits and surface codes.",
    }
    res = finalize_node(state)
    assert res["status"] == "completed"
    assert res["progress_pct"] == 100
    assert res["total_words"] == 15
