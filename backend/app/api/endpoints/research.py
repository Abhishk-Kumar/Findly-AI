import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_db
from backend.app.database.repository import ResearchRepository
from backend.app.schemas.research import (
    ResearchCreateRequest,
    ResearchRunSummary,
    ResearchRunDetail,
)
from backend.app.services.research_runner import execute_research_run_async

router = APIRouter(prefix="/research", tags=["Research Runs"])


@router.post("", response_model=ResearchRunDetail, status_code=201)
async def create_research_run(
    req: ResearchCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    run = await repo.create_run(
        topic=req.topic.strip(),
        depth=req.depth,
        tone=req.tone,
        quality_bar=req.quality_bar,
        max_revisions=req.max_revisions,
    )

    # Launch graph background runner
    background_tasks.add_task(
        execute_research_run_async,
        run_id=run.id,
        topic=run.topic,
        depth=run.depth,
        tone=run.tone,
        quality_bar=run.quality_bar,
        max_revisions=run.max_revisions,
    )

    # Re-fetch with loaded relationships
    detailed_run = await repo.get_run_by_id(run.id)
    return detailed_run


@router.get("", response_model=List[ResearchRunSummary])
async def list_research_runs(
    search: Optional[str] = Query(None, description="Search topics"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    runs = await repo.list_runs(search=search, status=status, limit=limit, offset=offset)
    summaries = []
    for r in runs:
        summary_dict = {
            "id": r.id,
            "topic": r.topic,
            "depth": r.depth,
            "tone": r.tone,
            "quality_bar": r.quality_bar,
            "status": r.status,
            "current_step": r.current_step,
            "progress_pct": r.progress_pct,
            "initial_score": r.initial_score,
            "final_score": r.final_score,
            "revision_count": r.revision_count,
            "total_words": r.total_words,
            "elapsed_seconds": r.elapsed_seconds,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
            "sources_count": len(r.sources) if r.sources else 0,
        }
        summaries.append(ResearchRunSummary(**summary_dict))
    return summaries


@router.get("/{run_id}", response_model=ResearchRunDetail)
async def get_research_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    run = await repo.get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    return run


@router.delete("/{run_id}", status_code=204)
async def delete_research_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    success = await repo.delete_run(run_id)
    if not success:
        raise HTTPException(status_code=404, detail="Research run not found")
    return None
