"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { DigitalClock } from "@/components/DigitalClock";
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

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="grid gap-4 lg:grid-cols-[1fr_minmax(260px,340px)]">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{t("welcome")}</h2>
          {profile && (
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              {profile.full_name} · {profile.center_name}
            </p>
          )}
        </div>
        <DigitalClock />
      </div>
      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="bg-white rounded-xl border p-4">
              <p className="text-sm text-gray-500">{t("myGroups")}</p>
              <p className="text-3xl font-bold text-naqsh-primary">{groups.length}</p>
            </div>
            <div className="bg-white rounded-xl border p-4">
              <p className="text-sm text-gray-500">{t("totalStudents")}</p>
              <p className="text-3xl font-bold text-naqsh-primary">
                {groups.reduce((sum, g) => sum + g.enrollment_count, 0)}
              </p>
            </div>
          </div>
          <section className="bg-white rounded-xl border p-4">
            <h3 className="font-semibold text-naqsh-primary mb-3">{t("quickGroups")}</h3>
            {groups.length === 0 ? (
              <p className="text-sm text-gray-400">{t("noGroups")}</p>
            ) : (
              <ul className="space-y-2">
                {groups.map((g) => (
                  <li key={g.id}>
                    <Link
                      href={`/teacher/groups/${g.id}`}
                      className="text-sm text-naqsh-accent hover:underline"
                    >
                      {g.name}
                      {g.subject_name_uz ? ` · ${g.subject_name_uz}` : ""}
                      {" "}
                      ({g.enrollment_count})
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </div>
  );
}
