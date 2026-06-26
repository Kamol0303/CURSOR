"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
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
    <form onSubmit={submit} className="space-y-3 border-t pt-4 mt-4">
      <h3 className="font-semibold">{t("adminResetTitle")}</h3>
      <p className="text-xs text-gray-500">{t("adminResetHint")}</p>
      <input
        type="text"
        className="w-full border rounded-lg px-3 py-2"
        placeholder={t("targetUsername")}
        value={username}
        onChange={(e) => setUsername(e.target.value)}
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
      {error && <p className="text-sm text-red-600">{error}</p>}
      {message && <p className="text-sm text-green-700">{message}</p>}
      <button
        type="submit"
        disabled={saving}
        className="px-4 py-2 bg-naqsh-accent text-white rounded-lg text-sm disabled:opacity-50"
      >
        {saving ? t("saving") : t("adminResetButton")}
      </button>
    </form>
  );
}
