"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  Button,
  Card,
  CardBody,
  DataTable,
  EmptyState,
  FormField,
  Input,
  Label,
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

type AuditRow = {
  id: string;
  created_at: string;
  username: string | null;
  user_role: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  ip_address: string | null;
  details: Record<string, unknown> | null;
};

export default function AuditPage() {
  const t = useTranslations("audit");
  const [rows, setRows] = useState<AuditRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState("");
  const [resourceFilter, setResourceFilter] = useState("");

  const load = () => {
    setLoading(true);
    const params = new URLSearchParams({ per_page: "50" });
    if (actionFilter.trim()) params.set("action", actionFilter.trim());
    if (resourceFilter.trim()) params.set("resource_type", resourceFilter.trim());
    apiFetch<AuditRow[]>(`/audit-logs?${params}`)
      .then((res) => {
        if (res.success && res.data) setRows(res.data);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <PageSection>
      <PageHeader title={t("title")} description={t("subtitle")} />

      <Card>
        <CardBody>
          <div className="flex flex-wrap gap-3 items-end">
            <FormField>
              <Label>{t("filterAction")}</Label>
              <Input
                value={actionFilter}
                onChange={(e) => setActionFilter(e.target.value)}
                placeholder="lesson.generate"
              />
            </FormField>
            <FormField>
              <Label>{t("filterResource")}</Label>
              <Input
                value={resourceFilter}
                onChange={(e) => setResourceFilter(e.target.value)}
                placeholder="course"
              />
            </FormField>
            <Button type="button" onClick={load}>
              {t("apply")}
            </Button>
          </div>
        </CardBody>
      </Card>

      {loading ? (
        <DataTable>
          <TableSkeleton rows={8} cols={5} />
        </DataTable>
      ) : rows.length === 0 ? (
        <DataTable>
          <EmptyState title={t("empty")} />
        </DataTable>
      ) : (
        <DataTable>
          <Table className="min-w-[800px]">
            <TableHeader>
              <TableRow>
                <TableHead>{t("time")}</TableHead>
                <TableHead>{t("user")}</TableHead>
                <TableHead>{t("action")}</TableHead>
                <TableHead>{t("resource")}</TableHead>
                <TableHead>{t("details")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id}>
                  <TableCell className="whitespace-nowrap text-caption text-muted-foreground">
                    {new Date(row.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <div>{row.username || "—"}</div>
                    <div className="text-caption text-muted-foreground">{row.user_role}</div>
                  </TableCell>
                  <TableCell className="font-mono text-caption">{row.action}</TableCell>
                  <TableCell>
                    <div>{row.resource_type}</div>
                    <div className="text-caption text-muted-foreground truncate max-w-[120px]">
                      {row.resource_id}
                    </div>
                  </TableCell>
                  <TableCell className="text-caption text-muted-foreground max-w-md truncate">
                    {row.details ? JSON.stringify(row.details) : "—"}
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
