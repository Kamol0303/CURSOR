"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
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
      <header className="flex justify-end p-4">
        <LanguageSwitcher />
      </header>
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-lg bg-white/95 rounded-2xl shadow-xl border border-naqsh-primary/10 p-8">
          <h1 className="text-xl font-bold text-naqsh-primary mb-2">{t("title")}</h1>
          <p className="text-sm text-gray-600 mb-6">{t("subtitle")}</p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (number.trim()) verify(number.trim());
            }}
            className="space-y-4"
          >
            <input
              type="text"
              value={number}
              onChange={(e) => setNumber(e.target.value)}
              placeholder={t("placeholder")}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-naqsh-primary/30 outline-none"
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-naqsh-primary text-white rounded-lg font-medium disabled:opacity-50"
            >
              {loading ? t("checking") : t("check")}
            </button>
          </form>
          {result && (
            <div
              className={`mt-6 p-4 rounded-lg border ${
                result.valid ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"
              }`}
            >
              <p className="font-semibold">{result.valid ? t("valid") : t("invalid")}</p>
              {result.holder_name && (
                <dl className="mt-3 space-y-1 text-sm">
                  <div>
                    <dt className="text-gray-500">{t("holder")}</dt>
                    <dd>{result.holder_name}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">{t("course")}</dt>
                    <dd>{result.course_name}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">{t("center")}</dt>
                    <dd>{result.center_name}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">{t("date")}</dt>
                    <dd>{result.issue_date}</dd>
                  </div>
                </dl>
              )}
            </div>
          )}
          {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
        </div>
      </main>
    </div>
  );
}
