"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardTitle,
  FormActions,
  FormField,
  FormGrid,
  Input,
  Label,
  PageHeader,
  PageSection,
  Select,
  Spinner,
} from "@/components/ui";
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

export default function TeacherLessonStartPage() {
  const t = useTranslations("lessonStart");
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [subjectId, setSubjectId] = useState("");
  const [groupId, setGroupId] = useState("");
  const [topic, setTopic] = useState("");
  const [contentType, setContentType] = useState<"presentation" | "game">("presentation");
  const [material, setMaterial] = useState<Material | null>(null);
  const [history, setHistory] = useState<Material[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiFetch<Subject[]>("/teacher/subjects"),
      apiFetch<Group[]>("/teacher/groups"),
      apiFetch<Material[]>("/teacher/lesson-materials?per_page=10"),
    ]).then(([subjRes, groupRes, histRes]) => {
      if (subjRes.success && subjRes.data) {
        setSubjects(subjRes.data);
        setSubjectId(subjRes.data[0]?.id || "");
      }
      if (groupRes.success && groupRes.data) setGroups(groupRes.data);
      if (histRes.success && histRes.data) setHistory(histRes.data);
      setLoading(false);
    });
  }, []);

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
      }),
    });
    setGenerating(false);
    if (!res.success || !res.data) {
      setError(t("generateError"));
      return;
    }
    setMaterial(res.data);
    setHistory((prev) => [res.data!, ...prev.filter((h) => h.id !== res.data!.id)]);
  };

  const startLesson = async () => {
    if (!material) return;
    setStarting(true);
    const res = await apiFetch<Material>(`/teacher/lesson-materials/${material.id}/start`, {
      method: "POST",
    });
    setStarting(false);
    if (res.success && res.data) setMaterial(res.data);
  };

  if (loading) {
    return (
      <PageSection className="max-w-4xl">
        <Spinner label={t("loading")} className="py-16" />
      </PageSection>
    );
  }

  return (
    <PageSection className="max-w-4xl">
      <PageHeader title={t("title")} description={t("subtitle")} />

      <Card>
        <CardBody>
          <form onSubmit={generate} className="space-y-5">
            <FormGrid>
              <FormField>
                <Label required>{t("subject")}</Label>
                <Select
                  value={subjectId}
                  onChange={(e) => {
                    setSubjectId(e.target.value);
                    setGroupId("");
                  }}
                  required
                >
                  {subjects.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name_uz}
                    </option>
                  ))}
                </Select>
              </FormField>
              <FormField>
                <Label>{t("groupOptional")}</Label>
                <Select value={groupId} onChange={(e) => setGroupId(e.target.value)}>
                  <option value="">{t("noGroup")}</option>
                  {filteredGroups.map((g) => (
                    <option key={g.id} value={g.id}>
                      {g.name}
                    </option>
                  ))}
                </Select>
              </FormField>
            </FormGrid>

            <FormField>
              <Label>{t("contentType")}</Label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 text-small text-foreground cursor-pointer">
                  <input
                    type="radio"
                    name="contentType"
                    checked={contentType === "presentation"}
                    onChange={() => setContentType("presentation")}
                    className="accent-naqsh-primary"
                  />
                  {t("presentation")}
                </label>
                <label className="flex items-center gap-2 text-small text-foreground cursor-pointer">
                  <input
                    type="radio"
                    name="contentType"
                    checked={contentType === "game"}
                    onChange={() => setContentType("game")}
                    className="accent-naqsh-primary"
                  />
                  {t("game")}
                </label>
              </div>
            </FormField>

            <FormField>
              <Label required>{t("topic")}</Label>
              <Input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder={t("topicPlaceholder")}
                required
                minLength={2}
              />
            </FormField>

            {error && <Alert variant="danger">{error}</Alert>}

            <FormActions className="justify-start pt-0">
              <Button type="submit" loading={generating} disabled={subjects.length === 0}>
                {generating ? t("generating") : t("generate")}
              </Button>
            </FormActions>
          </form>
        </CardBody>
      </Card>

      {material && (
        <Card>
          <CardBody className="space-y-5">
            <div className="flex flex-wrap justify-between gap-3 items-start">
              <div>
                <CardTitle>{material.title}</CardTitle>
                <p className="text-small text-muted-foreground mt-1">
                  {material.subject_name_uz} · {material.topic} · {material.content_type}
                </p>
              </div>
              {material.status !== "started" ? (
                <Button
                  type="button"
                  variant="accent"
                  onClick={startLesson}
                  loading={starting}
                >
                  {starting ? t("starting") : t("startLesson")}
                </Button>
              ) : (
                <Badge variant="success">{t("started")}</Badge>
              )}
            </div>

            {material.content_type === "presentation" && material.content_json.slides && (
              <div className="space-y-3">
                {material.content_json.slides.map((slide, idx) => (
                  <div key={idx} className="border border-border rounded-lg p-4">
                    <h4 className="font-medium text-foreground">
                      {idx + 1}. {slide.title}
                    </h4>
                    <ul className="list-disc list-inside text-small text-foreground-secondary mt-2">
                      {slide.bullets?.map((b, i) => (
                        <li key={i}>{b}</li>
                      ))}
                    </ul>
                    {slide.speaker_notes && (
                      <p className="text-caption text-muted-foreground mt-2 italic">
                        {slide.speaker_notes}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}

            {material.content_type === "game" && material.content_json.rounds && (
              <div className="space-y-3">
                {material.content_json.rules && (
                  <Alert variant="warning">{material.content_json.rules}</Alert>
                )}
                {material.content_json.rounds.map((round, idx) => (
                  <div key={idx} className="border border-border rounded-lg p-4">
                    <p className="font-medium text-foreground">
                      {t("round")} {idx + 1}: {round.question}
                    </p>
                    {round.hint && (
                      <p className="text-small text-muted-foreground mt-1">
                        {t("hint")}: {round.hint}
                      </p>
                    )}
                    <p className="text-small text-success mt-2">
                      {t("answer")}: {round.answer}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      )}

      {history.length > 0 && (
        <Card>
          <CardBody>
            <CardTitle className="mb-4">{t("recent")}</CardTitle>
            <ul className="space-y-1">
              {history.map((h) => (
                <li key={h.id}>
                  <button
                    type="button"
                    className="w-full text-left rounded-lg px-3 py-2.5 text-small text-foreground-secondary hover:bg-muted hover:text-foreground transition-colors"
                    onClick={() => setMaterial(h)}
                  >
                    {h.title} — {h.status}
                  </button>
                </li>
              ))}
            </ul>
          </CardBody>
        </Card>
      )}
    </PageSection>
  );
}
