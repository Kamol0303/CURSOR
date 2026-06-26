"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
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
    <div className="min-h-screen bg-gray-50">
      <header className="bg-naqsh-primary text-white px-4 py-4 flex justify-between items-center">
        <div>
          <h1 className="font-bold text-lg">{t("dashboardTitle")}</h1>
          <p className="text-xs text-white/70">{t("subtitle")}</p>
        </div>
        <button type="button" onClick={logout} className="text-sm underline">
          {t("logout")}
        </button>
      </header>

      <main className="p-4 max-w-lg mx-auto space-y-4">
        {loading ? (
          <p className="text-gray-500">{t("loading")}</p>
        ) : children.length === 0 ? (
          <p className="text-gray-500">{t("noChildren")}</p>
        ) : (
          <>
            <section className="bg-white rounded-xl border p-4">
              <h2 className="font-semibold text-naqsh-primary mb-3">{t("myChildren")}</h2>
              <div className="space-y-2">
                {children.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => setSelected(c.id)}
                    className={`w-full text-left p-3 rounded-lg border ${
                      selected === c.id ? "border-naqsh-accent bg-amber-50" : "border-gray-200"
                    }`}
                  >
                    <p className="font-medium">{c.full_name}</p>
                    <p className="text-xs text-gray-500">
                      {c.center_name} · {c.grade || "—"}
                    </p>
                  </button>
                ))}
              </div>
            </section>

            <section className="bg-white rounded-xl border p-4">
              <h2 className="font-semibold text-naqsh-primary mb-3">{t("certificates")}</h2>
              {certs.length === 0 ? (
                <p className="text-sm text-gray-500">{t("noCertificates")}</p>
              ) : (
                <ul className="space-y-2">
                  {certs.map((cert) => (
                    <li key={cert.id} className="p-3 border rounded-lg text-sm">
                      <p className="font-medium">{cert.course_name}</p>
                      <p className="text-gray-500">{cert.certificate_number}</p>
                      <p className="text-xs text-gray-400">{cert.issue_date}</p>
                      <div className="flex gap-3 mt-1">
                        <Link
                          href={`/verify/${cert.certificate_number}`}
                          className="text-naqsh-accent text-xs hover:underline"
                        >
                          {t("verify")}
                        </Link>
                        {cert.file_id && (
                          <button
                            type="button"
                            onClick={() =>
                              downloadFile(cert.file_id!, `certificate-${cert.certificate_number}`)
                            }
                            className="text-naqsh-accent text-xs hover:underline"
                          >
                            {t("download")}
                          </button>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}
