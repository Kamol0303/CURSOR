#!/usr/bin/env python3
"""Read-only demo/test data inventory for production cutover (Stage 1.1).

Scans PostgreSQL for:
  - is_demo_account / is_demo_data flagged rows
  - Name/pattern heuristics (Demo, Test, Aspect, etc.)
  - Known seed usernames, STIR, PINFL, phones

Usage:
  python scripts/inventory_demo_data.py
  python scripts/inventory_demo_data.py --format markdown
  python scripts/inventory_demo_data.py --format csv > demo-inventory.csv

Does NOT delete or modify any data.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import io
import sys
from dataclasses import dataclass

from sqlalchemy import or_, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, ".")

from app.core.config import settings
from app.core.rls import apply_rls_context, set_rls_role
from app.models.analytics_notifications import AiAnalysisLog, AiPrediction, Notification
from app.models.education import Enrollment, Group, Guardian, Student, Teacher
from app.models.identity import ApiKey, TrainingCenter, User
from app.models.ratings_certs import Certificate, RatingHistory

# Known seed/demo identifiers from backend/scripts/seed_demo_users.py
KNOWN_DEMO_USERNAMES = frozenset(
    {
        "admin.tmb",
        "operator.hokimiyat",
        "director.aspect",
        "admin.aspect",
        "teacher.dilnoza",
        "student.sardor",
        "auditor.tuman",
    }
)
KNOWN_DEMO_PHONES = frozenset({"+998901234567", "+998901112233"})
KNOWN_DEMO_STIR = frozenset({"123456789", "987654321"})
KNOWN_DEMO_PINFL = frozenset({"12345678901234"})
NAME_PATTERNS = ("%Demo%", "%Test%", "%Aspect%", "%Sardor%", "%Karimova%", "%Sample%", "%Example%")
KNOWN_DEMO_CENTER_NAMES = frozenset({"Aspect Ta'lim Markazi", "Demo Boshqa Markaz"})
KNOWN_DEMO_STUDENT_NAMES = frozenset({"Aliyev Sardor", "Demo Boshqa O'quvchi"})
KNOWN_DEMO_TEACHER_NAMES = frozenset({"Dilnoza Karimova"})
KNOWN_DEMO_GUARDIAN_NAMES = frozenset({"Aliyev Botir"})


@dataclass
class InventoryRow:
    table: str
    record_id: str
    label: str
    reason: str
    flagged: str  # yes | no | partial
    purge_safe: str  # yes | review | no


def _like(*cols):
    return or_(*[c.ilike(p) for p in NAME_PATTERNS for c in cols])


async def collect_inventory(session) -> list[InventoryRow]:
    rows: list[InventoryRow] = []

    # --- users ---
    users = (await session.execute(select(User))).scalars().all()
    for u in users:
        reasons: list[str] = []
        if u.is_demo_account:
            reasons.append("is_demo_account=true")
        if u.username in KNOWN_DEMO_USERNAMES:
            reasons.append(f"known seed username: {u.username}")
        if u.phone in KNOWN_DEMO_PHONES:
            reasons.append(f"known seed phone: {u.phone}")
        if u.username and any(p.strip("%") in (u.username or "") for p in NAME_PATTERNS):
            reasons.append("username matches demo pattern")
        if reasons:
            rows.append(
                InventoryRow(
                    table="users",
                    record_id=str(u.id),
                    label=u.username or u.phone or "(no login)",
                    reason="; ".join(reasons),
                    flagged="yes" if u.is_demo_account else "no",
                    purge_safe="yes" if u.is_demo_account else "review",
                )
            )

    # --- training_centers ---
    centers = (await session.execute(select(TrainingCenter))).scalars().all()
    for c in centers:
        reasons: list[str] = []
        if c.is_demo_data:
            reasons.append("is_demo_data=true")
        if c.name in KNOWN_DEMO_CENTER_NAMES:
            reasons.append(f"known seed center: {c.name}")
        if c.stir in KNOWN_DEMO_STIR:
            reasons.append(f"test STIR: {c.stir}")
        if any(p.strip("%").lower() in c.name.lower() for p in NAME_PATTERNS):
            reasons.append("name matches demo pattern")
        if reasons:
            rows.append(
                InventoryRow(
                    table="training_centers",
                    record_id=str(c.id),
                    label=c.name,
                    reason="; ".join(reasons),
                    flagged="yes" if c.is_demo_data else "no",
                    purge_safe="yes" if c.is_demo_data else "review",
                )
            )

    # --- students ---
    students = (await session.execute(select(Student))).scalars().all()
    for s in students:
        reasons: list[str] = []
        if s.is_demo_data:
            reasons.append("is_demo_data=true")
        if s.full_name in KNOWN_DEMO_STUDENT_NAMES:
            reasons.append(f"known seed student: {s.full_name}")
        if any(p.strip("%") in s.full_name for p in NAME_PATTERNS):
            reasons.append("name matches demo pattern")
        if reasons:
            rows.append(
                InventoryRow(
                    table="students",
                    record_id=str(s.id),
                    label=s.full_name,
                    reason="; ".join(reasons),
                    flagged="yes" if s.is_demo_data else "no",
                    purge_safe="yes" if s.is_demo_data else "review",
                )
            )

    # --- teachers ---
    teachers = (await session.execute(select(Teacher))).scalars().all()
    for t in teachers:
        reasons: list[str] = []
        if t.is_demo_data:
            reasons.append("is_demo_data=true")
        if t.full_name in KNOWN_DEMO_TEACHER_NAMES:
            reasons.append(f"known seed teacher: {t.full_name}")
        if t.phone in KNOWN_DEMO_PHONES:
            reasons.append(f"known seed phone: {t.phone}")
        if any(p.strip("%") in (t.full_name or "") for p in NAME_PATTERNS):
            reasons.append("name matches demo pattern")
        if reasons:
            rows.append(
                InventoryRow(
                    table="teachers",
                    record_id=str(t.id),
                    label=t.full_name,
                    reason="; ".join(reasons),
                    flagged="yes" if t.is_demo_data else "no",
                    purge_safe="yes" if t.is_demo_data else "review",
                )
            )

    # --- certificates ---
    certs = (await session.execute(select(Certificate))).scalars().all()
    for cert in certs:
        if cert.is_demo_data:
            rows.append(
                InventoryRow(
                    table="certificates",
                    record_id=str(cert.id),
                    label=cert.certificate_number,
                    reason="is_demo_data=true",
                    flagged="yes",
                    purge_safe="yes",
                )
            )

    # --- guardians (no demo flag) ---
    guardians = (await session.execute(select(Guardian))).scalars().all()
    for g in guardians:
        reasons: list[str] = []
        if g.full_name in KNOWN_DEMO_GUARDIAN_NAMES:
            reasons.append(f"known seed guardian: {g.full_name}")
        if g.phone in KNOWN_DEMO_PHONES:
            reasons.append(f"known seed phone: {g.phone}")
        if reasons:
            rows.append(
                InventoryRow(
                    table="guardians",
                    record_id=str(g.id),
                    label=g.full_name,
                    reason="; ".join(reasons),
                    flagged="no",
                    purge_safe="yes",
                )
            )

    # --- api_keys ---
    keys = (await session.execute(select(ApiKey))).scalars().all()
    for k in keys:
        if (k.label or "").startswith("tamor_demo"):
            rows.append(
                InventoryRow(
                    table="api_keys",
                    record_id=str(k.id),
                    label=k.label or "(no label)",
                    reason="seed label prefix tamor_demo",
                    flagged="no",
                    purge_safe="review",
                )
            )

    # --- child tables without demo flags (linked to demo centers) ---
    demo_center_ids = {c.id for c in centers if c.is_demo_data}
    demo_center_names = {c.name for c in centers if c.is_demo_data}
    if not demo_center_ids:
        demo_center_ids = {c.id for c in centers if c.name in KNOWN_DEMO_CENTER_NAMES}

    for g in (await session.execute(select(Group).where(Group.center_id.in_(demo_center_ids)))).scalars():
        rows.append(
            InventoryRow(
                table="groups",
                record_id=str(g.id),
                label=g.name,
                reason=f"belongs to demo center",
                flagged="no",
                purge_safe="yes",
            )
        )

    for e in (
        await session.execute(select(Enrollment).where(Enrollment.center_id.in_(demo_center_ids)))
    ).scalars():
        rows.append(
            InventoryRow(
                table="enrollments",
                record_id=str(e.id),
                label=f"student={e.student_id}",
                reason="belongs to demo center",
                flagged="no",
                purge_safe="yes",
            )
        )

    for rh in (
        await session.execute(select(RatingHistory).where(RatingHistory.center_id.in_(demo_center_ids)))
    ).scalars():
        rows.append(
            InventoryRow(
                table="rating_history",
                record_id=str(rh.id),
                label=str(rh.center_id),
                reason="demo center rating",
                flagged="no",
                purge_safe="yes",
            )
        )

    for pred in (await session.execute(select(AiPrediction))).scalars():
        payload_name = (pred.payload or {}).get("center_name", "")
        if payload_name in demo_center_names or payload_name in KNOWN_DEMO_CENTER_NAMES:
            rows.append(
                InventoryRow(
                    table="ai_predictions",
                    record_id=str(pred.id),
                    label=pred.prediction_type,
                    reason=f"references demo center: {payload_name}",
                    flagged="no",
                    purge_safe="review",
                )
            )

    for log in (await session.execute(select(AiAnalysisLog).where(AiAnalysisLog.triggered_by == "seed"))).scalars():
        rows.append(
            InventoryRow(
                table="ai_analysis_logs",
                record_id=str(log.id),
                label=log.status,
                reason="triggered_by=seed",
                flagged="no",
                purge_safe="review",
            )
        )

    # --- summary counts by table ---
    return rows


def format_markdown(rows: list[InventoryRow]) -> str:
    lines = [
        "# Demo data inventory",
        "",
        f"Environment: `{settings.ENVIRONMENT}`",
        f"Total suspicious rows: **{len(rows)}**",
        "",
        "| Jadval | ID | Yozuv | Sabab | Flag | Purge? |",
        "|--------|-----|-------|-------|------|--------|",
    ]
    for r in rows:
        lines.append(
            f"| {r.table} | `{r.record_id[:8]}…` | {r.label} | {r.reason} | {r.flagged} | {r.purge_safe} |"
        )
    return "\n".join(lines)


def format_csv(rows: list[InventoryRow]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["table", "record_id", "label", "reason", "flagged", "purge_safe"])
    for r in rows:
        writer.writerow([r.table, r.record_id, r.label, r.reason, r.flagged, r.purge_safe])
    return buf.getvalue()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only demo data inventory")
    parser.add_argument("--format", choices=("markdown", "csv", "text"), default="markdown")
    args = parser.parse_args()

    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        set_rls_role("system")
        await apply_rls_context(session)
        # sanity
        await session.execute(text("SELECT 1"))
        rows = await collect_inventory(session)

    if args.format == "markdown":
        print(format_markdown(rows))
    elif args.format == "csv":
        print(format_csv(rows), end="")
    else:
        for r in rows:
            print(f"{r.table}\t{r.record_id}\t{r.label}\t{r.reason}\tflagged={r.flagged}\tpurge={r.purge_safe}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
