"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { CenterFormModal } from "@/components/CenterFormModal";
import { CenterOnboardModal } from "@/components/CenterOnboardModal";
import { PermissionGate } from "@/components/PermissionGate";
import { apiFetch, listCenters } from "@/lib/api";
import { usePermissions } from "@/hooks/usePermissions";
import { useAuth } from "@/contexts/AuthContext";

type Center = {
  id: string;
  name: string;
  stir: string | null;
  director_name: string | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  license_number: string | null;
  license_expiry: string | null;
  center_type: string;
  is_active: boolean;
  mahalla_name_uz: string | null;
};

export default function CentersPage() {
  const t = useTranslations("centers");
  const { can } = usePermissions();
  const { role } = useAuth();
  const [centers, setCenters] = useState<Center[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showOnboard, setShowOnboard] = useState(false);
  const [editCenter, setEditCenter] = useState<Center | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    listCenters()
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setCenters(res.data as Center[]);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const deleteCenter = async (center: Center) => {
    if (!window.confirm(t("deleteConfirm", { name: center.name }))) return;
    const res = await apiFetch(`/centers/${center.id}`, { method: "DELETE" });
    if (!res.success) {
      alert(t("deleteError"));
      return;
    }
    load();
  };

  const showActions = can("centers.update") || can("centers.delete");
  const isSuperAdmin = role === "super_admin";

  return (
    <>
      <div className="space-y-4">
        <div className="flex justify-between items-center flex-wrap gap-2">
          <div>
            <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
            <p className="text-sm text-gray-500">{t("subtitle")}</p>
          </div>
          <div className="flex gap-2">
            {isSuperAdmin && (
              <PermissionGate permission="centers.create">
                <button
                  type="button"
                  onClick={() => {
                    setEditCenter(null);
                    setShowForm(true);
                  }}
                  className="px-4 py-2 border border-naqsh-primary text-naqsh-primary rounded-lg text-sm font-medium"
                >
                  {t("add")}
                </button>
              </PermissionGate>
            )}
            <PermissionGate permission="centers.create">
              <button
                type="button"
                onClick={() => {
                  setEditCenter(null);
                  setShowOnboard(true);
                }}
                className="px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm font-medium"
              >
                {t("onboardAdd")}
              </button>
            </PermissionGate>
          </div>
        </div>
        {loading ? (
          <p className="text-gray-400">{t("loading")}</p>
        ) : (
          <div className="bg-white rounded-xl shadow border overflow-hidden overflow-x-auto">
            <table className="w-full text-sm min-w-[720px]">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left p-3 font-medium">{t("name")}</th>
                  <th className="text-left p-3 font-medium">{t("mahalla")}</th>
                  <th className="text-left p-3 font-medium">{t("stir")}</th>
                  <th className="text-left p-3 font-medium">{t("director")}</th>
                  <th className="text-left p-3 font-medium">{t("licenseExpiry")}</th>
                  <th className="text-left p-3 font-medium">{t("status")}</th>
                  {showActions && <th className="p-3" />}
                </tr>
              </thead>
              <tbody>
                {centers.map((c) => (
                  <tr key={c.id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="p-3">{c.name}</td>
                    <td className="p-3">{c.mahalla_name_uz || "—"}</td>
                    <td className="p-3">{c.stir || "—"}</td>
                    <td className="p-3">{c.director_name || "—"}</td>
                    <td className="p-3">
                      {c.license_expiry ? new Date(c.license_expiry).toLocaleDateString() : "—"}
                    </td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs ${
                          c.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {c.is_active ? t("active") : t("inactive")}
                      </span>
                    </td>
                    {showActions && (
                      <td className="p-3 text-right space-x-2">
                        {can("centers.update") && (
                          <button
                            type="button"
                            className="text-naqsh-accent text-sm hover:underline"
                            onClick={() => {
                              setEditCenter(c);
                              setShowForm(true);
                            }}
                          >
                            {t("edit")}
                          </button>
                        )}
                        {can("centers.delete") && (
                          <button
                            type="button"
                            className="text-red-600 text-sm hover:underline"
                            onClick={() => deleteCenter(c)}
                          >
                            {t("delete")}
                          </button>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
                {centers.length === 0 && (
                  <tr>
                    <td colSpan={showActions ? 7 : 6} className="p-6 text-center text-gray-400">
                      {t("empty")}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {showOnboard && (
        <CenterOnboardModal onClose={() => setShowOnboard(false)} onSaved={load} />
      )}
      {showForm && (
        <CenterFormModal
          center={editCenter}
          onClose={() => setShowForm(false)}
          onSaved={load}
        />
      )}
    </>
  );
}
