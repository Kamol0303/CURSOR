"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardTitle,
  Spinner,
} from "@/components/ui";
import { apiFetch } from "@/lib/api";

type Question = {
  id: string;
  question_text: string;
  options_json: string[] | null;
};

type ExamDetail = {
  id: string;
  title: string;
  pass_score: number;
  duration_minutes: number;
  questions: Question[];
};

export default function StudentTakeExamPage() {
  const t = useTranslations("studentCabinet");
  const params = useParams();
  const router = useRouter();
  const examId = params.id as string;
  const [exam, setExam] = useState<ExamDetail | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ score: number; max_score: number; passed: boolean } | null>(null);

  useEffect(() => {
    apiFetch<ExamDetail>(`/exams/${examId}`)
      .then((res) => {
        if (res.success && res.data) setExam(res.data);
      })
      .finally(() => setLoading(false));
  }, [examId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!exam) return;
    setSubmitting(true);
    const res = await apiFetch<{ score: number; max_score: number; passed: boolean }>(`/exams/${examId}/submit`, {
      method: "POST",
      body: JSON.stringify({
        answers: exam.questions.map((q) => ({
          question_id: q.id,
          answer: answers[q.id] || "",
        })),
      }),
    });
    setSubmitting(false);
    if (res.success && res.data) {
      setResult(res.data);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-4">
        <Spinner label={t("loading")} className="py-16" />
      </div>
    );
  }

  if (!exam) {
    return (
      <div className="min-h-screen bg-background p-4 max-w-lg mx-auto">
        <Alert variant="danger">{t("examNotFound")}</Alert>
      </div>
    );
  }

  if (result) {
    return (
      <div className="min-h-screen bg-background p-4 max-w-lg mx-auto flex items-center">
        <Card className="w-full">
          <CardBody className="text-center space-y-4">
            <CardTitle>{t("examSubmitted")}</CardTitle>
            <p className="text-3xl font-semibold text-foreground">
              {result.score}/{result.max_score}
            </p>
            <Badge variant={result.passed ? "success" : "danger"}>
              {result.passed ? t("passed") : t("failed")}
            </Badge>
            <Button type="button" onClick={() => router.push("/student/dashboard")} className="mt-2">
              {t("backToDashboard")}
            </Button>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-naqsh-primary text-white px-4 py-5 shadow-sm">
        <Link href="/student/dashboard" className="text-small text-white/80 hover:text-white transition-colors">
          ← {t("back")}
        </Link>
        <h1 className="font-bold text-lg mt-2">{exam.title}</h1>
        <p className="text-caption text-white/70 mt-0.5">
          {t("passScore")}: {exam.pass_score}% · {exam.duration_minutes} min
        </p>
      </header>
      <form onSubmit={submit} className="p-4 max-w-lg mx-auto space-y-4">
        {exam.questions.map((q, idx) => (
          <Card key={q.id}>
            <CardBody>
              <p className="font-medium text-small text-foreground mb-4">
                {idx + 1}. {q.question_text}
              </p>
              <div className="space-y-2">
                {(q.options_json || []).map((opt) => (
                  <label
                    key={opt}
                    className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-small text-foreground cursor-pointer hover:bg-muted transition-colors"
                  >
                    <input
                      type="radio"
                      name={q.id}
                      value={opt}
                      checked={answers[q.id] === opt}
                      onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: opt }))}
                      required
                      className="accent-naqsh-primary"
                    />
                    {opt}
                  </label>
                ))}
              </div>
            </CardBody>
          </Card>
        ))}
        <Button type="submit" loading={submitting} className="w-full" size="lg">
          {submitting ? t("submitting") : t("submitExam")}
        </Button>
      </form>
    </div>
  );
}
