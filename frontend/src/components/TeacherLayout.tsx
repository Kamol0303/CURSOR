"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { getApiBaseUrl } from "@/lib/api";
import { clearAuthCookie } from "@/lib/auth-cookie";

const NAV = [
  { href: "/teacher/dashboard", key: "dashboard", exact: true },
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

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-56 bg-naqsh-primary text-white flex flex-col shrink-0 min-h-screen">
        <div className="p-4 border-b border-white/10">
          <div className="font-bold text-lg">TMB</div>
          <div className="text-xs text-white/70">{t("subtitle")}</div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`block px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive(pathname, item.href, "exact" in item && item.exact)
                  ? "bg-white/20 font-medium"
                  : "hover:bg-white/10"
              }`}
            >
              {t(`nav.${item.key}`)}
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
        <header className="bg-white border-b px-6 py-3 flex justify-end">
          <LanguageSwitcher />
        </header>
        <main className="flex-1 p-6 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
