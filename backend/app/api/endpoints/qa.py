from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_db
from backend.app.database.repository import ResearchRepository
from backend.app.schemas.qa import QARequest, QAResponse
from backend.app.services.llm_service import LLMService

router = APIRouter(prefix="/research", tags=["Grounded Q&A"])


@router.post("/{run_id}/qa", response_model=QAResponse)
async def ask_research_question(
    run_id: str,
    req: QARequest,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    run = await repo.get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")

    report_text = run.final_report or run.draft_report or ""
    if not report_text:
        raise HTTPException(status_code=400, detail="Report has not been drafted yet.")

    notes = run.synthesized_notes or ""

    llm = LLMService()
    try:
        res = llm.answer_question(
            report=report_text,
            research_notes=notes,
            question=req.question.strip(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")

    saved_qa = await repo.add_qa_message(
        run_id=run.id,
        question=req.question.strip(),
        answer=res["answer"],
        is_grounded=res["is_grounded"],
    )
    return saved_qa


@router.get("/{run_id}/qa", response_model=List[QAResponse])
async def get_run_qa_history(
    run_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    messages = await repo.list_qa_messages(run_id)
    return messages
