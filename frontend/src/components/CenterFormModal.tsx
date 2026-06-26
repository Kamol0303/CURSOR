"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

type Center = {
  id: string;
  name: string;
  stir: string | null;
  director_name: string | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  license_number: string | null;
  center_type: string;
  is_active: boolean;
};

type Props = {
  center?: Center | null;
  onClose: () => void;
  onSaved: () => void;
};

export function CenterFormModal({ center, onClose, onSaved }: Props) {
  const t = useTranslations("centers");
  const isEdit = Boolean(center?.id);
  const [name, setName] = useState(center?.name || "");
  const [stir, setStir] = useState(center?.stir || "");
  const [directorName, setDirectorName] = useState(center?.director_name || "");
  const [phone, setPhone] = useState(center?.phone || "");
  const [email, setEmail] = useState(center?.email || "");
  const [address, setAddress] = useState(center?.address || "");
  const [licenseNumber, setLicenseNumber] = useState(center?.license_number || "");
  const [centerType, setCenterType] = useState(center?.center_type || "private");
  const [isActive, setIsActive] = useState(center?.is_active ?? true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

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
      const path = isEdit ? `/centers/${center!.id}` : "/centers";
      const method = isEdit ? "PATCH" : "POST";
      const body = isEdit
        ? {
            name,
            stir: stir || null,
            director_name: directorName || null,
            phone: phone || null,
            email: email || null,
            address: address || null,
            license_number: licenseNumber || null,
            center_type: centerType,
            is_active: isActive,
          }
        : {
            name,
            stir: stir || null,
            director_name: directorName || null,
            phone: phone || null,
            email: email || null,
            address: address || null,
            license_number: licenseNumber || null,
            center_type: centerType,
          };
      const res = await apiFetch(path, { method, body: JSON.stringify(body) });
      if (!res.success) {
        setError(t("saveError"));
        return;
      }
      onSaved();
      onClose();
    } catch {
      setError(t("saveError"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <form onSubmit={submit} className="p-6 space-y-4">
          <h3 className="text-lg font-semibold text-naqsh-primary">
            {isEdit ? t("editTitle") : t("addTitle")}
          </h3>
          <div>
            <label className="block text-sm font-medium mb-1">{t("name")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">{t("stir")}</label>
              <input
                className="w-full border rounded-lg px-3 py-2 font-mono"
                value={stir}
                onChange={(e) => setStir(e.target.value)}
                pattern="\d{9}"
                placeholder="9 raqam"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">{t("type")}</label>
              <select
                className="w-full border rounded-lg px-3 py-2"
                value={centerType}
                onChange={(e) => setCenterType(e.target.value)}
              >
                <option value="private">{t("typePrivate")}</option>
                <option value="public">{t("typePublic")}</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t("director")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2"
              value={directorName}
              onChange={(e) => setDirectorName(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">{t("phone")}</label>
              <input className="w-full border rounded-lg px-3 py-2" value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">{t("email")}</label>
              <input
                type="email"
                className="w-full border rounded-lg px-3 py-2"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t("address")}</label>
            <textarea className="w-full border rounded-lg px-3 py-2" rows={2} value={address} onChange={(e) => setAddress(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t("license")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2"
              value={licenseNumber}
              onChange={(e) => setLicenseNumber(e.target.value)}
            />
          </div>
          {isEdit && (
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
              {t("active")}
            </label>
          )}
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-2 justify-end pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg border">
              {t("cancel")}
            </button>
            <button type="submit" disabled={saving} className="px-4 py-2 rounded-lg bg-naqsh-primary text-white disabled:opacity-50">
              {saving ? t("saving") : t("save")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
