"use client";

import { AuthProvider } from "@/contexts/AuthContext";
import { DashboardLayout } from "@/components/DashboardLayout";
import { DashboardRouteGuard } from "@/components/DashboardRouteGuard";

export default function DashboardSectionLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <DashboardRouteGuard>
        <DashboardLayout>{children}</DashboardLayout>
      </DashboardRouteGuard>
    </AuthProvider>
  );
}
