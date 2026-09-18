from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_db
from backend.app.database.repository import ResearchRepository

router = APIRouter(prefix="/stats", tags=["Dashboard Statistics"])


@router.get("", response_model=Dict[str, Any])
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    repo = ResearchRepository(db)
    return await repo.get_stats()
