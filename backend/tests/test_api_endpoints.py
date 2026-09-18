import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.app.main import app
from backend.app.database.models import Base
from backend.app.database.session import get_db

TEST_DB_PATH = "./test_api.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"


@pytest_asyncio.fixture(autouse=True)
async def test_db():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Also patch background runner's session maker to test database
    import backend.app.services.research_runner as runner_mod
    orig_session_maker = runner_mod.AsyncSessionLocal
    runner_mod.AsyncSessionLocal = async_session

    yield async_session

    app.dependency_overrides.clear()
    runner_mod.AsyncSessionLocal = orig_session_maker

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "Findly" in data["app"]


@pytest.mark.asyncio
async def test_research_run_creation_and_listing():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create run
        payload = {
            "topic": "Neuromorphic Computing Architectures",
            "depth": "Standard",
            "tone": "Technical",
            "quality_bar": 7,
            "max_revisions": 2,
        }
        create_resp = await client.post("/api/research", json=payload)
        assert create_resp.status_code == 201
        created = create_resp.json()
        assert created["id"] is not None
        assert created["topic"] == "Neuromorphic Computing Architectures"
        assert created["status"] in ("queued", "searching", "selecting_sources")

        run_id = created["id"]

        # Get details
        detail_resp = await client.get(f"/api/research/{run_id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["id"] == run_id

        # List runs
        list_resp = await client.get("/api/research?search=Neuromorphic")
        assert list_resp.status_code == 200
        runs = list_resp.json()
        assert len(runs) >= 1
        assert runs[0]["id"] == run_id


@pytest.mark.asyncio
async def test_bookmarks_and_stats_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create run
        run_resp = await client.post(
            "/api/research",
            json={"topic": "Direct Air Carbon Capture", "depth": "Quick", "tone": "Formal"},
        )
        assert run_resp.status_code == 201
        run_id = run_resp.json()["id"]

        # 2. Add bookmark
        bm_payload = {
            "quote_text": "Solid sorbent DAC achieved $150/ton energy costs at pilot scale.",
            "section_title": "Economic Feasibility",
            "source_url": "https://carbon-brief.org/dac-2026",
            "notes": "Cost inflection point metric",
        }
        bm_resp = await client.post(f"/api/research/{run_id}/bookmarks", json=bm_payload)
        assert bm_resp.status_code == 201
        bm = bm_resp.json()
        assert bm["id"] is not None
        assert "Solid sorbent" in bm["quote_text"]

        # 3. List bookmarks
        list_bm = await client.get("/api/bookmarks")
        assert list_bm.status_code == 200
        assert len(list_bm.json()) >= 1

        # 4. Get stats
        stats_resp = await client.get("/api/stats")
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert stats["total_runs"] >= 1
        assert stats["total_bookmarks"] >= 1

        # 5. Delete bookmark
        del_resp = await client.delete(f"/api/bookmarks/{bm['id']}")
        assert del_resp.status_code == 204
