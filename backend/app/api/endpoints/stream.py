import asyncio
import orjson
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_db
from backend.app.database.repository import ResearchRepository
from backend.app.services.research_runner import event_bus

router = APIRouter(prefix="/research", tags=["Live Stream"])


@router.get("/{run_id}/stream")
async def stream_research_events(
    run_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    run = await repo.get_run_by_id(run_id, load_relations=False)
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")

    async def event_generator():
        # Yield initial state immediately
        initial_payload = {
            "run_id": run.id,
            "status": run.status,
            "current_step": run.current_step,
            "progress_pct": run.progress_pct,
            "score": run.final_score,
            "revision_count": run.revision_count,
            "step_timings": run.step_timings or {},
        }
        yield f"data: {orjson.dumps(initial_payload).decode('utf-8')}\n\n"

        if run.status in ("completed", "failed"):
            return

        queue = await event_bus.subscribe(run_id)
        try:
            while True:
                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"data: {orjson.dumps(event_data).decode('utf-8')}\n\n"
                    if event_data.get("status") in ("completed", "failed"):
                        break
                except asyncio.TimeoutError:
                    # Send keep-alive comment
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            await event_bus.unsubscribe(run_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
