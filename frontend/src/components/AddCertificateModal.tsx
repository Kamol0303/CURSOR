"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch, uploadFile } from "@/lib/api";

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
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <form onSubmit={submit} className="p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-naqsh-primary">{t("addTitle")}</h3>
            <button type="button" onClick={onClose} className="text-gray-400 hover:text-gray-600">
              ✕
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("student")}</label>
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setSelectedStudent(null);
              }}
              placeholder={t("studentSearch")}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
            {loadingStudents ? (
              <p className="text-xs text-gray-400 mt-1">{t("loadingStudents")}</p>
            ) : (
              <ul className="mt-2 max-h-32 overflow-y-auto border rounded-lg divide-y">
                {filteredStudents.map((s) => (
                  <li key={s.id}>
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedStudent(s);
                        setSearch(s.full_name);
                      }}
                      className={`w-full text-left px-3 py-2 text-sm hover:bg-amber-50 ${
                        selectedStudent?.id === s.id ? "bg-amber-50 font-medium" : ""
                      }`}
                    >
                      {s.full_name}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("certTitle")}</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("issueDate")}</label>
            <input
              type="date"
              value={issueDate}
              onChange={(e) => setIssueDate(e.target.value)}
              required
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("file")}</label>
            <input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
              onChange={onFileChange}
              className="w-full text-sm"
            />
            <p className="text-xs text-gray-400 mt-1">{t("fileHint")}</p>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm"
            >
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
