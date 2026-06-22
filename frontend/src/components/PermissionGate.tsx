"use client";

import { usePermissions } from "@/hooks/usePermissions";

export function PermissionGate({
  permission,
  children,
  fallback = null,
}: {
  permission: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}) {
  const { can, loading } = usePermissions();
  if (loading) return null;
  if (!can(permission)) return <>{fallback}</>;
  return <>{children}</>;
}
