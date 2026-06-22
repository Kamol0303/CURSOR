"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { NotificationBell } from "@/components/NotificationBell";

const NAV = [
  { href: "/dashboard", key: "dashboard" },
  { href: "/dashboard/centers", key: "centers" },
  { href: "/dashboard/students", key: "students" },
  { href: "/dashboard/teachers", key: "teachers" },
  { href: "/dashboard/ratings", key: "ratings" },
  { href: "/dashboard/certificates", key: "certificates" },
  { href: "/dashboard/analytics", key: "analytics" },
  { href: "/dashboard/security", key: "security" },
] as const;

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const t = useTranslations("nav");
  const pathname = usePathname();

  const logout = async () => {
    await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    localStorage.removeItem("tamor_access_token");
    window.location.href = "/";
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-56 bg-naqsh-primary text-white flex flex-col shrink-0">
        <div className="p-4 border-b border-white/10">
          <div className="font-bold text-lg">TaMoR</div>
          <div className="text-xs text-white/70">{t("subtitle")}</div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {NAV.map(({ href, key }) => (
            <Link
              key={href}
              href={href}
              className={`block px-3 py-2 rounded-lg text-sm transition-colors ${
                pathname === href ? "bg-white/20 font-medium" : "hover:bg-white/10"
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
