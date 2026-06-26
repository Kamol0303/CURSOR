"""LLM helpers for AI exam question generation."""

from __future__ import annotations

import json
import re

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.exams import ExamQuestionCreate


def _build_prompt(
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


def _parse_questions_payload(raw: str) -> list[ExamQuestionCreate]:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail={"code": "AI_INVALID_JSON"}) from exc

    items = payload.get("questions") if isinstance(payload, dict) else None
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

    if settings.OPENAI_API_KEY and settings.AI_EXAM_ENABLED:
        prompt = _build_prompt(
            subject_name=subject_name,
            topic=topic,
            question_count=question_count,
            difficulty=difficulty,
            locale=locale,
        )
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are an educational assessment author. Output JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.4,
                },
            )
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail={"code": "AI_PROVIDER_ERROR"})
        content = response.json()["choices"][0]["message"]["content"]
        return _parse_questions_payload(content)

    return generate_questions_mock(topic=topic, question_count=question_count, difficulty=difficulty)
