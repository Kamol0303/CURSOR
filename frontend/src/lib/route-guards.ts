/** Dashboard route → required permission (mirrors backend NAV_PERMISSIONS). */

export type DashboardNavItem = {
  href: string;
  key: string;
  permission: string;
  exact?: boolean;
};

export const DASHBOARD_NAV_ROUTES: readonly DashboardNavItem[] = [
  { href: "/dashboard", key: "dashboard", permission: "dashboard.view", exact: true },
  { href: "/dashboard/centers", key: "centers", permission: "centers.read" },
  { href: "/dashboard/students", key: "students", permission: "students.read" },
  { href: "/dashboard/teachers", key: "teachers", permission: "teachers.read" },
  { href: "/dashboard/groups", key: "groups", permission: "groups.read" },
  { href: "/dashboard/courses", key: "courses", permission: "courses.read" },
  { href: "/dashboard/messages", key: "messages", permission: "messages.read" },
  { href: "/dashboard/messages/monitor", key: "messagesMonitor", permission: "messages.monitor" },
  { href: "/dashboard/attendance", key: "attendance", permission: "attendance.read" },
  { href: "/dashboard/payments", key: "payments", permission: "payments.read" },
  { href: "/dashboard/exams", key: "exams", permission: "exams.read" },
  { href: "/dashboard/grades", key: "grades", permission: "grades.read" },
  { href: "/dashboard/ratings", key: "ratings", permission: "ratings.view" },
  { href: "/dashboard/certificates", key: "certificates", permission: "ratings.view" },
  { href: "/dashboard/analytics", key: "analytics", permission: "analytics.view" },
  { href: "/dashboard/security", key: "security", permission: "users.password_reset" },
] as const;

const ONBOARDING_PATH = "/dashboard/onboarding";

const SORTED_ROUTES = [...DASHBOARD_NAV_ROUTES].sort((a, b) => b.href.length - a.href.length);

export function requiredPermissionForPath(pathname: string): string | null {
  if (pathname === ONBOARDING_PATH || pathname.startsWith(`${ONBOARDING_PATH}/`)) {
    return "__onboarding__";
  }

  for (const route of SORTED_ROUTES) {
    if (route.exact) {
      if (pathname === route.href) return route.permission;
      continue;
    }
    if (pathname === route.href || pathname.startsWith(`${route.href}/`)) {
      return route.permission;
    }
  }

  if (pathname.startsWith("/dashboard")) {
    return "dashboard.view";
  }

  return null;
}

export function canAccessDashboardRoute(
  pathname: string,
  permissions: string[],
  role: string | null,
): boolean {
  const required = requiredPermissionForPath(pathname);
  if (required === "__onboarding__") {
    return role === "center_director";
  }
  if (!required) return true;
  return permissions.includes(required);
}

export function homePathForPortalRole(role: string | null): string {
  if (role === "student") return "/student/dashboard";
  if (role === "parent") return "/parent/dashboard";
  if (role === "teacher") return "/teacher/dashboard";
  return "/dashboard";
}
