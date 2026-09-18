from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SourceItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    url: str
    title: str
    domain: str
    snippet: Optional[str] = None
    scraped_content: Optional[str] = None
    status: str  # discovered, scraped, failed, skipped
    error_reason: Optional[str] = None
    relevance_score: Optional[float] = None
    char_count: int = 0
    created_at: datetime
