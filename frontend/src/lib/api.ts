const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface APIError {
  code: string;
  field: string | null;
}

interface APIResponse<T> {
  success: boolean;
  data: T | null;
  meta: Record<string, unknown> | null;
  error: APIError | null;
}

export interface LoginResult {
  access_token?: string;
  token_type?: string;
  mfa_required?: boolean;
  mfa_token?: string;
  must_change_password?: boolean;
  user?: {
    id: string;
    username: string | null;
    role: string;
    role_name_uz: string;
    role_name_ru: string;
    role_name_en: string;
    locale_preference: string;
    permissions: string[];
  };
}

export async function apiLogin(username: string, password: string): Promise<APIResponse<LoginResult>> {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ username, password }),
  });
  return res.json();
}

export async function apiMfaVerify(mfaToken: string, code: string): Promise<APIResponse<LoginResult>> {
  const res = await fetch(`${API_URL}/auth/mfa/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ mfa_token: mfaToken, code }),
  });
  return res.json();
}

export async function apiOtpRequest(phone: string): Promise<APIResponse<{ otp_sent: boolean; dev_code?: string }>> {
  const res = await fetch(`${API_URL}/auth/login/otp/request`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone }),
  });
  return res.json();
}

export async function apiOtpVerify(phone: string, code: string): Promise<APIResponse<LoginResult>> {
  const res = await fetch(`${API_URL}/auth/login/otp/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ phone, code }),
  });
  return res.json();
}

export async function apiLogout(): Promise<void> {
  await fetch(`${API_URL}/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  });
  localStorage.removeItem('tamor_access_token');
}

export function setAccessToken(token: string) {
  localStorage.setItem('tamor_access_token', token);
}

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('tamor_access_token');
}
