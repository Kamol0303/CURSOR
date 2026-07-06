"""Unit tests for LLM service (no external API calls)."""

from __future__ import annotations

import pytest

from app.core.config import settings
from app.services import llm_service


def test_resolve_llm_settings_bazaarlink_model_prefix(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "sk-bl-test")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(settings, "LLM_BASE_URL", "https://bazaarlink.ai/api/v1")
    monkeypatch.setattr(settings, "LLM_MODEL", "gpt-4o-mini")

    api_key, base_url, model = llm_service.resolve_llm_settings()
    assert api_key == "sk-bl-test"
    assert base_url == "https://bazaarlink.ai/api/v1"
    assert model == "openai/gpt-4o-mini"


def test_llm_provider_label_mock_when_no_key(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    assert llm_service.llm_provider_label() == "mock"


@pytest.mark.asyncio
async def test_generate_lesson_mock_presentation(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(settings, "AI_ENABLED", True)

    content = await llm_service.generate_lesson_content(
        subject_name="Ingliz tili",
        topic="Present Simple",
        content_type="presentation",
        locale="uz",
    )
    assert "slides" in content
    assert len(content["slides"]) >= 1


@pytest.mark.asyncio
async def test_generate_lesson_mock_game(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(settings, "AI_ENABLED", True)

    content = await llm_service.generate_lesson_content(
        subject_name="Informatika",
        topic="Algoritmlar",
        content_type="game",
        locale="uz",
    )
    assert "rounds" in content
    assert len(content["rounds"]) >= 1
