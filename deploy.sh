#!/usr/bin/env bash

set -Eeuo pipefail

VPS="root@smichub.org"

PROJECT_DIR="/var/www/SMICHUB"
SERVICE_NAME="smichub"

ENV_FILE="/etc/smichub.env"
VENV_DIR="/var/www/SMICHUB/venv"
DB_FILE="/var/www/SMICHUB/db.sqlite3"

BACKUP_DIR="/root/smichubbackup"
DOMAIN="smichub.org"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo
echo "=========================================="
echo "        Deploying SMICHUB"
echo "=========================================="

if [[ ! -f "manage.py" ]]; then
    echo "ERROR: manage.py not found."
    echo "deploy.sh must be in the same folder as manage.py."
    exit 1
fi

echo
echo "1. Finding local Python..."
"""
if [[ -x ".venv/Scripts/python.exe" ]]; then
    LOCAL_PYTHON=".venv/Scripts/python.exe"
elif [[ -x "venv/Scripts/python.exe" ]]; then
    LOCAL_PYTHON="venv/Scripts/python.exe"
elif [[ -x ".venv/bin/python" ]]; then
    LOCAL_PYTHON=".venv/bin/python"
elif [[ -x "venv/bin/python" ]]; then
    LOCAL_PYTHON="venv/bin/python"
elif command -v python >/dev/null 2>&1; then
    LOCAL_PYTHON="python"
elif command -v python3 >/dev/null 2>&1; then
    LOCAL_PYTHON="python3"
else
    echo "ERROR: Could not find Python."
    exit 1
"""
fi
LOCAL_PYTHON="python3"
echo "Using: $LOCAL_PYTHON"

echo
echo "2. Running local Django check..."
"$LOCAL_PYTHON" manage.py check

echo
echo "3. Running local tests..."
"$LOCAL_PYTHON" manage.py test

echo
echo "4. Checking VPS..."

ssh "$VPS" bash -s --     "$PROJECT_DIR"     "$SERVICE_NAME"     "$ENV_FILE"     "$VENV_DIR"     "$DB_FILE" <<'REMOTE_CHECK'

set -Eeuo pipefail

PROJECT_DIR="$1"
SERVICE_NAME="$2"
ENV_FILE="$3"
VENV_DIR="$4"
DB_FILE="$5"

[[ -d "$PROJECT_DIR" ]] || { echo "ERROR: Project directory missing: $PROJECT_DIR"; exit 1; }
[[ -f "$PROJECT_DIR/manage.py" ]] || { echo "ERROR: manage.py missing on VPS."; exit 1; }
[[ -f "$ENV_FILE" ]] || { echo "ERROR: Environment file missing: $ENV_FILE"; exit 1; }
[[ -x "$VENV_DIR/bin/python" ]] || { echo "ERROR: venv Python missing: $VENV_DIR/bin/python"; exit 1; }
[[ -f "$DB_FILE" ]] || { echo "ERROR: Database missing: $DB_FILE"; exit 1; }

systemctl cat "$SERVICE_NAME" >/dev/null 2>&1 || {
    echo "ERROR: systemd service not found: $SERVICE_NAME"
    exit 1
}

command -v sqlite3 >/dev/null 2>&1 || {
    echo "ERROR: sqlite3 is not installed on VPS."
    echo "Run once: apt update && apt install -y sqlite3"
    exit 1
}

echo "VPS check OK."
REMOTE_CHECK

echo
echo "5. Backing up production database..."

ssh "$VPS" bash -s --     "$DB_FILE"     "$BACKUP_DIR" <<'REMOTE_BACKUP'

set -Eeuo pipefail

DB_FILE="$1"
BACKUP_DIR="$2"

mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/db-before-deploy-$TIMESTAMP.sqlite3"

sqlite3 "$DB_FILE" ".backup '$BACKUP_FILE'"

RESULT="$(sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;")"

if [[ "$RESULT" != "ok" ]]; then
    echo "ERROR: Database backup failed integrity check."
    rm -f "$BACKUP_FILE"
    exit 1
