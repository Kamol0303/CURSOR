"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch, uploadFile } from "@/lib/api";
import {
  Alert,
  Button,
  FormActions,
  FormField,
  Input,
  Label,
  Modal,
} from "@/components/ui";

type StudentOption = {
  id: string;
  full_name: string;
};

type Props = {
  centerId: string;
  onClose: () => void;
  onSaved: () => void;
};

const ACCEPTED_TYPES = ["application/pdf", "image/jpeg", "image/png"];
const MAX_BYTES = 10 * 1024 * 1024;

export function AddCertificateModal({ centerId, onClose, onSaved }: Props) {
  const t = useTranslations("certificates");
  const [students, setStudents] = useState<StudentOption[]>([]);
  const [search, setSearch] = useState("");
  const [selectedStudent, setSelectedStudent] = useState<StudentOption | null>(null);
  const [title, setTitle] = useState("");
  const [issueDate, setIssueDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [file, setFile] = useState<File | null>(null);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadStudents = useCallback(async () => {
    setLoadingStudents(true);
    const res = await apiFetch<StudentOption[]>("/students?per_page=100");
    setLoadingStudents(false);
    if (res.success && Array.isArray(res.data)) {
      setStudents(
        res.data.map((s) => ({
          id: s.id,
          full_name: s.full_name,
        })),
      );
    }
  }, []);

  useEffect(() => {
    void loadStudents();
  }, [loadStudents]);

  const filteredStudents = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return students.slice(0, 20);
    return students.filter((s) => s.full_name.toLowerCase().includes(q)).slice(0, 20);
  }, [students, search]);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const picked = e.target.files?.[0] ?? null;
    setError(null);
    if (!picked) {
      setFile(null);
      return;
    }
    if (!ACCEPTED_TYPES.includes(picked.type)) {
      setError(t("fileTypeError"));
      setFile(null);
      return;
    }
    if (picked.size > MAX_BYTES) {
      setError(t("fileSizeError"));
      setFile(null);
      return;
    }
    setFile(picked);
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStudent || !file || !title.trim()) {
      setError(t("formIncomplete"));
      return;
    }

    setSaving(true);
    setError(null);
    try {
      const ownerId = crypto.randomUUID();
      const uploadRes = await uploadFile(file, {
        center_id: centerId,
        owner_type: "certificate",
        owner_id: ownerId,
      });
      if (!uploadRes.success) {
        setError(t("fileUploadError"));
        return;
      }
      const fileId = (uploadRes.data as { id: string }).id;

      const createRes = await apiFetch("/certificates", {
        method: "POST",
        body: JSON.stringify({
          student_id: selectedStudent.id,
          title: title.trim(),
          issue_date: issueDate,
          file_id: fileId,
        }),
      });
      if (!createRes.success) {
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
    <Modal onClose={onClose} title={t("addTitle")}>
      <form onSubmit={submit} className="space-y-4">
        <FormField>
          <Label>{t("student")}</Label>
          <Input
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setSelectedStudent(null);
            }}
            placeholder={t("studentSearch")}
          />
          {loadingStudents ? (
            <p className="text-xs text-muted-foreground mt-1">{t("loadingStudents")}</p>
          ) : (
            <ul className="mt-2 max-h-32 overflow-y-auto border border-border rounded-lg divide-y divide-border">
              {filteredStudents.map((s) => (
                <li key={s.id}>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedStudent(s);
                      setSearch(s.full_name);
                    }}
                    className={`w-full text-left px-3 py-2 text-small hover:bg-muted transition-colors ${
                      selectedStudent?.id === s.id ? "bg-muted font-medium" : ""
                    }`}
                  >
                    {s.full_name}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </FormField>

        <FormField>
          <Label>{t("certTitle")}</Label>
          <Input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required />
        </FormField>

        <FormField>
          <Label>{t("issueDate")}</Label>
          <Input type="date" value={issueDate} onChange={(e) => setIssueDate(e.target.value)} required />
        </FormField>

        <FormField>
          <Label>{t("file")}</Label>
          <Input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
            className="h-auto py-2"
            onChange={onFileChange}
          />
          <p className="text-xs text-muted-foreground mt-1">{t("fileHint")}</p>
        </FormField>

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
