"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { PermissionGate } from "@/components/PermissionGate";
import { StudentFormModal } from "@/components/StudentFormModal";
import { getMe, listCenters, listStudents } from "@/lib/api";
import { usePermissions } from "@/hooks/usePermissions";

type Student = {
  id: string;
  full_name: string;
  grade: string | null;
  school: string | null;
  phone: string | null;
  address: string | null;
  jshshir_masked: string | null;
};

export default function StudentsPage() {
  const t = useTranslations("students");
  const { can } = usePermissions();
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [centerId, setCenterId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editStudent, setEditStudent] = useState<Student | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    listStudents()
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setStudents(res.data as Student[]);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    getMe().then(async (res) => {
      if (res.success && res.data?.center_id) {
        setCenterId(res.data.center_id as string);
      } else {
        const centers = await listCenters();
        if (centers.success && Array.isArray(centers.data) && centers.data[0]) {
          setCenterId((centers.data[0] as { id: string }).id);
        }
      }
    });
  }, [load]);

  return (
    <>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
          <PermissionGate permission="students.create">
            {centerId && (
              <button
                type="button"
                onClick={() => {
                  setEditStudent(null);
                  setShowForm(true);
                }}
                className="px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm font-medium"
              >
                {t("add")}
              </button>
            )}
          </PermissionGate>
        </div>
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
                  <th className="text-left p-3 font-medium">{t("phone")}</th>
                  <th className="text-left p-3 font-medium">{t("pinfl")}</th>
                  {can("students.update") && <th className="p-3" />}
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="p-3">{s.full_name}</td>
                    <td className="p-3">{s.grade || "—"}</td>
                    <td className="p-3">{s.school || "—"}</td>
                    <td className="p-3">{s.phone || "—"}</td>
                    <td className="p-3 font-mono text-gray-500">{s.jshshir_masked || "—"}</td>
                    {can("students.update") && (
                      <td className="p-3 text-right">
                        <button
                          type="button"
                          className="text-naqsh-accent text-sm hover:underline"
                          onClick={() => {
                            setEditStudent(s);
                            setShowForm(true);
                          }}
                        >
                          {t("edit")}
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
                {students.length === 0 && (
                  <tr>
                    <td colSpan={6} className="p-6 text-center text-gray-400">
                      {t("empty")}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {showForm && centerId && (
        <StudentFormModal
          centerId={centerId}
          student={editStudent}
          onClose={() => setShowForm(false)}
          onSaved={load}
        />
      )}
    </>
  );
}
