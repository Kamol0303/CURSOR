"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { cn } from "@/lib/cn";
import { TmbLogo } from "@/components/TmbLogo";

export type NavItem = {
  href: string;
  label: string;
  key?: string;
  exact?: boolean;
  icon?: React.ReactNode;
};

function isNavActive(pathname: string, href: string, exact?: boolean) {
  if (exact) return pathname === href;
  return pathname === href || pathname.startsWith(`${href}/`);
}

function NavIcon({ name }: { name: string }) {
  const cls = "h-[18px] w-[18px] shrink-0 opacity-80";
  switch (name) {
    case "dashboard":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
      );
    case "centers":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0H5m14 0h-2m-2 0H9m-2 0H5" />
        </svg>
      );
    case "students":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
        </svg>
      );
    case "teachers":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      );
    case "groups":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      );
    case "subjects":
    case "courses":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      );
    case "messages":
    case "messagesMonitor":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      );
    case "attendance":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      );
    case "payments":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      );
    case "exams":
    case "grades":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
        </svg>
      );
    case "ratings":
    case "analytics":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      );
    case "certificates":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      );
    case "audit":
    case "security":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      );
    case "lessonStart":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      );
    case "schedule":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      );
    case "profile":
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    default:
      return (
        <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      );
  }
}

type AppShellProps = {
  brandTitle?: string;
  brandSubtitle?: string;
  roleBadge?: string;
  navItems: NavItem[];
  pageTitle?: string;
  pageSubtitle?: string;
  headerActions?: React.ReactNode;
  onLogout: () => void;
  logoutLabel: string;
  children: React.ReactNode;
  hideSidebar?: boolean;
  minimalHeader?: boolean;
};

export function AppShell({
  brandTitle = "TMB",
  brandSubtitle,
  roleBadge,
  navItems,
  pageTitle,
  pageSubtitle,
  headerActions,
  onLogout,
  logoutLabel,
  children,
  hideSidebar,
  minimalHeader,
}: AppShellProps) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const sidebar = (
  <aside
    className={cn(
      "flex flex-col shrink-0 text-white",
      "bg-gradient-to-b from-[#1b4d3e] via-[#163328] to-[#0f221c]",
      "ring-1 ring-white/10 shadow-xl",
      "w-64 h-[100dvh] overflow-hidden",
      "fixed inset-y-0 left-0 z-40 lg:sticky lg:top-0 lg:translate-x-0 transition-transform duration-slow ease-premium",
      mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
    )}
  >
    <div className="p-5 border-b border-white/10">
      <div className="flex items-center gap-3">
        <TmbLogo className="w-9 h-9 text-naqsh-accent shrink-0" />
        <div className="min-w-0">
          <div className="font-semibold text-base tracking-tight">{brandTitle}</div>
          {brandSubtitle && (
            <div className="text-caption text-white/60 truncate">{brandSubtitle}</div>
          )}
        </div>
      </div>
      {roleBadge && (
        <div className="mt-3 inline-flex text-caption font-medium uppercase tracking-wider text-naqsh-accent bg-white/10 rounded-md px-2 py-0.5">
          {roleBadge}
        </div>
      )}
    </div>

    <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto scrollbar-thin" aria-label="Main navigation">
      {navItems.map((item) => {
        const active = isNavActive(pathname, item.href, item.exact);
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={() => setMobileOpen(false)}
            className={cn(
              "flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-small transition-all duration-slow ease-premium",
              active
                ? "bg-white/15 font-medium text-white shadow-sm border-l-2 border-naqsh-accent pl-[10px] shadow-inset-highlight"
                : "text-white/75 hover:bg-white/10 hover:text-white border-l-2 border-transparent pl-[10px]",
            )}
            aria-current={active ? "page" : undefined}
          >
            {item.icon ?? <NavIcon name={item.key || item.href.split("/").pop() || "dashboard"} />}
            <span className="truncate">{item.label}</span>
          </Link>
        );
      })}
    </nav>

    <div className="p-3 border-t border-white/10">
      <button
        type="button"
        onClick={onLogout}
        className="w-full flex items-center gap-2.5 px-3 py-2.5 text-small rounded-lg text-white/70 hover:bg-white/10 hover:text-white transition-colors duration-fast"
      >
        <svg className="h-[18px] w-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        {logoutLabel}
      </button>
    </div>
  </aside>
  );

  return (
    <div className="min-h-[100dvh] bg-background flex overflow-hidden">
      {!hideSidebar && (
        <>
          {mobileOpen && (
            <div
              className="fixed inset-0 z-30 bg-black/50 lg:hidden animate-fade-in"
              onClick={() => setMobileOpen(false)}
              aria-hidden
            />
          )}
          {sidebar}
        </>
      )}

      <div className="flex-1 flex flex-col min-w-0 min-h-0">
        <header
          className={cn(
            "sticky top-0 z-20 shrink-0 bg-surface/90 dark:bg-card/90 backdrop-blur-xl",
            "border-b border-border px-4 sm:px-6 py-3",
            "flex justify-between items-center gap-4",
          )}
        >
          <div className="flex items-center gap-3 min-w-0">
            {!hideSidebar && (
              <button
                type="button"
                onClick={() => setMobileOpen(true)}
                className="lg:hidden p-2 -ml-1 rounded-lg hover:bg-muted transition-colors"
                aria-label="Open menu"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            )}
            {!minimalHeader && (pageTitle || pageSubtitle) && (
              <div className="min-w-0">
                {pageTitle && (
                  <h1 className="text-h4 text-naqsh-primary dark:text-naqsh-accent truncate">
                    {pageTitle}
                  </h1>
                )}
                {pageSubtitle && (
                  <p className="text-caption text-muted-foreground hidden sm:block truncate">{pageSubtitle}</p>
                )}
              </div>
            )}
          </div>
          {headerActions && (
            <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">{headerActions}</div>
          )}
        </header>

        <main className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}

export { NavIcon, isNavActive };
