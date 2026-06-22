"use client";

import { useEffect, useState } from "react";
import { getMe } from "@/lib/api";

type Me = {
  role: string;
  center_id: string | null;
  permissions: string[];
};

export function usePermissions() {
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMe()
      .then((res) => {
        if (res.success && res.data) setMe(res.data as Me);
      })
      .finally(() => setLoading(false));
  }, []);

  const can = (permission: string) => me?.permissions.includes(permission) ?? false;

  return { me, loading, can };
}
