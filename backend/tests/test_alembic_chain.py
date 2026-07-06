"""Ensure Alembic revision IDs form a single valid chain."""

from pathlib import Path

import pytest

VERSIONS_DIR = Path(__file__).resolve().parents[1] / "alembic" / "versions"


def _load_revisions():
    revisions: dict[str, str | None] = {}
    for path in sorted(VERSIONS_DIR.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        rev = None
        down = None
        for line in text.splitlines():
            if line.startswith("revision:"):
                rev = line.split("=", 1)[1].strip().strip('"').strip("'")
            if line.startswith("down_revision:"):
                raw = line.split("=", 1)[1].strip()
                if raw in ("None", "null"):
                    down = None
                else:
                    down = raw.strip('"').strip("'")
        if rev:
            revisions[rev] = down
    return revisions


def test_alembic_revision_chain_is_valid():
    revisions = _load_revisions()
    assert revisions, "No Alembic revisions found"

    for rev, down in revisions.items():
        if down is not None:
            assert down in revisions, f"{rev} references missing down_revision {down!r}"

    roots = [rev for rev, down in revisions.items() if down is None]
    assert len(roots) == 1, f"Expected one root revision, got {roots}"

    referenced = {down for down in revisions.values() if down}
    heads = [rev for rev in revisions if rev not in referenced]
    assert len(heads) == 1, f"Expected single Alembic head, got {heads}"
