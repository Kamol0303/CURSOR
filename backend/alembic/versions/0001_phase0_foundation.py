"""phase0 foundation

Revision ID: 0001_phase0
Revises:
Create Date: 2026-06-20 11:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_phase0"
down_revision = None
branch_labels = None
depends_on = None


def audit_columns():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name_uz", sa.String(length=255), nullable=False),
        sa.Column("name_ru", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        *audit_columns(),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "permissions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        *audit_columns(),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "files",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=128), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        *audit_columns(),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_table(
        "regions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name_uz", sa.String(length=255), nullable=False),
        sa.Column("name_ru", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        *audit_columns(),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "mahallas",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("region_id", sa.Uuid(), sa.ForeignKey("regions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name_uz", sa.String(length=255), nullable=False),
        sa.Column("name_ru", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        *audit_columns(),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "training_centers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("tax_id", sa.String(length=9), nullable=False),
        sa.Column("director_full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("mahalla_id", sa.Uuid(), sa.ForeignKey("mahallas.id", ondelete="SET NULL"), nullable=True),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("license_number", sa.String(length=128), nullable=False),
        sa.Column("license_expiry", sa.Date(), nullable=True),
        sa.Column("license_scan_file_id", sa.Uuid(), sa.ForeignKey("files.id", ondelete="SET NULL"), nullable=True),
        sa.Column("logo_file_id", sa.Uuid(), sa.ForeignKey("files.id", ondelete="SET NULL"), nullable=True),
        sa.Column("center_type", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("founding_date", sa.Date(), nullable=True),
        sa.Column("bank_account", sa.String(length=64), nullable=True),
        sa.Column("working_hours", sa.Text(), nullable=True),
        *audit_columns(),
        sa.UniqueConstraint("tax_id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("username", sa.String(length=150), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("password_hash", sa.String(length=512), nullable=True),
        sa.Column("role_id", sa.Uuid(), sa.ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("center_id", sa.Uuid(), sa.ForeignKey("training_centers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("locale_preference", sa.String(length=8), nullable=False, server_default="uz"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_locked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lockout_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("mfa_secret_encrypted", sa.Text(), nullable=True),
        sa.Column("mfa_method", sa.String(length=16), nullable=False, server_default="none"),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_demo_account", sa.Boolean(), nullable=False, server_default=sa.false()),
        *audit_columns(),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone"),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Uuid(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", sa.Uuid(), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("refresh_token_hash", sa.String(length=64), nullable=False),
        sa.Column("device_info", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("family_id", sa.String(length=128), nullable=False),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by_token_hash", sa.String(length=64), nullable=True),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_table(
        "login_audit_log",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("username_attempted", sa.String(length=255), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("failure_reason", sa.String(length=255), nullable=True),
        sa.Column("mfa_used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_table(
        "password_history",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "mfa_recovery_codes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("code_hash"),
    )
    op.create_table(
        "otp_challenges",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("purpose", sa.String(length=64), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "guardians",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("locale_preference", sa.String(length=8), nullable=False, server_default="uz"),
        *audit_columns(),
        sa.UniqueConstraint("phone"),
    )
    op.create_table(
        "students",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("center_id", sa.Uuid(), sa.ForeignKey("training_centers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("guardian_id", sa.Uuid(), sa.ForeignKey("guardians.id", ondelete="SET NULL"), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("pinfl_encrypted", sa.Text(), nullable=True),
        sa.Column("pinfl_masked", sa.String(length=32), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=16), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("school", sa.String(length=255), nullable=True),
        sa.Column("grade", sa.String(length=32), nullable=True),
        sa.Column("enrollment_date", sa.Date(), nullable=True),
        sa.Column("graduation_date", sa.Date(), nullable=True),
        sa.Column("certificate_status", sa.String(length=32), nullable=True),
        sa.Column("certificate_number", sa.String(length=64), nullable=True),
        sa.Column("qr_code", sa.String(length=255), nullable=True),
        *audit_columns(),
        sa.UniqueConstraint("certificate_number"),
    )
    op.create_table(
        "student_consents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("student_id", sa.Uuid(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("consent_given_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consent_by", sa.String(length=255), nullable=False),
        sa.Column("recorded_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        *audit_columns(),
    )
    op.create_table(
        "subjects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name_uz", sa.String(length=255), nullable=False),
        sa.Column("name_ru", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        *audit_columns(),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "teachers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("center_id", sa.Uuid(), sa.ForeignKey("training_centers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("specialization", sa.String(length=255), nullable=True),
        sa.Column("diploma_file_id", sa.Uuid(), sa.ForeignKey("files.id", ondelete="SET NULL"), nullable=True),
        sa.Column("years_of_experience", sa.Integer(), nullable=True),
        sa.Column("certifications", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("performance_index", sa.Numeric(8, 2), nullable=True),
        *audit_columns(),
    )
    op.create_table(
        "teacher_subjects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("teacher_id", sa.Uuid(), sa.ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_id", sa.Uuid(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
        *audit_columns(),
    )
    op.create_table(
        "branches",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("center_id", sa.Uuid(), sa.ForeignKey("training_centers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("mahalla_id", sa.Uuid(), sa.ForeignKey("mahallas.id", ondelete="SET NULL"), nullable=True),
        *audit_columns(),
    )
    op.create_table(
        "license_history",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("center_id", sa.Uuid(), sa.ForeignKey("training_centers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("license_number", sa.String(length=128), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("license_scan_file_id", sa.Uuid(), sa.ForeignKey("files.id", ondelete="SET NULL"), nullable=True),
        *audit_columns(),
    )
    op.create_table(
        "courses",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("center_id", sa.Uuid(), sa.ForeignKey("training_centers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("subject_id", sa.Uuid(), sa.ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("average_duration_days", sa.Integer(), nullable=True),
        *audit_columns(),
    )
    op.create_table(
        "groups",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("center_id", sa.Uuid(), sa.ForeignKey("training_centers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("course_id", sa.Uuid(), sa.ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("teacher_id", sa.Uuid(), sa.ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("starts_at", sa.Date(), nullable=True),
        sa.Column("ends_at", sa.Date(), nullable=True),
        *audit_columns(),
    )
    op.create_table(
        "group_schedule",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("group_id", sa.Uuid(), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("starts_at", sa.String(length=8), nullable=False),
        sa.Column("ends_at", sa.String(length=8), nullable=False),
        *audit_columns(),
    )
    op.create_table(
        "enrollments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("student_id", sa.Uuid(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", sa.Uuid(), sa.ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("group_id", sa.Uuid(), sa.ForeignKey("groups.id", ondelete="SET NULL"), nullable=True),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *audit_columns(),
    )
    op.create_table(
        "attendance",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("group_id", sa.Uuid(), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", sa.Uuid(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("attended_on", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        *audit_columns(),
    )
    op.create_table(
        "rating_formula_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("version_label", sa.String(length=64), nullable=False),
        sa.Column("weights_json", sa.JSON(), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        *audit_columns(),
    )
    op.create_table(
        "ratings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("center_id", sa.Uuid(), sa.ForeignKey("training_centers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("formula_version_id", sa.Uuid(), sa.ForeignKey("rating_formula_versions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("period", sa.String(length=16), nullable=False),
        sa.Column("score", sa.Numeric(8, 2), nullable=False),
        sa.Column("criteria_json", sa.JSON(), nullable=False),
        *audit_columns(),
    )
    op.create_table(
        "rating_history",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("center_id", sa.Uuid(), sa.ForeignKey("training_centers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("period", sa.String(length=16), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("score", sa.Numeric(8, 2), nullable=False),
        *audit_columns(),
    )
    op.create_table(
        "certificates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("student_id", sa.Uuid(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("center_id", sa.Uuid(), sa.ForeignKey("training_centers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("certificate_number", sa.String(length=64), nullable=False),
        sa.Column("course_name", sa.String(length=255), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("pdf_file_id", sa.Uuid(), sa.ForeignKey("files.id", ondelete="SET NULL"), nullable=True),
        sa.Column("qr_code", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=8), nullable=False),
        *audit_columns(),
        sa.UniqueConstraint("certificate_number"),
    )
    op.create_table(
        "certificate_verifications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("certificate_id", sa.Uuid(), sa.ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("verification_channel", sa.String(length=32), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        *audit_columns(),
    )
    op.create_table(
        "ai_predictions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("center_id", sa.Uuid(), sa.ForeignKey("training_centers.id", ondelete="CASCADE"), nullable=True),
        sa.Column("subject_id", sa.Uuid(), sa.ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True),
        sa.Column("prediction_type", sa.String(length=64), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("explanation_key", sa.String(length=255), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        *audit_columns(),
    )
    op.create_table(
        "ai_analysis_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("prediction_id", sa.Uuid(), sa.ForeignKey("ai_predictions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        *audit_columns(),
    )
    op.create_table(
        "monthly_statistics",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("center_id", sa.Uuid(), sa.ForeignKey("training_centers.id", ondelete="CASCADE"), nullable=True),
        sa.Column("subject_id", sa.Uuid(), sa.ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True),
        sa.Column("month_key", sa.String(length=7), nullable=False),
        sa.Column("student_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("teacher_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("graduate_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("certificate_count", sa.Integer(), nullable=False, server_default="0"),
        *audit_columns(),
    )
    op.create_table(
        "report_templates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name_uz", sa.String(length=255), nullable=False),
        sa.Column("name_ru", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("template_body", sa.Text(), nullable=False),
        *audit_columns(),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("template_id", sa.Uuid(), sa.ForeignKey("report_templates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("generated_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("language", sa.String(length=8), nullable=False),
        sa.Column("parameters_json", sa.JSON(), nullable=False),
        sa.Column("file_id", sa.Uuid(), sa.ForeignKey("files.id", ondelete="SET NULL"), nullable=True),
        *audit_columns(),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("template_key", sa.String(length=255), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *audit_columns(),
    )
    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("notification_id", sa.Uuid(), sa.ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        *audit_columns(),
    )
    op.create_table(
        "sms_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("notification_id", sa.Uuid(), sa.ForeignKey("notifications.id", ondelete="SET NULL"), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("provider_message_id", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        *audit_columns(),
    )
    op.create_table(
        "translations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("namespace", sa.String(length=64), nullable=False),
        sa.Column("translation_key", sa.String(length=255), nullable=False),
        sa.Column("locale", sa.String(length=8), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        *audit_columns(),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("actor_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("entity_type", sa.String(length=128), nullable=False),
        sa.Column("entity_id", sa.String(length=128), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "system_settings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        *audit_columns(),
        sa.UniqueConstraint("key"),
    )
    op.create_table(
        "import_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("entity_type", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        *audit_columns(),
    )
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("key_id", sa.String(length=64), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("secret_hash", sa.String(length=64), nullable=False),
        sa.Column("secret_encrypted", sa.Text(), nullable=False),
        sa.Column("key_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("owner_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("active_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("grace_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        *audit_columns(),
        sa.UniqueConstraint("key_id"),
        sa.UniqueConstraint("key_hash"),
    )
    op.create_table(
        "api_key_scopes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("api_key_id", sa.Uuid(), sa.ForeignKey("api_keys.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scope_code", sa.String(length=128), nullable=False),
    )

    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_phone", "users", ["phone"])
    op.create_index("ix_refresh_tokens_family", "refresh_tokens", ["family_id"])
    op.create_index("ix_otp_challenges_phone", "otp_challenges", ["phone"])
    op.create_index("ix_training_centers_name", "training_centers", ["name"])
    op.create_index("ix_students_certificate_number", "students", ["certificate_number"])
    op.create_index("ix_ratings_center_period", "ratings", ["center_id", "period"])


def downgrade() -> None:
    tables = [
        "api_key_scopes",
        "api_keys",
        "import_logs",
        "system_settings",
        "audit_logs",
        "translations",
        "sms_logs",
        "notification_logs",
        "notifications",
        "reports",
        "report_templates",
        "monthly_statistics",
        "ai_analysis_logs",
        "ai_predictions",
        "certificate_verifications",
        "certificates",
        "rating_history",
        "ratings",
        "rating_formula_versions",
        "attendance",
        "enrollments",
        "group_schedule",
        "groups",
        "courses",
        "license_history",
        "branches",
        "teacher_subjects",
        "teachers",
        "subjects",
        "student_consents",
        "students",
        "guardians",
        "otp_challenges",
        "mfa_recovery_codes",
        "password_history",
        "password_reset_tokens",
        "login_audit_log",
        "refresh_tokens",
        "sessions",
        "role_permissions",
        "users",
        "training_centers",
        "mahallas",
        "regions",
        "files",
        "permissions",
        "roles",
    ]
    op.drop_index("ix_ratings_center_period", table_name="ratings")
    op.drop_index("ix_students_certificate_number", table_name="students")
    op.drop_index("ix_training_centers_name", table_name="training_centers")
    op.drop_index("ix_otp_challenges_phone", table_name="otp_challenges")
    op.drop_index("ix_refresh_tokens_family", table_name="refresh_tokens")
    op.drop_index("ix_users_phone", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    for table in tables:
        op.drop_table(table)
