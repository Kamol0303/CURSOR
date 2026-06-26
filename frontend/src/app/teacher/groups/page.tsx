"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

type Group = {
  id: string;
  name: string;
  subject_name_uz: string | null;
  teacher_name: string | null;
  room: string | null;
  enrollment_count: number;
  is_active: boolean;
};

export default function TeacherGroupsPage() {
  const t = useTranslations("teacherPortal");
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Group[]>("/teacher/groups")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setGroups(res.data);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-4 max-w-3xl">
      <h2 className="text-xl font-bold text-naqsh-primary">{t("nav.groups")}</h2>
      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : groups.length === 0 ? (
        <p className="text-gray-400">{t("noGroups")}</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {groups.map((g) => (
            <Link
              key={g.id}
              href={`/teacher/groups/${g.id}`}
              className="bg-white rounded-xl border p-4 shadow-sm hover:border-naqsh-primary/30 transition-colors"
            >
              <h3 className="font-semibold text-naqsh-primary">{g.name}</h3>
              <p className="text-sm text-gray-600">{g.subject_name_uz || "—"}</p>
              <p className="text-sm text-gray-500 mt-1">
                {t("room")}: {g.room || "—"} · {t("students")}: {g.enrollment_count}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
