"use client";

import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { AppShell } from "@/components/AppShell";
import { DigitalClock } from "@/components/DigitalClock";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";
import { ChangePasswordForm } from "@/components/ChangePasswordForm";
import { Card, CardBody, CardDescription, CardTitle } from "@/components/ui";
import { useAuth } from "@/contexts/AuthContext";
import { getApiBaseUrl } from "@/lib/api";
import { clearAuthCookie } from "@/lib/auth-cookie";

const NAV = [
  { href: "/teacher/dashboard", key: "dashboard", exact: true },
  { href: "/teacher/lesson-start", key: "lessonStart" },
  { href: "/teacher/groups", key: "groups" },
  { href: "/teacher/attendance", key: "attendance" },
  { href: "/teacher/grades", key: "grades" },
  { href: "/teacher/schedule", key: "schedule" },
  { href: "/teacher/profile", key: "profile" },
] as const;

function isActive(pathname: string, href: string, exact?: boolean) {
  if (exact) return pathname === href;
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function TeacherLayout({ children }: { children: React.ReactNode }) {
  const t = useTranslations("teacherPortal");
  const pathname = usePathname();
  const { mustChangePassword, refresh } = useAuth();

  const logout = async () => {
    await fetch(`${getApiBaseUrl()}/api/v1/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    localStorage.removeItem("tmb_access_token");
    sessionStorage.removeItem("tmb_me_cache");
    clearAuthCookie();
    window.location.href = "/";
  };

  const activeItem = NAV.find((item) => isActive(pathname, item.href, "exact" in item && item.exact));

  return (
    <AppShell
      brandSubtitle={t("subtitle")}
      navItems={NAV.map((item) => ({
        href: item.href,
        key: item.key,
        label: t(`nav.${item.key}`),
        exact: "exact" in item ? item.exact : undefined,
      }))}
      pageTitle={activeItem ? t(`nav.${activeItem.key}`) : t("subtitle")}
      headerActions={
        <>
          <DigitalClock variant="compact" />
          <ThemeToggle />
          <LanguageSwitcher />
        </>
      }
      onLogout={logout}
      logoutLabel={t("logout")}
    >
      {mustChangePassword ? (
        <div className="max-w-md mx-auto animate-slide-up">
          <Card>
            <CardBody className="space-y-4">
              <div>
                <CardTitle>{t("changePasswordTitle")}</CardTitle>
                <CardDescription>{t("changePasswordHint")}</CardDescription>
              </div>
              <ChangePasswordForm onSuccess={() => void refresh()} />
            </CardBody>
          </Card>
        </div>
      ) : (
        children
      )}
    </AppShell>
  );
}