fi

echo "Backup created:"
echo "$BACKUP_FILE"
REMOTE_BACKUP

echo
echo "6. Uploading project files..."

rsync -rtvz     --exclude ".git/"     --exclude ".github/"     --exclude ".venv/"     --exclude "venv/"     --exclude "settings.py"     --exclude "*.sqlite3*"     --exclude "staticfiles/"     --exclude "media/"     --exclude "uploads/"     --exclude "__pycache__/"     --exclude "*.pyc"     --exclude ".env"     --exclude ".env.*"     --exclude "*.env"     --exclude ".vscode/"     --exclude ".idea/"     --exclude ".DS_Store"     --exclude "deploy.sh"     ./ "$VPS:$PROJECT_DIR/"

echo
echo "7. Updating Django on VPS..."

ssh "$VPS" bash -s --     "$PROJECT_DIR"     "$SERVICE_NAME"     "$ENV_FILE"     "$VENV_DIR"     "$DB_FILE" <<'REMOTE_DEPLOY'

set -Eeuo pipefail

PROJECT_DIR="$1"
SERVICE_NAME="$2"
ENV_FILE="$3"
VENV_DIR="$4"
DB_FILE="$5"

PYTHON="$VENV_DIR/bin/python"

cd "$PROJECT_DIR"

set -a
source "$ENV_FILE"
set +a

echo
echo "Fixing production permissions..."

chown root:www-data "$PROJECT_DIR"
chmod 775 "$PROJECT_DIR"

chown www-data:www-data "$DB_FILE"
chmod 664 "$DB_FILE"

if [[ -d "$PROJECT_DIR/media" ]]; then
    chown -R www-data:www-data "$PROJECT_DIR/media"
fi

if [[ -d "$PROJECT_DIR/uploads" ]]; then
    chown -R www-data:www-data "$PROJECT_DIR/uploads"
fi

echo
echo "Installing dependencies..."

if [[ -f "$PROJECT_DIR/requirements.txt" ]]; then
    "$PYTHON" -m pip install -r "$PROJECT_DIR/requirements.txt"
else
    echo "No requirements.txt found; skipping dependency installation."
fi

echo
echo "Running production Django check..."
"$PYTHON" manage.py check

echo
echo "Applying migrations..."
"$PYTHON" manage.py migrate --noinput

echo
echo "Collecting static files..."
"$PYTHON" manage.py collectstatic --noinput

chown root:www-data "$PROJECT_DIR"
chmod 775 "$PROJECT_DIR"

chown www-data:www-data "$DB_FILE"
chmod 664 "$DB_FILE"

echo
echo "Testing production database write access..."

sudo -u www-data sqlite3 "$DB_FILE" 'BEGIN IMMEDIATE; CREATE TABLE __deploy_permission_test__(x INTEGER); ROLLBACK;'

echo "SQLite write test OK."

echo
echo "Restarting $SERVICE_NAME..."
systemctl restart "$SERVICE_NAME"

if ! systemctl is-active --quiet "$SERVICE_NAME"; then
    echo
    echo "ERROR: $SERVICE_NAME failed to start."
    systemctl status "$SERVICE_NAME" --no-pager || true
    echo
    journalctl -u "$SERVICE_NAME" -n 80 --no-pager || true
    exit 1
fi

echo "$SERVICE_NAME is running."
REMOTE_DEPLOY

echo
echo "8. Checking public website..."

sleep 2

if ! curl     --fail     --silent     --show-error     --max-time 20     "https://$DOMAIN/"     > /dev/null
then
    echo
    echo "ERROR: Deployment completed, but public website check failed."
    echo "Check logs with:"
    echo "ssh $VPS"
    echo "journalctl -u $SERVICE_NAME -n 100 --no-pager"
    exit 1
fi

echo
echo "=========================================="
echo "      DEPLOYMENT SUCCESSFUL"
echo "=========================================="
echo
echo "https://$DOMAIN"
