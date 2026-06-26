"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

type CredentialTarget = {
  id: string;
  username: string | null;
  phone: string | null;
  role: string;
  display_name: string;
};

export function IssueCredentialsForm() {
  const t = useTranslations("security");
  const [search, setSearch] = useState("");
  const [targets, setTargets] = useState<CredentialTarget[]>([]);
  const [selected, setSelected] = useState<CredentialTarget | null>(null);
  const [issued, setIssued] = useState<{ login: string; temporary_password: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [issuing, setIssuing] = useState(false);

  const loadTargets = useCallback(async (query: string) => {
    setLoading(true);
    const params = query.trim() ? `?search=${encodeURIComponent(query.trim())}` : "";
    const res = await apiFetch<CredentialTarget[]>(`/auth/admin/credential-targets${params}`);
    setLoading(false);
    if (res.success && Array.isArray(res.data)) {
      setTargets(res.data);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      void loadTargets(search);
    }, 250);
    return () => clearTimeout(timer);
  }, [search, loadTargets]);

  const issue = async () => {
    if (!selected) return;
    setError(null);
    setIssued(null);
    setIssuing(true);
    const res = await apiFetch<{ login: string; temporary_password: string }>("/auth/admin/issue-credentials", {
      method: "POST",
      body: JSON.stringify({ target_user_id: selected.id }),
    });
    setIssuing(false);
    if (!res.success) {
      const code = (res as { error?: { code?: string } }).error?.code || "UNKNOWN";
      setError(t(`passwordErrors.${code}` as "passwordErrors.UNKNOWN"));
      return;
    }
    const data = res.data as { login: string; temporary_password: string };
    setIssued({ login: data.login, temporary_password: data.temporary_password });
    setSelected(null);
    setSearch("");
  };

  return (
    <div className="space-y-3 border-t pt-4 mt-4">
      <h3 className="font-semibold">{t("issueCredentialsTitle")}</h3>
      <p className="text-xs text-gray-500">{t("issueCredentialsHint")}</p>

      <input
        type="text"
        className="w-full border rounded-lg px-3 py-2"
        placeholder={t("searchUser")}
        value={search}
        onChange={(e) => {
          setSearch(e.target.value);
          setSelected(null);
        }}
      />

      {loading && <p className="text-xs text-gray-400">{t("searching")}</p>}

      {!selected && targets.length > 0 && (
        <ul className="border rounded-lg divide-y max-h-48 overflow-y-auto">
          {targets.map((target) => (
            <li key={target.id}>
              <button
                type="button"
                className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50"
                onClick={() => setSelected(target)}
              >
                <span className="font-medium">{target.display_name}</span>
                <span className="text-gray-500 ml-2 text-xs">
                  {t(`roles.${target.role}` as "roles.teacher")}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {selected && (
        <div className="rounded-lg bg-blue-50 border border-blue-200 p-3 text-sm flex justify-between items-center">
          <span>
            {selected.display_name} ({t(`roles.${selected.role}` as "roles.teacher")})
          </span>
          <button type="button" className="text-xs text-blue-700 underline" onClick={() => setSelected(null)}>
            {t("clearSelection")}
          </button>
        </div>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}

      {issued && (
        <div className="rounded-lg bg-amber-50 border border-amber-200 p-3 space-y-2">
          <p className="text-xs font-semibold text-amber-900">{t("credentialsOnce")}</p>
          <p className="text-sm">
            <span className="text-gray-600">{t("issuedLogin")}: </span>
            <code className="font-mono">{issued.login}</code>
          </p>
          <p className="text-sm">
            <span className="text-gray-600">{t("issuedPassword")}: </span>
            <code className="font-mono">{issued.temporary_password}</code>
          </p>
        </div>
      )}

      <button
        type="button"
        disabled={!selected || issuing}
        onClick={() => void issue()}
        className="px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm disabled:opacity-50"
      >
        {issuing ? t("saving") : t("issueCredentialsButton")}
      </button>
    </div>
  );
}
