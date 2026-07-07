"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/cn";
import { Badge } from "@/components/ui";
import { apiFetch } from "@/lib/api";

type NotificationItem = {
  id: string;
  title: string;
  body: string;
  read_at: string | null;
  created_at: string;
  event_type: string;
};

export function NotificationBell() {
  const t = useTranslations("notifications");
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [unread, setUnread] = useState(0);
  const ref = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    const res = await apiFetch<NotificationItem[]>("/notifications?limit=10");
    if (res.success) {
      setItems(res.data || []);
      setUnread((res.meta?.unread_count as number) || 0);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 60_000);
    return () => clearInterval(interval);
  }, [load]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const markRead = async (id: string) => {
    await apiFetch(`/notifications/${id}/read`, { method: "PATCH" });
    load();
  };

  const markAllRead = async () => {
    await apiFetch("/notifications/read-all", { method: "POST" });
    load();
  };

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={cn(
          "relative p-2 rounded-lg border border-border bg-surface dark:bg-card",
          "text-foreground-secondary hover:text-foreground hover:bg-muted",
          "transition-all duration-fast",
        )}
        aria-label={t("title")}
        aria-expanded={open}
      >
        <svg className="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.75}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
        {unread > 0 && (
          <span className="absolute -top-1 -right-1 bg-danger text-white text-[10px] font-medium rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 bg-card border border-border rounded-xl shadow-lg z-50 animate-slide-up overflow-hidden">
          <div className="flex justify-between items-center px-4 py-3 border-b border-border">
            <span className="font-semibold text-small">{t("title")}</span>
            {unread > 0 && (
              <button
                type="button"
                onClick={markAllRead}
                className="text-caption text-naqsh-accent hover:underline transition-colors"
              >
                {t("markAllRead")}
              </button>
            )}
          </div>
          <div className="max-h-72 overflow-y-auto scrollbar-thin">
            {items.length === 0 ? (
              <p className="p-6 text-small text-muted-foreground text-center">{t("empty")}</p>
            ) : (
              items.map((n) => (
                <button
                  key={n.id}
                  type="button"
                  onClick={() => !n.read_at && markRead(n.id)}
                  className={cn(
                    "w-full text-left px-4 py-3 border-b border-border last:border-0",
                    "hover:bg-muted/60 transition-colors duration-fast",
                    !n.read_at && "bg-info-bg/50",
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-small font-medium text-foreground">{n.title}</p>
                    {!n.read_at && <Badge variant="info" className="shrink-0">New</Badge>}
                  </div>
                  <p className="text-caption text-muted-foreground mt-0.5 line-clamp-2">{n.body}</p>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
