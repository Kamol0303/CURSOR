"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { DashboardLayout } from "@/components/DashboardLayout";
import { PermissionGate } from "@/components/PermissionGate";
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

  return (
    <DashboardLayout>
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
        <p className="text-sm text-gray-500">{t("clickPaymeNote")}</p>
        {loading ? (
          <p>{t("loading")}</p>
        ) : (
          <div className="bg-white rounded-xl border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left p-3">{t("student")}</th>
                  <th className="text-left p-3">{t("amount")}</th>
                  <th className="text-left p-3">{t("status")}</th>
                  <th className="text-left p-3">{t("dueDate")}</th>
                  <th className="p-3" />
                </tr>
              </thead>
              <tbody>
                {payments.map((p) => (
                  <tr key={p.id} className="border-b">
                    <td className="p-3">{p.student_name}</td>
                    <td className="p-3">{p.amount.toLocaleString()} {p.currency}</td>
                    <td className="p-3">{p.status}</td>
                    <td className="p-3">{p.due_date || "—"}</td>
                    <td className="p-3">
                      <PermissionGate permission="payments.update">
                        {p.status === "pending" && (
                          <button type="button" className="text-sm text-naqsh-accent" onClick={() => markPaid(p.id)}>
                            {t("markPaid")}
                          </button>
                        )}
                      </PermissionGate>
                    </td>
                  </tr>
                ))}
                {payments.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-gray-400">{t("empty")}</td>
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
