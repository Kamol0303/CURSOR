"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { canAccessDashboardRoute } from "@/lib/route-guards";

export function DashboardRouteGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading } = useAuth();

  const allowed =
    !user || canAccessDashboardRoute(pathname, user.permissions, user.role);

  useEffect(() => {
    if (loading || !user) return;
    if (!canAccessDashboardRoute(pathname, user.permissions, user.role)) {
      router.replace("/forbidden");
    }
  }, [loading, user, pathname, router]);

  if (loading) return null;
  if (!allowed) return null;

  return <>{children}</>;
}
