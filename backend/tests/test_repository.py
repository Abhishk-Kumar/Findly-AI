import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.app.database.models import Base
from backend.app.database.repository import ResearchRepository

# In-memory SQLite for repository testing
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_run_crud_and_lifecycle(async_session: AsyncSession):
    repo = ResearchRepository(async_session)

    # 1. Create run
    run = await repo.create_run(
        topic="Solid State Batteries",
        depth="Deep",
        tone="Technical",
        quality_bar=8,
        max_revisions=2,
    )
    assert run.id is not None
    assert run.topic == "Solid State Batteries"
    assert run.status == "queued"
    assert run.progress_pct == 5

    # 2. Update progress
    updated = await repo.update_run_progress(
        run_id=run.id,
        status="searching",
        current_step="Executing search query",
        progress_pct=25,
        step_timings={"search": 1.25},
    )
    assert updated.status == "searching"
    assert updated.progress_pct == 25
    assert updated.step_timings["search"] == 1.25

    # 3. Add sources
    sources = await repo.add_sources(
        run.id,
        [
            {
                "url": "https://battery-tech.org/solid-state",
                "title": "Solid State Innovations",
                "domain": "battery-tech.org",
                "snippet": "New lithium metal anodes show 500 Wh/kg density.",
                "status": "discovered",
                "relevance_score": 0.95,
            }
        ],
    )
    assert len(sources) == 1

    # 4. Finalize results
    completed = await repo.update_run_results(
        run_id=run.id,
        status="completed",
        current_step="Completed",
        progress_pct=100,
        final_report="# Solid State Battery Dossier\nAnalysis of ceramic electrolyte interfaces.",
        initial_score=6,
        final_score=8,
        critique_feedback="Score: 8/10\nStrengths: Deep technical analysis",
        revision_count=1,
        total_words=250,
        elapsed_seconds=12.4,
    )
    assert completed.status == "completed"
    assert completed.final_score == 8
    assert completed.revision_count == 1

    # 5. List and filter
    all_runs = await repo.list_runs(search="Solid State")
    assert len(all_runs) == 1
    assert all_runs[0].topic == "Solid State Batteries"


@pytest.mark.asyncio
async def test_bookmarks_and_stats(async_session: AsyncSession):
    repo = ResearchRepository(async_session)
    run = await repo.create_run(topic="Synthetic Biology")

    # Bookmark a finding
    bm = await repo.add_bookmark(
        run_id=run.id,
        topic=run.topic,
        quote_text="CRISPR-Cas12b demonstrates zero off-target cleavage in human cells.",
        section_title="Precision Gene Editing",
        source_url="https://nature.com/articles/crispr",
        notes="Key benchmark for therapeutic index",
    )
    assert bm.id is not None
    assert "CRISPR-Cas12b" in bm.quote_text

    # List bookmarks
    bookmarks = await repo.list_bookmarks(search="CRISPR")
    assert len(bookmarks) == 1

    # Stats
    stats = await repo.get_stats()
    assert stats["total_runs"] == 1
    assert stats["total_bookmarks"] == 1

    # Delete bookmark
    deleted = await repo.delete_bookmark(bm.id)
    assert deleted is True
    assert len(await repo.list_bookmarks()) == 0
