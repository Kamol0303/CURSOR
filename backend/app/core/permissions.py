MANDATORY_MFA_ROLES = {"super_admin", "hokimiyat_operator", "center_director"}

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "super_admin": [
        "centers.create",
        "centers.read",
        "centers.update",
        "centers.delete",
        "students.create",
        "students.read",
        "students.update",
        "students.delete",
        "ratings.view",
        "reports.generate",
        "system.settings",
        "audit.read",
    ],
    "hokimiyat_operator": [
        "centers.read",
        "students.read",
        "ratings.view",
        "reports.generate",
        "audit.read",
    ],
    "center_director": [
        "centers.read",
        "centers.update",
        "students.create",
        "students.read",
        "students.update",
        "ratings.view",
        "reports.generate",
    ],
    "center_admin": [
        "centers.read",
        "students.create",
        "students.read",
        "students.update",
        "ratings.view",
    ],
    "teacher": [
        "students.read",
        "ratings.view",
    ],
    "auditor": [
        "centers.read",
        "students.read",
        "ratings.view",
        "reports.generate",
        "audit.read",
        "pinfl.reveal",
    ],
    "parent": [
        "students.read",
        "ratings.view",
    ],
    "external_api": [
        "aggregate_stats.read",
    ],
}

ROLE_DEFINITIONS = [
    ("super_admin", "Super administrator", "Super administrator", "Super administrator"),
    ("hokimiyat_operator", "Hokimiyat operatori", "Оператор хокимията", "Hokimiyat operator"),
    ("center_director", "Markaz direktori", "Директор центра", "Center director"),
    ("center_admin", "Markaz administratori", "Администратор центра", "Center admin"),
    ("teacher", "O'qituvchi", "Учитель", "Teacher"),
    ("auditor", "Auditor", "Аудитор", "Auditor"),
    ("parent", "Ota-ona", "Родитель", "Parent/Guardian"),
    ("external_api", "Tashqi API", "Внешний API", "External API consumer"),
]
