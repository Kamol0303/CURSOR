"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import {
  Button,
  Card,
  CardBody,
  CardTitle,
  EmptyState,
  PageSkeleton,
} from "@/components/ui";
import { InternalCyberBackground } from "@/components/InternalCyberBackground";
import { DigitalClock } from "@/components/DigitalClock";
import { apiFetch, downloadFile, getApiBaseUrl } from "@/lib/api";

type Child = {
  id: string;
  full_name: string;
  grade: string | null;
  school: string | null;
  center_name: string;
  certificates_count: number;
};

type Certificate = {
  id: string;
  certificate_number: string;
  course_name: string;
  issue_date: string;
  status: string;
  file_id: string | null;
};

export default function ParentDashboardPage() {
  const t = useTranslations("parent");
  const [children, setChildren] = useState<Child[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [certs, setCerts] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Child[]>("/parent/children").then((res) => {
      if (res.success && res.data) {
        setChildren(res.data);
        if (res.data.length > 0) setSelected(res.data[0].id);
      }
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    if (!selected) return;
    apiFetch<Certificate[]>(`/parent/children/${selected}/certificates`).then((res) => {
      if (res.success) setCerts(res.data || []);
    });
  }, [selected]);

  const logout = async () => {
    await fetch(`${getApiBaseUrl()}/api/v1/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    localStorage.removeItem("tmb_access_token");
    window.location.href = "/parent/login";
  };

  return (
    <div className="internal-page-shell min-h-screen bg-background/95">
      <InternalCyberBackground />
      <header className="relative z-10 bg-naqsh-primary text-white px-4 py-5 flex justify-between items-center shadow-sm">
        <div>
          <h1 className="font-bold text-lg">{t("dashboardTitle")}</h1>
          <p className="text-caption text-white/70 mt-0.5">{t("subtitle")}</p>
        </div>
        <Button variant="ghost" size="sm" onClick={logout} className="text-white hover:bg-white/10">
          {t("logout")}
        </Button>
      </header>

      <main className="relative z-10 p-4 max-w-lg mx-auto space-y-5">
        <DigitalClock />
        {loading ? (
          <PageSkeleton />
        ) : children.length === 0 ? (
          <EmptyState title={t("noChildren")} />
        ) : (
          <>
            <Card>
              <CardBody>
                <CardTitle className="mb-4">{t("myChildren")}</CardTitle>
                <div className="space-y-2">
                  {children.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => setSelected(c.id)}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        selected === c.id
                          ? "border-naqsh-accent bg-naqsh-accent/10"
                          : "border-border hover:bg-muted"
                      }`}
                    >
                      <p className="font-medium text-foreground">{c.full_name}</p>
                      <p className="text-caption text-muted-foreground mt-0.5">
                        {c.center_name} · {c.grade || "—"}
                      </p>
                    </button>
                  ))}
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <CardTitle className="mb-4">{t("certificates")}</CardTitle>
                {certs.length === 0 ? (
                  <EmptyState title={t("noCertificates")} className="py-8" />
                ) : (
                  <ul className="space-y-3">
                    {certs.map((cert) => (
                      <li key={cert.id} className="p-4 border border-border rounded-lg text-small">
                        <p className="font-medium text-foreground">{cert.course_name}</p>
                        <p className="text-muted-foreground mt-0.5">{cert.certificate_number}</p>
                        <p className="text-caption text-muted-foreground mt-0.5">{cert.issue_date}</p>
                        <div className="flex gap-3 mt-2">
                          <Link
                            href={`/verify/${cert.certificate_number}`}
                            className="text-naqsh-accent text-caption hover:underline"
                          >
                            {t("verify")}
                          </Link>
                          {cert.file_id && (
                            <button
                              type="button"
                              onClick={() =>
                                downloadFile(cert.file_id!, `certificate-${cert.certificate_number}`)
                              }
                              className="text-naqsh-accent text-caption hover:underline"
                            >
                              {t("download")}
                            </button>
                          )}
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </CardBody>
            </Card>
          </>
        )}
      </main>
    </div>
  );
}
