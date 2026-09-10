import asyncio
import time
from contextlib import contextmanager
from unittest.mock import Mock

import httpx
import pytest
from app.api import chat as chat_api
from app.database import get_db
from app.schemas.chat import ChatMode, ChatResponse
from fastapi import FastAPI


@pytest.fixture
def api(monkeypatch):
    app = FastAPI()
    app.include_router(chat_api.router)
    app.dependency_overrides[get_db] = lambda: Mock()
    sessions = []

    @contextmanager
    def session():
        db = Mock()
        sessions.append(db)
        yield db

    monkeypatch.setattr(chat_api, "SessionLocal", session, raising=False)
    return app, sessions


@pytest.mark.asyncio
async def test_pipeline_does_not_block_event_loop(api, monkeypatch):
    app, sessions = api
    def process(*args, **kwargs):
        time.sleep(0.12)
        return ChatResponse(answer="No information", mode=ChatMode.NATURAL, confidence=0)
    monkeypatch.setattr(chat_api, "get_chatbot_service", lambda db: Mock(process_message=process))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        started = time.perf_counter()
        pending = asyncio.create_task(client.post('/api/chat', json={"message": "Python?"}))
        await asyncio.sleep(0.02)
        assert time.perf_counter() - started < 0.09
        assert (await pending).status_code == 200
        assert len(sessions) == 1


@pytest.mark.asyncio
async def test_overload_is_bounded_and_returns_retry_header(api, monkeypatch):
    app, _ = api
    def process(*args, **kwargs):
        time.sleep(0.12)
        return ChatResponse(answer="No information", mode=ChatMode.NATURAL, confidence=0)
    monkeypatch.setattr(chat_api, "get_chatbot_service", lambda db: Mock(process_message=process))
    monkeypatch.setattr(chat_api, "chat_slots", asyncio.Semaphore(1), raising=False)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        responses = await asyncio.gather(*[client.post('/api/chat', json={"message": "Python?"}) for _ in range(3)])
    assert sorted(r.status_code for r in responses) == [200, 503, 503]
    assert all(r.headers.get('retry-after') for r in responses if r.status_code == 503)


@pytest.mark.asyncio
async def test_error_does_not_expose_internal_exception(api, monkeypatch):
    app, _ = api
    monkeypatch.setattr(chat_api, "get_chatbot_service", Mock(side_effect=RuntimeError("private-server-address")))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post('/api/chat', json={"message": "Python?"})
    assert response.status_code == 500
    assert "private-server-address" not in response.text


@pytest.mark.asyncio
async def test_startup_warms_model_before_readiness(monkeypatch):
    from app import main
    embedding = Mock()
    monkeypatch.setattr(main, "get_embedding_service", lambda: embedding, raising=False)
    monkeypatch.setattr(main, "get_generator_service", Mock(), raising=False)
    monkeypatch.setattr(main, "get_verifier_service", Mock(), raising=False)
    await main.startup_event()
    embedding.generate_embedding.assert_called_once()
    assert main.app.state.chat_ready is True


@pytest.mark.asyncio
async def test_failed_warmup_does_not_report_ready(monkeypatch):
    from app import main
    main.app.state.chat_ready = False
    monkeypatch.setattr(main, "get_embedding_service", Mock(side_effect=RuntimeError("model missing")), raising=False)
    with pytest.raises(RuntimeError):
        await main.startup_event()
    assert main.app.state.chat_ready is False


@pytest.mark.asyncio
async def test_rate_limit_is_http_429_through_real_middleware(api):
    from app.middleware.rate_limiter import DailyMonthlyRateLimiter
    app, _ = api
    app.add_middleware(DailyMonthlyRateLimiter, mode_limits={"natural": {"daily": 0, "monthly": 0}})
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        response = await client.post('/api/chat', json={"message": "Python?"})
    assert response.status_code == 429
    assert response.headers['retry-after']
    assert response.headers['x-ratelimit-daily-remaining'] == '0'


@pytest.mark.asyncio
async def test_middleware_preserves_body_and_rejects_unknown_modes(api, monkeypatch):
    from app.middleware.rate_limiter import DailyMonthlyRateLimiter
    app, _ = api
    process = Mock(return_value=ChatResponse(answer="No information", mode=ChatMode.NATURAL, confidence=0))
    monkeypatch.setattr(chat_api, "get_chatbot_service", lambda db: Mock(process_message=process))
    app.add_middleware(DailyMonthlyRateLimiter, mode_limits={"natural": {"daily": 10, "monthly": 20}})
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        success = await client.post('/api/chat', json={"message": "Python?", "mode": "natural"})
        invalid = await client.post('/api/chat', json={"message": "Python?", "mode": "invalid"})
    assert success.status_code == 200
    assert success.headers['x-ratelimit-daily-remaining'] == '9'
    assert invalid.status_code == 422
    process.assert_called_once_with("Python?", ChatMode.NATURAL)
