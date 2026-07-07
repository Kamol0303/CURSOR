"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";
import { MessageRecipientSelect, type RecipientOption } from "@/components/MessageRecipientSelect";
import { PermissionGate } from "@/components/PermissionGate";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardDescription,
  CardTitle,
  EmptyState,
  Input,
  PageHeader,
  PageSection,
  Textarea,
  CardSkeleton,
} from "@/components/ui";
import { cn } from "@/lib/cn";

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
  const [recipient, setRecipient] = useState<RecipientOption | null>(null);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [error, setError] = useState<string | null>(null);

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
    if (!recipient) return;
    setError(null);
    const res = await apiFetch("/messages", {
      method: "POST",
      body: JSON.stringify({ recipient_id: recipient.id, title, body }),
    });
    if (!res.success) {
      const code = (res as { error?: { code?: string } }).error?.code || "UNKNOWN";
      setError(t(`errors.${code}` as "errors.UNKNOWN"));
      return;
    }
    setTitle("");
    setBody("");
    setRecipient(null);
    setBox("sent");
    load();
  };

  return (
    <PageSection>
      <PageHeader
        title={t("title")}
        actions={
          <div className="flex gap-2">
            <Button
              variant={box === "inbox" ? "primary" : "outline"}
              size="sm"
              onClick={() => setBox("inbox")}
            >
              {t("inbox")}
            </Button>
            <Button
              variant={box === "sent" ? "primary" : "outline"}
              size="sm"
              onClick={() => setBox("sent")}
            >
              {t("sent")}
            </Button>
          </div>
        }
      />

      <PermissionGate permission="messages.send">
        <Card>
          <CardBody>
            <form onSubmit={send} className="space-y-3">
              <CardTitle>{t("compose")}</CardTitle>
              <CardDescription>{t("centerOnlyHint")}</CardDescription>
              <MessageRecipientSelect value={recipient} onChange={setRecipient} />
              <Input
                placeholder={t("subject")}
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
              <Textarea
                rows={3}
                placeholder={t("body")}
                value={body}
                onChange={(e) => setBody(e.target.value)}
                required
              />
              {error && <Alert variant="danger">{error}</Alert>}
              <Button type="submit" disabled={!recipient}>
                {t("send")}
              </Button>
            </form>
          </CardBody>
        </Card>
      </PermissionGate>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : items.length === 0 ? (
        <EmptyState title={t("empty")} />
      ) : (
        <div className="space-y-2">
          {items.map((m) => (
            <Card
              key={m.id}
              className={cn(!m.is_read && box === "inbox" && "border-naqsh-accent")}
            >
              <CardBody>
                <div className="flex justify-between text-small mb-1">
                  <span className="font-semibold">{m.title}</span>
                  <span className="text-muted-foreground">{new Date(m.sent_at).toLocaleString()}</span>
                </div>
                <p className="text-small text-muted-foreground mb-2">{m.body}</p>
                <p className="text-caption text-muted-foreground">
                  {box === "inbox" ? m.sender_name : m.recipient_name}
                </p>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </PageSection>
  );
}
