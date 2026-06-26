"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { getMe } from "@/lib/api";

export type AuthUser = {
  id: string;
  username: string | null;
  role: string;
  center_id: string | null;
  permissions: string[];
};

type AuthContextValue = {
  user: AuthUser | null;
  loading: boolean;
  can: (permission: string) => boolean;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

const CACHE_KEY = "tmb_me_cache";

function readCache(): AuthUser | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(CACHE_KEY);
    return raw ? (JSON.parse(raw) as AuthUser) : null;
  } catch {
    return null;
  }
}

function writeCache(user: AuthUser | null) {
  if (typeof window === "undefined") return;
  if (user) sessionStorage.setItem(CACHE_KEY, JSON.stringify(user));
  else sessionStorage.removeItem(CACHE_KEY);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => readCache());
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("tmb_access_token") : null;
    if (!token) {
      setUser(null);
      writeCache(null);
      return;
    }
    const res = await getMe();
    if (res.success && res.data) {
      const next: AuthUser = {
        id: res.data.id,
        username: res.data.username ?? null,
        role: res.data.role,
        center_id: res.data.center_id ?? null,
        permissions: res.data.permissions ?? [],
      };
      setUser(next);
      writeCache(next);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("tmb_access_token");
    if (!token) {
      setLoading(false);
      window.location.href = "/";
      return;
    }
    refresh().finally(() => setLoading(false));
  }, [refresh]);

  const can = useCallback((permission: string) => user?.permissions.includes(permission) ?? false, [user]);

  const value = useMemo(() => ({ user, loading, can, refresh }), [user, loading, can, refresh]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
