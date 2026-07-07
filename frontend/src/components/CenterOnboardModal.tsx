"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";
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

type Props = {
  onClose: () => void;
  onSaved: () => void;
};

type OnboardResult = {
  center: { id: string; name: string };
  director_username: string;
  temporary_password: string;
};

export function CenterOnboardModal({ onClose, onSaved }: Props) {
  const t = useTranslations("centers");
  const [name, setName] = useState("");
  const [directorUsername, setDirectorUsername] = useState("");
  const [directorFullName, setDirectorFullName] = useState("");
  const [directorEmail, setDirectorEmail] = useState("");
  const [directorPhone, setDirectorPhone] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [result, setResult] = useState<OnboardResult | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const res = await apiFetch<OnboardResult>("/centers/onboard", {
        method: "POST",
        body: JSON.stringify({
          name,
          director_username: directorUsername.trim(),
          director_full_name: directorFullName.trim(),
          director_email: directorEmail || null,
          director_phone: directorPhone || null,
        }),
      });
      if (!res.success || !res.data) {
        setError(t("onboardError"));
        return;
      }
      setResult(res.data);
      onSaved();
    } catch {
      setError(t("onboardError"));
    } finally {
      setSaving(false);
    }
  };

  if (result) {
    return (
      <Modal
        onClose={onClose}
        title={t("onboardSuccessTitle")}
        description={t("onboardSuccessHint")}
      >
        <dl className="text-small space-y-2 bg-muted rounded-lg p-4">
          <div>
            <dt className="text-muted-foreground">{t("name")}</dt>
            <dd className="font-medium">{result.center.name}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">{t("onboardDirectorLogin")}</dt>
            <dd className="font-mono">{result.director_username}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">{t("onboardTempPassword")}</dt>
            <dd className="font-mono break-all text-naqsh-primary dark:text-naqsh-accent">
              {result.temporary_password}
            </dd>
          </div>
        </dl>
        <Button type="button" onClick={onClose} className="w-full mt-4">
          {t("onboardDone")}
        </Button>
      </Modal>
    );
  }

  return (
    <Modal onClose={onClose} title={t("onboardTitle")} description={t("onboardSubtitle")}>
      <form onSubmit={submit} className="space-y-4">
        <FormField>
          <Label>{t("name")}</Label>
          <Input value={name} onChange={(e) => setName(e.target.value)} required />
        </FormField>
        <FormField>
          <Label>{t("onboardDirectorLogin")}</Label>
          <Input
            className="font-mono"
            value={directorUsername}
            onChange={(e) => setDirectorUsername(e.target.value)}
            pattern="[a-zA-Z0-9._-]{3,100}"
            required
          />
        </FormField>
        <FormField>
          <Label>{t("director")}</Label>
          <Input value={directorFullName} onChange={(e) => setDirectorFullName(e.target.value)} required />
        </FormField>
        <FormGrid>
          <FormField>
            <Label>{t("email")}</Label>
            <Input type="email" value={directorEmail} onChange={(e) => setDirectorEmail(e.target.value)} />
          </FormField>
          <FormField>
            <Label>{t("phone")}</Label>
            <Input value={directorPhone} onChange={(e) => setDirectorPhone(e.target.value)} />
          </FormField>
        </FormGrid>
        {error && <Alert variant="danger">{error}</Alert>}
        <FormActions>
          <Button type="button" variant="secondary" onClick={onClose}>
            {t("cancel")}
          </Button>
          <Button type="submit" loading={saving}>
            {saving ? t("saving") : t("onboardSubmit")}
          </Button>
        </FormActions>
      </form>
    </Modal>
  );
}
