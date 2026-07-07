"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { PermissionGate } from "@/components/PermissionGate";
import { SubjectFormModal } from "@/components/SubjectFormModal";
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

  const showActions = can("subjects.update") || can("subjects.delete");

  return (
    <>
      <PageSection>
        <PageHeader
          title={t("title")}
          actions={
            <PermissionGate permission="subjects.create">
              <Button
                onClick={() => {
                  setEditSubject(null);
                  setShowForm(true);
                }}
              >
                {t("add")}
              </Button>
            </PermissionGate>
          }
        />

        {loading ? (
          <DataTable>
            <TableSkeleton rows={6} cols={5} />
          </DataTable>
        ) : subjects.length === 0 ? (
          <DataTable>
            <EmptyState title={t("empty")} />
          </DataTable>
        ) : (
          <DataTable>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t("nameUz")}</TableHead>
                  <TableHead>{t("nameRu")}</TableHead>
                  <TableHead>{t("nameEn")}</TableHead>
                  <TableHead>{t("status")}</TableHead>
                  {showActions && <TableHead className="text-right">{t("edit")}</TableHead>}
                </TableRow>
              </TableHeader>
              <TableBody>
                {subjects.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell className="font-medium">{s.name_uz}</TableCell>
                    <TableCell>{s.name_ru}</TableCell>
                    <TableCell>{s.name_en}</TableCell>
                    <TableCell>
                      <StatusBadge
                        active={s.is_active}
                        activeLabel={t("active")}
                        inactiveLabel={t("inactive")}
                      />
                    </TableCell>
                    {showActions && (
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          {can("subjects.update") && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setEditSubject(s);
                                setShowForm(true);
                              }}
                            >
                              {t("edit")}
                            </Button>
                          )}
                          {can("subjects.delete") && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-danger hover:text-danger"
                              onClick={() => remove(s)}
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
