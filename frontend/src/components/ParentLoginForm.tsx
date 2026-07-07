"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import Link from "next/link";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardDescription,
  CardTitle,
  FormField,
  Input,
  Label,
} from "@/components/ui";
import { apiFetch } from "@/lib/api";

export function ParentLoginForm() {
  const t = useTranslations("parent");
  const [phone, setPhone] = useState("+998");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const requestOtp = async () => {
    setLoading(true);
    setError("");
    const res = await apiFetch("/auth/parent/request-otp", {
      method: "POST",
      body: JSON.stringify({ phone }),
    });
    setLoading(false);
    if (res.success) {
      setStep("otp");
    } else {
      setError(t(`errors.${res.error?.code || "UNKNOWN"}`));
    }
  };

  const verifyOtp = async () => {
    setLoading(true);
    setError("");
    const res = await apiFetch<{ access_token: string }>("/auth/parent/verify-otp", {
      method: "POST",
      body: JSON.stringify({ phone, otp }),
    });
    setLoading(false);
    if (res.success && res.data?.access_token) {
      localStorage.setItem("tmb_access_token", res.data.access_token);
      window.location.href = "/parent/dashboard";
    } else {
      setError(t(`errors.${res.error?.code || "UNKNOWN"}`));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardBody className="p-8">
          <CardTitle className="text-h2 text-naqsh-primary">{t("title")}</CardTitle>
          <CardDescription className="mb-6">{t("subtitle")}</CardDescription>

          {step === "phone" ? (
            <div className="space-y-4">
              <FormField>
                <Label>{t("phone")}</Label>
                <Input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+998901234567"
                />
              </FormField>
              <Button
                type="button"
                onClick={requestOtp}
                loading={loading}
                disabled={phone.length < 13}
                className="w-full"
              >
                {loading ? t("sending") : t("sendOtp")}
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <FormField>
                <Label>{t("otp")}</Label>
                <Input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  className="tracking-widest"
                  placeholder="123456"
                  maxLength={6}
                />
              </FormField>
              <Button
                type="button"
                onClick={verifyOtp}
                loading={loading}
                disabled={otp.length < 4}
                className="w-full"
              >
                {loading ? t("verifying") : t("verify")}
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setStep("phone")}
                className="w-full"
              >
                {t("changePhone")}
              </Button>
            </div>
          )}

          {error && (
            <Alert variant="danger" className="mt-4">
              {error}
            </Alert>
          )}

          <p className="mt-6 text-center text-small text-muted-foreground">
            <Link href="/" className="text-naqsh-accent hover:underline">
              {t("staffLogin")}
            </Link>
          </p>
        </CardBody>
      </Card>
    </div>
  );
}
