"use client";

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
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
        <h3 className="text-lg font-semibold text-naqsh-primary">{title}</h3>
        <div className="rounded-lg bg-amber-50 border border-amber-200 p-4 space-y-2 text-sm">
          <p>
            <span className="text-gray-600">Login: </span>
            <code className="font-mono">{login}</code>
          </p>
          <p>
            <span className="text-gray-600">Parol: </span>
            <code className="font-mono">{temporaryPassword}</code>
          </p>
        </div>
        {smsSent && smsHint && <p className="text-xs text-green-700">{smsHint}</p>}
        <button type="button" onClick={onClose} className="w-full px-4 py-2 bg-naqsh-primary text-white rounded-lg">
          OK
        </button>
      </div>
    </div>
  );
}
