"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

type Teacher = {
  id: string;
  center_id: string;
  full_name: string;
  phone: string | null;
  specialization: string | null;
  years_of_experience: number;
  is_active: boolean;
};

type Props = {
  centerId: string;
  teacher?: Teacher | null;
  onClose: () => void;
  onSaved: () => void;
};

export function TeacherFormModal({ centerId, teacher, onClose, onSaved }: Props) {
  const t = useTranslations("teachers");
  const isEdit = Boolean(teacher?.id);
  const [fullName, setFullName] = useState(teacher?.full_name || "");
  const [phone, setPhone] = useState(teacher?.phone || "");
  const [specialization, setSpecialization] = useState(teacher?.specialization || "");
  const [yearsOfExperience, setYearsOfExperience] = useState(teacher?.years_of_experience ?? 0);
  const [isActive, setIsActive] = useState(teacher?.is_active ?? true);
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
    try {
      const path = isEdit ? `/teachers/${teacher!.id}` : "/teachers";
      const method = isEdit ? "PATCH" : "POST";
      const body = isEdit
        ? {
            full_name: fullName,
            phone: phone || null,
            specialization: specialization || null,
            years_of_experience: yearsOfExperience,
            is_active: isActive,
          }
        : {
            center_id: centerId,
            full_name: fullName,
            phone: phone || null,
            specialization: specialization || null,
            years_of_experience: yearsOfExperience,
          };
      const res = await apiFetch(path, { method, body: JSON.stringify(body) });
      if (!res.success) {
        setError(t("saveError"));
        return;
      }
      onSaved();
      onClose();
    } catch {
      setError(t("saveError"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <form onSubmit={submit} className="p-6 space-y-4">
          <h3 className="text-lg font-semibold text-naqsh-primary">
            {isEdit ? t("editTitle") : t("addTitle")}
          </h3>
          <div>
            <label className="block text-sm font-medium mb-1">{t("name")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">{t("phone")}</label>
              <input className="w-full border rounded-lg px-3 py-2" value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">{t("experience")}</label>
              <input
                type="number"
                min={0}
                className="w-full border rounded-lg px-3 py-2"
                value={yearsOfExperience}
                onChange={(e) => setYearsOfExperience(Number(e.target.value))}
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t("specialization")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2"
              value={specialization}
              onChange={(e) => setSpecialization(e.target.value)}
            />
          </div>
          {isEdit && (
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
              {t("active")}
            </label>
          )}
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-2 justify-end pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg border">
              {t("cancel")}
            </button>
            <button type="submit" disabled={saving} className="px-4 py-2 rounded-lg bg-naqsh-primary text-white disabled:opacity-50">
              {saving ? t("saving") : t("save")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
