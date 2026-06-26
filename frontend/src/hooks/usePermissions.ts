"use client";

import { useAuth } from "@/contexts/AuthContext";

/** @deprecated Use useAuth() from contexts/AuthContext */
export function usePermissions() {
  const { user, loading, can } = useAuth();
  return { me: user, loading, can };
}
