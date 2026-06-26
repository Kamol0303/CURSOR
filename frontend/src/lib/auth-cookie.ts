const COOKIE_NAME = "tmb_access_token";
const MAX_AGE_SECONDS = 15 * 60;

export function setAuthCookie(token: string) {
  if (typeof document === "undefined") return;
  document.cookie = `${COOKIE_NAME}=${encodeURIComponent(token)}; path=/; max-age=${MAX_AGE_SECONDS}; SameSite=Lax`;
}

export function clearAuthCookie() {
  if (typeof document === "undefined") return;
  document.cookie = `${COOKIE_NAME}=; path=/; max-age=0; SameSite=Lax`;
}

export function getRoleFromToken(token: string): string | null {
  try {
    const segment = token.split(".")[1];
    if (!segment) return null;
    const normalized = segment.replace(/-/g, "+").replace(/_/g, "/");
    const payload = JSON.parse(atob(normalized)) as { role?: string };
    return payload.role ?? null;
  } catch {
    return null;
  }
}

export function homePathForRole(role: string | null): string {
  if (role === "student") return "/student/dashboard";
  if (role === "parent") return "/parent/dashboard";
  return "/dashboard";
}
