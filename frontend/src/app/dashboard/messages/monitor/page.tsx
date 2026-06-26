"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
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
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
        <p className="text-sm text-gray-500 mt-1">{t("privacyNotice")}</p>
      </div>

      <div className="flex flex-wrap gap-3 items-center">
        <select
          className="border rounded-lg px-3 py-2 text-sm"
          value={centerId}
          onChange={(e) => setCenterId(e.target.value)}
        >
          <option value="">{t("allCenters")}</option>
          {centers.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <span className="text-xs text-gray-400">{t("readOnly")}</span>
      </div>

      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3">{t("center")}</th>
                <th className="text-left p-3">{t("sender")}</th>
                <th className="text-left p-3">{t("recipient")}</th>
                <th className="text-left p-3">{t("subject")}</th>
                <th className="text-left p-3">{t("sentAt")}</th>
              </tr>
            </thead>
            <tbody>
              {items.map((m) => (
                <tr key={m.id} className="border-b align-top">
                  <td className="p-3">{m.center_name}</td>
                  <td className="p-3">{m.sender_name || "—"}</td>
                  <td className="p-3">{m.recipient_name || "—"}</td>
                  <td className="p-3">
                    <div className="font-medium">{m.title}</div>
                    <div className="text-gray-500 text-xs mt-1 line-clamp-2">{m.body}</div>
                  </td>
                  <td className="p-3 whitespace-nowrap text-gray-500">
                    {new Date(m.sent_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {items.length === 0 && <p className="p-4 text-gray-400">{t("empty")}</p>}
        </div>
      )}
    </div>
  );
}
