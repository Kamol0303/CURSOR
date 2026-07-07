"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { PermissionGate } from "@/components/PermissionGate";
import { StudentFormModal } from "@/components/StudentFormModal";
import {
  Button,
  DataTable,
  EmptyState,
  PageHeader,
  PageSection,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableSkeleton,
} from "@/components/ui";
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
      <PageSection>
        <PageHeader
          title={t("title")}
          actions={
            <PermissionGate permission="students.create">
              {centerId && (
                <Button
                  onClick={() => {
                    setEditStudent(null);
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
            <TableSkeleton rows={6} cols={6} />
          </DataTable>
        ) : students.length === 0 ? (
          <DataTable>
            <EmptyState title={t("empty")} />
          </DataTable>
        ) : (
          <DataTable>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t("name")}</TableHead>
                  <TableHead>{t("grade")}</TableHead>
                  <TableHead>{t("school")}</TableHead>
                  <TableHead>{t("phone")}</TableHead>
                  <TableHead>{t("pinfl")}</TableHead>
                  {can("students.update") && <TableHead className="text-right">{t("edit")}</TableHead>}
                </TableRow>
              </TableHeader>
              <TableBody>
                {students.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell className="font-medium">{s.full_name}</TableCell>
                    <TableCell>{s.grade || "—"}</TableCell>
                    <TableCell>{s.school || "—"}</TableCell>
                    <TableCell>{s.phone || "—"}</TableCell>
                    <TableCell className="font-mono text-caption text-muted-foreground">
                      {s.jshshir_masked || "—"}
                    </TableCell>
                    {can("students.update") && (
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setEditStudent(s);
                            setShowForm(true);
                          }}
                        >
                          {t("edit")}
                        </Button>
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
