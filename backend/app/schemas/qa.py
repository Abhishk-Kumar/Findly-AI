from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class QARequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)


class QAResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    question: str
    answer: str
    is_grounded: bool = True
    created_at: datetime
