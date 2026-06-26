"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch, uploadFile } from "@/lib/api";

type Props = {
  centerId: string;
  student?: Record<string, unknown> | null;
  onClose: () => void;
  onSaved: () => void;
};

export function StudentFormModal({ centerId, student, onClose, onSaved }: Props) {
  const t = useTranslations("students");
  const isEdit = Boolean(student?.id);
  const [fullName, setFullName] = useState((student?.full_name as string) || "");
  const [phone, setPhone] = useState((student?.phone as string) || "");
  const [grade, setGrade] = useState((student?.grade as string) || "");
  const [school, setSchool] = useState((student?.school as string) || "");
  const [address, setAddress] = useState((student?.address as string) || "");
  const [guardianName, setGuardianName] = useState("");
  const [guardianPhone, setGuardianPhone] = useState("");
  const [jshshir, setJshshir] = useState("");
  const [noPassport, setNoPassport] = useState(false);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [parentSmsSent, setParentSmsSent] = useState(false);

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
      let photoFileId: string | null = null;
      if (!isEdit && noPassport) {
        if (!photoFile) {
          setError(t("photoRequired"));
          setSaving(false);
          return;
        }
        const ownerId = crypto.randomUUID();
        const uploadRes = await uploadFile(photoFile, {
          center_id: centerId,
          owner_type: "student_photo",
          owner_id: ownerId,
        });
        if (!uploadRes.success) {
          setError(t("photoUploadError"));
          setSaving(false);
          return;
        }
        photoFileId = (uploadRes.data as { id: string }).id;
      }

      const path = isEdit ? `/students/${student!.id}` : "/students";
      const method = isEdit ? "PATCH" : "POST";
      const body = isEdit
        ? { full_name: fullName, phone, grade, school, address }
        : {
            center_id: centerId,
            full_name: fullName,
            phone: phone || null,
            grade: grade || null,
            school: school || null,
            address: address || null,
            jshshir: noPassport ? null : jshshir || null,
            no_passport: noPassport,
            photo_file_id: photoFileId,
            guardian_name: guardianName || null,
            guardian_phone: guardianPhone || null,
          };
      const res = await apiFetch<{ student: unknown; parent?: { sms_sent?: boolean; created?: boolean } }>(path, {
        method,
        body: JSON.stringify(body),
      });
      if (!res.success) {
        setError(t("saveError"));
        return;
      }
      if (res.data?.parent?.sms_sent) {
        setParentSmsSent(true);
        onSaved();
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

  if (parentSmsSent) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
        <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
          <h3 className="text-lg font-semibold text-naqsh-primary">{t("parentSmsTitle")}</h3>
          <p className="text-sm text-gray-600">{t("parentSmsSent")}</p>
          <button type="button" onClick={onClose} className="w-full px-4 py-2 bg-naqsh-primary text-white rounded-lg">
            OK
          </button>
        </div>
      </div>
    );
  }

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
          {!isEdit && (
            <>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={noPassport}
                  onChange={(e) => {
                    setNoPassport(e.target.checked);
                    if (e.target.checked) setJshshir("");
                  }}
                />
                {t("noPassport")}
              </label>
              {!noPassport ? (
                <div>
                  <label className="block text-sm font-medium mb-1">{t("pinfl")}</label>
                  <input
                    className="w-full border rounded-lg px-3 py-2 font-mono"
                    value={jshshir}
                    onChange={(e) => setJshshir(e.target.value)}
                    pattern="\d{14}"
                    placeholder="14 raqam"
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium mb-1">{t("photo")}</label>
                  <input
                    type="file"
                    accept=".jpg,.jpeg,.png,image/jpeg,image/png"
                    className="w-full border rounded-lg px-3 py-2 text-sm"
                    onChange={(e) => setPhotoFile(e.target.files?.[0] || null)}
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">{t("photoHint")}</p>
                </div>
              )}
            </>
          )}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">{t("phone")}</label>
              <input className="w-full border rounded-lg px-3 py-2" value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">{t("grade")}</label>
              <input className="w-full border rounded-lg px-3 py-2" value={grade} onChange={(e) => setGrade(e.target.value)} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t("school")}</label>
            <input className="w-full border rounded-lg px-3 py-2" value={school} onChange={(e) => setSchool(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t("address")}</label>
            <textarea className="w-full border rounded-lg px-3 py-2" rows={2} value={address} onChange={(e) => setAddress(e.target.value)} />
          </div>
          {!isEdit && (
            <>
              <div>
                <label className="block text-sm font-medium mb-1">{t("guardianName")}</label>
                <input className="w-full border rounded-lg px-3 py-2" value={guardianName} onChange={(e) => setGuardianName(e.target.value)} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">{t("guardianPhone")}</label>
                <input
                  className="w-full border rounded-lg px-3 py-2"
                  value={guardianPhone}
                  onChange={(e) => setGuardianPhone(e.target.value)}
                  placeholder="+998901234567"
                />
                <p className="text-xs text-gray-500 mt-1">{t("guardianPhoneHint")}</p>
              </div>
            </>
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
