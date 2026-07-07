"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";
import {
  Alert,
  Button,
  FormActions,
  FormField,
  FormGrid,
  Input,
  Label,
  Modal,
  Select,
} from "@/components/ui";

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
    <Modal onClose={onClose} title={t("generateTitle")} description={t("generateHint")}>
      <form onSubmit={submit} className="space-y-4">
        <FormField>
          <Label>{t("subject")}</Label>
          <Select value={subjectId} onChange={(e) => setSubjectId(e.target.value)} required>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name_uz}
              </option>
            ))}
          </Select>
        </FormField>
        <FormField>
          <Label>{t("topic")}</Label>
          <Input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder={t("topicPlaceholder")}
            required
          />
        </FormField>
        <FormGrid>
          <FormField>
            <Label>{t("questionCount")}</Label>
            <Input
              type="number"
              min={1}
              max={30}
              value={questionCount}
              onChange={(e) => setQuestionCount(Number(e.target.value))}
            />
          </FormField>
          <FormField>
            <Label>{t("difficulty")}</Label>
            <Select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
              <option value="easy">{t("difficultyEasy")}</option>
              <option value="medium">{t("difficultyMedium")}</option>
              <option value="hard">{t("difficultyHard")}</option>
            </Select>
          </FormField>
        </FormGrid>
        <FormField>
          <Label>{t("examTitle")}</Label>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder={t("titleOptional")}
          />
        </FormField>
        {error && <Alert variant="danger">{error}</Alert>}
        <FormActions>
          <Button type="button" variant="secondary" onClick={onClose} className="flex-1 sm:flex-none">
            {t("cancel")}
          </Button>
          <Button type="submit" variant="accent" loading={saving} className="flex-1 sm:flex-none">
            {saving ? t("generating") : t("generate")}
          </Button>
        </FormActions>
      </form>
    </Modal>
  );
}
