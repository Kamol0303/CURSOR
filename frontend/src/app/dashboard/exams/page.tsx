"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { PermissionGate } from "@/components/PermissionGate";
import { apiFetch } from "@/lib/api";

type Exam = {
  id: string;
  title: string;
  pass_score: number;
  duration_minutes: number;
  is_published: boolean;
  question_count: number;
};

export default function ExamsPage() {
  const t = useTranslations("exams");
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [subjects, setSubjects] = useState<{ id: string; name_uz: string }[]>([]);

  const load = useCallback(() => {
    setLoading(true);
    apiFetch<Exam[]>("/exams")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setExams(res.data);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    apiFetch<{ id: string; name_uz: string }[]>("/subjects").then((res) => {
      if (res.success && Array.isArray(res.data)) {
        setSubjects(res.data);
        if (res.data[0]) setSubjectId(res.data[0].id);
      }
    });
  }, [load]);

  const createExam = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subjectId) return;
    await apiFetch("/exams", {
      method: "POST",
      body: JSON.stringify({
        title,
        subject_id: subjectId,
        questions: [
          {
            question_text: t("defaultQuestion"),
            options_json: ["A", "B", "C", "D"],
            correct_answer: "A",
            points: 1,
          },
        ],
      }),
    });
    setTitle("");
    load();
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
      </div>
      <PermissionGate permission="exams.create">
        <form onSubmit={createExam} className="bg-white p-4 rounded-xl border space-y-3">
          <input
            className="w-full border rounded-lg px-3 py-2"
            placeholder={t("examTitle")}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <select className="w-full border rounded-lg px-3 py-2" value={subjectId} onChange={(e) => setSubjectId(e.target.value)}>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>{s.name_uz}</option>
            ))}
          </select>
          <button type="submit" className="px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm">
            {t("create")}
          </button>
        </form>
      </PermissionGate>
      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {exams.map((exam) => (
            <div key={exam.id} className="bg-white border rounded-xl p-4">
              <h3 className="font-semibold">{exam.title}</h3>
              <p className="text-sm text-gray-500">
                {t("questions")}: {exam.question_count} · {t("passScore")}: {exam.pass_score}%
              </p>
              <span className={`text-xs px-2 py-0.5 rounded ${exam.is_published ? "bg-green-100 text-green-800" : "bg-gray-100"}`}>
                {exam.is_published ? t("published") : t("draft")}
              </span>
            </div>
          ))}
          {exams.length === 0 && <p className="text-gray-400">{t("empty")}</p>}
        </div>
      )}
    </div>
  );
}
