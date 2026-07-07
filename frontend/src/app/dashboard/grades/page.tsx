"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { PermissionGate } from "@/components/PermissionGate";
import {
  Button,
  Card,
  CardBody,
  DataTable,
  EmptyState,
  Input,
  PageHeader,
  PageSection,
  Select,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableSkeleton,
} from "@/components/ui";
import { apiFetch, listStudents } from "@/lib/api";

type Grade = {
  id: string;
  student_id: string;
  grade_value: number;
  grade_type: string;
  term: string | null;
};

export default function GradesPage() {
  const t = useTranslations("grades");
  const [grades, setGrades] = useState<Grade[]>([]);
  const [students, setStudents] = useState<{ id: string; full_name: string }[]>([]);
  const [subjects, setSubjects] = useState<{ id: string; name_uz: string }[]>([]);
  const [studentId, setStudentId] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [value, setValue] = useState("85");
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    apiFetch<Grade[]>("/grades")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setGrades(res.data);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    listStudents().then((res) => {
      if (res.success && Array.isArray(res.data)) {
        const rows = res.data as { id: string; full_name: string }[];
        setStudents(rows);
        if (rows[0]) setStudentId(rows[0].id);
      }
    });
    apiFetch<{ id: string; name_uz: string }[]>("/subjects").then((res) => {
      if (res.success && Array.isArray(res.data)) {
        setSubjects(res.data);
        if (res.data[0]) setSubjectId(res.data[0].id);
      }
    });
  }, [load]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    await apiFetch("/grades", {
      method: "POST",
      body: JSON.stringify({
        student_id: studentId,
        subject_id: subjectId,
        grade_value: Number(value),
        grade_type: "monthly",
      }),
    });
    load();
  };

  return (
    <PageSection>
      <PageHeader title={t("title")} />

      <PermissionGate permission="grades.create">
        <Card>
          <CardBody>
            <form onSubmit={submit} className="grid gap-3 md:grid-cols-4 items-end">
              <Select value={studentId} onChange={(e) => setStudentId(e.target.value)}>
                {students.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.full_name}
                  </option>
                ))}
              </Select>
              <Select value={subjectId} onChange={(e) => setSubjectId(e.target.value)}>
                {subjects.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name_uz}
                  </option>
                ))}
              </Select>
              <Input
                type="number"
                min={0}
                max={100}
                value={value}
                onChange={(e) => setValue(e.target.value)}
              />
              <Button type="submit">{t("add")}</Button>
            </form>
          </CardBody>
        </Card>
      </PermissionGate>

      {loading ? (
        <DataTable>
          <TableSkeleton rows={6} cols={3} />
        </DataTable>
      ) : grades.length === 0 ? (
        <DataTable>
          <EmptyState title={t("empty")} />
        </DataTable>
      ) : (
        <DataTable>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("student")}</TableHead>
                <TableHead>{t("grade")}</TableHead>
                <TableHead>{t("type")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {grades.map((g) => (
                <TableRow key={g.id}>
                  <TableCell className="font-mono text-caption">{g.student_id.slice(0, 8)}…</TableCell>
                  <TableCell className="font-semibold">{g.grade_value}</TableCell>
                  <TableCell>{g.grade_type}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </DataTable>
      )}
    </PageSection>
  );
}
