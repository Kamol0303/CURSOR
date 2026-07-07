"use client";

import { Alert, Button, Modal } from "@/components/ui";

type Props = {
  title: string;
  login: string;
  temporaryPassword: string;
  smsSent?: boolean;
  smsHint?: string;
  onClose: () => void;
};

export function CredentialsRevealModal({
  title,
  login,
  temporaryPassword,
  smsSent,
  smsHint,
  onClose,
}: Props) {
  return (
    <Modal onClose={onClose} title={title} size="sm">
      <Alert variant="warning" className="space-y-2">
        <p>
          <span className="text-muted-foreground">Login: </span>
          <code className="font-mono">{login}</code>
        </p>
        <p>
          <span className="text-muted-foreground">Parol: </span>
          <code className="font-mono">{temporaryPassword}</code>
        </p>
      </Alert>
      {smsSent && smsHint && <Alert variant="success">{smsHint}</Alert>}
      <Button type="button" onClick={onClose} className="w-full mt-4">
        OK
      </Button>
    </Modal>
  );
}
