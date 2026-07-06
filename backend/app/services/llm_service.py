"""LLM helpers — BazaarLink gateway (OpenAI-compatible) with mock fallback."""

from __future__ import annotations

import json
import re

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.exams import ExamQuestionCreate


def resolve_llm_settings() -> tuple[str, str, str]:
    """Return (api_key, base_url, model) for chat completions."""
    api_key = (settings.LLM_API_KEY or settings.OPENAI_API_KEY or "").strip()
    if not api_key:
        return "", "", ""

    if settings.LLM_API_KEY:
        base_url = settings.LLM_BASE_URL.rstrip("/")
        model = settings.LLM_MODEL
        if "/" not in model and not model.startswith("auto:"):
            model = f"openai/{model}"
    else:
        base_url = "https://api.openai.com/v1"
        model = settings.OPENAI_MODEL

    return api_key, base_url, model


def llm_provider_label() -> str:
    api_key, base_url, _ = resolve_llm_settings()
    if not api_key or not settings.AI_ENABLED:
        return "mock"
    if "bazaarlink" in base_url.lower():
        return "bazaarlink"
    return "openai"


async def chat_json_completion(
    *,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.4,
    timeout: float = 90.0,
) -> str:
    api_key, base_url, model = resolve_llm_settings()
    if not api_key or not settings.AI_ENABLED:
        raise HTTPException(status_code=503, detail={"code": "AI_NOT_CONFIGURED"})

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": temperature,
            },
        )
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail={"code": "AI_PROVIDER_ERROR"})
    return response.json()["choices"][0]["message"]["content"]


def _build_exam_prompt(
    *,
    subject_name: str,
    topic: str,
    question_count: int,
    difficulty: str,
    locale: str,
) -> str:
    lang = {"uz": "Uzbek", "ru": "Russian", "en": "English"}.get(locale, "Uzbek")
    return f"""Generate exactly {question_count} multiple-choice exam questions for subject "{subject_name}" on topic "{topic}".
Difficulty: {difficulty}. Write question text in {lang}.

Return ONLY valid JSON with this shape:
{{
  "questions": [
    {{
      "question_text": "string",
      "options_json": ["option A", "option B", "option C", "option D"],
      "correct_answer": "exact option text that is correct",
      "points": 1.0,
      "order_index": 0
    }}
  ]
}}

Rules:
- Each question must have 3-5 options in options_json.
- correct_answer must exactly match one option string.
- No personal data, no harmful content.
- order_index starts at 0 and increments.
"""


def _build_lesson_prompt(
    *,
    subject_name: str,
    topic: str,
    content_type: str,
    locale: str,
    max_slides: int,
    max_rounds: int,
) -> str:
    lang = {"uz": "Uzbek", "ru": "Russian", "en": "English"}.get(locale, "Uzbek")
    if content_type == "game":
        return f"""Create an educational classroom game for subject "{subject_name}" on topic "{topic}".
Write all learner-facing text in {lang}. Max {max_rounds} rounds.

Return ONLY valid JSON:
{{
  "title": "short game title",
  "rules": "how to play in class",
  "rounds": [
    {{
      "question": "challenge for students",
      "hint": "optional hint",
      "answer": "expected answer"
    }}
  ]
}}
"""
    return f"""Create a classroom presentation for subject "{subject_name}" on topic "{topic}".
Write all slide text in {lang}. Max {max_slides} slides.

Return ONLY valid JSON:
{{
  "title": "presentation title",
  "slides": [
    {{
      "title": "slide heading",
      "bullets": ["point 1", "point 2"],
      "speaker_notes": "what the teacher says"
    }}
  ]
}}
"""


def generate_questions_mock(
    *,
    topic: str,
    question_count: int,
    difficulty: str,
) -> list[ExamQuestionCreate]:
    questions: list[ExamQuestionCreate] = []
    for i in range(question_count):
        option_a = f"{topic} — A ({difficulty})"
        questions.append(
            ExamQuestionCreate(
                question_text=f"{topic}: savol {i + 1}?",
                options_json=[option_a, f"Variant B {i + 1}", f"Variant C {i + 1}", f"Variant D {i + 1}"],
                correct_answer=option_a,
                points=1.0,
                order_index=i,
            )
        )
    return questions


