"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  Alert,
  Button,
  FormField,
  Input,
  Label,
  Spinner,
} from "@/components/ui";
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
    <div className="space-y-4 border-t border-border pt-4 mt-4">
      <h3 className="font-semibold text-foreground">{t("issueCredentialsTitle")}</h3>
      <p className="text-caption text-muted-foreground">{t("issueCredentialsHint")}</p>

      <FormField>
        <Label htmlFor="credential-search">{t("searchUser")}</Label>
        <Input
          id="credential-search"
          type="text"
          placeholder={t("searchUser")}
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setSelected(null);
          }}
        />
      </FormField>

      {loading && <Spinner label={t("searching")} className="py-2 justify-start" />}

      {!selected && targets.length > 0 && (
        <ul className="border border-border rounded-lg divide-y divide-border max-h-48 overflow-y-auto">
          {targets.map((target) => (
            <li key={target.id}>
              <button
                type="button"
                className="w-full text-left px-3 py-2.5 text-small hover:bg-muted transition-colors"
                onClick={() => setSelected(target)}
              >
                <span className="font-medium text-foreground">{target.display_name}</span>
                <span className="text-muted-foreground ml-2 text-caption">
                  {t(`roles.${target.role}` as "roles.teacher")}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {selected && (
        <Alert variant="info" className="flex justify-between items-center">
          <span>
            {selected.display_name} ({t(`roles.${selected.role}` as "roles.teacher")})
          </span>
          <Button type="button" variant="ghost" size="sm" onClick={() => setSelected(null)}>
            {t("clearSelection")}
          </Button>
        </Alert>
      )}

      {error && <Alert variant="danger">{error}</Alert>}

      {issued && (
        <Alert variant="warning">
          <p className="text-caption font-semibold">{t("credentialsOnce")}</p>
          <p className="text-small mt-2">
            <span className="text-muted-foreground">{t("issuedLogin")}: </span>
            <code className="font-mono">{issued.login}</code>
          </p>
          <p className="text-small mt-1">
            <span className="text-muted-foreground">{t("issuedPassword")}: </span>
            <code className="font-mono">{issued.temporary_password}</code>
          </p>
        </Alert>
      )}

      <Button type="button" disabled={!selected} loading={issuing} onClick={() => void issue()}>
        {issuing ? t("saving") : t("issueCredentialsButton")}
      </Button>
    </div>
  );
}
