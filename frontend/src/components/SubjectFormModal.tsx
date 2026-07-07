"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";
import {
  Alert,
  Button,
  FormActions,
  FormField,
  Input,
  Label,
  Modal,
} from "@/components/ui";

type Subject = {
  id: string;
  name_uz: string;
  name_ru: string;
  name_en: string;
  is_active: boolean;
};

type Props = {
  subject?: Subject | null;
  onClose: () => void;
  onSaved: () => void;
};

export function SubjectFormModal({ subject, onClose, onSaved }: Props) {
  const t = useTranslations("subjects");
  const isEdit = Boolean(subject?.id);
  const [nameUz, setNameUz] = useState(subject?.name_uz || "");
  const [nameRu, setNameRu] = useState(subject?.name_ru || "");
  const [nameEn, setNameEn] = useState(subject?.name_en || "");
  const [isActive, setIsActive] = useState(subject?.is_active ?? true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    const path = isEdit ? `/subjects/${subject!.id}` : "/subjects";
    const method = isEdit ? "PATCH" : "POST";
    const body = isEdit
      ? { name_uz: nameUz, name_ru: nameRu, name_en: nameEn, is_active: isActive }
      : { name_uz: nameUz, name_ru: nameRu, name_en: nameEn, is_active: isActive };
    const res = await apiFetch(path, { method, body: JSON.stringify(body) });
    setSaving(false);
    if (!res.success) {
      const code = (res as { error?: { code?: string } }).error?.code || "UNKNOWN";
      setError(t(`errors.${code}` as "errors.UNKNOWN"));
      return;
    }
    onSaved();
    onClose();
  };

  return (
    <Modal onClose={onClose} title={isEdit ? t("editTitle") : t("addTitle")}>
      <form onSubmit={submit} className="space-y-4">
        <FormField>
          <Label>{t("nameUz")}</Label>
          <Input value={nameUz} onChange={(e) => setNameUz(e.target.value)} required />
        </FormField>
        <FormField>
          <Label>{t("nameRu")}</Label>
          <Input value={nameRu} onChange={(e) => setNameRu(e.target.value)} required />
        </FormField>
        <FormField>
          <Label>{t("nameEn")}</Label>
          <Input value={nameEn} onChange={(e) => setNameEn(e.target.value)} required />
        </FormField>
        <Label className="flex items-center gap-2 mb-0 cursor-pointer">
          <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
          {t("active")}
        </Label>
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
