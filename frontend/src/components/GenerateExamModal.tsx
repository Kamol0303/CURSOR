"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

type Props = {
  subjects: { id: string; name_uz: string }[];
  onClose: () => void;
  onGenerated: (examId: string) => void;
};

export function GenerateExamModal({ subjects, onClose, onGenerated }: Props) {
  const t = useTranslations("exams");
  const [subjectId, setSubjectId] = useState(subjects[0]?.id || "");
  const [topic, setTopic] = useState("");
  const [questionCount, setQuestionCount] = useState(5);
  const [difficulty, setDifficulty] = useState("medium");
  const [title, setTitle] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subjectId || !topic.trim()) return;
    setSaving(true);
    setError(null);
    const res = await apiFetch<{ id: string }>("/exams/generate", {
      method: "POST",
      body: JSON.stringify({
        subject_id: subjectId,
        topic: topic.trim(),
        question_count: questionCount,
        difficulty,
        title: title.trim() || undefined,
      }),
    });
    setSaving(false);
    if (!res.success || !res.data?.id) {
      setError(t("generateError"));
      return;
    }
    onGenerated(res.data.id);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <form onSubmit={submit} className="p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-naqsh-primary">{t("generateTitle")}</h3>
            <button type="button" onClick={onClose} className="text-gray-400 hover:text-gray-600">
              ✕
            </button>
          </div>
          <p className="text-sm text-gray-500">{t("generateHint")}</p>
          <div>
            <label className="block text-sm font-medium mb-1">{t("subject")}</label>
            <select
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={subjectId}
              onChange={(e) => setSubjectId(e.target.value)}
              required
            >
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name_uz}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t("topic")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder={t("topicPlaceholder")}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">{t("questionCount")}</label>
              <input
                type="number"
                min={1}
                max={30}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={questionCount}
                onChange={(e) => setQuestionCount(Number(e.target.value))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">{t("difficulty")}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
              >
                <option value="easy">{t("difficultyEasy")}</option>
                <option value="medium">{t("difficultyMedium")}</option>
                <option value="hard">{t("difficultyHard")}</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t("examTitle")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={t("titleOptional")}
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose} className="flex-1 px-4 py-2 border rounded-lg text-sm">
              {t("cancel")}
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 px-4 py-2 bg-naqsh-accent text-white rounded-lg text-sm disabled:opacity-50"
            >
              {saving ? t("generating") : t("generate")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
