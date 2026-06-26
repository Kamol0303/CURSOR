"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

type Message = {
  id: string;
  title: string;
  body: string;
  is_read: boolean;
  sent_at: string;
  sender_name: string | null;
  recipient_name: string | null;
};

export default function MessagesPage() {
  const t = useTranslations("messages");
  const [box, setBox] = useState<"inbox" | "sent">("inbox");
  const [items, setItems] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [recipientId, setRecipientId] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");

  const load = useCallback(() => {
    setLoading(true);
    apiFetch<Message[]>(`/messages?box=${box}`)
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setItems(res.data);
      })
      .finally(() => setLoading(false));
  }, [box]);

  useEffect(() => {
    load();
  }, [load]);

  const send = async (e: React.FormEvent) => {
    e.preventDefault();
    await apiFetch("/messages", {
      method: "POST",
      body: JSON.stringify({ recipient_id: recipientId, title, body }),
    });
    setTitle("");
    setBody("");
    setBox("sent");
    load();
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
        <div className="flex gap-2 text-sm">
          <button
            type="button"
            onClick={() => setBox("inbox")}
            className={`px-3 py-1 rounded-lg ${box === "inbox" ? "bg-naqsh-primary text-white" : "border"}`}
          >
            {t("inbox")}
          </button>
          <button
            type="button"
            onClick={() => setBox("sent")}
            className={`px-3 py-1 rounded-lg ${box === "sent" ? "bg-naqsh-primary text-white" : "border"}`}
          >
            {t("sent")}
          </button>
        </div>
      </div>

      <form onSubmit={send} className="bg-white p-4 rounded-xl border space-y-3">
        <h3 className="font-semibold text-naqsh-primary">{t("compose")}</h3>
        <input
          className="w-full border rounded-lg px-3 py-2 font-mono text-sm"
          placeholder={t("recipientId")}
          value={recipientId}
          onChange={(e) => setRecipientId(e.target.value)}
          required
        />
        <input className="w-full border rounded-lg px-3 py-2" placeholder={t("subject")} value={title} onChange={(e) => setTitle(e.target.value)} required />
        <textarea className="w-full border rounded-lg px-3 py-2" rows={3} placeholder={t("body")} value={body} onChange={(e) => setBody(e.target.value)} required />
        <button type="submit" className="px-4 py-2 bg-naqsh-primary text-white rounded-lg">{t("send")}</button>
      </form>

      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : (
        <div className="space-y-2">
          {items.map((m) => (
            <div key={m.id} className={`bg-white border rounded-xl p-4 ${!m.is_read && box === "inbox" ? "border-naqsh-accent" : ""}`}>
              <div className="flex justify-between text-sm mb-1">
                <span className="font-semibold">{m.title}</span>
                <span className="text-gray-400">{new Date(m.sent_at).toLocaleString()}</span>
              </div>
              <p className="text-sm text-gray-600 mb-2">{m.body}</p>
              <p className="text-xs text-gray-400">
                {box === "inbox" ? m.sender_name : m.recipient_name}
              </p>
            </div>
          ))}
          {items.length === 0 && <p className="text-gray-400">{t("empty")}</p>}
        </div>
      )}
    </div>
  );
}
