"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { NotificationBell } from "@/components/NotificationBell";
import { useAuth } from "@/contexts/AuthContext";
import { getApiBaseUrl } from "@/lib/api";
import { clearAuthCookie } from "@/lib/auth-cookie";

const NAV: ReadonlyArray<{
  href: string;
  key: string;
  permission: string;
  exact?: boolean;
}> = [
  { href: "/dashboard", key: "dashboard", permission: "dashboard.view", exact: true },
  { href: "/dashboard/centers", key: "centers", permission: "centers.read" },
  { href: "/dashboard/students", key: "students", permission: "students.read" },
  { href: "/dashboard/teachers", key: "teachers", permission: "teachers.read" },
  { href: "/dashboard/groups", key: "groups", permission: "groups.read" },
  { href: "/dashboard/courses", key: "courses", permission: "courses.read" },
  { href: "/dashboard/attendance", key: "attendance", permission: "attendance.read" },
  { href: "/dashboard/payments", key: "payments", permission: "payments.read" },
  { href: "/dashboard/exams", key: "exams", permission: "exams.read" },
  { href: "/dashboard/grades", key: "grades", permission: "grades.read" },
  { href: "/dashboard/ratings", key: "ratings", permission: "ratings.view" },
  { href: "/dashboard/certificates", key: "certificates", permission: "students.read" },
  { href: "/dashboard/analytics", key: "analytics", permission: "analytics.view" },
  { href: "/dashboard/security", key: "security", permission: "dashboard.view" },
];

function isNavActive(pathname: string, href: string, exact?: boolean) {
  if (exact) return pathname === href;
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const t = useTranslations("nav");
  const pathname = usePathname();
  const { user, loading, can } = useAuth();

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
  const visibleNav = NAV.filter((item) => can(item.permission));

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-56 bg-naqsh-primary text-white flex flex-col shrink-0 min-h-screen">
        <div className="p-4 border-b border-white/10">
          <div className="font-bold text-lg">TMB</div>
          <div className="text-xs text-white/70">{t("subtitle")}</div>
          {roleLabel && <div className="text-xs text-white/50 mt-1">{roleLabel}</div>}
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {visibleNav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`block px-3 py-2 rounded-lg text-sm transition-colors ${
                isNavActive(pathname, item.href, item.exact)
                  ? "bg-white/20 font-medium"
                  : "hover:bg-white/10"
              }`}
            >
              {t(item.key)}
            </Link>
          ))}
        </nav>
        <div className="p-3 border-t border-white/10">
          <button
            type="button"
            onClick={logout}
            className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-white/10"
          >
            {t("logout")}
          </button>
        </div>
      </aside>
      <div className="flex-1 flex flex-col min-w-0">
        <header className="bg-white border-b px-6 py-3 flex justify-between items-center">
          <h1 className="text-lg font-semibold text-naqsh-primary">{t("platform")}</h1>
          <div className="flex items-center gap-2">
            <NotificationBell />
            <LanguageSwitcher />
          </div>
        </header>
        <main className="flex-1 p-6 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
