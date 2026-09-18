from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BookmarkCreateRequest(BaseModel):
    quote_text: str = Field(..., min_length=3, max_length=5000)
    section_title: Optional[str] = None
    source_url: Optional[str] = None
    notes: Optional[str] = None


class BookmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    topic: str
    quote_text: str
    section_title: Optional[str] = None
    source_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
