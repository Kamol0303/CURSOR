"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch, uploadFile } from "@/lib/api";
import {
  Alert,
  Button,
  FormActions,
  FormField,
  FormGrid,
  Input,
  Label,
  Modal,
  Textarea,
} from "@/components/ui";

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
      <Modal onClose={onClose} title={t("parentSmsTitle")} description={t("parentSmsSent")} size="sm">
        <Button type="button" onClick={onClose} className="w-full">
          OK
        </Button>
      </Modal>
    );
  }

  return (
    <Modal onClose={onClose} title={isEdit ? t("editTitle") : t("addTitle")}>
      <form onSubmit={submit} className="space-y-4">
        <FormField>
          <Label>{t("name")}</Label>
          <Input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
        </FormField>
        {!isEdit && (
          <>
            <Label className="flex items-center gap-2 mb-0 cursor-pointer">
              <input
                type="checkbox"
                checked={noPassport}
                onChange={(e) => {
                  setNoPassport(e.target.checked);
                  if (e.target.checked) setJshshir("");
                }}
              />
              {t("noPassport")}
            </Label>
            {!noPassport ? (
              <FormField>
                <Label>{t("pinfl")}</Label>
                <Input
                  className="font-mono"
                  value={jshshir}
                  onChange={(e) => setJshshir(e.target.value)}
                  pattern="\d{14}"
                  placeholder="14 raqam"
                />
              </FormField>
            ) : (
              <FormField>
                <Label>{t("photo")}</Label>
                <Input
                  type="file"
                  accept=".jpg,.jpeg,.png,image/jpeg,image/png"
                  className="h-auto py-2"
                  onChange={(e) => setPhotoFile(e.target.files?.[0] || null)}
                  required
                />
                <p className="text-xs text-muted-foreground mt-1">{t("photoHint")}</p>
              </FormField>
            )}
          </>
        )}
        <FormGrid>
          <FormField>
            <Label>{t("phone")}</Label>
            <Input value={phone} onChange={(e) => setPhone(e.target.value)} />
          </FormField>
          <FormField>
            <Label>{t("grade")}</Label>
            <Input value={grade} onChange={(e) => setGrade(e.target.value)} />
          </FormField>
        </FormGrid>
        <FormField>
          <Label>{t("school")}</Label>
          <Input value={school} onChange={(e) => setSchool(e.target.value)} />
        </FormField>
        <FormField>
          <Label>{t("address")}</Label>
          <Textarea rows={2} value={address} onChange={(e) => setAddress(e.target.value)} />
        </FormField>
        {!isEdit && (
          <>
            <FormField>
              <Label>{t("guardianName")}</Label>
              <Input value={guardianName} onChange={(e) => setGuardianName(e.target.value)} />
            </FormField>
            <FormField>
              <Label>{t("guardianPhone")}</Label>
              <Input
                value={guardianPhone}
                onChange={(e) => setGuardianPhone(e.target.value)}
                placeholder="+998901234567"
              />
              <p className="text-xs text-muted-foreground mt-1">{t("guardianPhoneHint")}</p>
            </FormField>
          </>
        )}
        {error && <Alert variant="danger">{error}</Alert>}
        <FormActions>
          <Button type="button" variant="secondary" onClick={onClose}>
            {t("cancel")}
          </Button>
          <Button type="submit" loading={saving}>
            {saving ? t("saving") : t("save")}
          </Button>
        </FormActions>
      </form>
    </Modal>
  );
}
