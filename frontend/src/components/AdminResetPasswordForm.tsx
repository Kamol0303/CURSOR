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

export function AdminResetPasswordForm() {
  const t = useTranslations("security");
  const [username, setUsername] = useState("");
  const [newPass, setNewPass] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setSaving(true);
    const res = await apiFetch("/auth/admin/reset-password", {
      method: "POST",
      body: JSON.stringify({ username, new_password: newPass }),
    });
    setSaving(false);
    if (!res.success) {
      const code = (res as { error?: { code?: string } }).error?.code || "UNKNOWN";
      setError(t(`passwordErrors.${code}` as "passwordErrors.INVALID_CREDENTIALS"));
      return;
    }
    setMessage(t("adminResetSuccess", { username }));
    setUsername("");
    setNewPass("");
  };

  return (
    <form onSubmit={submit} className="space-y-4 border-t border-border pt-4 mt-4">
      <h3 className="font-semibold text-foreground">{t("adminResetTitle")}</h3>
      <p className="text-caption text-muted-foreground">{t("adminResetHint")}</p>
      <FormField>
        <Label htmlFor="reset-username">{t("targetUsername")}</Label>
        <Input
          id="reset-username"
          type="text"
          placeholder={t("targetUsername")}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </FormField>
      <FormField>
        <Label htmlFor="reset-password">{t("newPassword")}</Label>
        <Input
          id="reset-password"
          type="password"
          placeholder={t("newPassword")}
          value={newPass}
          onChange={(e) => setNewPass(e.target.value)}
          required
          minLength={12}
        />
      </FormField>
      {error && <Alert variant="danger">{error}</Alert>}
      {message && <Alert variant="success">{message}</Alert>}
      <FormActions className="justify-start pt-0">
        <Button type="submit" loading={saving} variant="accent">
          {saving ? t("saving") : t("adminResetButton")}
        </Button>
      </FormActions>
    </form>
  );
}
