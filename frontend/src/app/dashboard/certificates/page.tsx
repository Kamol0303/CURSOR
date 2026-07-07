"use client";

import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { AddCertificateModal } from "@/components/AddCertificateModal";
import { PermissionGate } from "@/components/PermissionGate";
import {
  Alert,
  Button,
  Card,
  CardBody,
  EmptyState,
  PageHeader,
  PageSection,
  CardSkeleton,
} from "@/components/ui";
import { apiFetch, downloadFile, downloadRatingsReport, getMe, listCenters } from "@/lib/api";

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
    <PageSection>
      <PageHeader
        title={t("title")}
        actions={
          <>
            <PermissionGate permission="certificates.create">
              <Button variant="accent" onClick={() => setShowAdd(true)} disabled={!centerId}>
                {t("add")}
              </Button>
            </PermissionGate>
            <PermissionGate permission="reports.generate">
              <Button onClick={() => handleExport("pdf")} loading={exporting === "pdf"} disabled={exporting !== null}>
                {exporting === "pdf" ? t("exporting") : t("exportPdf")}
              </Button>
              <Button variant="outline" onClick={() => handleExport("excel")} loading={exporting === "excel"} disabled={exporting !== null}>
                {exporting === "excel" ? t("exporting") : t("exportExcel")}
              </Button>
            </PermissionGate>
          </>
        }
      />

      {exportError && <Alert variant="danger">{exportError}</Alert>}
      {downloadError && <Alert variant="danger">{downloadError}</Alert>}

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : certs.length === 0 ? (
        <EmptyState title={t("empty", { defaultValue: "No certificates found" })} />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {certs.map((c) => (
            <Card key={c.certificate_number} hover>
              <CardBody>
                <div className="flex gap-4">
                  <img src={`data:image/png;base64,${c.qr_base64}`} alt="QR" className="w-20 h-20" />
                  <div className="flex-1 min-w-0">
                    <p className="font-mono text-small text-naqsh-primary">{c.certificate_number}</p>
                    <p className="font-medium mt-1">{c.student_name}</p>
                    <p className="text-small text-muted-foreground">{c.course_name}</p>
                    <p className="text-caption text-muted-foreground mt-1">{c.issue_date}</p>
                    {c.file_id && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="mt-2"
                        onClick={() => handleCertDownload(c.file_id!, `certificate-${c.certificate_number}`)}
                      >
                        {t("download")}
                      </Button>
                    )}
                  </div>
                </div>
              </CardBody>
            </Card>
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
    </PageSection>
  );
}
