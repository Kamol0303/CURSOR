"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  Badge,
  Button,
  Card,
  CardBody,
  DataTable,
  EmptyState,
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
} from "@/components/ui";
import { apiFetch } from "@/lib/api";

type Group = { id: string; name: string };
type Member = { student_id: string; full_name: string };
type Record = { student_id: string; student_name: string; status: string };

export default function TeacherAttendancePage() {
  const t = useTranslations("teacherPortal");
  const ta = useTranslations("attendance");
  const [groups, setGroups] = useState<Group[]>([]);
  const [groupId, setGroupId] = useState("");
  const [sessionDate, setSessionDate] = useState(new Date().toISOString().slice(0, 10));
  const [members, setMembers] = useState<Member[]>([]);
  const [records, setRecords] = useState<Record[]>([]);

  useEffect(() => {
    apiFetch<Group[]>("/teacher/groups").then((res) => {
      if (res.success && Array.isArray(res.data)) {
        setGroups(res.data);
        if (res.data[0]) setGroupId(res.data[0].id);
      }
    });
  }, []);

  useEffect(() => {
    if (!groupId) return;
    apiFetch<Member[]>(`/teacher/groups/${groupId}/students`).then((res) => {
      if (res.success && Array.isArray(res.data)) {
        setMembers(res.data.map((m) => ({ student_id: m.student_id, full_name: m.full_name })));
      }
    });
    apiFetch<Record[]>(`/attendance?group_id=${groupId}&session_date=${sessionDate}`).then((res) => {
      if (res.success && Array.isArray(res.data)) setRecords(res.data);
    });
  }, [groupId, sessionDate]);

  const mark = async (studentId: string, status: string) => {
    await apiFetch("/attendance/mark", {
      method: "POST",
      body: JSON.stringify({
        student_id: studentId,
        group_id: groupId,
        session_date: sessionDate,
        status,
      }),
    });
    const res = await apiFetch<Record[]>(`/attendance?group_id=${groupId}&session_date=${sessionDate}`);
    if (res.success && Array.isArray(res.data)) setRecords(res.data);
  };

  const statusFor = (studentId: string) => records.find((r) => r.student_id === studentId)?.status;

  return (
    <PageSection className="max-w-3xl">
      <PageHeader title={t("nav.attendance")} />

      <Card>
        <CardBody>
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
              <Input
                type="date"
                aria-label={ta("status")}
                value={sessionDate}
                onChange={(e) => setSessionDate(e.target.value)}
              />
            </FormField>
          </FormGrid>
        </CardBody>
      </Card>

      <DataTable>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{ta("student")}</TableHead>
              <TableHead>{ta("status")}</TableHead>
              <TableHead className="text-right">{ta("actions")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {members.map((s) => {
              const status = statusFor(s.student_id);
              return (
                <TableRow key={s.student_id}>
                  <TableCell className="font-medium">{s.full_name}</TableCell>
                  <TableCell>
                    {status ? (
                      <Badge variant={status === "present" ? "success" : "danger"}>
                        {status}
                      </Badge>
                    ) : (
                      "—"
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={() => mark(s.student_id, "present")}
                      >
                        {ta("present")}
                      </Button>
                      <Button
                        type="button"
                        size="sm"
                        variant="danger"
                        onClick={() => mark(s.student_id, "absent")}
                      >
                        {ta("absent")}
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
            {members.length === 0 && (
              <TableRow>
                <TableCell colSpan={3}>
                  <EmptyState title={t("noStudents")} className="py-8" />
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </DataTable>
    </PageSection>
  );
}
