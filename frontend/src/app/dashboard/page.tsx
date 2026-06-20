"use client";

import { useEffect } from "react";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";

export default function DashboardPage() {
  const t = useTranslations("auth");

  useEffect(() => {
    const token = localStorage.getItem("tamor_access_token");
    if (!token) {
      window.location.href = "/";
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <h1 className="text-lg font-bold text-naqsh-primary">TaMoR Dashboard</h1>
        <LanguageSwitcher />
      </header>
      <main className="p-6">
        <div className="bg-white rounded-xl shadow p-6 border">
          <p className="text-gray-600">
            Phase 0 — Authentication complete. Full dashboard coming in Phase 1.
          </p>
        </div>
      </main>
    </div>
  );
}
