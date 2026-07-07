"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

type Subject = { id: string; name_uz: string; name_ru?: string; name_en?: string };
type Group = { id: string; name: string; subject_id: string };
type Slide = { title: string; bullets: string[]; speaker_notes?: string };
type Round = { question: string; hint?: string; answer: string };
type Material = {
  id: string;
  title: string;
  topic: string;
  content_type: string;
  status: string;
  content_json: { title?: string; slides?: Slide[]; rounds?: Round[]; rules?: string };
  subject_name_uz?: string;
};

function subjectLabel(subject: Subject, locale: string): string {
  if (locale === "ru" && subject.name_ru) return subject.name_ru;
  if (locale === "en" && subject.name_en) return subject.name_en;
  return subject.name_uz;
}

function mapError(t: ReturnType<typeof useTranslations<"lessonStart">>, code?: string): string {
  if (!code) return t("errors.UNKNOWN");
  const key = `errors.${code}` as const;
  return t.has(key) ? t(key) : t("errors.UNKNOWN");
}

export default function TeacherLessonStartPage() {
  const t = useTranslations("lessonStart");
  const locale = useLocale();
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [subjectId, setSubjectId] = useState("");
  const [groupId, setGroupId] = useState("");
  const [topic, setTopic] = useState("");
  const [contentType, setContentType] = useState<"presentation" | "game">("presentation");
  const [material, setMaterial] = useState<Material | null>(null);
  const [history, setHistory] = useState<Material[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiFetch<Subject[]>("/teacher/subjects"),
      apiFetch<Group[]>("/teacher/groups"),
      apiFetch<Material[]>("/teacher/lesson-materials?per_page=10"),
    ]).then(([subjRes, groupRes, histRes]) => {
      if (!subjRes.success) {
        setLoadError(mapError(t, subjRes.error?.code));
      } else if (subjRes.data) {
        setSubjects(subjRes.data);
        setSubjectId(subjRes.data[0]?.id || "");
      }
      if (groupRes.success && groupRes.data) setGroups(groupRes.data);
      if (histRes.success && histRes.data) setHistory(histRes.data);
      setLoading(false);
    });
  }, [t]);

  const filteredGroups = groups.filter((g) => !subjectId || g.subject_id === subjectId);

  const generate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subjectId || !topic.trim()) return;
    setGenerating(true);
    setError(null);
    const res = await apiFetch<Material>("/teacher/lesson-materials/generate", {
      method: "POST",
      body: JSON.stringify({
        subject_id: subjectId,
        topic: topic.trim(),
        content_type: contentType,
        group_id: groupId || undefined,
        locale,
      }),
    });
    setGenerating(false);
    if (!res.success || !res.data) {
      setError(mapError(t, res.error?.code));
      return;
    }
    setMaterial(res.data);
    setHistory((prev) => [res.data!, ...prev.filter((h) => h.id !== res.data!.id)]);
  };

  const startLesson = async () => {
    if (!material) return;
    setStarting(true);
    setError(null);
    const res = await apiFetch<Material>(`/teacher/lesson-materials/${material.id}/start`, {
      method: "POST",
    });
    setStarting(false);
    if (!res.success || !res.data) {
      setError(mapError(t, res.error?.code));
      return;
    }
    setMaterial(res.data);
    setHistory((prev) => prev.map((h) => (h.id === res.data!.id ? res.data! : h)));
  };

  if (loading) return <p className="text-gray-500">{t("loading")}</p>;

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-2xl font-bold text-naqsh-primary">{t("title")}</h2>
        <p className="text-gray-600 text-sm mt-1">{t("subtitle")}</p>
      </div>

      {loadError && <p className="text-sm text-red-600">{loadError}</p>}

      {subjects.length === 0 && !loadError && (
        <p className="text-sm text-amber-700 bg-amber-50 border border-amber-100 rounded-lg p-4">
          {t("noSubjects")}
        </p>
      )}

      <form onSubmit={generate} className="bg-white rounded-xl border p-6 space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">{t("subject")}</label>
            <select
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={subjectId}
              onChange={(e) => {
                setSubjectId(e.target.value);
                setGroupId("");
              }}
              required
              disabled={subjects.length === 0}
            >
              {subjects.length === 0 && <option value="">{t("noSubjectsShort")}</option>}
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {subjectLabel(s, locale)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t("groupOptional")}</label>
            <select
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={groupId}
              onChange={(e) => setGroupId(e.target.value)}
              disabled={subjects.length === 0}
            >
              <option value="">{t("noGroup")}</option>
              {filteredGroups.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">{t("contentType")}</label>
          <div className="flex gap-3">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="contentType"
                checked={contentType === "presentation"}
                onChange={() => setContentType("presentation")}
              />
              {t("presentation")}
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="contentType"
                checked={contentType === "game"}
                onChange={() => setContentType("game")}
              />
              {t("game")}
            </label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">{t("topic")}</label>
          <input
            className="w-full border rounded-lg px-3 py-2 text-sm"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder={t("topicPlaceholder")}
            required
            minLength={2}
            maxLength={500}
            disabled={subjects.length === 0}
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={generating || subjects.length === 0}
          className="bg-naqsh-primary text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50"
        >
          {generating ? t("generating") : t("generate")}
        </button>
      </form>

      {material && (
        <div className="bg-white rounded-xl border p-6 space-y-4">
          <div className="flex flex-wrap justify-between gap-3 items-start">
            <div>
              <h3 className="text-lg font-semibold text-naqsh-primary">{material.title}</h3>
              <p className="text-sm text-gray-500">
                {material.subject_name_uz} · {material.topic} · {material.content_type}
              </p>
            </div>
            {material.status !== "started" && (
              <button
                type="button"
                onClick={startLesson}
                disabled={starting}
                className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50"
              >
                {starting ? t("starting") : t("startLesson")}
              </button>
            )}
            {material.status === "started" && (
              <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-1 rounded-full">{t("started")}</span>
            )}
          </div>

          {material.content_type === "presentation" && material.content_json.slides && (
            <div className="space-y-3">
              {material.content_json.slides.map((slide, idx) => (
                <div key={idx} className="border rounded-lg p-4">
                  <h4 className="font-medium">
                    {idx + 1}. {slide.title}
                  </h4>
                  <ul className="list-disc list-inside text-sm text-gray-700 mt-2">
                    {slide.bullets?.map((b, i) => (
                      <li key={i}>{b}</li>
                    ))}
                  </ul>
                  {slide.speaker_notes && (
                    <p className="text-xs text-gray-500 mt-2 italic">{slide.speaker_notes}</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {material.content_type === "game" && material.content_json.rounds && (
            <div className="space-y-3">
              {material.content_json.rules && (
                <p className="text-sm bg-amber-50 border border-amber-100 rounded-lg p-3">{material.content_json.rules}</p>
              )}
              {material.content_json.rounds.map((round, idx) => (
                <div key={idx} className="border rounded-lg p-4">
                  <p className="font-medium">
                    {t("round")} {idx + 1}: {round.question}
                  </p>
                  {round.hint && <p className="text-sm text-gray-500 mt-1">{t("hint")}: {round.hint}</p>}
                  <p className="text-sm text-emerald-700 mt-2">
                    {t("answer")}: {round.answer}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {history.length > 0 && (
        <div className="bg-white rounded-xl border p-6">
          <h3 className="font-semibold text-naqsh-primary mb-3">{t("recent")}</h3>
          <ul className="space-y-2 text-sm">
            {history.map((h) => (
              <li key={h.id}>
                <button
                  type="button"
                  className="text-left hover:text-naqsh-primary w-full"
                  onClick={() => setMaterial(h)}
                >
                  {h.title} — {h.status}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
