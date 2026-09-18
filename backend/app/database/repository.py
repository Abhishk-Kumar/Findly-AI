from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc, func, delete, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models import (
    ResearchRun,
    ResearchSource,
    BookmarkedFinding,
    QAMessage,
)


class ResearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_run(
        self,
        topic: str,
        depth: str = "Standard",
        tone: str = "Formal",
        quality_bar: int = 7,
        max_revisions: int = 3,
        run_id: Optional[str] = None,
    ) -> ResearchRun:
        run_data = {
            "topic": topic,
            "depth": depth,
            "tone": tone,
            "quality_bar": quality_bar,
            "max_revisions": max_revisions,
            "status": "queued",
            "current_step": "Queued",
            "progress_pct": 5,
        }
        if run_id:
            run_data["id"] = run_id

        run = ResearchRun(**run_data)
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def get_run_by_id(self, run_id: str, load_relations: bool = True) -> Optional[ResearchRun]:
        stmt = select(ResearchRun).where(ResearchRun.id == run_id)
        if load_relations:
            stmt = stmt.options(
                selectinload(ResearchRun.sources),
                selectinload(ResearchRun.bookmarks),
                selectinload(ResearchRun.qa_messages),
            )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_runs(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ResearchRun]:
        stmt = (
            select(ResearchRun)
            .options(selectinload(ResearchRun.sources))
            .order_by(desc(ResearchRun.created_at))
            .limit(limit)
            .offset(offset)
        )
        if search:
            stmt = stmt.where(ResearchRun.topic.ilike(f"%{search}%"))
        if status:
            stmt = stmt.where(ResearchRun.status == status)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_run_progress(
        self,
        run_id: str,
        status: str,
        current_step: str,
        progress_pct: int,
        step_timings: Optional[Dict[str, float]] = None,
        error_message: Optional[str] = None,
    ) -> Optional[ResearchRun]:
        run = await self.get_run_by_id(run_id, load_relations=False)
        if not run:
            return None

        run.status = status
        run.current_step = current_step
        run.progress_pct = progress_pct
        if step_timings is not None:
            run.step_timings = {**run.step_timings, **step_timings}
        if error_message:
            run.error_message = error_message
        run.updated_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def update_run_results(
        self,
        run_id: str,
        status: str,
        current_step: str,
        progress_pct: int,
        draft_report: Optional[str] = None,
        final_report: Optional[str] = None,
        initial_score: Optional[int] = None,
        final_score: Optional[int] = None,
        critique_feedback: Optional[str] = None,
        initial_critique: Optional[str] = None,
        synthesized_notes: Optional[str] = None,
        raw_search_summary: Optional[str] = None,
        revision_count: Optional[int] = None,
        total_words: Optional[int] = None,
        elapsed_seconds: Optional[float] = None,
        step_timings: Optional[Dict[str, float]] = None,
        error_message: Optional[str] = None,
    ) -> Optional[ResearchRun]:
        run = await self.get_run_by_id(run_id, load_relations=False)
        if not run:
            return None

        run.status = status
        run.current_step = current_step
        run.progress_pct = progress_pct

        if draft_report is not None:
            run.draft_report = draft_report
        if final_report is not None:
            run.final_report = final_report
        if initial_score is not None:
            run.initial_score = initial_score
        if final_score is not None:
            run.final_score = final_score
        if critique_feedback is not None:
            run.critique_feedback = critique_feedback
        if initial_critique is not None:
            run.initial_critique = initial_critique
        if synthesized_notes is not None:
            run.synthesized_notes = synthesized_notes
        if raw_search_summary is not None:
            run.raw_search_summary = raw_search_summary
        if revision_count is not None:
            run.revision_count = revision_count
        if total_words is not None:
            run.total_words = total_words
        if elapsed_seconds is not None:
            run.elapsed_seconds = elapsed_seconds
        if step_timings is not None:
            run.step_timings = {**run.step_timings, **step_timings}
        if error_message is not None:
            run.error_message = error_message

        run.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def add_sources(self, run_id: str, sources_data: List[Dict[str, Any]]) -> List[ResearchSource]:
        sources = []
        for s in sources_data:
            source = ResearchSource(
                run_id=run_id,
                url=s.get("url", ""),
                title=s.get("title", "Untitled Source"),
                domain=s.get("domain", ""),
                snippet=s.get("snippet", ""),
                scraped_content=s.get("scraped_content"),
                status=s.get("status", "discovered"),
                error_reason=s.get("error_reason"),
                relevance_score=s.get("relevance_score"),
                char_count=s.get("char_count", 0),
            )
            self.session.add(source)
            sources.append(source)
        await self.session.commit()
        return sources

    async def update_source_status(
        self,
        source_id: str,
        status: str,
        scraped_content: Optional[str] = None,
        error_reason: Optional[str] = None,
        char_count: Optional[int] = None,
    ) -> Optional[ResearchSource]:
        stmt = select(ResearchSource).where(ResearchSource.id == source_id)
        result = await self.session.execute(stmt)
        source = result.scalar_one_or_none()
        if not source:
            return None

        source.status = status
        if scraped_content is not None:
            source.scraped_content = scraped_content
        if error_reason is not None:
            source.error_reason = error_reason
        if char_count is not None:
            source.char_count = char_count

        await self.session.commit()
        await self.session.refresh(source)
        return source

    async def delete_run(self, run_id: str) -> bool:
        stmt = select(ResearchRun).where(ResearchRun.id == run_id)
        result = await self.session.execute(stmt)
        run = result.scalar_one_or_none()
        if not run:
            return False
        await self.session.delete(run)
        await self.session.commit()
        return True

    # Bookmarks
    async def add_bookmark(
        self,
        run_id: str,
        topic: str,
        quote_text: str,
        section_title: Optional[str] = None,
        source_url: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> BookmarkedFinding:
        bookmark = BookmarkedFinding(
            run_id=run_id,
            topic=topic,
            quote_text=quote_text,
            section_title=section_title,
            source_url=source_url,
            notes=notes,
        )
        self.session.add(bookmark)
        await self.session.commit()
        await self.session.refresh(bookmark)
        return bookmark

    async def list_bookmarks(self, search: Optional[str] = None, limit: int = 100) -> List[BookmarkedFinding]:
        stmt = select(BookmarkedFinding).order_by(desc(BookmarkedFinding.created_at)).limit(limit)
        if search:
            stmt = stmt.where(
                (BookmarkedFinding.quote_text.ilike(f"%{search}%"))
                | (BookmarkedFinding.topic.ilike(f"%{search}%"))
                | (BookmarkedFinding.notes.ilike(f"%{search}%"))
            )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_bookmark(self, bookmark_id: str) -> bool:
        stmt = select(BookmarkedFinding).where(BookmarkedFinding.id == bookmark_id)
        result = await self.session.execute(stmt)
        bm = result.scalar_one_or_none()
        if not bm:
            return False
        await self.session.delete(bm)
        await self.session.commit()
        return True

    # Q&A Messages
    async def add_qa_message(
        self,
        run_id: str,
        question: str,
        answer: str,
        is_grounded: bool = True,
    ) -> QAMessage:
        qa = QAMessage(
            run_id=run_id,
            question=question,
            answer=answer,
            is_grounded=is_grounded,
        )
        self.session.add(qa)
        await self.session.commit()
        await self.session.refresh(qa)
        return qa

    async def list_qa_messages(self, run_id: str) -> List[QAMessage]:
        stmt = select(QAMessage).where(QAMessage.run_id == run_id).order_by(QAMessage.created_at)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Dashboard Statistics
    async def get_stats(self) -> Dict[str, Any]:
        total_runs = await self.session.scalar(select(func.count(ResearchRun.id)))
        completed_runs = await self.session.scalar(
            select(func.count(ResearchRun.id)).where(ResearchRun.status == "completed")
        )
        failed_runs = await self.session.scalar(
            select(func.count(ResearchRun.id)).where(ResearchRun.status == "failed")
        )
        avg_score = await self.session.scalar(
            select(func.avg(ResearchRun.final_score)).where(ResearchRun.final_score.isnot(None))
        )
        total_sources = await self.session.scalar(select(func.count(ResearchSource.id)))
        total_bookmarks = await self.session.scalar(select(func.count(BookmarkedFinding.id)))
        avg_duration = await self.session.scalar(
            select(func.avg(ResearchRun.elapsed_seconds)).where(ResearchRun.status == "completed")
        )

        return {
            "total_runs": total_runs or 0,
            "completed_runs": completed_runs or 0,
            "failed_runs": failed_runs or 0,
            "avg_score": round(float(avg_score), 1) if avg_score is not None else 0.0,
            "total_sources": total_sources or 0,
            "total_bookmarks": total_bookmarks or 0,
            "avg_duration_seconds": round(float(avg_duration), 1) if avg_duration is not None else 0.0,
        }
