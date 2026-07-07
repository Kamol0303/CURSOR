/**
 * API base URL resolution:
 * - Staging/prod behind nginx: NEXT_PUBLIC_API_URL = https://your-host (or empty + /api rewrite)
 * - Local dev (docker): NEXT_PUBLIC_API_URL = http://localhost:8000 (REQUIRED for browser)
 */
export function getApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
  if (configured) {
    return configured;
  }
  // Same-origin when nginx or Next.js rewrites proxy /api/*
  return "";
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("tmb_access_token");
}

export async function apiFetch<T = unknown>(
  path: string,
  options: RequestInit = {},
): Promise<{ success: boolean; data: T; meta?: Record<string, unknown>; error?: { code: string } }> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${getApiBaseUrl()}/api/v1${path}`, {
      ...options,
      headers,
      credentials: "include",
    });
  } catch {
    return {
      success: false,
      data: null as T,
      error: { code: "NETWORK_ERROR" },
    };
  }

  try {
    return await res.json();
  } catch {
    return {
      success: false,
      data: null as T,
      error: { code: res.ok ? "PARSE_ERROR" : "HTTP_ERROR" },
    };
  }
}

export async function getMe() {
  return apiFetch<{
    id: string;
    username: string;
    role: string;
    center_id: string | null;
    permissions: string[];
    locale_preference: string;
    mfa_enabled: boolean;
    mfa_required?: boolean;
    mfa_configured?: boolean;
    must_change_password?: boolean;
    center_profile_completed?: boolean | null;
  }>("/auth/me");
}

export async function getDashboardKpis() {
  return apiFetch<{
    total_centers: number;
    total_students: number;
    active_students: number;
    total_teachers: number;
    total_subjects: number;
    total_courses: number;
    active_centers: number;
    new_registrations_month: number;
    license_expiring_30_days: number;
    monthly_revenue: number;
    debtors_count: number;
    kpis: { key: string; value: number }[];
    daily_stats: { label: string; value: number }[];
    weekly_stats: { label: string; value: number }[];
    monthly_stats: { label: string; value: number }[];
  }>("/dashboard/kpis");
}

export async function getOperatorSummary() {
  return apiFetch<{
    active_centers: number;
    total_teachers: number;
    total_students: number;
    certificates_ytd: number;
    total_courses: number;
    certificates_by_center: {
      center_id: string;
      center_name: string;
      certificate_count: number;
    }[];
    certificates_by_center_total: number;
    student_trend: { label: string; value: number; is_forecast?: boolean }[];
    certificate_trend: { label: string; value: number; is_forecast?: boolean }[];
  }>("/dashboard/operator-summary");
}

export async function listCenters(page = 1) {
  return apiFetch<Record<string, unknown>[]>("/centers?page=" + page);
}

export async function listStudents(page = 1) {
  return apiFetch<Record<string, unknown>[]>("/students?page=" + page);
}

export async function listTeachers(page = 1) {
  return apiFetch<Record<string, unknown>[]>("/teachers?page=" + page);
}

export async function getAnalyticsInsights() {
  return apiFetch<{
    predictions: Record<string, unknown>[];
    last_run: Record<string, unknown> | null;
  }>("/analytics/insights");
}

export async function getNotifications(limit = 10) {
  return apiFetch<Record<string, unknown>[]>("/notifications?limit=" + limit);
}

export async function downloadFile(fileId: string, fileName = "download") {
  const token = getToken();
  const res = await fetch(`${getApiBaseUrl()}/api/v1/files/${fileId}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    credentials: "include",
  });
  if (!res.ok) return false;
  const blob = await res.blob();
  const disposition = res.headers.get("content-disposition");
  const match = disposition?.match(/filename="?([^";]+)"?/i);
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = match?.[1] || fileName;
  a.click();
  URL.revokeObjectURL(a.href);
  return true;
}

function parseApiErrorCode(body: unknown, status: number): string {
  if (body && typeof body === "object") {
    const record = body as Record<string, unknown>;
    const detail = record.detail;
    if (detail && typeof detail === "object" && "code" in detail) {
      return String((detail as { code: string }).code);
    }
    const error = record.error;
    if (error && typeof error === "object" && "code" in error) {
      return String((error as { code: string }).code);
    }
  }
  if (status === 403) return "FORBIDDEN";
  return "HTTP_ERROR";
}

export async function downloadRatingsReport(
  format: "pdf" | "excel",
  locale?: string,
): Promise<{ ok: true } | { ok: false; code: string }> {
  const token = getToken();
  const params = new URLSearchParams({ format: format === "excel" ? "excel" : "pdf" });
  if (locale) params.set("locale", locale);

  let res: Response;
  try {
    res = await fetch(`${getApiBaseUrl()}/api/v1/reports/ratings?${params}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: "include",
    });
  } catch {
    return { ok: false, code: "NETWORK_ERROR" };
  }

  if (!res.ok) {
    try {
      const body = await res.json();
      return { ok: false, code: parseApiErrorCode(body, res.status) };
    } catch {
      return { ok: false, code: parseApiErrorCode(null, res.status) };
    }
  }

  const contentType = res.headers.get("content-type") || "";
  if (!contentType.includes("pdf") && !contentType.includes("spreadsheet") && !contentType.includes("excel")) {
    return { ok: false, code: "INVALID_RESPONSE" };
  }

  const blob = await res.blob();
  const disposition = res.headers.get("content-disposition");
  const match = disposition?.match(/filename="?([^";]+)"?/i);
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = match?.[1] || `tmb-ratings.${format === "excel" ? "xlsx" : "pdf"}`;
  a.click();
  URL.revokeObjectURL(a.href);
  return { ok: true };
}

export async function uploadFile(
  file: File,
  params: { center_id: string; owner_type: string; owner_id: string },
) {
  const token = getToken();
  const form = new FormData();
  form.append("file", file);
  form.append("center_id", params.center_id);
  form.append("owner_type", params.owner_type);
  form.append("owner_id", params.owner_id);

  const res = await fetch(`${getApiBaseUrl()}/api/v1/files`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    credentials: "include",
    body: form,
  });

  try {
    return await res.json();
  } catch {
    return { success: false, data: null, error: { code: "PARSE_ERROR" } };
  }
}
