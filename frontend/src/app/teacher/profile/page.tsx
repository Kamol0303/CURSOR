"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { ChangePasswordForm } from "@/components/ChangePasswordForm";
import { apiFetch } from "@/lib/api";

type Profile = {
  full_name: string;
  phone: string | null;
  specialization: string | null;
  center_name: string;
  username: string | null;
};

export default function TeacherProfilePage() {
  const t = useTranslations("teacherPortal");
  const [profile, setProfile] = useState<Profile | null>(null);

  useEffect(() => {
    apiFetch<Profile>("/teacher/me").then((res) => {
      if (res.success && res.data) setProfile(res.data);
    });
  }, []);

  return (
    <div className="space-y-6 max-w-lg">
      <h2 className="text-xl font-bold text-naqsh-primary">{t("nav.profile")}</h2>
      {profile && (
        <section className="bg-white rounded-xl border p-4 space-y-2 text-sm">
          <p>
            <span className="text-gray-500">{t("profileName")}:</span> {profile.full_name}
          </p>
          <p>
            <span className="text-gray-500">{t("profileLogin")}:</span> {profile.username || "—"}
          </p>
          <p>
            <span className="text-gray-500">{t("profileCenter")}:</span> {profile.center_name}
          </p>
          <p>
            <span className="text-gray-500">{t("profilePhone")}:</span> {profile.phone || "—"}
          </p>
          <p>
            <span className="text-gray-500">{t("profileSpec")}:</span> {profile.specialization || "—"}
          </p>
        </section>
      )}
      <section className="bg-white rounded-xl border p-4">
        <h3 className="font-semibold mb-4">{t("changePassword")}</h3>
        <ChangePasswordForm />
      </section>
    </div>
  );
}
