from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_db
from backend.app.database.repository import ResearchRepository
from backend.app.services.export_service import ExportService

router = APIRouter(prefix="/research", tags=["Export"])


@router.get("/{run_id}/export/pdf")
async def export_research_pdf(
    run_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    run = await repo.get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")

    report_text = run.final_report or run.draft_report
    if not report_text:
        raise HTTPException(status_code=400, detail="No report available for export.")

    try:
        pdf_bytes = ExportService.generate_pdf(run.topic, report_text, score=run.final_score)
        filename = f"research_{run.topic[:30].strip().replace(' ', '_').lower()}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/{run_id}/export/md")
async def export_research_markdown(
    run_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    run = await repo.get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")

    report_text = run.final_report or run.draft_report
    if not report_text:
        raise HTTPException(status_code=400, detail="No report available for export.")

    md_content = ExportService.generate_markdown(run.topic, report_text, score=run.final_score)
    filename = f"research_{run.topic[:30].strip().replace(' ', '_').lower()}.md"
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
