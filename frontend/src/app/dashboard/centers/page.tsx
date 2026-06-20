"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { DashboardLayout } from "@/components/DashboardLayout";
import { listCenters } from "@/lib/api";

type Center = {
  id: string;
  name: string;
  stir: string | null;
  director_name: string | null;
  center_type: string;
  is_active: boolean;
};

export default function CentersPage() {
  const t = useTranslations("centers");
  const [centers, setCenters] = useState<Center[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listCenters()
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setCenters(res.data as Center[]);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
        {loading ? (
          <p className="text-gray-400">{t("loading")}</p>
        ) : (
          <div className="bg-white rounded-xl shadow border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left p-3 font-medium">{t("name")}</th>
                  <th className="text-left p-3 font-medium">{t("stir")}</th>
                  <th className="text-left p-3 font-medium">{t("director")}</th>
                  <th className="text-left p-3 font-medium">{t("type")}</th>
                  <th className="text-left p-3 font-medium">{t("status")}</th>
                </tr>
              </thead>
              <tbody>
                {centers.map((c) => (
                  <tr key={c.id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="p-3">{c.name}</td>
                    <td className="p-3">{c.stir || "—"}</td>
                    <td className="p-3">{c.director_name || "—"}</td>
                    <td className="p-3">{c.center_type}</td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs ${
                          c.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {c.is_active ? t("active") : t("inactive")}
                      </span>
                    </td>
                  </tr>
                ))}
                {centers.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-gray-400">
                      {t("empty")}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
