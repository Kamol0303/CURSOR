"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  DataTable,
  EmptyState,
  PageHeader,
  PageSection,
  Select,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableSkeleton,
} from "@/components/ui";
import { apiFetch } from "@/lib/api";

type MonitorMessage = {
  id: string;
  center_id: string;
  center_name: string;
  sender_name: string | null;
  recipient_name: string | null;
  title: string;
  body: string;
  sent_at: string;
};

type Center = { id: string; name: string };

export default function MessagesMonitorPage() {
  const t = useTranslations("messagesMonitor");
  const [centerId, setCenterId] = useState("");
  const [centers, setCenters] = useState<Center[]>([]);
  const [items, setItems] = useState<MonitorMessage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Center[]>("/centers?per_page=100").then((res) => {
      if (res.success && Array.isArray(res.data)) setCenters(res.data);
    });
  }, []);

  const load = useCallback(() => {
    setLoading(true);
    const params = centerId ? `?center_id=${centerId}` : "";
    apiFetch<MonitorMessage[]>(`/messages/monitor${params}`)
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setItems(res.data);
      })
      .finally(() => setLoading(false));
  }, [centerId]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <PageSection>
      <PageHeader title={t("title")} description={t("privacyNotice")} />

      <div className="flex flex-wrap gap-3 items-center">
        <Select value={centerId} onChange={(e) => setCenterId(e.target.value)} className="w-auto min-w-[200px]">
          <option value="">{t("allCenters")}</option>
          {centers.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </Select>
        <span className="text-caption text-muted-foreground">{t("readOnly")}</span>
      </div>

      {loading ? (
        <DataTable>
          <TableSkeleton rows={8} cols={5} />
        </DataTable>
      ) : items.length === 0 ? (
        <DataTable>
          <EmptyState title={t("empty")} />
        </DataTable>
      ) : (
        <DataTable>
          <Table className="min-w-[720px]">
            <TableHeader>
              <TableRow>
                <TableHead>{t("center")}</TableHead>
                <TableHead>{t("sender")}</TableHead>
                <TableHead>{t("recipient")}</TableHead>
                <TableHead>{t("subject")}</TableHead>
                <TableHead>{t("sentAt")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((m) => (
                <TableRow key={m.id} className="align-top">
                  <TableCell>{m.center_name}</TableCell>
                  <TableCell>{m.sender_name || "—"}</TableCell>
                  <TableCell>{m.recipient_name || "—"}</TableCell>
                  <TableCell>
                    <div className="font-medium">{m.title}</div>
                    <div className="text-muted-foreground text-caption mt-1 line-clamp-2">{m.body}</div>
                  </TableCell>
                  <TableCell className="whitespace-nowrap text-muted-foreground">
                    {new Date(m.sent_at).toLocaleString()}
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
