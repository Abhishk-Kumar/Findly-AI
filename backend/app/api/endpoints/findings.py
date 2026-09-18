from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_db
from backend.app.database.repository import ResearchRepository
from backend.app.schemas.finding import BookmarkCreateRequest, BookmarkResponse

router = APIRouter(tags=["Bookmarked Findings"])


@router.post("/research/{run_id}/bookmarks", response_model=BookmarkResponse, status_code=201)
async def create_bookmark(
    run_id: str,
    req: BookmarkCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    run = await repo.get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")

    bookmark = await repo.add_bookmark(
        run_id=run.id,
        topic=run.topic,
        quote_text=req.quote_text.strip(),
        section_title=req.section_title,
        source_url=req.source_url,
        notes=req.notes,
    )
    return bookmark


@router.get("/bookmarks", response_model=List[BookmarkResponse])
async def list_bookmarks(
    search: Optional[str] = Query(None, description="Search bookmarks"),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    return await repo.list_bookmarks(search=search, limit=limit)


@router.delete("/bookmarks/{bookmark_id}", status_code=204)
async def delete_bookmark(
    bookmark_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    success = await repo.delete_bookmark(bookmark_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return None
