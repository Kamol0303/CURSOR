"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { getRoleFromToken, homePathForRole } from "@/lib/auth-cookie";

export default function ForbiddenPage() {
  const t = useTranslations("forbidden");
  const [home, setHome] = useState("/dashboard");

  useEffect(() => {
    const token = localStorage.getItem("tmb_access_token");
    if (token) {
      setHome(homePathForRole(getRoleFromToken(token)));
    }
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <div className="text-center max-w-md">
        <p className="text-5xl font-bold text-naqsh-primary">403</p>
        <h1 className="text-xl font-semibold text-gray-900 mt-4">{t("title")}</h1>
        <p className="text-gray-600 mt-2">{t("message")}</p>
        <Link
          href={home}
          className="inline-block mt-8 px-5 py-2.5 bg-naqsh-primary text-white rounded-lg text-sm font-medium hover:bg-naqsh-primary/90"
        >
          {t("goHome")}
        </Link>
      </div>
    </div>
  );
}
