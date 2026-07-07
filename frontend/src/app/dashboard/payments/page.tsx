"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { PermissionGate } from "@/components/PermissionGate";
import {
  Badge,
  Button,
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

type Payment = {
  id: string;
  student_name: string | null;
  amount: number;
  status: string;
  due_date: string | null;
  currency: string;
};

export default function PaymentsPage() {
  const t = useTranslations("payments");
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    apiFetch<Payment[]>("/payments")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setPayments(res.data);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const markPaid = async (id: string) => {
    await apiFetch(`/payments/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: "paid", payment_method: "cash" }),
    });
    load();
  };

  const statusVariant = (status: string) => {
    if (status === "paid") return "success" as const;
    if (status === "pending") return "warning" as const;
    return "default" as const;
  };

  return (
    <PageSection>
      <PageHeader title={t("title")} description={t("clickPaymeNote")} />

      {loading ? (
        <DataTable>
          <TableSkeleton rows={6} cols={5} />
        </DataTable>
      ) : payments.length === 0 ? (
        <DataTable>
          <EmptyState title={t("empty")} />
        </DataTable>
      ) : (
        <DataTable>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("student")}</TableHead>
                <TableHead>{t("amount")}</TableHead>
                <TableHead>{t("status")}</TableHead>
                <TableHead>{t("dueDate")}</TableHead>
                <TableHead className="text-right">{t("markPaid")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {payments.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-medium">{p.student_name}</TableCell>
                  <TableCell>
                    {p.amount.toLocaleString()} {p.currency}
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusVariant(p.status)}>{p.status}</Badge>
                  </TableCell>
                  <TableCell>{p.due_date || "—"}</TableCell>
                  <TableCell className="text-right">
                    <PermissionGate permission="payments.update">
                      {p.status === "pending" && (
                        <Button variant="ghost" size="sm" onClick={() => markPaid(p.id)}>
                          {t("markPaid")}
                        </Button>
                      )}
                    </PermissionGate>
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
