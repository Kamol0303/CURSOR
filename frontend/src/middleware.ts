import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { getPermissionsFromToken, getRoleFromToken } from "@/lib/auth-cookie";
import { canAccessDashboardRoute, homePathForPortalRole } from "@/lib/route-guards";

export function middleware(request: NextRequest) {
  const rawToken = request.cookies.get("tmb_access_token")?.value;
  const token = rawToken ? decodeURIComponent(rawToken) : null;
  const { pathname } = request.nextUrl;

  if (pathname === "/forbidden") {
    if (!token) {
      return NextResponse.redirect(new URL("/", request.url));
    }
    return NextResponse.next();
  }

  const isDashboard = pathname.startsWith("/dashboard");
  const isStudent = pathname.startsWith("/student");
  const isParent = pathname.startsWith("/parent") && !pathname.startsWith("/parent/login");
  const isTeacher = pathname.startsWith("/teacher");

  if (!isDashboard && !isStudent && !isParent && !isTeacher) {
    return NextResponse.next();
  }

  if (!token) {
    const login = isParent ? "/parent/login" : "/";
    return NextResponse.redirect(new URL(login, request.url));
  }

  const role = getRoleFromToken(token);
  const permissions = getPermissionsFromToken(token);
  const portalHome = homePathForPortalRole(role);

  if (isDashboard) {
    if (role === "student" || role === "parent" || role === "teacher") {
      return NextResponse.redirect(new URL(portalHome, request.url));
    }
    if (!canAccessDashboardRoute(pathname, permissions, role)) {
      return NextResponse.redirect(new URL("/forbidden", request.url));
    }
    return NextResponse.next();
  }

  if (isStudent && role !== "student") {
    return NextResponse.redirect(new URL(portalHome, request.url));
  }
  if (isParent && role !== "parent") {
    return NextResponse.redirect(new URL(portalHome, request.url));
  }
  if (isTeacher && role !== "teacher") {
    return NextResponse.redirect(new URL(portalHome, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/student/:path*",
    "/parent/:path*",
    "/teacher/:path*",
    "/forbidden",
  ],
};
