import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Set
import orjson
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import AsyncSessionLocal
from backend.app.database.repository import ResearchRepository
from backend.app.graph.workflow import research_graph
from backend.app.graph.state import ResearchState


class ResearchEventBus:
    """Manages active SSE subscriber queues for research runs."""
    def __init__(self):
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, run_id: str) -> asyncio.Queue:
        async with self._lock:
            if run_id not in self._subscribers:
                self._subscribers[run_id] = set()
            q: asyncio.Queue = asyncio.Queue()
            self._subscribers[run_id].add(q)
            return q

    async def unsubscribe(self, run_id: str, q: asyncio.Queue) -> None:
        async with self._lock:
            if run_id in self._subscribers:
                self._subscribers[run_id].discard(q)
                if not self._subscribers[run_id]:
                    del self._subscribers[run_id]

    async def emit(self, run_id: str, event_data: Dict[str, Any]) -> None:
        async with self._lock:
            queues = list(self._subscribers.get(run_id, set()))
        for q in queues:
            await q.put(event_data)


event_bus = ResearchEventBus()


async def execute_research_run_async(
    run_id: str,
    topic: str,
    depth: str = "Standard",
    tone: str = "Formal",
    quality_bar: int = 7,
    max_revisions: int = 3,
) -> None:
    """Background task orchestrating database updates, graph execution, and SSE emission."""
    t_start = time.time()

    initial_state: ResearchState = {
        "run_id": run_id,
        "topic": topic,
        "depth": depth,
        "tone": tone,
        "quality_bar": quality_bar,
        "max_revisions": max_revisions,
        "status": "queued",
        "current_step": "Initializing pipeline",
        "progress_pct": 5,
        "search_results": [],
        "selected_sources": [],
        "scraped_content": [],
        "synthesized_notes": "",
        "draft_report": "",
        "critique_feedback": "",
        "initial_critique": "",
        "initial_score": None,
        "final_score": None,
        "revision_count": 0,
        "final_report": "",
        "step_timings": {},
        "elapsed_seconds": 0.0,
        "error_message": None,
    }

    async def emit_progress(
        status: str,
        step: str,
        pct: int,
        score: Optional[int] = None,
        timings: Optional[Dict[str, float]] = None,
    ):
        event = {
            "run_id": run_id,
            "status": status,
            "current_step": step,
            "progress_pct": pct,
            "score": score,
            "revision_count": initial_state.get("revision_count", 0),
            "step_timings": timings or initial_state.get("step_timings", {}),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await event_bus.emit(run_id, event)

    try:
        await emit_progress("searching", "Searching web sources", 15)

        # Stream LangGraph events step-by-step
        current_state = initial_state
        async for output in research_graph.astream(initial_state):
            for node_name, node_state in output.items():
                current_state.update(node_state)

                # Persist progress to DB
                async with AsyncSessionLocal() as session:
                    repo = ResearchRepository(session)
                    await repo.update_run_progress(
                        run_id=run_id,
                        status=current_state.get("status", "running"),
                        current_step=current_state.get("current_step", node_name),
                        progress_pct=current_state.get("progress_pct", 50),
                        step_timings=current_state.get("step_timings", {}),
                    )

                    # If search node finished, persist discovered sources
                    if node_name == "search" and current_state.get("search_results"):
                        await repo.add_sources(run_id, current_state["search_results"])

                await emit_progress(
                    current_state.get("status", "running"),
                    current_state.get("current_step", node_name),
                    current_state.get("progress_pct", 50),
                    score=current_state.get("final_score"),
                    timings=current_state.get("step_timings"),
                )

        # Finalize and persist full results
        total_time = round(time.time() - t_start, 2)
        total_words = len(current_state.get("final_report", "").split())

        async with AsyncSessionLocal() as session:
            repo = ResearchRepository(session)
            await repo.update_run_results(
                run_id=run_id,
                status="completed",
                current_step="Research dossier finalized",
                progress_pct=100,
                draft_report=current_state.get("draft_report"),
                final_report=current_state.get("final_report"),
                initial_score=current_state.get("initial_score"),
                final_score=current_state.get("final_score"),
                critique_feedback=current_state.get("critique_feedback"),
                initial_critique=current_state.get("initial_critique"),
                synthesized_notes=current_state.get("synthesized_notes"),
                revision_count=current_state.get("revision_count", 0),
                total_words=total_words,
                elapsed_seconds=total_time,
                step_timings=current_state.get("step_timings", {}),
            )

        await emit_progress("completed", "Research dossier finalized", 100, score=current_state.get("final_score"))

    except Exception as e:
        total_time = round(time.time() - t_start, 2)
        error_str = str(e)
        async with AsyncSessionLocal() as session:
            repo = ResearchRepository(session)
            await repo.update_run_progress(
                run_id=run_id,
                status="failed",
                current_step="Execution failed",
                progress_pct=100,
                error_message=error_str,
            )

        err_event = {
            "run_id": run_id,
            "status": "failed",
            "current_step": "Execution failed",
            "progress_pct": 100,
            "error_message": error_str,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await event_bus.emit(run_id, err_event)
