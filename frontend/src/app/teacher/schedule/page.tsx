"use client";

import { useEffect, useState } from "react";
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

type ScheduleItem = {
  group_id: string;
  group_name: string;
  room: string | null;
  subject_name: string | null;
  schedule: Record<string, unknown>;
};

export default function TeacherSchedulePage() {
  const t = useTranslations("teacherPortal");
  const [items, setItems] = useState<ScheduleItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<ScheduleItem[]>("/teacher/schedule")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setItems(res.data);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <PageSkeleton />;

  return (
    <PageSection className="max-w-3xl">
      <PageHeader title={t("nav.schedule")} />

      {items.length === 0 ? (
        <EmptyState title={t("noSchedule")} />
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <Card key={item.group_id}>
              <CardBody>
                <CardTitle>{item.group_name}</CardTitle>
                <CardDescription>
                  {item.subject_name || "—"} · {t("room")}: {item.room || "—"}
                </CardDescription>
                <pre className="mt-4 text-caption bg-muted rounded-lg p-4 overflow-x-auto text-muted-foreground">
                  {JSON.stringify(item.schedule, null, 2)}
                </pre>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </PageSection>
  );
}
