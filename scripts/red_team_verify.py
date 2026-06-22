#!/usr/bin/env python3
"""Automated red-team checklist verification (Section 24A).

Usage:
  python scripts/red_team_verify.py --offline          # CI / no running server
  python scripts/red_team_verify.py --url http://localhost:8000
  python scripts/red_team_verify.py --url https://tamor.toyloq.uz --production
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.core.permissions import MANDATORY_MFA_ROLES
from app.integrations.http_client import SSRFError, validate_external_url


@dataclass
class CheckResult:
    code: str
    title: str
    passed: bool
    detail: str = ""
    manual: bool = False


@dataclass
class Report:
    results: list[CheckResult] = field(default_factory=list)

    def add(self, code: str, title: str, passed: bool, detail: str = "", manual: bool = False):
        self.results.append(CheckResult(code, title, passed, detail, manual))

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed and not r.manual)

    def print_report(self) -> None:
        for r in self.results:
            icon = "○" if r.manual else ("✓" if r.passed else "✗")
            suffix = " (manual)" if r.manual else ""
            line = f"  {icon} {r.code} {r.title}{suffix}"
            if r.detail:
                line += f" — {r.detail}"
            print(line)
        print()
        auto = [r for r in self.results if not r.manual]
        passed = sum(1 for r in auto if r.passed)
        print(f"Automated: {passed}/{len(auto)} passed, {self.failed} failed")


async def verify(base_url: str, production: bool, offline: bool) -> Report:
    report = Report()
    repo = Path(__file__).resolve().parents[1]
    base = base_url.rstrip("/")

    if offline:
        report.add("RT-15", "Health endpoint", True, "skipped (--offline)", manual=True)
        report.add("RT-17", "Verify rate limit", True, "CI integration test", manual=True)
        report.add("RT-20", "TLS/HSTS", True, "use --production against staging", manual=True)
    else:
        try:
            async with httpx.AsyncClient(base_url=base, timeout=5.0) as client:
                health = await client.get("/health")
                report.add("RT-15", "Health endpoint responds", health.status_code == 200)

                statuses = []
                for _ in range(12):
                    r = await client.get("/api/v1/public/verify/TMB-NOTFOUND-XXXX")
                    statuses.append(r.status_code)
                report.add(
                    "RT-17",
                    "Certificate verify rate-limited",
                    429 in statuses,
                    f"last={statuses[-3:]}",
                )

                if production:
                    r = await client.get("/", follow_redirects=True)
                    hsts = r.headers.get("strict-transport-security", "")
                    report.add("RT-20", "HSTS header present", "max-age" in hsts.lower(), hsts or "missing")
                else:
                    report.add("RT-20", "TLS/HSTS via Nginx", True, "dev — use --production", manual=True)
        except httpx.ConnectError:
            report.add("RT-15", "Health endpoint responds", False, "server unreachable")
            report.add("RT-17", "Certificate verify rate-limited", False, "server unreachable")

    nginx_conf = repo / "infra/nginx/nginx.conf"
    report.add(
        "RT-21",
        "Nginx rate limit config in repo",
        nginx_conf.exists() and "limit_req_zone" in nginx_conf.read_text(),
    )

    report.add(
        "RT-03",
        "MFA mandatory roles configured",
        MANDATORY_MFA_ROLES == {"super_admin", "hokimiyat_operator", "center_director"},
    )

    leaked = [p for p in repo.glob("**/*.pem") if ".git" not in str(p)]
    report.add("RT-04", "No PEM keys committed to repo", len(leaked) == 0, f"found={len(leaked)}")

    from app.core.config import settings

    report.add("RT-05", "Access token TTL <= 15 min", settings.ACCESS_TOKEN_EXPIRE_MINUTES <= 15)

    try:
        validate_external_url("https://notify.eskiz.uz/api/auth/login")
        ssrf_blocks = False
        try:
            validate_external_url("http://127.0.0.1/internal")
        except SSRFError:
            ssrf_blocks = True
        report.add("RT-19", "SSRF blocks internal URLs", ssrf_blocks)
    except Exception as exc:
        report.add("RT-19", "SSRF blocks internal URLs", False, str(exc))

    report.add("RT-22", "Cosign workflow exists", (repo / ".github/workflows/cosign.yml").exists())
    report.add("RT-23", "Vault secrets ADR documented", (repo / "docs/adr/008-vault-secrets.md").exists())

    backup = repo / "scripts/backup_postgres.sh"
    restore = repo / "scripts/restore_postgres.sh"
    report.add(
        "RT-26",
        "Backup/restore scripts exist",
        backup.exists() and restore.exists(),
        "scripts/backup_postgres.sh, scripts/restore_postgres.sh",
    )

    for code, title in [
        ("RT-01", "Login rate limit (CI)"),
        ("RT-02", "Refresh token reuse (CI)"),
        ("RT-06", "Parent OTP max attempts (CI)"),
        ("RT-07", "IDOR center isolation (CI)"),
        ("RT-08", "Teacher admin denial (CI)"),
        ("RT-09", "Parent child scope (CI)"),
        ("RT-10", "RLS FORCE policies (CI)"),
        ("RT-11", "PINFL reveal audit (CI)"),
        ("RT-12", "PINFL encrypted at rest (CI)"),
        ("RT-14", "AI service no PINFL"),
        ("RT-16", "No demo accounts"),
        ("RT-18", "Certificate tamper (CI)"),
        ("RT-24", "Database not public"),
        ("RT-25", "Incident response roles"),
        ("RT-27", "Demo data purged"),
        ("RT-28", "Load test baseline"),
    ]:
        report.add(code, title, True, manual=True)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="TMB red-team automated verification")
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--production", action="store_true")
    parser.add_argument("--offline", action="store_true", help="Skip live HTTP checks (CI)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = asyncio.run(verify(args.url, args.production, args.offline))
    if args.json:
        print(json.dumps([r.__dict__ for r in report.results], indent=2))
    else:
        mode = "offline" if args.offline else args.url
        print(f"TMB Red-Team Verification — {mode}\n")
        report.print_report()
    sys.exit(1 if report.failed else 0)


if __name__ == "__main__":
    main()
