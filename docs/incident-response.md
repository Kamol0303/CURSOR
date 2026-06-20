# TaMoR Incident Response Runbook

> Section 17A deliverable — operational response for security events

## 17A.1 Detection — Alerting Pipeline

`security_events` writes feed Grafana alert rules. Page on-call within **1 minute** of `critical` severity.

**Minimum alert triggers:**
- Refresh-token family revocation (reuse detected)
- Failed logins exceeding threshold (per account or IP)
- PINFL reveal rate limit exceeded
- Spike in 401/403 responses (active probing)
- Certificate verification endpoint rate spike

## 17A.2 Containment — First 15 Minutes

1. Acknowledge alert; pull `security_events`, `login_audit_log`, `audit_logs` context.
2. **Compromised account:** Force-revoke all sessions (Redis JWT denylist + refresh family revoke); set `is_locked = true`.
3. **Credential-stuffing campaign:** Apply Nginx IP block while reviewing application evidence.
4. **Suspected PINFL exfiltration:** Suspend implicated admin; notify Data Protection Lead within 1 hour.

## 17A.3 Assessment

- Query immutable audit logs for exact rows read/modified, session IDs, time window.
- Classify severity tier (Section 10A):
  - **Tier 1:** Unauthorized PINFL/sensitive access → full breach plan
  - **Tier 2:** Account compromise without confirmed sensitive access
  - **Tier 3:** Availability incident only

## 17A.4 Remediation

- Rotate exposed credentials/keys immediately (off-cadence if needed).
- Patch gap; add regression test to security suite (Section 16).

## 17A.5 Post-Incident Review

Blameless review within 5 business days: timeline, root cause, action items with owners. File alongside ADR log.

## 17A.6 Named Ownership (fill before go-live)

| Role | Responsibility |
|---|---|
| Incident Commander (on-call) | First responder, coordinates containment |
| Data Protection Lead | PINFL incident notification decisions |
| Super Admin (district IT) | Credential/key rotation |
| Hokimlik liaison | External communication if disclosure warranted |
