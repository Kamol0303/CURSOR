# ADR 0005: Exclude Uzbek Cyrillic from v1

## Status
Accepted

## Decision

Support Uzbek Latin, Russian Cyrillic, and English in v1, while explicitly excluding Uzbek Cyrillic.

## Rationale

The client specification defines Uzbek Latin as the default Uzbek experience. Adding Uzbek Cyrillic would materially expand translation, QA, typography, and reporting effort without changing the core Phase 0 architecture. The locale framework remains extensible, so Uzbek Cyrillic can be added later as a deliberate project phase rather than an implicit, under-tested partial implementation.
