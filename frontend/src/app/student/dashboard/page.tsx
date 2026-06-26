"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch, getApiBaseUrl } from "@/lib/api";
import { clearAuthCookie } from "@/lib/auth-cookie";

type Profile = {
  full_name: string;
  grade: string | null;
  school: string | null;
  center_name: string;
};

type GradeRow = {
  subject_name: string;
  grade_value: number;
  grade_type: string;
  graded_at: string;
};

type ExamRow = {
  title: string;
  pass_score: number;
  duration_minutes: number;
};

export default function StudentDashboardPage() {
  const t = useTranslations("studentCabinet");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [grades, setGrades] = useState<GradeRow[]>([]);
  const [exams, setExams] = useState<ExamRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch<Profile>("/student/me"),
      apiFetch<GradeRow[]>("/student/grades"),
      apiFetch<ExamRow[]>("/student/exams"),
    ]).then(([me, gradesRes, examsRes]) => {
      if (me.success && me.data) setProfile(me.data);
      if (gradesRes.success && Array.isArray(gradesRes.data)) setGrades(gradesRes.data);
      if (examsRes.success && Array.isArray(examsRes.data)) setExams(examsRes.data);
      setLoading(false);
    });
  }, []);

  const logout = async () => {
    await fetch(`${getApiBaseUrl()}/api/v1/auth/logout`, { method: "POST", credentials: "include" });
    localStorage.removeItem("tmb_access_token");
    sessionStorage.removeItem("tmb_me_cache");
    clearAuthCookie();
    window.location.href = "/";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-naqsh-primary text-white px-4 py-4 flex justify-between items-center">
        <div>
          <h1 className="font-bold text-lg">{t("title")}</h1>
          <p className="text-xs text-white/70">{profile?.center_name}</p>
        </div>
        <button type="button" onClick={logout} className="text-sm underline">
          {t("logout")}
        </button>
      </header>

      <main className="p-4 max-w-lg mx-auto space-y-4">
        {loading ? (
          <p className="text-gray-500">{t("loading")}</p>
        ) : (
          <>
            {profile && (
              <section className="bg-white rounded-xl border p-4">
                <h2 className="font-semibold text-naqsh-primary">{profile.full_name}</h2>
                <p className="text-sm text-gray-600">
                  {profile.grade || "—"} · {profile.school || "—"}
                </p>
              </section>
            )}

            <section className="bg-white rounded-xl border p-4">
              <h3 className="font-semibold mb-2">{t("grades")}</h3>
              {grades.length === 0 ? (
                <p className="text-sm text-gray-400">{t("emptyGrades")}</p>
              ) : (
                <ul className="space-y-2 text-sm">
                  {grades.map((g, i) => (
                    <li key={`${g.subject_name}-${i}`} className="flex justify-between border-b pb-1">
                      <span>{g.subject_name}</span>
                      <span className="font-medium">{g.grade_value}</span>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="bg-white rounded-xl border p-4">
              <h3 className="font-semibold mb-2">{t("exams")}</h3>
              {exams.length === 0 ? (
                <p className="text-sm text-gray-400">{t("emptyExams")}</p>
              ) : (
                <ul className="space-y-2 text-sm">
                  {exams.map((e, i) => (
                    <li key={`${e.title}-${i}`} className="border-b pb-1">
                      <div className="font-medium">{e.title}</div>
                      <div className="text-gray-500">
                        {t("passScore")}: {e.pass_score}% · {e.duration_minutes} min
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}
