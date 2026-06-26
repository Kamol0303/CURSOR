"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { GenerateExamModal } from "@/components/GenerateExamModal";
import { PermissionGate } from "@/components/PermissionGate";
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
    <div className="space-y-4">
      <div className="flex justify-between items-center flex-wrap gap-2">
        <div>
          <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
          <p className="text-sm text-gray-500">{t("subtitle")}</p>
        </div>
        <PermissionGate permission="exams.create">
          <button
            type="button"
            onClick={() => setShowGenerate(true)}
            disabled={subjects.length === 0}
            className="px-4 py-2 bg-naqsh-accent text-white rounded-lg text-sm font-medium disabled:opacity-50"
          >
            {t("generate")}
          </button>
        </PermissionGate>
      </div>
      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {exams.map((exam) => (
            <Link
              key={exam.id}
              href={`/dashboard/exams/${exam.id}`}
              className="bg-white border rounded-xl p-4 hover:ring-2 hover:ring-naqsh-accent/40 block"
            >
              <h3 className="font-semibold">{exam.title}</h3>
              <p className="text-sm text-gray-500">
                {t("questions")}: {exam.question_count} · {t("passScore")}: {exam.pass_score}%
              </p>
              <span
                className={`text-xs px-2 py-0.5 rounded ${
                  exam.is_published ? "bg-green-100 text-green-800" : "bg-gray-100"
                }`}
              >
                {exam.is_published ? t("published") : t("draft")}
              </span>
            </Link>
          ))}
          {exams.length === 0 && <p className="text-gray-400">{t("empty")}</p>}
        </div>
      )}
      {showGenerate && (
        <GenerateExamModal
          subjects={subjects}
          onClose={() => setShowGenerate(false)}
          onGenerated={(examId) => router.push(`/dashboard/exams/${examId}`)}
        />
      )}
    </div>
  );
}
