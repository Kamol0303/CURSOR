#!/usr/bin/env bash
# Install systemd timer for daily PostgreSQL backups (on-prem Linux).
# Usage: sudo ./scripts/install-backup-timer.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_SCRIPT="$REPO_ROOT/scripts/backup_postgres.sh"
ENV_FILE="${BACKUP_ENV_FILE:-$REPO_ROOT/.env.production}"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

if [[ ! -f "$BACKUP_SCRIPT" ]]; then
  echo "Backup script not found: $BACKUP_SCRIPT" >&2
  exit 1
fi

chmod +x "$BACKUP_SCRIPT"

cat > /etc/systemd/system/tmb-postgres-backup.service <<EOF
[Unit]
Description=TMB PostgreSQL backup
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$REPO_ROOT
EnvironmentFile=-$ENV_FILE
Environment=PGHOST=\${PGHOST:-localhost}
Environment=PGPORT=\${PGPORT:-5432}
ExecStart=$BACKUP_SCRIPT /var/backups/tmb
StandardOutput=journal
StandardError=journal
EOF

cat > /etc/systemd/system/tmb-postgres-backup.timer <<EOF
[Unit]
Description=Daily TMB PostgreSQL backup

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now tmb-postgres-backup.timer

echo "Installed tmb-postgres-backup.timer (daily 02:00)."
echo "Check status: systemctl status tmb-postgres-backup.timer"
echo "Manual run:   systemctl start tmb-postgres-backup.service"
