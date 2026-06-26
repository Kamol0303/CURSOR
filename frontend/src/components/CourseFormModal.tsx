"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch, getMe, listCenters } from "@/lib/api";

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
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("name")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("selectSubject")}</label>
            <select
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={subjectId}
              onChange={(e) => setSubjectId(e.target.value)}
              required
            >
              <option value="">{t("selectSubject")}</option>
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name_uz}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("description")}</label>
            <textarea
              className="w-full border rounded-lg px-3 py-2 text-sm"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t("price")}</label>
              <input
                type="number"
                min="0"
                step="0.01"
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t("durationWeeks")}</label>
              <input
                type="number"
                min="1"
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={durationWeeks}
                onChange={(e) => setDurationWeeks(e.target.value)}
              />
            </div>
          </div>
          {isEdit && (
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
              {t("active")}
            </label>
          )}
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
