"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { GenerateExamModal } from "@/components/GenerateExamModal";
import { PermissionGate } from "@/components/PermissionGate";
import {
  Badge,
  Button,
  Card,
  CardBody,
  CardDescription,
  CardTitle,
  EmptyState,
  PageHeader,
  PageSection,
  CardSkeleton,
} from "@/components/ui";
import { apiFetch } from "@/lib/api";

type Exam = {
  id: string;
  title: string;
  pass_score: number;
  duration_minutes: number;
  is_published: boolean;
  question_count: number;
};

export default function ExamsPage() {
  const t = useTranslations("exams");
  const router = useRouter();
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [subjects, setSubjects] = useState<{ id: string; name_uz: string }[]>([]);
  const [showGenerate, setShowGenerate] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    apiFetch<Exam[]>("/exams")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setExams(res.data);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    apiFetch<{ id: string; name_uz: string }[]>("/subjects").then((res) => {
      if (res.success && Array.isArray(res.data)) setSubjects(res.data);
    });
  }, [load]);

  return (
    <PageSection>
      <PageHeader
        title={t("title")}
        description={t("subtitle")}
        actions={
          <PermissionGate permission="exams.create">
            <Button variant="accent" onClick={() => setShowGenerate(true)} disabled={subjects.length === 0}>
              {t("generate")}
            </Button>
          </PermissionGate>
        }
      />

      {loading ? (
        <div className="grid gap-3 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : exams.length === 0 ? (
        <EmptyState title={t("empty")} />
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {exams.map((exam) => (
            <Link key={exam.id} href={`/dashboard/exams/${exam.id}`}>
              <Card hover className="h-full">
                <CardBody>
                  <CardTitle>{exam.title}</CardTitle>
                  <CardDescription>
                    {t("questions")}: {exam.question_count} · {t("passScore")}: {exam.pass_score}%
                  </CardDescription>
                  <Badge variant={exam.is_published ? "success" : "default"} className="mt-2">
                    {exam.is_published ? t("published") : t("draft")}
                  </Badge>
                </CardBody>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {showGenerate && (
        <GenerateExamModal
          subjects={subjects}
          onClose={() => setShowGenerate(false)}
          onGenerated={(examId) => router.push(`/dashboard/exams/${examId}`)}
        />
      )}
    </PageSection>
  );
}
