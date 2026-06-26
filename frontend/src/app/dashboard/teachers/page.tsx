"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { TeacherFormModal } from "@/components/TeacherFormModal";
import { PermissionGate } from "@/components/PermissionGate";
import { apiFetch, getMe, listCenters, listTeachers } from "@/lib/api";
import { usePermissions } from "@/hooks/usePermissions";

type Teacher = {
  id: string;
  center_id: string;
  full_name: string;
  phone: string | null;
  specialization: string | null;
  years_of_experience: number;
  is_active: boolean;
};

export default function TeachersPage() {
  const t = useTranslations("teachers");
  const { can } = usePermissions();
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [centerId, setCenterId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editTeacher, setEditTeacher] = useState<Teacher | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    listTeachers()
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setTeachers(res.data as Teacher[]);
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

  const deleteTeacher = async (teacher: Teacher) => {
    if (!window.confirm(t("deleteConfirm", { name: teacher.full_name }))) return;
    const res = await apiFetch(`/teachers/${teacher.id}`, { method: "DELETE" });
    if (res.success) load();
  };

  const showActions = can("teachers.update") || can("teachers.delete");

  return (
    <>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
          <PermissionGate permission="teachers.create">
            {centerId && (
              <button
                type="button"
                onClick={() => {
                  setEditTeacher(null);
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
                  <th className="text-left p-3 font-medium">{t("specialization")}</th>
                  <th className="text-left p-3 font-medium">{t("experience")}</th>
                  <th className="text-left p-3 font-medium">{t("status")}</th>
                  {showActions && <th className="p-3" />}
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
                    {showActions && (
                      <td className="p-3 text-right space-x-2">
                        {can("teachers.update") && (
                          <button
                            type="button"
                            className="text-naqsh-accent text-sm hover:underline"
                            onClick={() => {
                              setEditTeacher(teacher);
                              setShowForm(true);
                            }}
                          >
                            {t("edit")}
                          </button>
                        )}
                        {can("teachers.delete") && (
                          <button
                            type="button"
                            className="text-red-600 text-sm hover:underline"
                            onClick={() => deleteTeacher(teacher)}
                          >
                            {t("delete")}
                          </button>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
                {teachers.length === 0 && (
                  <tr>
                    <td colSpan={showActions ? 5 : 4} className="p-6 text-center text-gray-400">
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
        <TeacherFormModal
          centerId={centerId}
          teacher={editTeacher}
          onClose={() => setShowForm(false)}
          onSaved={load}
        />
      )}
    </>
  );
}
