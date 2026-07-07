"use client";

import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { AddCertificateModal } from "@/components/AddCertificateModal";
import { PermissionGate } from "@/components/PermissionGate";
import {
  apiFetch,
  downloadFile,
  downloadRatingsReport,
  getMe,
  listCenters,
} from "@/lib/api";

type Cert = {
  id: string;
  certificate_number: string;
  student_name: string;
  center_name: string;
  course_name: string;
  issue_date: string;
  status: string;
  file_id: string | null;
  qr_base64: string;
};

export default function CertificatesPage() {
  const t = useTranslations("certificates");
  const locale = useLocale();
  const [certs, setCerts] = useState<Cert[]>([]);
  const [loading, setLoading] = useState(true);
  const [centerId, setCenterId] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [exporting, setExporting] = useState<"pdf" | "excel" | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    apiFetch<Cert[]>("/certificates")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setCerts(res.data);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    getMe().then(async (res) => {
      if (res.success && res.data?.center_id) {
        setCenterId(res.data.center_id as string);
      } else {
        const centers = await listCenters();
        if (centers.success && Array.isArray(centers.data) && centers.data[0]) {
          setCenterId((centers.data[0] as { id: string }).id);
        }
      }
    });
  }, [load]);

  const handleExport = async (format: "pdf" | "excel") => {
    setExporting(format);
    setExportError(null);
    const result = await downloadRatingsReport(format, locale);
    setExporting(null);
    if (!result.ok) {
      const key = `exportErrors.${result.code}` as const;
      setExportError(t.has(key) ? t(key) : t("exportErrors.UNKNOWN"));
    }
  };

  const handleCertDownload = async (fileId: string, fileName: string) => {
    setDownloadError(null);
    const ok = await downloadFile(fileId, fileName);
    if (!ok) setDownloadError(t("downloadError"));
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center flex-wrap gap-2">
        <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
        <div className="flex gap-2 flex-wrap">
          <PermissionGate permission="certificates.create">
            <button
              type="button"
              onClick={() => setShowAdd(true)}
              disabled={!centerId}
              className="px-3 py-1.5 text-sm bg-naqsh-accent text-white rounded-lg disabled:opacity-50"
            >
              {t("add")}
            </button>
          </PermissionGate>
          <PermissionGate permission="reports.generate">
            <button
              type="button"
              onClick={() => handleExport("pdf")}
              disabled={exporting !== null}
              className="px-3 py-1.5 text-sm bg-naqsh-primary text-white rounded-lg disabled:opacity-50"
            >
              {exporting === "pdf" ? t("exporting") : t("exportPdf")}
            </button>
            <button
              type="button"
              onClick={() => handleExport("excel")}
              disabled={exporting !== null}
              className="px-3 py-1.5 text-sm border border-naqsh-primary text-naqsh-primary rounded-lg disabled:opacity-50"
            >
              {exporting === "excel" ? t("exporting") : t("exportExcel")}
            </button>
          </PermissionGate>
        </div>
      </div>

      {exportError && <p className="text-sm text-red-600">{exportError}</p>}
      {downloadError && <p className="text-sm text-red-600">{downloadError}</p>}

      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {certs.map((c) => (
            <div key={c.certificate_number} className="bg-white rounded-xl border p-4 shadow-sm">
              <div className="flex gap-4">
                <img src={`data:image/png;base64,${c.qr_base64}`} alt="QR" className="w-20 h-20" />
                <div className="flex-1 min-w-0">
                  <p className="font-mono text-sm text-naqsh-primary">{c.certificate_number}</p>
                  <p className="font-medium mt-1">{c.student_name}</p>
                  <p className="text-sm text-gray-500">{c.course_name}</p>
                  <p className="text-xs text-gray-400 mt-1">{c.issue_date}</p>
                  {c.file_id && (
                    <button
                      type="button"
                      onClick={() => handleCertDownload(c.file_id!, `certificate-${c.certificate_number}`)}
                      className="text-xs text-naqsh-accent hover:underline mt-2"
                    >
                      {t("download")}
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      {showAdd && centerId && (
        <AddCertificateModal
          centerId={centerId}
          onClose={() => setShowAdd(false)}
          onSaved={load}
        />
      )}
    </div>
  );
}
