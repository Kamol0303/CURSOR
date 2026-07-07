"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  Badge,
  Button,
  Card,
  CardBody,
  CardTitle,
  EmptyState,
  PageSkeleton,
} from "@/components/ui";
import { InternalCyberBackground } from "@/components/InternalCyberBackground";
import { DigitalClock } from "@/components/DigitalClock";
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
  id: string;
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
    <div className="internal-page-shell min-h-screen bg-background/95">
      <InternalCyberBackground />
      <header className="relative z-10 bg-naqsh-primary text-white px-4 py-5 flex justify-between items-center shadow-sm">
        <div>
          <h1 className="font-bold text-lg">{t("title")}</h1>
          <p className="text-caption text-white/70 mt-0.5">{profile?.center_name}</p>
        </div>
        <Button variant="ghost" size="sm" onClick={logout} className="text-white hover:bg-white/10">
          {t("logout")}
        </Button>
      </header>

      <main className="relative z-10 p-4 max-w-lg mx-auto space-y-5">
        <DigitalClock />
        {loading ? (
          <PageSkeleton />
        ) : (
          <>
            {profile && (
              <Card>
                <CardBody>
                  <CardTitle>{profile.full_name}</CardTitle>
                  <p className="text-small text-muted-foreground mt-1">
                    {profile.grade || "—"} · {profile.school || "—"}
                  </p>
                </CardBody>
              </Card>
            )}

            <Card>
              <CardBody>
                <CardTitle className="mb-4">{t("grades")}</CardTitle>
                {grades.length === 0 ? (
                  <EmptyState title={t("emptyGrades")} className="py-8" />
                ) : (
                  <ul className="space-y-2">
                    {grades.map((g, i) => (
                      <li
                        key={`${g.subject_name}-${i}`}
                        className="flex justify-between items-center border-b border-border pb-2 last:border-0 text-small"
                      >
                        <span className="text-foreground">{g.subject_name}</span>
                        <Badge variant="primary">{g.grade_value}</Badge>
                      </li>
                    ))}
                  </ul>
                )}
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <CardTitle className="mb-4">{t("exams")}</CardTitle>
                {exams.length === 0 ? (
                  <EmptyState title={t("emptyExams")} className="py-8" />
                ) : (
                  <ul className="space-y-3">
                    {exams.map((e) => (
                      <li key={e.id} className="border-b border-border pb-3 last:border-0">
                        <a
                          href={`/student/exams/${e.id}`}
                          className="font-medium text-naqsh-primary hover:underline"
                        >
                          {e.title}
                        </a>
                        <p className="text-caption text-muted-foreground mt-1">
                          {t("passScore")}: {e.pass_score}% · {e.duration_minutes} min
                        </p>
                      </li>
                    ))}
                  </ul>
                )}
              </CardBody>
            </Card>
          </>
        )}
      </main>
    </div>
  );
}
