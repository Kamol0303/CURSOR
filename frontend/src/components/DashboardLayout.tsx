"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { NotificationBell } from "@/components/NotificationBell";
import { getApiBaseUrl } from "@/lib/api";
import { usePermissions } from "@/hooks/usePermissions";

const NAV = [
  { href: "/dashboard", key: "dashboard", permission: "dashboard.view" },
  { href: "/dashboard/centers", key: "centers", permission: "centers.read" },
  { href: "/dashboard/students", key: "students", permission: "students.read" },
  { href: "/dashboard/teachers", key: "teachers", permission: "teachers.read" },
  { href: "/dashboard/groups", key: "groups", permission: "groups.read" },
  { href: "/dashboard/attendance", key: "attendance", permission: "attendance.read" },
  { href: "/dashboard/payments", key: "payments", permission: "payments.read" },
  { href: "/dashboard/ratings", key: "ratings", permission: "ratings.view" },
  { href: "/dashboard/certificates", key: "certificates", permission: "students.read" },
  { href: "/dashboard/analytics", key: "analytics", permission: "analytics.view" },
  { href: "/dashboard/security", key: "security", permission: "dashboard.view" },
] as const;

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const t = useTranslations("nav");
  const pathname = usePathname();
  const { can, me, loading } = usePermissions();

  const logout = async () => {
    await fetch(`${getApiBaseUrl()}/api/v1/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    localStorage.removeItem("tmb_access_token");
    window.location.href = "/";
  };

  const roleLabel = me?.role ? t(`roles.${me.role}` as "roles.super_admin") : "";

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-56 bg-naqsh-primary text-white flex flex-col shrink-0">
        <div className="p-4 border-b border-white/10">
          <div className="font-bold text-lg">TMB</div>
          <div className="text-xs text-white/70">{t("subtitle")}</div>
          {!loading && roleLabel && <div className="text-xs text-white/50 mt-1">{roleLabel}</div>}
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {NAV.filter((item) => can(item.permission)).map(({ href, key }) => (
            <Link
              key={href}
              href={href}
              className={`block px-3 py-2 rounded-lg text-sm transition-colors ${
                pathname === href || pathname.startsWith(href + "/")
                  ? "bg-white/20 font-medium"
                  : "hover:bg-white/10"
              }`}
            >
              {t(key)}
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
