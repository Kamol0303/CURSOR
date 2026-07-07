"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import {
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
import { apiFetch } from "@/lib/api";

type Member = {
  student_id: string;
  full_name: string;
  grade: string | null;
};

export default function TeacherGroupDetailPage() {
  const t = useTranslations("teacherPortal");
  const params = useParams();
  const groupId = params.id as string;
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Member[]>(`/teacher/groups/${groupId}/students`)
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setMembers(res.data);
      })
      .finally(() => setLoading(false));
  }, [groupId]);

  return (
    <PageSection className="max-w-3xl">
      <Link
        href="/teacher/groups"
        className="inline-flex items-center text-small text-muted-foreground hover:text-foreground transition-colors"
      >
        ← {t("backToGroups")}
      </Link>

      <PageHeader title={t("groupStudents")} />

      {loading ? (
        <DataTable>
          <TableSkeleton rows={5} cols={2} />
        </DataTable>
      ) : members.length === 0 ? (
        <EmptyState title={t("noStudents")} />
      ) : (
        <DataTable>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("studentName")}</TableHead>
                <TableHead>{t("grade")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {members.map((m) => (
                <TableRow key={m.student_id}>
                  <TableCell className="font-medium">{m.full_name}</TableCell>
                  <TableCell>{m.grade || "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </DataTable>
      )}
    </PageSection>
  );
}
