"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { PermissionGate } from "@/components/PermissionGate";
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
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
      <PermissionGate permission="grades.create">
        <form onSubmit={submit} className="bg-white p-4 rounded-xl border grid gap-3 md:grid-cols-4">
          <select className="border rounded-lg px-3 py-2" value={studentId} onChange={(e) => setStudentId(e.target.value)}>
            {students.map((s) => (
              <option key={s.id} value={s.id}>{s.full_name}</option>
            ))}
          </select>
          <select className="border rounded-lg px-3 py-2" value={subjectId} onChange={(e) => setSubjectId(e.target.value)}>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>{s.name_uz}</option>
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
            {t("add")}
          </button>
        </form>
      </PermissionGate>
      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3">{t("student")}</th>
                <th className="text-left p-3">{t("grade")}</th>
                <th className="text-left p-3">{t("type")}</th>
              </tr>
            </thead>
            <tbody>
              {grades.map((g) => (
                <tr key={g.id} className="border-b">
                  <td className="p-3 font-mono text-xs">{g.student_id.slice(0, 8)}…</td>
                  <td className="p-3 font-semibold">{g.grade_value}</td>
                  <td className="p-3">{g.grade_type}</td>
                </tr>
              ))}
              {grades.length === 0 && (
                <tr>
                  <td colSpan={3} className="p-6 text-center text-gray-400">{t("empty")}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
