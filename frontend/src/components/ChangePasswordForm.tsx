"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import {
  Alert,
  Button,
  FormActions,
  FormField,
  Input,
  Label,
} from "@/components/ui";
import { apiFetch } from "@/lib/api";

export function ChangePasswordForm({ onSuccess }: { onSuccess?: () => void }) {
  const t = useTranslations("security");
  const [current, setCurrent] = useState("");
  const [newPass, setNewPass] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    if (newPass !== confirm) {
      setError(t("passwordMismatch"));
      return;
    }
    setSaving(true);
    const res = await apiFetch("/auth/change-password", {
      method: "POST",
      body: JSON.stringify({ current_password: current, new_password: newPass }),
    });
    setSaving(false);
    if (!res.success) {
      const code = (res as { error?: { code?: string } }).error?.code || "UNKNOWN";
      setError(t(`passwordErrors.${code}` as "passwordErrors.INVALID_CREDENTIALS"));
      return;
    }
    setCurrent("");
    setNewPass("");
    setConfirm("");
    setMessage(t("passwordChanged"));
    onSuccess?.();
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      <h3 className="font-semibold text-foreground">{t("changePasswordTitle")}</h3>
      <FormField>
        <Label htmlFor="current-password">{t("currentPassword")}</Label>
        <Input
          id="current-password"
          type="password"
          placeholder={t("currentPassword")}
          value={current}
          onChange={(e) => setCurrent(e.target.value)}
          required
        />
      </FormField>
      <FormField>
        <Label htmlFor="new-password">{t("newPassword")}</Label>
        <Input
          id="new-password"
          type="password"
          placeholder={t("newPassword")}
          value={newPass}
          onChange={(e) => setNewPass(e.target.value)}
          required
          minLength={12}
        />
      </FormField>
      <FormField>
        <Label htmlFor="confirm-password">{t("confirmPassword")}</Label>
        <Input
          id="confirm-password"
          type="password"
          placeholder={t("confirmPassword")}
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          required
          minLength={12}
        />
      </FormField>
      <p className="text-caption text-muted-foreground">{t("passwordPolicy")}</p>
      {error && <Alert variant="danger">{error}</Alert>}
      {message && <Alert variant="success">{message}</Alert>}
      <FormActions className="justify-start pt-0">
        <Button type="submit" loading={saving}>
          {saving ? t("saving") : t("changePasswordButton")}
        </Button>
      </FormActions>
    </form>
  );
}
