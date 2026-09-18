from fastapi import APIRouter
from backend.app.api.endpoints.research import router as research_router
from backend.app.api.endpoints.stream import router as stream_router
from backend.app.api.endpoints.qa import router as qa_router
from backend.app.api.endpoints.findings import router as findings_router
from backend.app.api.endpoints.export import router as export_router
from backend.app.api.endpoints.stats import router as stats_router

api_router = APIRouter(prefix="/api")

api_router.include_router(research_router)
api_router.include_router(stream_router)
api_router.include_router(qa_router)
api_router.include_router(findings_router)
api_router.include_router(export_router)
api_router.include_router(stats_router)
