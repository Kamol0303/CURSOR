"""Unit tests for LLM service (no external API calls)."""

from __future__ import annotations

import pytest

from app.core.config import settings
from app.services import llm_service


def test_list_llm_providers_full_chain(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "sk-bl-test")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "gemini-test-key")
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", "mistral-test-key")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")

    providers = llm_service.list_llm_providers()
    assert len(providers) == 3
    assert [p.name for p in providers] == ["bazaarlink", "gemini", "mistral"]
    assert providers[2].model == settings.MISTRAL_MODEL


def test_list_llm_providers_bazaarlink_then_gemini(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "sk-bl-test")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "gemini-test-key")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")

    providers = llm_service.list_llm_providers()
    assert len(providers) == 2
    assert providers[0].name == "bazaarlink"
    assert providers[1].name == "gemini"
    assert providers[1].model == settings.GEMINI_MODEL


def test_resolve_llm_settings_bazaarlink_model_prefix(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "sk-bl-test")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(settings, "LLM_BASE_URL", "https://bazaarlink.ai/api/v1")
    monkeypatch.setattr(settings, "LLM_MODEL", "gpt-4o-mini")

    api_key, base_url, model = llm_service.resolve_llm_settings()
    assert api_key == "sk-bl-test"
    assert base_url == "https://bazaarlink.ai/api/v1"
    assert model == "openai/gpt-4o-mini"


def test_llm_provider_label_with_fallback(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "sk-bl-test")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "gemini-key")
    monkeypatch.setattr(settings, "AI_ENABLED", True)
    assert llm_service.llm_provider_label() == "bazaarlink+fallback"


def test_llm_provider_label_mock_when_no_key(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    assert llm_service.llm_provider_label() == "mock"


@pytest.mark.asyncio
async def test_generate_lesson_mock_presentation(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(settings, "AI_ENABLED", True)

    content, provider = await llm_service.generate_lesson_content(
        subject_name="Ingliz tili",
        topic="Present Simple",
        content_type="presentation",
        locale="uz",
    )
    assert provider == "mock"
    assert "slides" in content
    assert len(content["slides"]) >= 1


@pytest.mark.asyncio
async def test_generate_lesson_mock_game(monkeypatch):
    monkeypatch.setattr(settings, "LLM_API_KEY", "")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(settings, "AI_ENABLED", True)

    content, provider = await llm_service.generate_lesson_content(
        subject_name="Informatika",
        topic="Algoritmlar",
        content_type="game",
        locale="uz",
    )
    assert provider == "mock"
    assert "rounds" in content
    assert len(content["rounds"]) >= 1
