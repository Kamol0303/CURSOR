# ADR-005: Password Hashing — argon2id

## Status
Accepted

## Context
Government system processing minors' data requires memory-hard password hashing resistant to GPU cracking.

## Decision
Use **argon2id** via `argon2-cffi` with parameters:
- `time_cost=3`
- `memory_cost=65536` (64 MiB)
- `parallelism=4`
- `hash_len=32`
- `salt_len=16`

bcrypt (cost 12) acceptable only if argon2 bindings unavailable in deployment environment.

## Consequences
- Higher memory per hash operation; acceptable at expected scale (<500 concurrent users)
- Stronger resistance to offline cracking vs bcrypt
