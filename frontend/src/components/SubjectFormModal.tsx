"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

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

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <form onSubmit={submit} className="p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-naqsh-primary">
              {isEdit ? t("editTitle") : t("addTitle")}
            </h3>
            <button type="button" onClick={onClose} className="text-gray-400 hover:text-gray-600">
              ✕
            </button>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("nameUz")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={nameUz}
              onChange={(e) => setNameUz(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("nameRu")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={nameRu}
              onChange={(e) => setNameRu(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("nameEn")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={nameEn}
              onChange={(e) => setNameEn(e.target.value)}
              required
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
            {t("active")}
          </label>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose} className="flex-1 px-4 py-2 border rounded-lg text-sm">
              {t("cancel")}
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm disabled:opacity-50"
            >
              {saving ? t("saving") : t("save")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
