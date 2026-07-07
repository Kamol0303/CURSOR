"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";
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

type VerifyResult = {
  valid: boolean;
  status: string;
  holder_name?: string;
  course_name?: string;
  center_name?: string;
  issue_date?: string;
  certificate_number?: string;
};

export default function VerifyPage({ certNumber }: { certNumber?: string }) {
  const t = useTranslations("verify");
  const [number, setNumber] = useState(certNumber || "");
  const [result, setResult] = useState<VerifyResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const verify = async (num: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await apiFetch<VerifyResult>(`/public/verify/${encodeURIComponent(num)}`);
      if (res.success) setResult(res.data);
      else setError(t("notFound"));
    } catch {
      setError(t("notFound"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (certNumber) verify(certNumber);
  }, [certNumber]);

  return (
    <div className="min-h-screen girih-bg flex flex-col">
      <header className="flex justify-end items-center gap-2 p-4">
        <ThemeToggle />
        <LanguageSwitcher />
      </header>
      <main className="flex-1 flex items-center justify-center p-4">
        <Card className="w-full max-w-lg shadow-xl bg-card/95 backdrop-blur-sm">
          <CardBody className="p-8">
            <CardTitle className="text-h3 text-naqsh-primary dark:text-naqsh-accent">
              {t("title")}
            </CardTitle>
            <CardDescription className="mb-6">{t("subtitle")}</CardDescription>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (number.trim()) verify(number.trim());
              }}
              className="space-y-4"
            >
              <FormField>
                <Label htmlFor="cert-number">{t("placeholder")}</Label>
                <Input
                  id="cert-number"
                  type="text"
                  value={number}
                  onChange={(e) => setNumber(e.target.value)}
                  placeholder={t("placeholder")}
                />
              </FormField>
              <Button type="submit" loading={loading} className="w-full">
                {loading ? t("checking") : t("check")}
              </Button>
            </form>
            {result && (
              <Alert variant={result.valid ? "success" : "danger"} className="mt-6">
                <p className="font-semibold">{result.valid ? t("valid") : t("invalid")}</p>
                {result.holder_name && (
                  <dl className="mt-3 space-y-2 text-small">
                    <div>
                      <dt className="text-muted-foreground">{t("holder")}</dt>
                      <dd className="text-foreground">{result.holder_name}</dd>
                    </div>
                    <div>
                      <dt className="text-muted-foreground">{t("course")}</dt>
                      <dd className="text-foreground">{result.course_name}</dd>
                    </div>
                    <div>
                      <dt className="text-muted-foreground">{t("center")}</dt>
                      <dd className="text-foreground">{result.center_name}</dd>
                    </div>
                    <div>
                      <dt className="text-muted-foreground">{t("date")}</dt>
                      <dd className="text-foreground">{result.issue_date}</dd>
                    </div>
                  </dl>
                )}
              </Alert>
            )}
            {error && (
              <Alert variant="danger" className="mt-4">
                {error}
              </Alert>
            )}
          </CardBody>
        </Card>
      </main>
    </div>
  );
}
