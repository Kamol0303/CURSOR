"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiFetch } from "@/lib/api";

type Cert = {
  certificate_number: string;
  student_name: string;
  center_name: string;
  course_name: string;
  issue_date: string;
  status: string;
  qr_base64: string;
};

export default function CertificatesPage() {
  const t = useTranslations("certificates");
  const [certs, setCerts] = useState<Cert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Cert[]>("/certificates")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setCerts(res.data);
      })
      .finally(() => setLoading(false));
  }, []);

  const downloadReport = (format: "pdf" | "excel") => {
    const token = localStorage.getItem("tmb_access_token");
    const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/reports/ratings?format=${format === "excel" ? "excel" : "pdf"}`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `tamor-ratings.${format === "excel" ? "xlsx" : "pdf"}`;
        a.click();
      });
  };

  return (
    <DashboardLayout>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => downloadReport("pdf")}
              className="px-3 py-1.5 text-sm bg-naqsh-primary text-white rounded-lg"
            >
              PDF
            </button>
            <button
              type="button"
              onClick={() => downloadReport("excel")}
              className="px-3 py-1.5 text-sm border border-naqsh-primary text-naqsh-primary rounded-lg"
            >
              Excel
            </button>
          </div>
        </div>
        {loading ? (
          <p className="text-gray-400">{t("loading")}</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {certs.map((c) => (
              <div key={c.certificate_number} className="bg-white rounded-xl border p-4 shadow-sm">
                <div className="flex gap-4">
                  <img
                    src={`data:image/png;base64,${c.qr_base64}`}
                    alt="QR"
                    className="w-20 h-20"
                  />
                  <div>
                    <p className="font-mono text-sm text-naqsh-primary">{c.certificate_number}</p>
                    <p className="font-medium mt-1">{c.student_name}</p>
                    <p className="text-sm text-gray-500">{c.course_name}</p>
                    <p className="text-xs text-gray-400 mt-1">{c.issue_date}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
