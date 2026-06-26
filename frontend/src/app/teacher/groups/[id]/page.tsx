"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
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
    <div className="space-y-4 max-w-3xl">
      <Link href="/teacher/groups" className="text-sm text-naqsh-accent hover:underline">
        ← {t("backToGroups")}
      </Link>
      <h2 className="text-xl font-bold text-naqsh-primary">{t("groupStudents")}</h2>
      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : members.length === 0 ? (
        <p className="text-gray-400">{t("noStudents")}</p>
      ) : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3">{t("studentName")}</th>
                <th className="text-left p-3">{t("grade")}</th>
              </tr>
            </thead>
            <tbody>
              {members.map((m) => (
                <tr key={m.student_id} className="border-b last:border-0">
                  <td className="p-3">{m.full_name}</td>
                  <td className="p-3">{m.grade || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
