"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

export type RecipientOption = {
  id: string;
  display_name: string;
  role: string;
  username: string | null;
};

type MessageRecipientSelectProps = {
  value: RecipientOption | null;
  onChange: (recipient: RecipientOption | null) => void;
  placeholder?: string;
};

export function MessageRecipientSelect({ value, onChange, placeholder }: MessageRecipientSelectProps) {
  const t = useTranslations("messages");
  const [search, setSearch] = useState("");
  const [options, setOptions] = useState<RecipientOption[]>([]);
  const [loading, setLoading] = useState(false);

  const loadOptions = useCallback(async (query: string) => {
    setLoading(true);
    const params = query.trim() ? `?search=${encodeURIComponent(query.trim())}` : "";
    const res = await apiFetch<RecipientOption[]>(`/messages/recipients${params}`);
    setLoading(false);
    if (res.success && Array.isArray(res.data)) {
      setOptions(res.data);
    }
  }, []);

  useEffect(() => {
    if (value) return;
    const timer = setTimeout(() => {
      void loadOptions(search);
    }, 250);
    return () => clearTimeout(timer);
  }, [search, loadOptions, value]);

  if (value) {
    return (
      <div className="rounded-lg bg-blue-50 border border-blue-200 p-3 text-sm flex justify-between items-center">
        <span>
          {value.display_name}
          <span className="text-gray-500 ml-2 text-xs">{t(`roles.${value.role}` as "roles.teacher")}</span>
        </span>
        <button
          type="button"
          className="text-xs text-blue-700 underline"
          onClick={() => {
            onChange(null);
            setSearch("");
          }}
        >
          {t("clearRecipient")}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <input
        type="text"
        className="w-full border rounded-lg px-3 py-2"
        placeholder={placeholder || t("searchRecipient")}
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      {loading && <p className="text-xs text-gray-400">{t("searching")}</p>}
      {options.length > 0 && (
        <ul className="border rounded-lg divide-y max-h-48 overflow-y-auto">
          {options.map((option) => (
            <li key={option.id}>
              <button
                type="button"
                className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50"
                onClick={() => {
                  onChange(option);
                  setSearch("");
                  setOptions([]);
                }}
              >
                <span className="font-medium">{option.display_name}</span>
                <span className="text-gray-500 ml-2 text-xs">
                  {t(`roles.${option.role}` as "roles.teacher")}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
