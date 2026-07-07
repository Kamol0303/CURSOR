"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";
import { NotificationBell } from "@/components/NotificationBell";
import { TmbLogo } from "@/components/TmbLogo";
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
    <div className="min-h-screen bg-gray-100/80 dark:bg-gray-950 flex">
      {!isOnboarding && (
      <aside className="w-60 bg-gradient-to-b from-[#1b4d3e] to-[#163328] text-white flex flex-col shrink-0 min-h-screen shadow-xl">
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <TmbLogo className="w-9 h-9 text-naqsh-accent shrink-0" />
            <div className="min-w-0">
              <div className="font-bold text-base tracking-tight">TMB</div>
              <div className="text-[11px] text-white/65 truncate">{t("subtitle")}</div>
            </div>
          </div>
          {roleLabel && (
            <div className="mt-2 inline-flex text-[10px] font-medium uppercase tracking-wider text-naqsh-accent bg-white/10 rounded px-2 py-0.5">
              {roleLabel}
            </div>
          )}
        </div>
        <nav className="flex-1 p-2.5 space-y-0.5 overflow-y-auto">
          {visibleNav.map((item) => {
            const active = isNavActive(pathname, item.href, item.exact);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm transition-colors duration-200 border-l-[3px] ${
                  active
                    ? "bg-white/15 font-medium border-naqsh-accent text-white"
                    : "border-transparent text-white/85 hover:bg-white/10 hover:text-white"
                }`}
              >
                {t(item.key)}
              </Link>
            );
          })}
        </nav>
        <div className="p-2.5 border-t border-white/10">
          <button
            type="button"
            onClick={logout}
            className="w-full text-left px-3 py-2.5 text-sm rounded-lg text-white/80 hover:bg-white/10 hover:text-white transition-colors"
          >
            {t("logout")}
          </button>
        </div>
      </aside>
      )}
      <div className="flex-1 flex flex-col min-w-0">
        {!isOnboarding && (
        <header className="sticky top-0 z-10 bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-gray-200/80 dark:border-gray-800 px-4 sm:px-6 py-3 flex justify-between items-center gap-4 shadow-sm">
          <div className="min-w-0">
            <h1 className="text-base sm:text-lg font-semibold text-naqsh-primary dark:text-naqsh-accent truncate">
              {activePage ? t(activePage.key) : t("platform")}
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400 hidden sm:block">{t("platform")}</p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <NotificationBell />
            <ThemeToggle />
            <LanguageSwitcher />
          </div>
        </header>
        )}
        {isOnboarding && (
        <header className="bg-white dark:bg-gray-900 border-b dark:border-gray-800 px-6 py-3 flex justify-end items-center gap-2">
          <ThemeToggle />
          <LanguageSwitcher />
        </header>
        )}
        <main className="flex-1 p-4 sm:p-6 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
