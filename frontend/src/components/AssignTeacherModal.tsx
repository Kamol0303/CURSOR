"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

type TeacherOption = {
  id: string;
  full_name: string;
  specialization: string | null;
};

type Props = {
  groupId: string;
  groupName: string;
  currentTeacherName: string | null;
  onClose: () => void;
  onAssigned: () => void;
};

export function AssignTeacherModal({ groupId, groupName, currentTeacherName, onClose, onAssigned }: Props) {
  const t = useTranslations("groups");
  const [search, setSearch] = useState("");
  const [teachers, setTeachers] = useState<TeacherOption[]>([]);
  const [selected, setSelected] = useState<TeacherOption | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTeachers = useCallback(async (query: string) => {
    setLoading(true);
    const params = new URLSearchParams({ per_page: "30" });
    if (query.trim()) params.set("search", query.trim());
    const res = await apiFetch<TeacherOption[]>(`/teachers?${params.toString()}`);
    setLoading(false);
    if (res.success && Array.isArray(res.data)) {
      setTeachers(
        res.data.map((item) => ({
          id: item.id,
          full_name: item.full_name,
          specialization: item.specialization ?? null,
        })),
      );
    }
  }, []);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      void loadTeachers(search);
    }, 250);
    return () => clearTimeout(timer);
  }, [search, loadTeachers]);

  const assign = async () => {
    if (!selected) return;
    setSaving(true);
    setError(null);
    const res = await apiFetch(`/groups/${groupId}/assign-teacher`, {
      method: "PATCH",
      body: JSON.stringify({ teacher_id: selected.id }),
    });
    setSaving(false);
    if (!res.success) {
      const code = (res as { error?: { code?: string } }).error?.code || "UNKNOWN";
      setError(t(`assignTeacherErrors.${code}` as "assignTeacherErrors.UNKNOWN"));
      return;
    }
    onAssigned();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="p-4 border-b flex justify-between items-start">
          <div>
            <h3 className="font-semibold text-naqsh-primary">{t("assignTeacherTitle")}</h3>
            <p className="text-sm text-gray-500">{groupName}</p>
            {currentTeacherName && (
              <p className="text-xs text-gray-400 mt-1">{t("currentTeacher", { name: currentTeacherName })}</p>
            )}
          </div>
          <button type="button" onClick={onClose} className="text-gray-400 hover:text-gray-600">
            ×
          </button>
        </div>

        <div className="p-4 space-y-3">
          <input
            type="text"
            className="w-full border rounded-lg px-3 py-2"
            placeholder={t("searchTeacher")}
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setSelected(null);
            }}
          />

          {loading && <p className="text-xs text-gray-400">{t("searching")}</p>}

          {!selected && teachers.length > 0 && (
            <ul className="border rounded-lg divide-y max-h-48 overflow-y-auto">
              {teachers.map((teacher) => (
                <li key={teacher.id}>
                  <button
                    type="button"
                    className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50"
                    onClick={() => setSelected(teacher)}
                  >
                    <span className="font-medium">{teacher.full_name}</span>
                    {teacher.specialization && (
                      <span className="text-gray-500 ml-2 text-xs">{teacher.specialization}</span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}

          {selected && (
            <div className="rounded-lg bg-blue-50 border border-blue-200 p-3 text-sm flex justify-between items-center">
              <span>{selected.full_name}</span>
              <button type="button" className="text-xs text-blue-700 underline" onClick={() => setSelected(null)}>
                {t("clearSelection")}
              </button>
            </div>
          )}

          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>

        <div className="p-4 border-t flex gap-2 justify-end">
          <button type="button" onClick={onClose} className="px-4 py-2 border rounded-lg text-sm">
            {t("cancel")}
          </button>
          <button
            type="button"
            disabled={!selected || saving}
            onClick={() => void assign()}
            className="px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm disabled:opacity-50"
          >
            {saving ? t("assigning") : t("assignTeacher")}
          </button>
        </div>
      </div>
    </div>
  );
}
