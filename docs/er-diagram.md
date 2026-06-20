# TaMoR Entity-Relationship Diagram

```mermaid
erDiagram
    roles ||--o{ users : has
    roles ||--o{ role_permissions : has
    permissions ||--o{ role_permissions : grants
    users ||--o{ sessions : has
    users ||--o{ refresh_tokens : has
    users ||--o{ login_audit_log : logs
    users }o--|| training_centers : belongs_to
    training_centers ||--o{ branches : has
    training_centers ||--o{ teachers : employs
    training_centers ||--o{ students : enrolls
    training_centers }o--|| mahallas : located_in
    mahallas }o--|| regions : part_of
    students ||--o{ guardians : has
    students ||--o{ student_consents : records
    students ||--o{ enrollments : has
    students ||--o{ certificates : receives
    teachers ||--o{ teacher_subjects : teaches
    subjects ||--o{ teacher_subjects : assigned
    subjects ||--o{ groups : offers
    groups ||--o{ enrollments : contains
    groups ||--o{ group_schedule : schedules
    groups ||--o{ attendance : tracks
    training_centers ||--o{ ratings : scored
    ratings ||--o{ rating_history : archives
    rating_formula_versions ||--o{ ratings : defines
    certificates ||--o{ certificate_verifications : verified
    users ||--o{ notifications : receives
    users ||--o{ audit_logs : triggers
    api_keys ||--o{ api_key_scopes : scoped
    files ||--o{ training_centers : stores
    system_settings ||--o{ rating_formula_versions : configures

    users {
        uuid id PK
        string username
        string email
        string phone
        string password_hash
        uuid role_id FK
        uuid center_id FK
        enum locale_preference
        boolean is_active
        boolean is_locked
        int failed_login_attempts
        boolean mfa_enabled
        enum mfa_method
        boolean is_demo_account
        timestamp deleted_at
    }

    roles {
        uuid id PK
        string code
        string name_uz
        string name_ru
        string name_en
    }

    permissions {
        uuid id PK
        string code
        string module
        string action
    }

    training_centers {
        uuid id PK
        string name
        string stir
        string license_number
        date license_expiry
        uuid mahalla_id FK
        enum center_type
        boolean is_active
        timestamp deleted_at
    }

    students {
        uuid id PK
        string full_name
        string pinfl_encrypted
        date date_of_birth
        uuid center_id FK
        timestamp deleted_at
    }

    ratings {
        uuid id PK
        uuid center_id FK
        decimal total_score
        uuid formula_version_id FK
        date period_date
    }
```

## Core Auth Tables (Phase 0)

| Table | Purpose |
|-------|---------|
| `users` | Identity records with MFA, locale, lockout state |
| `roles` | 8 system roles with trilingual names |
| `permissions` | Granular module.action permissions |
| `role_permissions` | RBAC mapping |
| `sessions` | Active session tracking |
| `refresh_tokens` | Opaque token rotation with family_id |
| `login_audit_log` | All login attempts (partitioned monthly) |
| `password_reset_tokens` | Password recovery flow |
| `api_keys` | External API consumer HMAC keys |
