"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
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
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-naqsh-primary">{t("title")}</h2>
        <p className="text-gray-600 text-sm mt-1">{t("subtitle")}</p>
      </div>

      <div className="bg-white rounded-xl border p-4 flex flex-wrap gap-3 items-end">
        <div>
          <label className="block text-xs font-medium mb-1">{t("filterAction")}</label>
          <input
            className="border rounded-lg px-3 py-2 text-sm"
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            placeholder="lesson.generate"
          />
        </div>
        <div>
          <label className="block text-xs font-medium mb-1">{t("filterResource")}</label>
          <input
            className="border rounded-lg px-3 py-2 text-sm"
            value={resourceFilter}
            onChange={(e) => setResourceFilter(e.target.value)}
            placeholder="course"
          />
        </div>
        <button
          type="button"
          onClick={load}
          className="bg-naqsh-primary text-white px-4 py-2 rounded-lg text-sm"
        >
          {t("apply")}
        </button>
      </div>

      {loading ? (
        <p className="text-gray-500">{t("loading")}</p>
      ) : rows.length === 0 ? (
        <p className="text-gray-500">{t("empty")}</p>
      ) : (
        <div className="bg-white rounded-xl border overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left">
              <tr>
                <th className="px-4 py-3">{t("time")}</th>
                <th className="px-4 py-3">{t("user")}</th>
                <th className="px-4 py-3">{t("action")}</th>
                <th className="px-4 py-3">{t("resource")}</th>
                <th className="px-4 py-3">{t("details")}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-t">
                  <td className="px-4 py-3 whitespace-nowrap text-xs text-gray-500">
                    {new Date(row.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <div>{row.username || "—"}</div>
                    <div className="text-xs text-gray-400">{row.user_role}</div>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">{row.action}</td>
                  <td className="px-4 py-3">
                    <div>{row.resource_type}</div>
                    <div className="text-xs text-gray-400 truncate max-w-[120px]">{row.resource_id}</div>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-600 max-w-md truncate">
                    {row.details ? JSON.stringify(row.details) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
