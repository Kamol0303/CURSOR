"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import {
  Card,
  CardBody,
  CardDescription,
  CardTitle,
  EmptyState,
  PageHeader,
  PageSection,
  PageSkeleton,
} from "@/components/ui";
import { apiFetch } from "@/lib/api";

type Group = {
  id: string;
  name: string;
  subject_name_uz: string | null;
  teacher_name: string | null;
  room: string | null;
  enrollment_count: number;
  is_active: boolean;
};

export default function TeacherGroupsPage() {
  const t = useTranslations("teacherPortal");
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Group[]>("/teacher/groups")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setGroups(res.data);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <PageSkeleton />;

  return (
    <PageSection className="max-w-3xl">
      <PageHeader title={t("nav.groups")} />

      {groups.length === 0 ? (
        <EmptyState title={t("noGroups")} />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {groups.map((g) => (
            <Link key={g.id} href={`/teacher/groups/${g.id}`}>
              <Card hover className="h-full">
                <CardBody>
                  <CardTitle>{g.name}</CardTitle>
                  <CardDescription>{g.subject_name_uz || "—"}</CardDescription>
                  <p className="text-small text-muted-foreground mt-3">
                    {t("room")}: {g.room || "—"} · {t("students")}: {g.enrollment_count}
                  </p>
                </CardBody>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </PageSection>
  );
}
