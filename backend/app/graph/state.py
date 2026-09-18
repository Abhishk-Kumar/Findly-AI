from typing import TypedDict, List, Dict, Any, Optional


class SourceMetadata(TypedDict, total=False):
    id: Optional[str]
    url: str
    title: str
    domain: str
    snippet: str
    scraped_content: Optional[str]
    status: str  # discovered, scraped, failed, skipped
    error_reason: Optional[str]
    relevance_score: Optional[float]
    char_count: int


class ResearchState(TypedDict, total=False):
    run_id: str
    topic: str
    depth: str
    tone: str
    quality_bar: int
    max_revisions: int

    status: str
    current_step: str
    progress_pct: int

    search_results: List[SourceMetadata]
    selected_sources: List[SourceMetadata]
    scraped_content: List[SourceMetadata]

    synthesized_notes: str
    draft_report: str
    critique_feedback: str
    initial_critique: str
    initial_score: Optional[int]
    final_score: Optional[int]

    revision_count: int
    final_report: str

    step_timings: Dict[str, float]
    elapsed_seconds: float
    error_message: Optional[str]
