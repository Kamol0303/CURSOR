"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { AppShell } from "@/components/AppShell";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { NotificationBell } from "@/components/NotificationBell";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useAuth } from "@/contexts/AuthContext";
import { getApiBaseUrl } from "@/lib/api";
import { clearAuthCookie } from "@/lib/auth-cookie";
import { navRoutesForRole } from "@/lib/route-guards";

function isNavActive(pathname: string, href: string, exact?: boolean) {
  if (exact) return pathname === href;
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const t = useTranslations("nav");
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading, can, needsOnboarding } = useAuth();

  useEffect(() => {
    if (loading || !needsOnboarding) return;
    if (pathname !== "/dashboard/onboarding") {
      router.replace("/dashboard/onboarding");
    }
  }, [loading, needsOnboarding, pathname, router]);

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

  const roleLabel = user?.role ? t(`roles.${user.role}` as "roles.super_admin") : "";
  const visibleNav = navRoutesForRole(user?.role ?? null).filter((item) => can(item.permission));
  const isOnboarding = pathname === "/dashboard/onboarding";
  const activePage = visibleNav.find((item) => isNavActive(pathname, item.href, item.exact));

  return (
    <AppShell
      brandSubtitle={t("subtitle")}
      roleBadge={roleLabel || undefined}
      navItems={visibleNav.map((item) => ({
        href: item.href,
        key: item.key,
        label: t(item.key),
        exact: item.exact,
      }))}
      pageTitle={isOnboarding ? undefined : activePage ? t(activePage.key) : t("platform")}
      pageSubtitle={isOnboarding ? undefined : t("platform")}
      headerActions={
        <>
          {!isOnboarding && <NotificationBell />}
          <ThemeToggle />
          <LanguageSwitcher />
        </>
      }
      onLogout={logout}
      logoutLabel={t("logout")}
      hideSidebar={isOnboarding}
      minimalHeader={isOnboarding}
    >
      {children}
    </AppShell>
  );
}
