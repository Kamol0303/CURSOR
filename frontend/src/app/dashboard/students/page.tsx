"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { DashboardLayout } from "@/components/DashboardLayout";
import { listStudents } from "@/lib/api";

type Student = {
  id: string;
  full_name: string;
  grade: string | null;
  school: string | null;
  jshshir_masked: string | null;
};

export default function StudentsPage() {
  const t = useTranslations("students");
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listStudents()
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setStudents(res.data as Student[]);
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
                  <th className="text-left p-3 font-medium">{t("name")}</th>
                  <th className="text-left p-3 font-medium">{t("grade")}</th>
                  <th className="text-left p-3 font-medium">{t("school")}</th>
                  <th className="text-left p-3 font-medium">{t("pinfl")}</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="p-3">{s.full_name}</td>
                    <td className="p-3">{s.grade || "—"}</td>
                    <td className="p-3">{s.school || "—"}</td>
                    <td className="p-3 font-mono text-gray-500">{s.jshshir_masked || "—"}</td>
                  </tr>
                ))}
                {students.length === 0 && (
                  <tr>
                    <td colSpan={4} className="p-6 text-center text-gray-400">
                      {t("empty")}
                    </td>
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
