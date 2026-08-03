"""Tests for internal research dashboard API."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def research_client():
    from api.routes.internal_research import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_dashboard_hidden_by_default(research_client):
    res = research_client.get("/internal/research/v1/dashboard")
    assert res.status_code == 404


def test_dashboard_when_enabled(monkeypatch, research_client):
    monkeypatch.setenv("RESEARCH_INTERNAL_API_ENABLED", "true")
    from research_platform.config import get_research_settings

    get_research_settings.cache_clear()
    res = research_client.get("/internal/research/v1/dashboard")
    assert res.status_code == 200
    body = res.json()
    assert body["promotion_policy"] == "manual_only"
    get_research_settings.cache_clear()


def test_dashboard_snapshot_shape(monkeypatch):
    monkeypatch.setenv("RESEARCH_INTERNAL_API_ENABLED", "true")
    from research_platform.config import get_research_settings
    from research_platform.dashboard.snapshot import build_dashboard_snapshot

    get_research_settings.cache_clear()
    snap = build_dashboard_snapshot()
    assert snap["promotion_policy"] == "manual_only"
    assert "scheduler" in snap
    get_research_settings.cache_clear()
