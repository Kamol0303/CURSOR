"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";
import { Alert, Button, FormField, Input, Label, Modal } from "@/components/ui";

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
    <Modal
      onClose={onClose}
      title={t("assignTeacherTitle")}
      description={
        <>
          <span>{groupName}</span>
          {currentTeacherName && (
            <span className="block text-xs text-muted-foreground mt-1">
              {t("currentTeacher", { name: currentTeacherName })}
            </span>
          )}
        </>
      }
      size="sm"
      footer={
        <>
          <Button type="button" variant="secondary" onClick={onClose}>
            {t("cancel")}
          </Button>
          <Button type="button" disabled={!selected || saving} loading={saving} onClick={() => void assign()}>
            {saving ? t("assigning") : t("assignTeacher")}
          </Button>
        </>
      }
    >
      <div className="space-y-3">
        <FormField>
          <Label className="sr-only">{t("searchTeacher")}</Label>
          <Input
            type="text"
            placeholder={t("searchTeacher")}
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setSelected(null);
            }}
          />
        </FormField>

        {loading && <p className="text-xs text-muted-foreground">{t("searching")}</p>}

        {!selected && teachers.length > 0 && (
          <ul className="border border-border rounded-lg divide-y divide-border max-h-48 overflow-y-auto">
            {teachers.map((teacher) => (
              <li key={teacher.id}>
                <button
                  type="button"
                  className="w-full text-left px-3 py-2 text-small hover:bg-muted transition-colors"
                  onClick={() => setSelected(teacher)}
                >
                  <span className="font-medium">{teacher.full_name}</span>
                  {teacher.specialization && (
                    <span className="text-muted-foreground ml-2 text-xs">{teacher.specialization}</span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        )}

        {selected && (
          <Alert variant="info" className="flex justify-between items-center">
            <span>{selected.full_name}</span>
            <button
              type="button"
              className="text-xs underline shrink-0 ml-2"
              onClick={() => setSelected(null)}
            >
              {t("clearSelection")}
            </button>
          </Alert>
        )}

        {error && <Alert variant="danger">{error}</Alert>}
      </div>
    </Modal>
  );
}
