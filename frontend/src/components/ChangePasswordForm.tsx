"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
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
    <form onSubmit={submit} className="space-y-3">
      <h3 className="font-semibold">{t("changePasswordTitle")}</h3>
      <input
        type="password"
        className="w-full border rounded-lg px-3 py-2"
        placeholder={t("currentPassword")}
        value={current}
        onChange={(e) => setCurrent(e.target.value)}
        required
      />
      <input
        type="password"
        className="w-full border rounded-lg px-3 py-2"
        placeholder={t("newPassword")}
        value={newPass}
        onChange={(e) => setNewPass(e.target.value)}
        required
        minLength={12}
      />
      <input
        type="password"
        className="w-full border rounded-lg px-3 py-2"
        placeholder={t("confirmPassword")}
        value={confirm}
        onChange={(e) => setConfirm(e.target.value)}
        required
        minLength={12}
      />
      <p className="text-xs text-gray-500">{t("passwordPolicy")}</p>
      {error && <p className="text-sm text-red-600">{error}</p>}
      {message && <p className="text-sm text-green-700">{message}</p>}
      <button
        type="submit"
        disabled={saving}
        className="px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm disabled:opacity-50"
      >
        {saving ? t("saving") : t("changePasswordButton")}
      </button>
    </form>
  );
}
