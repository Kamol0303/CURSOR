"use client";

import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { TmbLogo } from "@/components/TmbLogo";

const HOUR12_KEY = "tmb_clock_hour12";

function pad(n: number) {
  return String(n).padStart(2, "0");
}

function toBcp47(locale: string): string {
  const map: Record<string, string> = { uz: "uz-UZ", ru: "ru-RU", en: "en-US" };
  return map[locale] ?? "uz-UZ";
}

function readHour12Preference(): boolean {
  if (typeof window === "undefined") return true;
  const stored = localStorage.getItem(HOUR12_KEY);
  if (stored === "24") return false;
  if (stored === "12") return true;
  return true;
}

type DigitalClockProps = {
  variant?: "full" | "compact";
  className?: string;
};

export function DigitalClock({ variant = "full", className = "" }: DigitalClockProps) {
  const t = useTranslations("clock");
  const locale = useLocale();
  const bcp47 = toBcp47(locale);

  const [hour12, setHour12] = useState(true);
  const [timeText, setTimeText] = useState("00:00:00");
  const [ampmText, setAmpmText] = useState("");
  const [dateText, setDateText] = useState("");
  const [dayText, setDayText] = useState("");

  useEffect(() => {
    setHour12(readHour12Preference());
  }, []);

  const tick = useCallback(() => {
    const now = new Date();
    let h = now.getHours();
    const m = now.getMinutes();
    const s = now.getSeconds();
    let ampm = "";

    if (hour12) {
      ampm = h >= 12 ? t("pm") : t("am");
      h = h % 12 || 12;
    }

    setTimeText(`${pad(h)}:${pad(m)}:${pad(s)}`);
    setAmpmText(ampm);
    setDateText(
      now.toLocaleDateString(bcp47, { day: "numeric", month: "long", year: "numeric" }),
    );
    setDayText(now.toLocaleDateString(bcp47, { weekday: "long" }));
  }, [bcp47, hour12, t]);

  useEffect(() => {
    tick();
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, [tick]);

  const select12 = () => {
    setHour12(true);
    localStorage.setItem(HOUR12_KEY, "12");
  };

  const select24 = () => {
    setHour12(false);
    localStorage.setItem(HOUR12_KEY, "24");
  };

  if (variant === "compact") {
    return (
      <div
        className={`hidden sm:flex flex-col items-end leading-tight ${className}`}
        aria-live="polite"
        aria-label={t("title")}
      >
        <div className="flex items-baseline gap-1.5">
          <span className="font-mono text-sm font-semibold tabular-nums text-naqsh-primary dark:text-naqsh-accent tracking-wide">
            {timeText}
          </span>
          {hour12 && ampmText && (
            <span className="text-[10px] font-medium uppercase text-gray-500 dark:text-gray-400">
              {ampmText}
            </span>
          )}
        </div>
        <span className="text-[10px] text-gray-400 dark:text-gray-500">{dayText}</span>
      </div>
    );
  }

  return (
    <section
      className={`rounded-2xl border border-naqsh-primary/15 dark:border-naqsh-accent/20 bg-gradient-to-br from-[#1b4d3e] to-[#163328] text-white shadow-lg shadow-naqsh-primary/20 p-5 sm:p-6 flex flex-col gap-5 ${className}`}
      aria-live="polite"
    >
      <div className="flex flex-wrap justify-between items-center gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="shrink-0 p-2.5 rounded-xl bg-naqsh-accent/90 text-white">
            <TmbLogo className="w-7 h-7" />
          </div>
          <div className="min-w-0">
            <div className="font-semibold text-base truncate">{t("title")}</div>
            <div className="text-xs text-white/60">{t("subtitle")}</div>
          </div>
        </div>
        <div
          className="flex items-center gap-1 bg-white/5 rounded-full p-1"
          role="group"
          aria-label={t("formatToggle")}
        >
          <button
            type="button"
            onClick={select12}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
              hour12 ? "bg-white/15 text-naqsh-accent" : "text-white/70 hover:text-white"
            }`}
          >
            {t("hour12")}
          </button>
          <button
            type="button"
            onClick={select24}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
              !hour12 ? "bg-white/15 text-naqsh-accent" : "text-white/70 hover:text-white"
            }`}
          >
            {t("hour24")}
          </button>
        </div>
      </div>

      <div className="flex flex-wrap justify-between items-end gap-4">
        <div className="flex items-baseline gap-2 min-w-0">
          <div className="font-mono text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-[0.12em] tabular-nums text-white">
            {timeText}
          </div>
          {hour12 && (
            <span className="text-base sm:text-lg font-medium text-naqsh-accent uppercase">
              {ampmText}
            </span>
          )}
        </div>
        <div className="text-right text-sm text-white/70">
          <div>{dateText}</div>
          <div className="font-medium text-white/90">{dayText}</div>
        </div>
      </div>

      <div className="flex justify-between text-[11px] text-white/50 border-t border-white/10 pt-3">
        <span>{t("autoUpdate")}</span>
        <span>{t("localTime")}</span>
      </div>
    </section>
  );
}
