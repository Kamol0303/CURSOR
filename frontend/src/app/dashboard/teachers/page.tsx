"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { TeacherFormModal } from "@/components/TeacherFormModal";
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
      <PageSection>
        <PageHeader
          title={t("title")}
          actions={
            <PermissionGate permission="teachers.create">
              {centerId && (
                <Button
                  onClick={() => {
                    setEditTeacher(null);
                    setShowForm(true);
                  }}
                >
                  {t("add")}
                </Button>
              )}
            </PermissionGate>
          }
        />

        {loading ? (
          <DataTable>
            <TableSkeleton rows={6} cols={5} />
          </DataTable>
        ) : teachers.length === 0 ? (
          <DataTable>
            <EmptyState title={t("empty")} />
          </DataTable>
        ) : (
          <DataTable>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t("name")}</TableHead>
                  <TableHead>{t("specialization")}</TableHead>
                  <TableHead>{t("experience")}</TableHead>
                  <TableHead>{t("status")}</TableHead>
                  {showActions && <TableHead className="text-right">{t("edit")}</TableHead>}
                </TableRow>
              </TableHeader>
              <TableBody>
                {teachers.map((teacher) => (
                  <TableRow key={teacher.id}>
                    <TableCell className="font-medium">{teacher.full_name}</TableCell>
                    <TableCell>{teacher.specialization || "—"}</TableCell>
                    <TableCell>{teacher.years_of_experience}</TableCell>
                    <TableCell>
                      <StatusBadge
                        active={teacher.is_active}
                        activeLabel={t("active")}
                        inactiveLabel={t("inactive")}
                      />
                    </TableCell>
                    {showActions && (
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          {can("teachers.update") && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setEditTeacher(teacher);
                                setShowForm(true);
                              }}
                            >
                              {t("edit")}
                            </Button>
                          )}
                          {can("teachers.delete") && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-danger hover:text-danger"
                              onClick={() => deleteTeacher(teacher)}
                            >
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
