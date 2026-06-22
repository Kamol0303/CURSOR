"""Unit tests for exam scoring logic."""

from app.models.academics import ExamQuestion


def _score(questions: list[ExamQuestion], answers: dict[str, str]) -> tuple[float, float]:
    score = 0.0
    max_score = sum(q.points for q in questions)
    for q in questions:
        if answers.get(str(q.id), "").strip().lower() == q.correct_answer.strip().lower():
            score += q.points
    return score, max_score


def test_exam_scoring_all_correct():
    q1 = ExamQuestion(question_text="2+2?", correct_answer="4", points=2.0)
    q1.id = __import__("uuid").uuid4()
    q2 = ExamQuestion(question_text="Capital?", correct_answer="Tashkent", points=3.0)
    q2.id = __import__("uuid").uuid4()
    answers = {str(q1.id): "4", str(q2.id): "Tashkent"}
    score, max_score = _score([q1, q2], answers)
    assert score == 5.0
    assert max_score == 5.0


def test_exam_scoring_partial():
    q1 = ExamQuestion(question_text="2+2?", correct_answer="4", points=2.0)
    q1.id = __import__("uuid").uuid4()
    answers = {str(q1.id): "5"}
    score, max_score = _score([q1], answers)
    assert score == 0.0
    assert max_score == 2.0
