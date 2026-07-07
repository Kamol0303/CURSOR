"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { AddCertificateModal } from "@/components/AddCertificateModal";
import { PermissionGate } from "@/components/PermissionGate";
import {
  Button,
  Card,
  CardBody,
  EmptyState,
  PageHeader,
  PageSection,
  CardSkeleton,
} from "@/components/ui";
import { apiFetch, downloadFile, getApiBaseUrl, getMe, listCenters } from "@/lib/api";

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
  const [certs, setCerts] = useState<Cert[]>([]);
  const [loading, setLoading] = useState(true);
  const [centerId, setCenterId] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);

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

  const downloadReport = (format: "pdf" | "excel") => {
    const token = localStorage.getItem("tmb_access_token");
    const url = `${getApiBaseUrl()}/api/v1/reports/ratings?format=${format === "excel" ? "excel" : "pdf"}`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `tmb-ratings.${format === "excel" ? "xlsx" : "pdf"}`;
        a.click();
      });
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
            <Button onClick={() => downloadReport("pdf")}>PDF</Button>
            <Button variant="outline" onClick={() => downloadReport("excel")}>
              Excel
            </Button>
          </>
        }
      />

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
                        onClick={() => downloadFile(c.file_id!, `certificate-${c.certificate_number}`)}
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
