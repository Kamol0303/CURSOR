"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

type Props = {
  onClose: () => void;
  onSaved: () => void;
};

type OnboardResult = {
  center: { id: string; name: string };
  director_username: string;
  temporary_password: string;
};

export function CenterOnboardModal({ onClose, onSaved }: Props) {
  const t = useTranslations("centers");
  const [name, setName] = useState("");
  const [directorUsername, setDirectorUsername] = useState("");
  const [directorFullName, setDirectorFullName] = useState("");
  const [directorEmail, setDirectorEmail] = useState("");
  const [directorPhone, setDirectorPhone] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [result, setResult] = useState<OnboardResult | null>(null);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const res = await apiFetch<OnboardResult>("/centers/onboard", {
        method: "POST",
        body: JSON.stringify({
          name,
          director_username: directorUsername.trim(),
          director_full_name: directorFullName.trim(),
          director_email: directorEmail || null,
          director_phone: directorPhone || null,
        }),
      });
      if (!res.success || !res.data) {
        setError(t("onboardError"));
        return;
      }
      setResult(res.data);
      onSaved();
    } catch {
      setError(t("onboardError"));
    } finally {
      setSaving(false);
    }
  };

  if (result) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
        <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 space-y-4">
          <h3 className="text-lg font-semibold text-naqsh-primary">{t("onboardSuccessTitle")}</h3>
          <p className="text-sm text-gray-600">{t("onboardSuccessHint")}</p>
          <dl className="text-sm space-y-2 bg-gray-50 rounded-lg p-4">
            <div>
              <dt className="text-gray-500">{t("name")}</dt>
              <dd className="font-medium">{result.center.name}</dd>
            </div>
            <div>
              <dt className="text-gray-500">{t("onboardDirectorLogin")}</dt>
              <dd className="font-mono">{result.director_username}</dd>
            </div>
            <div>
              <dt className="text-gray-500">{t("onboardTempPassword")}</dt>
              <dd className="font-mono break-all text-naqsh-primary">{result.temporary_password}</dd>
            </div>
          </dl>
          <button
            type="button"
            onClick={onClose}
            className="w-full py-2 rounded-lg bg-naqsh-primary text-white"
          >
            {t("onboardDone")}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <form onSubmit={submit} className="p-6 space-y-4">
          <h3 className="text-lg font-semibold text-naqsh-primary">{t("onboardTitle")}</h3>
          <p className="text-sm text-gray-500">{t("onboardSubtitle")}</p>
          <div>
            <label className="block text-sm font-medium mb-1">{t("name")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t("onboardDirectorLogin")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2 font-mono"
              value={directorUsername}
              onChange={(e) => setDirectorUsername(e.target.value)}
              pattern="[a-zA-Z0-9._-]{3,100}"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t("director")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2"
              value={directorFullName}
              onChange={(e) => setDirectorFullName(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">{t("email")}</label>
              <input
                type="email"
                className="w-full border rounded-lg px-3 py-2"
                value={directorEmail}
                onChange={(e) => setDirectorEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">{t("phone")}</label>
              <input
                className="w-full border rounded-lg px-3 py-2"
                value={directorPhone}
                onChange={(e) => setDirectorPhone(e.target.value)}
              />
            </div>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-2 justify-end pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg border">
              {t("cancel")}
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 rounded-lg bg-naqsh-primary text-white disabled:opacity-50"
            >
              {saving ? t("saving") : t("onboardSubmit")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
