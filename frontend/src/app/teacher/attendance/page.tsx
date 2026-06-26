"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
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
    <div className="space-y-4 max-w-3xl">
      <h2 className="text-xl font-bold text-naqsh-primary">{t("nav.attendance")}</h2>
      <div className="flex flex-wrap gap-3">
        <select
          className="border rounded-lg px-3 py-2"
          value={groupId}
          onChange={(e) => setGroupId(e.target.value)}
        >
          {groups.map((g) => (
            <option key={g.id} value={g.id}>
              {g.name}
            </option>
          ))}
        </select>
        <input
          type="date"
          className="border rounded-lg px-3 py-2"
          value={sessionDate}
          onChange={(e) => setSessionDate(e.target.value)}
        />
      </div>
      <div className="bg-white rounded-xl border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left p-3">{ta("student")}</th>
              <th className="text-left p-3">{ta("status")}</th>
              <th className="p-3">{ta("actions")}</th>
            </tr>
          </thead>
          <tbody>
            {members.map((s) => (
              <tr key={s.student_id} className="border-b">
                <td className="p-3">{s.full_name}</td>
                <td className="p-3">{statusFor(s.student_id) || "—"}</td>
                <td className="p-3 space-x-1">
                  <button
                    type="button"
                    className="text-xs px-2 py-1 bg-green-100 rounded"
                    onClick={() => mark(s.student_id, "present")}
                  >
                    {ta("present")}
                  </button>
                  <button
                    type="button"
                    className="text-xs px-2 py-1 bg-red-100 rounded"
                    onClick={() => mark(s.student_id, "absent")}
                  >
                    {ta("absent")}
                  </button>
                </td>
              </tr>
            ))}
            {members.length === 0 && (
              <tr>
                <td colSpan={3} className="p-6 text-center text-gray-400">
                  {t("noStudents")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
