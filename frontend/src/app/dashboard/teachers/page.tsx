"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { DashboardLayout } from "@/components/DashboardLayout";
import { listTeachers } from "@/lib/api";

type Teacher = {
  id: string;
  full_name: string;
  specialization: string | null;
  years_of_experience: number;
  is_active: boolean;
};

export default function TeachersPage() {
  const t = useTranslations("teachers");
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listTeachers()
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setTeachers(res.data as Teacher[]);
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
                  <th className="text-left p-3 font-medium">{t("specialization")}</th>
                  <th className="text-left p-3 font-medium">{t("experience")}</th>
                  <th className="text-left p-3 font-medium">{t("status")}</th>
                </tr>
              </thead>
              <tbody>
                {teachers.map((teacher) => (
                  <tr key={teacher.id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="p-3">{teacher.full_name}</td>
                    <td className="p-3">{teacher.specialization || "—"}</td>
                    <td className="p-3">{teacher.years_of_experience}</td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs ${
                          teacher.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {teacher.is_active ? t("active") : t("inactive")}
                      </span>
                    </td>
                  </tr>
                ))}
                {teachers.length === 0 && (
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
