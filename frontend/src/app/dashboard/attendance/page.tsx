"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

type Group = { id: string; name: string };
type Student = { id: string; full_name: string };
type Record = { student_id: string; student_name: string; status: string };

export default function AttendancePage() {
  const t = useTranslations("attendance");
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

  return (
    
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
        <div className="flex flex-wrap gap-3">
          <select className="border rounded-lg px-3 py-2" value={groupId} onChange={(e) => setGroupId(e.target.value)}>
            {groups.map((g) => (
              <option key={g.id} value={g.id}>{g.name}</option>
            ))}
          </select>
          <input type="date" className="border rounded-lg px-3 py-2" value={sessionDate} onChange={(e) => setSessionDate(e.target.value)} />
          <button type="button" onClick={createQr} className="px-4 py-2 bg-naqsh-accent text-white rounded-lg text-sm">
            {t("qrSession")}
          </button>
        </div>
        {qrPayload && (
          <div className="bg-white border rounded-xl p-4 text-sm break-all">
            <p className="font-medium mb-1">{t("qrCode")}</p>
            <code>{qrPayload}</code>
          </div>
        )}
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3">{t("student")}</th>
                <th className="text-left p-3">{t("status")}</th>
                <th className="p-3">{t("actions")}</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s) => (
                <tr key={s.id} className="border-b">
                  <td className="p-3">{s.full_name}</td>
                  <td className="p-3">{statusFor(s.id) || "—"}</td>
                  <td className="p-3 space-x-1">
                    <button type="button" className="text-xs px-2 py-1 bg-green-100 rounded" onClick={() => mark(s.id, "present")}>+</button>
                    <button type="button" className="text-xs px-2 py-1 bg-red-100 rounded" onClick={() => mark(s.id, "absent")}>−</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    
  );
}
