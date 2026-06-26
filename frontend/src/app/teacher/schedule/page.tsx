"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

type ScheduleItem = {
  group_id: string;
  group_name: string;
  room: string | null;
  subject_name: string | null;
  schedule: Record<string, unknown>;
};

export default function TeacherSchedulePage() {
  const t = useTranslations("teacherPortal");
  const [items, setItems] = useState<ScheduleItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<ScheduleItem[]>("/teacher/schedule")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setItems(res.data);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-4 max-w-3xl">
      <h2 className="text-xl font-bold text-naqsh-primary">{t("nav.schedule")}</h2>
      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : items.length === 0 ? (
        <p className="text-gray-400">{t("noSchedule")}</p>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.group_id} className="bg-white rounded-xl border p-4">
              <h3 className="font-semibold text-naqsh-primary">{item.group_name}</h3>
              <p className="text-sm text-gray-600">
                {item.subject_name || "—"} · {t("room")}: {item.room || "—"}
              </p>
              <pre className="mt-2 text-xs bg-gray-50 rounded-lg p-3 overflow-x-auto">
                {JSON.stringify(item.schedule, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
