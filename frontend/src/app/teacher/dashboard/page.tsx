"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import {
  Badge,
  Card,
  CardBody,
  CardTitle,
  EmptyState,
  PageHeader,
  PageSection,
  PageSkeleton,
} from "@/components/ui";
import { apiFetch } from "@/lib/api";

type Profile = {
  full_name: string;
  center_name: string;
};

type Group = {
  id: string;
  name: string;
  subject_name_uz: string | null;
  enrollment_count: number;
  room: string | null;
};

export default function TeacherDashboardPage() {
  const t = useTranslations("teacherPortal");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([apiFetch<Profile>("/teacher/me"), apiFetch<Group[]>("/teacher/groups")]).then(
      ([me, groupsRes]) => {
        if (me.success && me.data) setProfile(me.data);
        if (groupsRes.success && Array.isArray(groupsRes.data)) setGroups(groupsRes.data);
        setLoading(false);
      },
    );
  }, []);

  if (loading) return <PageSkeleton />;

  const totalStudents = groups.reduce((sum, g) => sum + g.enrollment_count, 0);

  return (
    <PageSection className="max-w-3xl">
      <PageHeader
        title={t("welcome")}
        description={
          profile ? `${profile.full_name} · ${profile.center_name}` : undefined
        }
      />

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardBody>
            <p className="text-small text-muted-foreground">{t("myGroups")}</p>
            <p className="text-3xl font-bold text-naqsh-primary mt-1">{groups.length}</p>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <p className="text-small text-muted-foreground">{t("totalStudents")}</p>
            <p className="text-3xl font-bold text-naqsh-primary mt-1">{totalStudents}</p>
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardBody>
          <CardTitle className="mb-4">{t("quickGroups")}</CardTitle>
          {groups.length === 0 ? (
            <EmptyState title={t("noGroups")} className="py-8" />
          ) : (
            <ul className="space-y-2">
              {groups.map((g) => (
                <li key={g.id}>
                  <Link
                    href={`/teacher/groups/${g.id}`}
                    className="flex items-center justify-between gap-3 rounded-lg px-3 py-2.5 text-small transition-colors hover:bg-muted"
                  >
                    <span className="text-foreground font-medium">
                      {g.name}
                      {g.subject_name_uz ? ` · ${g.subject_name_uz}` : ""}
                    </span>
                    <Badge variant="primary">{g.enrollment_count}</Badge>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>
    </PageSection>
  );
}
