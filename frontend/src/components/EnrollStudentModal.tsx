"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";
import { usePermissions } from "@/hooks/usePermissions";
import { Alert, Button, FormField, Input, Label, Modal } from "@/components/ui";

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
    <Modal
      onClose={onClose}
      title={t("enrollTitle")}
      description={groupName}
      footer={
        <>
          <Button type="button" variant="secondary" onClick={onClose}>
            {t("cancel")}
          </Button>
          {canEnroll && (
            <Button
              type="button"
              disabled={saving || loading || selected.size === 0}
              loading={saving}
              onClick={enrollSelected}
            >
              {saving ? t("enrolling") : t("enrollSelected")}
            </Button>
          )}
        </>
      }
    >
      <div className="space-y-5">
        {loading ? (
          <p className="text-muted-foreground">{t("loading")}</p>
        ) : (
          <>
            <section>
              <h4 className="text-small font-semibold text-foreground-secondary mb-2">
                {t("currentMembers")} ({members.length})
              </h4>
              {members.length === 0 ? (
                <p className="text-small text-muted-foreground">{t("noMembers")}</p>
              ) : (
                <ul className="space-y-0 max-h-36 overflow-y-auto border border-border rounded-lg divide-y divide-border">
                  {members.map((m) => (
                    <li key={m.student_id} className="flex items-center justify-between px-3 py-2 text-small">
                      <span>
                        {m.full_name}
                        {m.grade ? <span className="text-muted-foreground"> · {m.grade}</span> : null}
                      </span>
                      {canEnroll && (
                        <button
                          type="button"
                          disabled={saving}
                          onClick={() => unenroll(m.student_id)}
                          className="text-danger hover:underline text-xs shrink-0 ml-2"
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
                <h4 className="text-small font-semibold text-foreground-secondary mb-2">{t("addStudents")}</h4>
                <FormField>
                  <Label className="sr-only">{t("searchStudent")}</Label>
                  <Input
                    type="search"
                    placeholder={t("searchStudent")}
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </FormField>
                {availableStudents.length === 0 ? (
                  <p className="text-small text-muted-foreground">{t("noAvailableStudents")}</p>
                ) : (
                  <ul className="space-y-1 max-h-48 overflow-y-auto border border-border rounded-lg p-2 mt-2">
                    {availableStudents.map((s) => (
                      <li key={s.id}>
                        <Label className="flex items-center gap-2 mb-0 px-2 py-1.5 rounded hover:bg-muted cursor-pointer text-small font-normal">
                          <input
                            type="checkbox"
                            checked={selected.has(s.id)}
                            onChange={() => toggleStudent(s.id)}
                            disabled={saving}
                          />
                          <span>
                            {s.full_name}
                            {s.grade ? <span className="text-muted-foreground"> ({s.grade})</span> : null}
                          </span>
                        </Label>
                      </li>
                    ))}
                  </ul>
                )}
                {selected.size > 0 && (
                  <p className="text-xs text-muted-foreground mt-2">{t("selectedCount", { count: selected.size })}</p>
                )}
              </section>
            )}
          </>
        )}
        {error && <Alert variant="danger">{error}</Alert>}
      </div>
    </Modal>
  );
}
