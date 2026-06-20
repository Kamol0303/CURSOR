"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiFetch } from "@/lib/api";

type Rating = {
  center_name: string;
  total_score: number;
  rank: number;
  rank_change: number | null;
  flagged_anomaly: boolean;
};

export default function RatingsPage() {
  const t = useTranslations("ratings");
  const [ratings, setRatings] = useState<Rating[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Rating[]>("/ratings?limit=20")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setRatings(res.data);
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
                  <th className="text-left p-3">{t("rank")}</th>
                  <th className="text-left p-3">{t("center")}</th>
                  <th className="text-left p-3">{t("score")}</th>
                  <th className="text-left p-3">{t("change")}</th>
                </tr>
              </thead>
              <tbody>
                {ratings.map((r) => (
                  <tr key={r.rank} className="border-b hover:bg-gray-50">
                    <td className="p-3">
                      {r.rank <= 3 ? ["🥇", "🥈", "🥉"][r.rank - 1] : r.rank}
                    </td>
                    <td className="p-3">{r.center_name}</td>
                    <td className="p-3 font-medium">{r.total_score.toFixed(1)}</td>
                    <td className="p-3">
                      {r.rank_change != null
                        ? r.rank_change > 0
                          ? `↑${r.rank_change}`
                          : r.rank_change < 0
                            ? `↓${Math.abs(r.rank_change)}`
                            : "—"
                        : "—"}
                      {r.flagged_anomaly && (
                        <span className="ml-2 text-xs text-amber-600">{t("flagged")}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
