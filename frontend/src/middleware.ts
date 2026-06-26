import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { getRoleFromToken } from "@/lib/auth-cookie";

export function middleware(request: NextRequest) {
  const rawToken = request.cookies.get("tmb_access_token")?.value;
  const token = rawToken ? decodeURIComponent(rawToken) : null;
  const { pathname } = request.nextUrl;

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

  if (isDashboard && role === "student") {
    return NextResponse.redirect(new URL("/student/dashboard", request.url));
  }
  if (isDashboard && role === "parent") {
    return NextResponse.redirect(new URL("/parent/dashboard", request.url));
  }
  if (isDashboard && role === "teacher") {
    return NextResponse.redirect(new URL("/teacher/dashboard", request.url));
  }
  if (isStudent && role !== "student") {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }
  if (isParent && role !== "parent") {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }
  if (isTeacher && role !== "teacher") {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/student/:path*", "/parent/:path*", "/teacher/:path*"],
};
