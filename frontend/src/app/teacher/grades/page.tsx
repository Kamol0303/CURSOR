"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  Button,
  Card,
  CardBody,
  DataTable,
  EmptyState,
  FormActions,
  FormField,
  FormGrid,
  Input,
  Label,
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
import { apiFetch } from "@/lib/api";

type Group = { id: string; name: string; subject_id: string };
type Member = { student_id: string; full_name: string };
type Grade = {
  id: string;
  student_id: string;
  grade_value: number;
  grade_type: string;
};

export default function TeacherGradesPage() {
  const t = useTranslations("teacherPortal");
  const tg = useTranslations("grades");
  const [groups, setGroups] = useState<Group[]>([]);
  const [groupId, setGroupId] = useState("");
  const [members, setMembers] = useState<Member[]>([]);
  const [grades, setGrades] = useState<Grade[]>([]);
  const [studentId, setStudentId] = useState("");
  const [value, setValue] = useState("85");
  const [loading, setLoading] = useState(true);

  const loadGrades = useCallback(() => {
    apiFetch<Grade[]>("/grades?per_page=50").then((res) => {
      if (res.success && Array.isArray(res.data)) setGrades(res.data);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    apiFetch<Group[]>("/teacher/groups").then((res) => {
      if (res.success && Array.isArray(res.data)) {
        setGroups(res.data);
        if (res.data[0]) setGroupId(res.data[0].id);
      }
    });
    loadGrades();
  }, [loadGrades]);

  useEffect(() => {
    if (!groupId) return;
    apiFetch<Member[]>(`/teacher/groups/${groupId}/students`).then((res) => {
      if (res.success && Array.isArray(res.data)) {
        setMembers(res.data);
        if (res.data[0]) setStudentId(res.data[0].student_id);
      }
    });
  }, [groupId]);

  const selectedGroup = groups.find((g) => g.id === groupId);
  const memberIds = new Set(members.map((m) => m.student_id));
  const visibleGrades = grades.filter((g) => memberIds.has(g.student_id));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGroup || !studentId) return;
    await apiFetch("/grades", {
      method: "POST",
      body: JSON.stringify({
        student_id: studentId,
        subject_id: selectedGroup.subject_id,
        group_id: groupId,
        grade_value: Number(value),
        grade_type: "monthly",
      }),
    });
    loadGrades();
  };

  return (
    <PageSection className="max-w-3xl">
      <PageHeader title={t("nav.grades")} />

      <Card>
        <CardBody>
          <form onSubmit={submit}>
            <FormGrid>
              <FormField>
                <Label>{t("nav.groups")}</Label>
                <Select value={groupId} onChange={(e) => setGroupId(e.target.value)}>
                  {groups.map((g) => (
                    <option key={g.id} value={g.id}>
                      {g.name}
                    </option>
                  ))}
                </Select>
              </FormField>
              <FormField>
                <Label>{tg("student")}</Label>
                <Select value={studentId} onChange={(e) => setStudentId(e.target.value)}>
                  {members.map((s) => (
                    <option key={s.student_id} value={s.student_id}>
                      {s.full_name}
                    </option>
                  ))}
                </Select>
              </FormField>
              <FormField>
                <Label>{tg("grade")}</Label>
                <Input
                  type="number"
                  min={0}
                  max={100}
                  value={value}
                  onChange={(e) => setValue(e.target.value)}
                />
              </FormField>
            </FormGrid>
            <FormActions>
              <Button type="submit">{tg("add")}</Button>
            </FormActions>
          </form>
        </CardBody>
      </Card>

      {loading ? (
        <DataTable>
          <TableSkeleton rows={5} cols={3} />
        </DataTable>
      ) : (
        <DataTable>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{tg("student")}</TableHead>
                <TableHead>{tg("grade")}</TableHead>
                <TableHead>{tg("type")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {visibleGrades.map((g) => (
                <TableRow key={g.id}>
                  <TableCell>
                    {members.find((m) => m.student_id === g.student_id)?.full_name ||
                      g.student_id.slice(0, 8)}
                  </TableCell>
                  <TableCell className="font-semibold">{g.grade_value}</TableCell>
                  <TableCell>{g.grade_type}</TableCell>
                </TableRow>
              ))}
              {visibleGrades.length === 0 && (
                <TableRow>
                  <TableCell colSpan={3}>
                    <EmptyState title={tg("empty")} className="py-8" />
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </DataTable>
      )}
    </PageSection>
  );
}
