"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { MfaSetupForm } from "@/components/MfaSetupForm";
import { ChangePasswordForm } from "@/components/ChangePasswordForm";
import { AdminResetPasswordForm } from "@/components/AdminResetPasswordForm";
import { IssueCredentialsForm } from "@/components/IssueCredentialsForm";
import { PermissionGate } from "@/components/PermissionGate";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardTitle,
  PageHeader,
  PageSection,
} from "@/components/ui";
import { getApiBaseUrl, getToken } from "@/lib/api";

export default function SecurityPage() {
  const t = useTranslations("security");
  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [mfaRequired, setMfaRequired] = useState(false);
  const [showSetup, setShowSetup] = useState(false);
  const [backupCodes, setBackupCodes] = useState<string[] | null>(null);
  const [regenerating, setRegenerating] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    import("@/lib/api").then(({ getMe }) => {
      getMe().then((me) => {
        if (!me.success) return;
        setMfaEnabled(me.data.mfa_enabled);
        setMfaRequired(me.data.mfa_required ?? false);
      });
    });
  }, []);

  const regenerateBackupCodes = async () => {
    setRegenerating(true);
    setError(null);
    setMessage(null);
    setBackupCodes(null);
    try {
      const token = getToken();
      const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/mfa/backup-codes/regenerate`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        credentials: "include",
      });
      const data = await res.json();
      if (!res.ok) {
        setError(t(`errors.${data.detail?.code || "MFA_NOT_CONFIGURED"}` as "errors.MFA_INVALID"));
        return;
      }
      setBackupCodes(data.data?.backup_codes || []);
      setMessage(t("backupCodesRegenerated"));
    } catch {
      setError(t("errors.MFA_INVALID"));
    } finally {
      setRegenerating(false);
    }
  };

  return (
    <PageSection className="max-w-lg">
      <PageHeader title={t("title")} description={t("subtitle")} />

      <Card>
        <CardBody>
          <ChangePasswordForm />
        </CardBody>
      </Card>

      <PermissionGate permission="users.password_reset">
        <Card>
          <CardBody>
            <AdminResetPasswordForm />
          </CardBody>
        </Card>
      </PermissionGate>

      <PermissionGate permission="security.credentials.issue">
        <Card>
          <CardBody>
            <IssueCredentialsForm />
          </CardBody>
        </Card>
      </PermissionGate>

      <Card>
        <CardBody className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>{t("mfaLabel")}</CardTitle>
              <p className="text-small text-muted-foreground mt-0.5">
                {mfaEnabled ? t("mfaEnabled") : t("mfaDisabled")}
                {mfaRequired && ` · ${t("mfaRequired")}`}
              </p>
            </div>
            <Badge variant={mfaEnabled ? "success" : "warning"}>
              {mfaEnabled ? t("statusOn") : t("statusOff")}
            </Badge>
          </div>

          {!mfaEnabled && !showSetup && (
            <Button
              onClick={() => {
                setShowSetup(true);
                setError(null);
                setMessage(null);
              }}
            >
              {t("enableMfa")}
            </Button>
          )}

          {showSetup && !mfaEnabled && (
            <MfaSetupForm
              accessToken={getToken() || undefined}
              onComplete={() => {
                setMfaEnabled(true);
                setShowSetup(false);
                setMessage(t("mfaEnabledSuccess"));
              }}
              onError={(code) => setError(t(`errors.${code}` as "errors.MFA_INVALID"))}
            />
          )}

          {mfaEnabled && (
            <div className="space-y-2 pt-2 border-t border-border">
              <p className="text-small text-muted-foreground">{t("backupCodesHint")}</p>
              <Button variant="outline" onClick={regenerateBackupCodes} disabled={regenerating} loading={regenerating}>
                {regenerating ? t("backupCodesRegenerating") : t("regenerateBackupCodes")}
              </Button>
              {backupCodes && (
                <Alert variant="warning">
                  <p className="text-caption font-semibold mb-2">{t("backupCodesOnce")}</p>
                  <ul className="font-mono text-small space-y-1">
                    {backupCodes.map((code) => (
                      <li key={code}>{code}</li>
                    ))}
                  </ul>
                </Alert>
              )}
            </div>
          )}

          {message && <Alert variant="success">{message}</Alert>}
          {error && <Alert variant="danger">{error}</Alert>}
        </CardBody>
      </Card>
    </PageSection>
  );
}
