"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { ChangePasswordForm } from "@/components/ChangePasswordForm";
import {
  Card,
  CardBody,
  CardTitle,
  PageHeader,
  PageSection,
} from "@/components/ui";
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
    <PageSection className="max-w-lg">
      <PageHeader title={t("nav.profile")} />

      {profile && (
        <Card>
          <CardBody className="space-y-3 text-small">
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">{t("profileName")}</span>
              <span className="text-foreground font-medium text-right">{profile.full_name}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">{t("profileLogin")}</span>
              <span className="text-foreground text-right">{profile.username || "—"}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">{t("profileCenter")}</span>
              <span className="text-foreground text-right">{profile.center_name}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">{t("profilePhone")}</span>
              <span className="text-foreground text-right">{profile.phone || "—"}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">{t("profileSpec")}</span>
              <span className="text-foreground text-right">{profile.specialization || "—"}</span>
            </div>
          </CardBody>
        </Card>
      )}

      <Card>
        <CardBody>
          <ChangePasswordForm />
        </CardBody>
      </Card>
    </PageSection>
  );
}
