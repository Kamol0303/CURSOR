# ADR-004: Uzbek Cyrillic Script Exclusion from v1

## Status
Accepted

## Context
Uzbekistan historically used Cyrillic script; some district staff may expect `uz-Cyrl` locale support.

## Decision
v1 supports only **Uzbek Latin** (`uz`), Russian (`ru`), and English (`en`). Uzbek Cyrillic is explicitly out of scope.

## Justification
- Government digital services in Uzbekistan have standardized on Latin script since 2021 reforms.
- Supporting Cyrillic doubles translation maintenance without clear user demand in Toyloq District pilot.
- Architecture supports adding `uz_cyrl` as a fourth locale in v2 via the same column pattern.

## Consequences
- Document in user guides that Uzbek is Latin-script only.
- Font stack must still include full Cyrillic for Russian (`ru`).
