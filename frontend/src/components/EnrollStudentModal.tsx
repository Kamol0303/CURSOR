"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch, listStudents } from "@/lib/api";

type Props = {
  groupId: string;
  groupName: string;
  onClose: () => void;
  onEnrolled: () => void;
};

type Student = {
  id: string;
  full_name: string;
  grade: string | null;
};

export function EnrollStudentModal({ groupId, groupName, onClose, onEnrolled }: Props) {
  const t = useTranslations("groups");
  const [students, setStudents] = useState<Student[]>([]);
  const [studentId, setStudentId] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  useEffect(() => {
    listStudents()
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setStudents(res.data as Student[]);
      })
      .finally(() => setLoading(false));
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!studentId) return;
    setSaving(true);
    setError(null);
    try {
      const res = await apiFetch(`/groups/${groupId}/enroll`, {
        method: "POST",
        body: JSON.stringify({ student_id: studentId }),
      });
      if (!res.success) {
        setError(t("enrollError"));
        return;
      }
      onEnrolled();
      onClose();
    } catch {
      setError(t("enrollError"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
        <form onSubmit={submit} className="p-6 space-y-4">
          <h3 className="text-lg font-semibold text-naqsh-primary">{t("enrollTitle")}</h3>
          <p className="text-sm text-gray-600">{groupName}</p>
          {loading ? (
            <p className="text-gray-400">{t("loading")}</p>
          ) : (
            <div>
              <label className="block text-sm font-medium mb-1">{t("selectStudent")}</label>
              <select
                className="w-full border rounded-lg px-3 py-2"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                required
              >
                <option value="">{t("selectStudent")}</option>
                {students.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.full_name}
                    {s.grade ? ` (${s.grade})` : ""}
                  </option>
                ))}
              </select>
            </div>
          )}
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-2 justify-end pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg border">
              {t("cancel")}
            </button>
            <button
              type="submit"
              disabled={saving || loading || !studentId}
              className="px-4 py-2 rounded-lg bg-naqsh-primary text-white disabled:opacity-50"
            >
              {saving ? t("enrolling") : t("enroll")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
