"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  Button,
  FormField,
  Input,
  Label,
  Spinner,
} from "@/components/ui";
import { getApiBaseUrl } from "@/lib/api";
import { setAuthCookie } from "@/lib/auth-cookie";

type SetupData = {
  provisioning_uri: string;
  secret: string;
  issuer: string;
};

type Props = {
  setupToken?: string;
  accessToken?: string;
  onComplete: (accessToken?: string) => void;
  onError: (code: string) => void;
};

export function MfaSetupForm({ setupToken, accessToken, onComplete, onError }: Props) {
  const t = useTranslations("auth");
  const [setup, setSetup] = useState<SetupData | null>(null);
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [initLoading, setInitLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      try {
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (accessToken) headers.Authorization = `Bearer ${accessToken}`;

        const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/mfa/setup/init`, {
          method: "POST",
          headers,
          credentials: "include",
          body: JSON.stringify(setupToken ? { setup_token: setupToken } : {}),
        });
        const data = await res.json();
        if (!res.ok) {
          onError(data.detail?.code || "MFA_SETUP_EXPIRED");
          return;
        }
        setSetup(data.data);
      } catch {
        onError("MFA_SETUP_EXPIRED");
      } finally {
        setInitLoading(false);
      }
    };
    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [setupToken, accessToken]);

  const handleConfirm = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (accessToken) headers.Authorization = `Bearer ${accessToken}`;

      const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/mfa/setup/confirm`, {
        method: "POST",
        headers,
        credentials: "include",
        body: JSON.stringify({
          code,
          ...(setupToken ? { setup_token: setupToken } : {}),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        onError(data.detail?.code || "MFA_INVALID");
        return;
      }
      onComplete(data.data?.access_token);
      if (data.data?.access_token) {
        setAuthCookie(data.data.access_token);
      }
      if (data.data?.backup_codes?.length) {
        window.alert(`Backup kodlar (bir marta ko'rsatiladi):\n${data.data.backup_codes.join("\n")}`);
      }
    } catch {
      onError("MFA_INVALID");
    } finally {
      setLoading(false);
    }
  };

  if (initLoading) {
    return <Spinner label={t("mfaSetupLoading")} className="py-4" />;
  }

  if (!setup) {
    return null;
  }

  return (
    <form onSubmit={handleConfirm} className="space-y-4">
      <h2 className="font-semibold text-naqsh-primary">{t("mfaSetupTitle")}</h2>
      <p className="text-small text-muted-foreground">{t("mfaSetupInstructions")}</p>
      <div className="rounded-lg bg-muted p-3 text-small font-mono break-all">
        <div className="text-caption text-muted-foreground mb-1">{t("mfaSetupSecret")}</div>
        {setup.secret}
      </div>
      <details className="text-caption text-muted-foreground">
        <summary className="cursor-pointer">{t("mfaSetupAdvanced")}</summary>
        <p className="mt-2 break-all font-mono">{setup.provisioning_uri}</p>
      </details>
      <FormField>
        <Label htmlFor="mfa-setup-code">{t("mfaCode")}</Label>
        <Input
          id="mfa-setup-code"
          type="text"
          inputMode="numeric"
          autoComplete="one-time-code"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="tracking-widest text-center"
          required
        />
      </FormField>
      <Button type="submit" loading={loading} className="w-full" variant="accent">
        {t("mfaSetupConfirm")}
      </Button>
    </form>
  );
}
