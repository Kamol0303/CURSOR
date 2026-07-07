"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";
import {
  Alert,
  Button,
  FormActions,
  FormField,
  FormGrid,
  Input,
  Label,
  Modal,
  Select,
  Textarea,
} from "@/components/ui";

type Center = {
  id: string;
  name: string;
  stir: string | null;
  director_name: string | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  license_number: string | null;
  license_expiry: string | null;
  center_type: string;
  is_active: boolean;
  mahalla_id: string | null;
};

type Region = { id: string; name_uz: string };
type Mahalla = { id: string; region_id: string; name_uz: string };

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
  const [licenseExpiry, setLicenseExpiry] = useState(
    center?.license_expiry ? center.license_expiry.slice(0, 10) : "",
  );
  const [centerType, setCenterType] = useState(center?.center_type || "private");
  const [isActive, setIsActive] = useState(center?.is_active ?? true);
  const [regions, setRegions] = useState<Region[]>([]);
  const [mahallas, setMahallas] = useState<Mahalla[]>([]);
  const [regionId, setRegionId] = useState("");
  const [mahallaId, setMahallaId] = useState(center?.mahalla_id || "");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    apiFetch<Region[]>("/regions").then((res) => {
      if (res.success && Array.isArray(res.data)) setRegions(res.data);
    });
  }, []);

  useEffect(() => {
    if (!regionId) {
      setMahallas([]);
      return;
    }
    apiFetch<Mahalla[]>(`/mahallas?region_id=${regionId}`).then((res) => {
      if (res.success && Array.isArray(res.data)) setMahallas(res.data);
    });
  }, [regionId]);

  useEffect(() => {
    if (!center?.mahalla_id || regions.length === 0) return;
    apiFetch<Mahalla[]>("/mahallas").then((res) => {
      if (!res.success || !Array.isArray(res.data)) return;
      const match = res.data.find((m) => m.id === center.mahalla_id);
      if (match) {
        setRegionId(match.region_id);
        setMahallaId(match.id);
      }
    });
  }, [center?.mahalla_id, regions.length]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const path = isEdit ? `/centers/${center!.id}` : "/centers";
      const method = isEdit ? "PATCH" : "POST";
      const shared = {
        name,
        stir: stir || null,
        director_name: directorName || null,
        phone: phone || null,
        email: email || null,
        address: address || null,
        license_number: licenseNumber || null,
        license_expiry: licenseExpiry ? `${licenseExpiry}T00:00:00Z` : null,
        center_type: centerType,
        mahalla_id: mahallaId || null,
      };
      const body = isEdit ? { ...shared, is_active: isActive } : shared;
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
    <Modal onClose={onClose} title={isEdit ? t("editTitle") : t("addTitle")}>
      <form onSubmit={submit} className="space-y-4">
        <FormField>
          <Label>{t("name")}</Label>
          <Input value={name} onChange={(e) => setName(e.target.value)} required />
        </FormField>
        <FormGrid>
          <FormField>
            <Label>{t("stir")}</Label>
            <Input
              className="font-mono"
              value={stir}
              onChange={(e) => setStir(e.target.value)}
              pattern="\d{9}"
              placeholder="9 raqam"
            />
          </FormField>
          <FormField>
            <Label>{t("type")}</Label>
            <Select value={centerType} onChange={(e) => setCenterType(e.target.value)}>
              <option value="private">{t("typePrivate")}</option>
              <option value="public">{t("typePublic")}</option>
            </Select>
          </FormField>
        </FormGrid>
        <FormGrid>
          <FormField>
            <Label>{t("region")}</Label>
            <Select
              value={regionId}
              onChange={(e) => {
                setRegionId(e.target.value);
                setMahallaId("");
              }}
            >
              <option value="">{t("selectRegion")}</option>
              {regions.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name_uz}
                </option>
              ))}
            </Select>
          </FormField>
          <FormField>
            <Label>{t("mahalla")}</Label>
            <Select
              value={mahallaId}
              onChange={(e) => setMahallaId(e.target.value)}
              disabled={!regionId}
            >
              <option value="">{t("selectMahalla")}</option>
              {mahallas.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name_uz}
                </option>
              ))}
            </Select>
          </FormField>
        </FormGrid>
        <FormField>
          <Label>{t("director")}</Label>
          <Input value={directorName} onChange={(e) => setDirectorName(e.target.value)} />
        </FormField>
        <FormGrid>
          <FormField>
            <Label>{t("phone")}</Label>
            <Input value={phone} onChange={(e) => setPhone(e.target.value)} />
          </FormField>
          <FormField>
            <Label>{t("email")}</Label>
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </FormField>
        </FormGrid>
        <FormField>
          <Label>{t("address")}</Label>
          <Textarea rows={2} value={address} onChange={(e) => setAddress(e.target.value)} />
        </FormField>
        <FormGrid>
          <FormField>
            <Label>{t("license")}</Label>
            <Input value={licenseNumber} onChange={(e) => setLicenseNumber(e.target.value)} />
          </FormField>
          <FormField>
            <Label>{t("licenseExpiry")}</Label>
            <Input
              type="date"
              value={licenseExpiry}
              onChange={(e) => setLicenseExpiry(e.target.value)}
            />
          </FormField>
        </FormGrid>
        {isEdit && (
          <Label className="flex items-center gap-2 mb-0 cursor-pointer">
            <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
            {t("active")}
          </Label>
        )}
        {error && <Alert variant="danger">{error}</Alert>}
        <FormActions>
          <Button type="button" variant="secondary" onClick={onClose}>
            {t("cancel")}
          </Button>
          <Button type="submit" loading={saving}>
            {saving ? t("saving") : t("save")}
          </Button>
        </FormActions>
      </form>
    </Modal>
  );
}
