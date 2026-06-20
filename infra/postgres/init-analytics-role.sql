-- Read-only role for AI analytics microservice (no PINFL access)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'tamor_analytics') THEN
        CREATE ROLE tamor_analytics WITH LOGIN PASSWORD 'tamor_dev';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE tamor TO tamor_analytics;
GRANT USAGE ON SCHEMA public TO tamor_analytics;

GRANT SELECT ON training_centers, teachers, subjects, teacher_subjects,
    enrollments, groups, rating_history, rating_formula_versions,
    certificates TO tamor_analytics;

GRANT SELECT, INSERT ON ai_predictions, ai_analysis_logs TO tamor_analytics;

-- Students: grant table access but revoke sensitive column via view
REVOKE ALL ON students FROM tamor_analytics;
GRANT SELECT (id, center_id, full_name, date_of_birth, grade, school, graduation_date,
    consent_given_at, is_demo_data, created_at, updated_at, deleted_at) ON students TO tamor_analytics;
