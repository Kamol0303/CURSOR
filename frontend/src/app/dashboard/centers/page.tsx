"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { CenterFormModal } from "@/components/CenterFormModal";
import { CenterOnboardModal } from "@/components/CenterOnboardModal";
import { PermissionGate } from "@/components/PermissionGate";
import {
  Button,
  DataTable,
  EmptyState,
  PageHeader,
  PageSection,
  StatusBadge,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableSkeleton,
} from "@/components/ui";
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
  mahalla_id: string | null;
  mahalla_name_uz: string | null;
};

export default function CentersPage() {
  const t = useTranslations("centers");
  const { can } = usePermissions();
  const { user } = useAuth();
  const role = user?.role;
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
      <PageSection>
        <PageHeader
          title={t("title")}
          description={t("subtitle")}
          actions={
            <>
              {isSuperAdmin && (
                <PermissionGate permission="centers.create">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setEditCenter(null);
                      setShowForm(true);
                    }}
                  >
                    {t("add")}
                  </Button>
                </PermissionGate>
              )}
              <PermissionGate permission="centers.create">
                <Button
                  onClick={() => {
                    setEditCenter(null);
                    setShowOnboard(true);
                  }}
                >
                  {t("onboardAdd")}
                </Button>
              </PermissionGate>
            </>
          }
        />

        {loading ? (
          <DataTable>
            <TableSkeleton rows={6} cols={6} />
          </DataTable>
        ) : centers.length === 0 ? (
          <DataTable>
            <EmptyState title={t("empty")} />
          </DataTable>
        ) : (
          <DataTable>
            <Table className="min-w-[720px]">
              <TableHeader>
                <TableRow>
                  <TableHead>{t("name")}</TableHead>
                  <TableHead>{t("mahalla")}</TableHead>
                  <TableHead>{t("stir")}</TableHead>
                  <TableHead>{t("director")}</TableHead>
                  <TableHead>{t("licenseExpiry")}</TableHead>
                  <TableHead>{t("status")}</TableHead>
                  {showActions && <TableHead className="text-right">{t("edit")}</TableHead>}
                </TableRow>
              </TableHeader>
              <TableBody>
                {centers.map((c) => (
                  <TableRow key={c.id}>
                    <TableCell className="font-medium">{c.name}</TableCell>
                    <TableCell>{c.mahalla_name_uz || "—"}</TableCell>
                    <TableCell className="font-mono text-caption">{c.stir || "—"}</TableCell>
                    <TableCell>{c.director_name || "—"}</TableCell>
                    <TableCell>
                      {c.license_expiry ? new Date(c.license_expiry).toLocaleDateString() : "—"}
                    </TableCell>
                    <TableCell>
                      <StatusBadge
                        active={c.is_active}
                        activeLabel={t("active")}
                        inactiveLabel={t("inactive")}
                      />
                    </TableCell>
                    {showActions && (
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          {can("centers.update") && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setEditCenter(c);
                                setShowForm(true);
                              }}
                            >
                              {t("edit")}
                            </Button>
                          )}
                          {can("centers.delete") && (
                            <Button variant="ghost" size="sm" className="text-danger hover:text-danger" onClick={() => deleteCenter(c)}>
                              {t("delete")}
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </DataTable>
        )}
      </PageSection>

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
