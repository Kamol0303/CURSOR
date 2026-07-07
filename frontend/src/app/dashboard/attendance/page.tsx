"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";
import { PermissionGate } from "@/components/PermissionGate";
import { useAuth } from "@/contexts/AuthContext";
import {
  Badge,
  Button,
  Card,
  CardBody,
  DataTable,
  PageHeader,
  PageSection,
  Select,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Input,
} from "@/components/ui";

type Group = { id: string; name: string };
type Student = { id: string; full_name: string };
type Record = { student_id: string; student_name: string; status: string };

export default function AttendancePage() {
  const t = useTranslations("attendance");
  const { can } = useAuth();
  const canMark = can("attendance.mark");
  const [groups, setGroups] = useState<Group[]>([]);
  const [groupId, setGroupId] = useState("");
  const [sessionDate, setSessionDate] = useState(new Date().toISOString().slice(0, 10));
  const [records, setRecords] = useState<Record[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [qrPayload, setQrPayload] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Group[]>("/groups").then((res) => {
      if (res.success && Array.isArray(res.data)) {
        setGroups(res.data);
        if (res.data[0]) setGroupId(res.data[0].id);
      }
    });
    apiFetch<Student[]>("/students?per_page=100").then((res) => {
      if (res.success && Array.isArray(res.data)) setStudents(res.data as Student[]);
    });
  }, []);

  useEffect(() => {
    if (!groupId) return;
    apiFetch<Record[]>(`/attendance?group_id=${groupId}&session_date=${sessionDate}`).then((res) => {
      if (res.success && Array.isArray(res.data)) setRecords(res.data);
    });
  }, [groupId, sessionDate]);

  const mark = async (studentId: string, status: string) => {
    await apiFetch("/attendance/mark", {
      method: "POST",
      body: JSON.stringify({ student_id: studentId, group_id: groupId, session_date: sessionDate, status }),
    });
    const res = await apiFetch<Record[]>(`/attendance?group_id=${groupId}&session_date=${sessionDate}`);
    if (res.success && Array.isArray(res.data)) setRecords(res.data);
  };

  const createQr = async () => {
    const res = await apiFetch<{ qr_payload: string }>(
      `/attendance/qr-session?group_id=${groupId}&session_date=${sessionDate}`,
      { method: "POST" },
    );
    if (res.success && res.data) setQrPayload((res.data as { qr_payload: string }).qr_payload);
  };

  const statusFor = (studentId: string) => records.find((r) => r.student_id === studentId)?.status;

  const statusVariant = (status: string | undefined) => {
    if (status === "present") return "success" as const;
    if (status === "absent") return "danger" as const;
    return "default" as const;
  };

  return (
    <PageSection>
      <PageHeader title={t("title")} />

      <div className="flex flex-wrap gap-3">
        <Select value={groupId} onChange={(e) => setGroupId(e.target.value)} className="w-auto min-w-[180px]">
          {groups.map((g) => (
            <option key={g.id} value={g.id}>
              {g.name}
            </option>
          ))}
        </Select>
        <Input
          type="date"
          className="w-auto"
          value={sessionDate}
          onChange={(e) => setSessionDate(e.target.value)}
        />
        <PermissionGate permission="attendance.mark">
          <Button variant="accent" onClick={createQr}>
            {t("qrSession")}
          </Button>
        </PermissionGate>
      </div>

      {qrPayload && (
        <Card>
          <CardBody>
            <p className="font-medium mb-1 text-small">{t("qrCode")}</p>
            <code className="text-caption break-all">{qrPayload}</code>
          </CardBody>
        </Card>
      )}

      <DataTable>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("student")}</TableHead>
              <TableHead>{t("status")}</TableHead>
              {canMark && <TableHead className="text-right">{t("actions")}</TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {students.map((s) => (
              <TableRow key={s.id}>
                <TableCell className="font-medium">{s.full_name}</TableCell>
                <TableCell>
                  {statusFor(s.id) ? (
                    <Badge variant={statusVariant(statusFor(s.id))}>{statusFor(s.id)}</Badge>
                  ) : (
                    "—"
                  )}
                </TableCell>
                {canMark && (
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Button variant="ghost" size="sm" onClick={() => mark(s.id, "present")}>
                        +
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-danger hover:text-danger"
                        onClick={() => mark(s.id, "absent")}
                      >
                        −
                      </Button>
                    </div>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DataTable>
    </PageSection>
  );
}
