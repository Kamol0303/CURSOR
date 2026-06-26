"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { PermissionGate } from "@/components/PermissionGate";
import { SubjectFormModal } from "@/components/SubjectFormModal";
import { apiFetch } from "@/lib/api";
import { usePermissions } from "@/hooks/usePermissions";

type Subject = {
  id: string;
  name_uz: string;
  name_ru: string;
  name_en: string;
  is_active: boolean;
};

export default function SubjectsPage() {
  const t = useTranslations("subjects");
  const { can } = usePermissions();
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editSubject, setEditSubject] = useState<Subject | null>(null);

  const load = () => {
    setLoading(true);
    apiFetch<Subject[]>("/subjects?active_only=false")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setSubjects(res.data);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const remove = async (subject: Subject) => {
    if (!window.confirm(t("deleteConfirm", { name: subject.name_uz }))) return;
    const res = await apiFetch(`/subjects/${subject.id}`, { method: "DELETE" });
    if (!res.success) {
      const code = (res as { error?: { code?: string } }).error?.code || "UNKNOWN";
      alert(t(`errors.${code}` as "errors.UNKNOWN"));
      return;
    }
    load();
  };

  return (
    <>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
          <PermissionGate permission="subjects.create">
            <button
              type="button"
              onClick={() => {
                setEditSubject(null);
                setShowForm(true);
              }}
              className="px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm font-medium"
            >
              {t("add")}
            </button>
          </PermissionGate>
        </div>
        {loading ? (
          <p className="text-gray-400">{t("loading")}</p>
        ) : (
          <div className="bg-white rounded-xl shadow border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left p-3 font-medium">{t("nameUz")}</th>
                  <th className="text-left p-3 font-medium">{t("nameRu")}</th>
                  <th className="text-left p-3 font-medium">{t("nameEn")}</th>
                  <th className="text-left p-3 font-medium">{t("status")}</th>
                  {(can("subjects.update") || can("subjects.delete")) && <th className="p-3" />}
                </tr>
              </thead>
              <tbody>
                {subjects.map((s) => (
                  <tr key={s.id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="p-3">{s.name_uz}</td>
                    <td className="p-3">{s.name_ru}</td>
                    <td className="p-3">{s.name_en}</td>
                    <td className="p-3">
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full ${
                          s.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
                        }`}
                      >
                        {s.is_active ? t("active") : t("inactive")}
                      </span>
                    </td>
                    {(can("subjects.update") || can("subjects.delete")) && (
                      <td className="p-3 text-right space-x-2">
                        {can("subjects.update") && (
                          <button
                            type="button"
                            className="text-naqsh-accent text-sm hover:underline"
                            onClick={() => {
                              setEditSubject(s);
                              setShowForm(true);
                            }}
                          >
                            {t("edit")}
                          </button>
                        )}
                        {can("subjects.delete") && (
                          <button
                            type="button"
                            className="text-red-600 text-sm hover:underline"
                            onClick={() => remove(s)}
                          >
                            {t("delete")}
                          </button>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
                {subjects.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-gray-400">
                      {t("empty")}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {showForm && (
        <SubjectFormModal
          subject={editSubject}
          onClose={() => setShowForm(false)}
          onSaved={load}
        />
      )}
    </>
  );
}
