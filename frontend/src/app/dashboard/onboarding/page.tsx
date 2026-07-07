"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { ChangePasswordForm } from "@/components/ChangePasswordForm";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardTitle,
  FormField,
  FormGrid,
  Input,
  Label,
  PageHeader,
  PageSection,
  Select,
  Textarea,
} from "@/components/ui";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function OnboardingPage() {
  const t = useTranslations("onboarding");
  const tc = useTranslations("centers");
  const router = useRouter();
  const { user, refresh, mustChangePassword, centerProfileCompleted } = useAuth();

  const [stir, setStir] = useState("");
  const [directorName, setDirectorName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [address, setAddress] = useState("");
  const [licenseNumber, setLicenseNumber] = useState("");
  const [centerType, setCenterType] = useState("private");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [step, setStep] = useState<"password" | "profile">("password");

  useEffect(() => {
    if (user && user.role !== "center_director") {
      router.replace("/dashboard");
    }
  }, [user, router]);

  useEffect(() => {
    if (!mustChangePassword) {
      setStep("profile");
    }
  }, [mustChangePassword]);

  useEffect(() => {
    if (user?.role === "center_director" && !mustChangePassword && centerProfileCompleted) {
      router.replace("/dashboard");
    }
  }, [user, mustChangePassword, centerProfileCompleted, router]);

  const submitProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const res = await apiFetch("/centers/onboarding/complete", {
        method: "POST",
        body: JSON.stringify({
          stir,
          director_name: directorName,
          phone,
          email: email || null,
          address,
          license_number: licenseNumber || null,
          center_type: centerType,
        }),
      });
      if (!res.success) {
        setError(tc("saveError"));
        return;
      }
      await refresh();
      router.replace("/dashboard");
    } catch {
      setError(tc("saveError"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <PageSection className="max-w-xl mx-auto">
      <PageHeader title={t("title")} description={t("subtitle")} />

      <div className="flex gap-2 text-small">
        <span className={step === "password" ? "font-semibold text-naqsh-primary" : "text-muted-foreground"}>
          1. {t("stepPassword")}
        </span>
        <span className="text-muted-foreground">→</span>
        <span className={step === "profile" ? "font-semibold text-naqsh-primary" : "text-muted-foreground"}>
          2. {t("stepProfile")}
        </span>
      </div>

      {step === "password" && mustChangePassword && (
        <Card>
          <CardBody>
            <CardTitle className="mb-4">{t("changePasswordTitle")}</CardTitle>
            <ChangePasswordForm
              onSuccess={async () => {
                await refresh();
                setStep("profile");
              }}
            />
          </CardBody>
        </Card>
      )}

      {step === "profile" && (
        <Card>
          <CardBody>
            <form onSubmit={submitProfile} className="space-y-4">
              <CardTitle>{t("profileTitle")}</CardTitle>
              <FormGrid>
                <FormField>
                  <Label>{tc("stir")}</Label>
                  <Input
                    className="font-mono"
                    value={stir}
                    onChange={(e) => setStir(e.target.value)}
                    pattern="\d{9}"
                    required
                  />
                </FormField>
                <FormField>
                  <Label>{tc("type")}</Label>
                  <Select value={centerType} onChange={(e) => setCenterType(e.target.value)}>
                    <option value="private">{tc("typePrivate")}</option>
                    <option value="public">{tc("typePublic")}</option>
                  </Select>
                </FormField>
              </FormGrid>
              <FormField>
                <Label>{tc("director")}</Label>
                <Input value={directorName} onChange={(e) => setDirectorName(e.target.value)} required />
              </FormField>
              <FormGrid>
                <FormField>
                  <Label>{tc("phone")}</Label>
                  <Input value={phone} onChange={(e) => setPhone(e.target.value)} required />
                </FormField>
                <FormField>
                  <Label>{tc("email")}</Label>
                  <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
                </FormField>
              </FormGrid>
              <FormField>
                <Label>{tc("address")}</Label>
                <Textarea rows={2} value={address} onChange={(e) => setAddress(e.target.value)} required />
              </FormField>
              <FormField>
                <Label>{tc("license")}</Label>
                <Input value={licenseNumber} onChange={(e) => setLicenseNumber(e.target.value)} />
              </FormField>
              {error && <Alert variant="danger">{error}</Alert>}
              <Button type="submit" disabled={saving} loading={saving} className="w-full">
                {saving ? tc("saving") : t("complete")}
              </Button>
            </form>
          </CardBody>
        </Card>
      )}
    </PageSection>
  );
}
