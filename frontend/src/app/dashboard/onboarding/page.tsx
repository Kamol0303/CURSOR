"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { ChangePasswordForm } from "@/components/ChangePasswordForm";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function OnboardingPage() {
  const t = useTranslations("onboarding");
  const tc = useTranslations("centers");
  const router = useRouter();
  const { user, refresh, mustChangePassword, centerProfileCompleted } = useAuth();

  const [stir, setStir] = useState("");
  const [directorName, setDirectorName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [address, setAddress] = useState("");
  const [licenseNumber, setLicenseNumber] = useState("");
  const [centerType, setCenterType] = useState("private");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [step, setStep] = useState<"password" | "profile">("password");

  useEffect(() => {
    if (user && user.role !== "center_director") {
      router.replace("/dashboard");
    }
  }, [user, router]);

  useEffect(() => {
    if (!mustChangePassword) {
      setStep("profile");
    }
  }, [mustChangePassword]);

  useEffect(() => {
    if (user?.role === "center_director" && !mustChangePassword && centerProfileCompleted) {
      router.replace("/dashboard");
    }
  }, [user, mustChangePassword, centerProfileCompleted, router]);

  const submitProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const res = await apiFetch("/centers/onboarding/complete", {
        method: "POST",
        body: JSON.stringify({
          stir,
          director_name: directorName,
          phone,
          email: email || null,
          address,
          license_number: licenseNumber || null,
          center_type: centerType,
        }),
      });
      if (!res.success) {
        setError(tc("saveError"));
        return;
      }
      await refresh();
      router.replace("/dashboard");
    } catch {
      setError(tc("saveError"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{t("title")}</h2>
        <p className="text-gray-500 mt-1">{t("subtitle")}</p>
      </div>

      <div className="flex gap-2 text-sm">
        <span className={step === "password" ? "font-semibold text-naqsh-primary" : "text-gray-400"}>
          1. {t("stepPassword")}
        </span>
        <span className="text-gray-300">→</span>
        <span className={step === "profile" ? "font-semibold text-naqsh-primary" : "text-gray-400"}>
          2. {t("stepProfile")}
        </span>
      </div>

      {step === "password" && mustChangePassword && (
        <div className="bg-white rounded-xl border p-6">
          <h3 className="font-semibold mb-4">{t("changePasswordTitle")}</h3>
          <ChangePasswordForm
            onSuccess={async () => {
              await refresh();
              setStep("profile");
            }}
          />
        </div>
      )}

      {step === "profile" && (
        <form onSubmit={submitProfile} className="bg-white rounded-xl border p-6 space-y-4">
          <h3 className="font-semibold">{t("profileTitle")}</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">{tc("stir")}</label>
              <input
                className="w-full border rounded-lg px-3 py-2 font-mono"
                value={stir}
                onChange={(e) => setStir(e.target.value)}
                pattern="\d{9}"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">{tc("type")}</label>
              <select
                className="w-full border rounded-lg px-3 py-2"
                value={centerType}
                onChange={(e) => setCenterType(e.target.value)}
              >
                <option value="private">{tc("typePrivate")}</option>
                <option value="public">{tc("typePublic")}</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{tc("director")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2"
              value={directorName}
              onChange={(e) => setDirectorName(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">{tc("phone")}</label>
              <input
                className="w-full border rounded-lg px-3 py-2"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">{tc("email")}</label>
              <input
                type="email"
                className="w-full border rounded-lg px-3 py-2"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{tc("address")}</label>
            <textarea
              className="w-full border rounded-lg px-3 py-2"
              rows={2}
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{tc("license")}</label>
            <input
              className="w-full border rounded-lg px-3 py-2"
              value={licenseNumber}
              onChange={(e) => setLicenseNumber(e.target.value)}
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            disabled={saving}
            className="w-full py-2.5 rounded-lg bg-naqsh-primary text-white disabled:opacity-50"
          >
            {saving ? tc("saving") : t("complete")}
          </button>
        </form>
      )}
    </div>
  );
}
