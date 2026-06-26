"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
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
    <div className="space-y-4 max-w-3xl">
      <h2 className="text-xl font-bold text-naqsh-primary">{t("nav.grades")}</h2>
      <form onSubmit={submit} className="bg-white p-4 rounded-xl border grid gap-3 md:grid-cols-2">
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
        <select
          className="border rounded-lg px-3 py-2"
          value={studentId}
          onChange={(e) => setStudentId(e.target.value)}
        >
          {members.map((s) => (
            <option key={s.student_id} value={s.student_id}>
              {s.full_name}
            </option>
          ))}
        </select>
        <input
          type="number"
          min={0}
          max={100}
          className="border rounded-lg px-3 py-2"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
        <button type="submit" className="px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm">
          {tg("add")}
        </button>
      </form>
      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3">{tg("student")}</th>
                <th className="text-left p-3">{tg("grade")}</th>
                <th className="text-left p-3">{tg("type")}</th>
              </tr>
            </thead>
            <tbody>
              {visibleGrades.map((g) => (
                <tr key={g.id} className="border-b">
                  <td className="p-3">
                    {members.find((m) => m.student_id === g.student_id)?.full_name ||
                      g.student_id.slice(0, 8)}
                  </td>
                  <td className="p-3 font-semibold">{g.grade_value}</td>
                  <td className="p-3">{g.grade_type}</td>
                </tr>
              ))}
              {visibleGrades.length === 0 && (
                <tr>
                  <td colSpan={3} className="p-6 text-center text-gray-400">
                    {tg("empty")}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
