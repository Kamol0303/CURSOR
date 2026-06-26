"""RT-14 — AI analytics service must not query PINFL columns."""

import re
from pathlib import Path


def test_analytics_engine_excludes_pinfl_columns():
    engine_path = Path(__file__).resolve().parents[1] / "app" / "services" / "analytics_engine.py"
    source = engine_path.read_text(encoding="utf-8")
    queries = re.findall(r'text\("""(.*?)"""\)', source, re.DOTALL)
    assert queries, "expected SQL text() blocks in analytics_engine"
    for query in queries:
        lowered = query.lower()
        assert "jshshir" not in lowered
        assert "pinfl" not in lowered
