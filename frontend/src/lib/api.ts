const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

  const res = await fetch(`${API_URL}/api/v1${path}`, {
    ...options,
    headers,
    credentials: "include",
  });
  return res.json();
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
  }>("/auth/me");
}

export async function getDashboardKpis() {
  return apiFetch<{
    total_centers: number;
    total_students: number;
    total_teachers: number;
    total_subjects: number;
    active_centers: number;
    new_registrations_month: number;
    license_expiring_30_days: number;
    kpis: { key: string; value: number }[];
  }>("/dashboard/kpis");
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
