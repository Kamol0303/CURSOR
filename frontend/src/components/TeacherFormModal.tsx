"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";
import { CredentialsRevealModal } from "@/components/CredentialsRevealModal";
import {
  Alert,
  Button,
  FormActions,
  FormField,
  FormGrid,
  Input,
  Label,
  Modal,
} from "@/components/ui";

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

type Credentials = {
  login: string;
  temporary_password: string;
  sms_sent: boolean;
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
  const [credentials, setCredentials] = useState<Credentials | null>(null);

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
      const res = await apiFetch<{ teacher: Teacher; credentials?: Credentials }>(path, {
        method,
        body: JSON.stringify(body),
      });
      if (!res.success) {
        setError(t("saveError"));
        return;
      }
      if (!isEdit && res.data?.credentials) {
        setCredentials(res.data.credentials);
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

  if (credentials) {
    return (
      <CredentialsRevealModal
        title={t("credentialsTitle")}
        login={credentials.login}
        temporaryPassword={credentials.temporary_password}
        smsSent={credentials.sms_sent}
        smsHint={credentials.sms_sent ? t("credentialsSmsSent") : undefined}
        onClose={() => {
          setCredentials(null);
          onClose();
        }}
      />
    );
  }

  return (
    <Modal
      onClose={onClose}
      title={isEdit ? t("editTitle") : t("addTitle")}
      description={!isEdit ? t("credentialsHint") : undefined}
    >
      <form onSubmit={submit} className="space-y-4">
        <FormField>
          <Label>{t("name")}</Label>
          <Input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
        </FormField>
        <FormGrid>
          <FormField>
            <Label>{t("phone")}</Label>
            <Input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+998901234567"
            />
          </FormField>
          <FormField>
            <Label>{t("experience")}</Label>
            <Input
              type="number"
              min={0}
              value={yearsOfExperience}
              onChange={(e) => setYearsOfExperience(Number(e.target.value))}
            />
          </FormField>
        </FormGrid>
        <FormField>
          <Label>{t("specialization")}</Label>
          <Input value={specialization} onChange={(e) => setSpecialization(e.target.value)} />
        </FormField>
        {isEdit && (
          <Label className="flex items-center gap-2 mb-0 cursor-pointer">
            <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
            {t("active")}
          </Label>
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
