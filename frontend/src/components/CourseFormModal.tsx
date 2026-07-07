"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch, getMe, listCenters } from "@/lib/api";
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
  Textarea,
} from "@/components/ui";

type Course = {
  id: string;
  name: string;
  subject_id: string;
  description: string | null;
  price: number | null;
  duration_weeks: number | null;
  is_active: boolean;
};

type Props = {
  centerId: string;
  course?: Course | null;
  subjects: { id: string; name_uz: string }[];
  onClose: () => void;
  onSaved: () => void;
};

export function CourseFormModal({ centerId, course, subjects, onClose, onSaved }: Props) {
  const t = useTranslations("courses");
  const isEdit = Boolean(course?.id);
  const [name, setName] = useState(course?.name || "");
  const [subjectId, setSubjectId] = useState(course?.subject_id || subjects[0]?.id || "");
  const [description, setDescription] = useState(course?.description || "");
  const [price, setPrice] = useState(course?.price?.toString() || "");
  const [durationWeeks, setDurationWeeks] = useState(course?.duration_weeks?.toString() || "");
  const [isActive, setIsActive] = useState(course?.is_active ?? true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    const payload: Record<string, unknown> = {
      name,
      subject_id: subjectId,
      description: description || null,
      price: price ? Number(price) : null,
      duration_weeks: durationWeeks ? Number(durationWeeks) : null,
    };
    if (isEdit) payload.is_active = isActive;

    const path = isEdit ? `/courses/${course!.id}` : "/courses";
    const method = isEdit ? "PATCH" : "POST";
    const body = isEdit ? payload : { ...payload, center_id: centerId };
    const res = await apiFetch(path, { method, body: JSON.stringify(body) });
    setSaving(false);
    if (!res.success) {
      setError(t("saveError"));
      return;
    }
    onSaved();
    onClose();
  };

  return (
    <Modal onClose={onClose} title={isEdit ? t("editTitle") : t("addTitle")}>
      <form onSubmit={submit} className="space-y-4">
        <FormField>
          <Label>{t("name")}</Label>
          <Input value={name} onChange={(e) => setName(e.target.value)} required />
        </FormField>
        <FormField>
          <Label>{t("selectSubject")}</Label>
          <Select value={subjectId} onChange={(e) => setSubjectId(e.target.value)} required>
            <option value="">{t("selectSubject")}</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name_uz}
              </option>
            ))}
          </Select>
        </FormField>
        <FormField>
          <Label>{t("description")}</Label>
          <Textarea rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
        </FormField>
        <FormGrid>
          <FormField>
            <Label>{t("price")}</Label>
            <Input
              type="number"
              min="0"
              step="0.01"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
            />
          </FormField>
          <FormField>
            <Label>{t("durationWeeks")}</Label>
            <Input
              type="number"
              min="1"
              value={durationWeeks}
              onChange={(e) => setDurationWeeks(e.target.value)}
            />
          </FormField>
        </FormGrid>
        {isEdit && (
          <Label className="flex items-center gap-2 mb-0 cursor-pointer">
            <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
            {t("active")}
          </Label>
        )}
        {error && <Alert variant="danger">{error}</Alert>}
        <FormActions>
          <Button type="button" variant="secondary" onClick={onClose} className="flex-1 sm:flex-none">
            {t("cancel")}
          </Button>
          <Button type="submit" loading={saving} className="flex-1 sm:flex-none">
            {saving ? t("saving") : t("save")}
          </Button>
        </FormActions>
      </form>
    </Modal>
  );
}

export function useCourseCenterId() {
  const [centerId, setCenterId] = useState<string | null>(null);
  useEffect(() => {
    getMe().then(async (res) => {
      if (res.success && res.data?.center_id) {
        setCenterId(res.data.center_id as string);
      } else {
        const centers = await listCenters();
        if (centers.success && Array.isArray(centers.data) && centers.data[0]) {
          setCenterId((centers.data[0] as { id: string }).id);
        }
      }
    });
  }, []);
  return centerId;
}
