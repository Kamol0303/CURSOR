"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  Badge,
  DataTable,
  EmptyState,
  PageHeader,
  PageSection,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableSkeleton,
} from "@/components/ui";
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
    <PageSection>
      <PageHeader title={t("title")} />

      {loading ? (
        <DataTable>
          <TableSkeleton rows={8} cols={4} />
        </DataTable>
      ) : ratings.length === 0 ? (
        <DataTable>
          <EmptyState title={t("empty", { defaultValue: "No ratings found" })} />
        </DataTable>
      ) : (
        <DataTable>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("rank")}</TableHead>
                <TableHead>{t("center")}</TableHead>
                <TableHead>{t("score")}</TableHead>
                <TableHead>{t("change")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {ratings.map((r) => (
                <TableRow key={r.rank}>
                  <TableCell>{r.rank <= 3 ? ["🥇", "🥈", "🥉"][r.rank - 1] : r.rank}</TableCell>
                  <TableCell className="font-medium">{r.center_name}</TableCell>
                  <TableCell className="font-semibold">{r.total_score.toFixed(1)}</TableCell>
                  <TableCell>
                    {r.rank_change != null
                      ? r.rank_change > 0
                        ? `↑${r.rank_change}`
                        : r.rank_change < 0
                          ? `↓${Math.abs(r.rank_change)}`
                          : "—"
                      : "—"}
                    {r.flagged_anomaly && (
                      <Badge variant="warning" className="ml-2">
                        {t("flagged")}
                      </Badge>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </DataTable>
      )}
    </PageSection>
  );
}