def generate_lesson_mock(*, topic: str, content_type: str, subject_name: str) -> dict:
    if content_type == "game":
        return {
            "title": f"{subject_name}: {topic} o'yini",
            "rules": "Jamoa bo'ling, savollarga javob bering.",
            "rounds": [
                {
                    "question": f"{topic} haqida savol {i + 1}",
                    "hint": "O'ylab ko'ring",
                    "answer": f"Javob {i + 1}",
                }
                for i in range(3)
            ],
        }
    return {
        "title": f"{subject_name}: {topic}",
        "slides": [
            {
                "title": f"Kirish — {topic}",
                "bullets": [f"{topic} nima?", f"Nega {subject_name} muhim?"],
                "speaker_notes": "Talabalarni jalb qiling.",
            },
            {
                "title": f"Asosiy qism — {topic}",
                "bullets": ["Tushuncha 1", "Tushuncha 2", "Misol"],
                "speaker_notes": "Misollar bilan tushuntiring.",
            },
            {
                "title": "Xulosa",
                "bullets": ["Asosiy fikrlar", "Savollar uchun vaqt"],
                "speaker_notes": "Qisqa takrorlash.",
            },
        ],
    }


def _clean_json_payload(raw: str) -> dict:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail={"code": "AI_INVALID_JSON"}) from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=502, detail={"code": "AI_INVALID_RESPONSE"})
    return payload


def _parse_questions_payload(raw: str) -> list[ExamQuestionCreate]:
    payload = _clean_json_payload(raw)
    items = payload.get("questions")
    if not isinstance(items, list) or not items:
        raise HTTPException(status_code=502, detail={"code": "AI_INVALID_RESPONSE"})

    questions: list[ExamQuestionCreate] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        options = item.get("options_json")
        if not isinstance(options, list) or len(options) < 2:
            raise HTTPException(status_code=502, detail={"code": "AI_INVALID_RESPONSE"})
        correct = str(item.get("correct_answer", "")).strip()
        if correct not in [str(o) for o in options]:
            raise HTTPException(status_code=502, detail={"code": "AI_INVALID_RESPONSE"})
        questions.append(
            ExamQuestionCreate(
                question_text=str(item.get("question_text", "")).strip(),
                options_json=[str(o) for o in options],
                correct_answer=correct,
                points=float(item.get("points", 1.0)),
                order_index=int(item.get("order_index", idx)),
            )
        )
    if not questions:
        raise HTTPException(status_code=502, detail={"code": "AI_INVALID_RESPONSE"})
    return questions


def _parse_lesson_payload(raw: str, *, content_type: str) -> dict:
    payload = _clean_json_payload(raw)
    title = str(payload.get("title", "")).strip()
    if not title:
        raise HTTPException(status_code=502, detail={"code": "AI_INVALID_RESPONSE"})

    if content_type == "game":
        rounds = payload.get("rounds")
        if not isinstance(rounds, list) or not rounds:
            raise HTTPException(status_code=502, detail={"code": "AI_INVALID_RESPONSE"})
        return {
            "title": title,
            "rules": str(payload.get("rules", "")).strip(),
            "rounds": rounds,
        }

    slides = payload.get("slides")
    if not isinstance(slides, list) or not slides:
        raise HTTPException(status_code=502, detail={"code": "AI_INVALID_RESPONSE"})
    return {"title": title, "slides": slides}


async def generate_exam_questions(
    *,
    subject_name: str,
    topic: str,
    question_count: int,
    difficulty: str,
    locale: str,
) -> list[ExamQuestionCreate]:
    if question_count < 1 or question_count > settings.AI_EXAM_MAX_QUESTIONS:
        raise HTTPException(status_code=422, detail={"code": "QUESTION_COUNT_OUT_OF_RANGE"})

    api_key, _, _ = resolve_llm_settings()
    if api_key and settings.AI_ENABLED and settings.AI_EXAM_ENABLED:
        prompt = _build_exam_prompt(
            subject_name=subject_name,
            topic=topic,
            question_count=question_count,
            difficulty=difficulty,
            locale=locale,
        )
        content = await chat_json_completion(
            system_prompt="You are an educational assessment author. Output JSON only.",
            user_prompt=prompt,
        )
        return _parse_questions_payload(content)

    return generate_questions_mock(topic=topic, question_count=question_count, difficulty=difficulty)


async def generate_lesson_content(
    *,
    subject_name: str,
    topic: str,
    content_type: str,
    locale: str,
) -> dict:
    if content_type not in {"presentation", "game"}:
        raise HTTPException(status_code=422, detail={"code": "INVALID_CONTENT_TYPE"})

    api_key, _, _ = resolve_llm_settings()
    if api_key and settings.AI_ENABLED:
        prompt = _build_lesson_prompt(
            subject_name=subject_name,
            topic=topic,
            content_type=content_type,
            locale=locale,
            max_slides=settings.AI_LESSON_MAX_SLIDES,
            max_rounds=settings.AI_LESSON_MAX_ROUNDS,
        )
        content = await chat_json_completion(
            system_prompt="You are an expert teacher assistant. Output JSON only.",
            user_prompt=prompt,
            temperature=0.5,
        )
        return _parse_lesson_payload(content, content_type=content_type)

    return generate_lesson_mock(topic=topic, content_type=content_type, subject_name=subject_name)
