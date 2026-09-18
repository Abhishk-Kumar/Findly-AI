from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict, Field
from backend.app.schemas.source import SourceItem
from backend.app.schemas.finding import BookmarkResponse
from backend.app.schemas.qa import QAResponse


class ResearchCreateRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500, description="The research question or topic")
    depth: str = Field("Standard", description="Quick (300w), Standard (700w), Deep (1200w+)")
    tone: str = Field("Formal", description="Formal, Conversational, Technical, Executive")
    quality_bar: int = Field(7, ge=4, le=9, description="Minimum score out of 10 to accept without auto-revision")
    max_revisions: int = Field(3, ge=1, le=5, description="Maximum auto-revision passes")


class ResearchRunSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    topic: str
    depth: str
    tone: str
    quality_bar: int
    status: str
    current_step: str
    progress_pct: int
    initial_score: Optional[int] = None
    final_score: Optional[int] = None
    revision_count: int
    total_words: int
    elapsed_seconds: float
    created_at: datetime
    updated_at: datetime
    sources_count: int = 0


class ResearchRunDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    topic: str
    depth: str
    tone: str
    quality_bar: int
    max_revisions: int
    status: str
    current_step: str
    progress_pct: int
    initial_score: Optional[int] = None
    final_score: Optional[int] = None
    revision_count: int
    draft_report: Optional[str] = None
    final_report: Optional[str] = None
    critique_feedback: Optional[str] = None
    initial_critique: Optional[str] = None
    synthesized_notes: Optional[str] = None
    raw_search_summary: Optional[str] = None
    error_message: Optional[str] = None
    total_words: int
    elapsed_seconds: float
    step_timings: Dict[str, float] = {}
    created_at: datetime
    updated_at: datetime
    sources: List[SourceItem] = []
    bookmarks: List[BookmarkResponse] = []
    qa_messages: List[QAResponse] = []


class StepTimingUpdate(BaseModel):
    step: str
    elapsed_seconds: float


class ResearchStatusEvent(BaseModel):
    run_id: str
    status: str
    current_step: str
    progress_pct: int
    message: str
    timestamp: str
    score: Optional[int] = None
    revision_count: Optional[int] = None
    timings: Optional[Dict[str, float]] = None
