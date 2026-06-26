"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";
import { usePermissions } from "@/hooks/usePermissions";

type Props = {
  groupId: string;
  groupName: string;
  onClose: () => void;
  onChanged: () => void;
};

type Student = {
  id: string;
  full_name: string;
  grade: string | null;
};

type Member = {
  enrollment_id: string;
  student_id: string;
  full_name: string;
  grade: string | null;
};

export function EnrollStudentModal({ groupId, groupName, onClose, onChanged }: Props) {
  const t = useTranslations("groups");
  const { can } = usePermissions();
  const canEnroll = can("groups.enroll");

  const [allStudents, setAllStudents] = useState<Student[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [studentsRes, membersRes] = await Promise.all([
        apiFetch<Student[]>("/students?per_page=100"),
        apiFetch<Member[]>(`/groups/${groupId}/enrollments`),
      ]);
      if (studentsRes.success && Array.isArray(studentsRes.data)) {
        setAllStudents(studentsRes.data as Student[]);
      }
      if (membersRes.success && Array.isArray(membersRes.data)) {
        setMembers(membersRes.data);
      }
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const enrolledIds = useMemo(() => new Set(members.map((m) => m.student_id)), [members]);

  const availableStudents = useMemo(() => {
    const q = search.trim().toLowerCase();
    return allStudents
      .filter((s) => !enrolledIds.has(s.id))
      .filter((s) => !q || s.full_name.toLowerCase().includes(q) || (s.grade || "").toLowerCase().includes(q));
  }, [allStudents, enrolledIds, search]);

  const toggleStudent = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const enrollSelected = async () => {
    if (selected.size === 0) return;
    setSaving(true);
    setError(null);
    try {
      const res = await apiFetch(`/groups/${groupId}/enroll/batch`, {
        method: "POST",
        body: JSON.stringify({ student_ids: Array.from(selected) }),
      });
      if (!res.success) {
        setError(t("enrollError"));
        return;
      }
      setSelected(new Set());
      await loadData();
      onChanged();
    } catch {
      setError(t("enrollError"));
    } finally {
      setSaving(false);
    }
  };

  const unenroll = async (studentId: string) => {
    if (!window.confirm(t("unenrollConfirm"))) return;
    setSaving(true);
    setError(null);
    try {
      const res = await apiFetch(`/groups/${groupId}/enroll/${studentId}`, { method: "DELETE" });
      if (!res.success) {
        setError(t("unenrollError"));
        return;
      }
      await loadData();
      onChanged();
    } catch {
      setError(t("unenrollError"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] flex flex-col">
        <div className="p-6 border-b shrink-0">
          <h3 className="text-lg font-semibold text-naqsh-primary">{t("enrollTitle")}</h3>
          <p className="text-sm text-gray-600">{groupName}</p>
        </div>

        <div className="p-6 overflow-y-auto flex-1 space-y-5">
          {loading ? (
            <p className="text-gray-400">{t("loading")}</p>
          ) : (
            <>
              <section>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">
                  {t("currentMembers")} ({members.length})
                </h4>
                {members.length === 0 ? (
                  <p className="text-sm text-gray-400">{t("noMembers")}</p>
                ) : (
                  <ul className="space-y-2 max-h-36 overflow-y-auto border rounded-lg divide-y">
                    {members.map((m) => (
                      <li key={m.student_id} className="flex items-center justify-between px-3 py-2 text-sm">
                        <span>
                          {m.full_name}
                          {m.grade ? <span className="text-gray-400"> · {m.grade}</span> : null}
                        </span>
                        {canEnroll && (
                          <button
                            type="button"
                            disabled={saving}
                            onClick={() => unenroll(m.student_id)}
                            className="text-red-600 hover:underline text-xs shrink-0 ml-2"
                          >
                            {t("unenroll")}
                          </button>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </section>

              {canEnroll && (
                <section>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">{t("addStudents")}</h4>
                  <input
                    type="search"
                    className="w-full border rounded-lg px-3 py-2 text-sm mb-2"
                    placeholder={t("searchStudent")}
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                  {availableStudents.length === 0 ? (
                    <p className="text-sm text-gray-400">{t("noAvailableStudents")}</p>
                  ) : (
                    <ul className="space-y-1 max-h-48 overflow-y-auto border rounded-lg p-2">
                      {availableStudents.map((s) => (
                        <li key={s.id}>
                          <label className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-gray-50 cursor-pointer text-sm">
                            <input
                              type="checkbox"
                              checked={selected.has(s.id)}
                              onChange={() => toggleStudent(s.id)}
                              disabled={saving}
                            />
                            <span>
                              {s.full_name}
                              {s.grade ? <span className="text-gray-400"> ({s.grade})</span> : null}
                            </span>
                          </label>
                        </li>
                      ))}
                    </ul>
                  )}
                  {selected.size > 0 && (
                    <p className="text-xs text-gray-500 mt-2">{t("selectedCount", { count: selected.size })}</p>
                  )}
                </section>
              )}
            </>
          )}
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>

        <div className="p-6 border-t flex gap-2 justify-end shrink-0">
          <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg border">
            {t("cancel")}
          </button>
          {canEnroll && (
            <button
              type="button"
              disabled={saving || loading || selected.size === 0}
              onClick={enrollSelected}
              className="px-4 py-2 rounded-lg bg-naqsh-primary text-white disabled:opacity-50"
            >
              {saving ? t("enrolling") : t("enrollSelected")}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
