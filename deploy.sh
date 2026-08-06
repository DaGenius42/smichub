#!/usr/bin/env bash

set -Eeuo pipefail

# ============================================================
# YOUR VERIFIED VPS SETTINGS
# ============================================================

VPS="root@smichub.org"

PROJECT_DIR="/var/www/SMICHUB"
SERVICE_NAME="smichub"

ENV_FILE="/etc/smichub.env"
VENV_DIR="/var/www/SMICHUB/venv"
DB_FILE="/var/www/SMICHUB/db.sqlite3"

BACKUP_DIR="/root/smichubbackup"
DOMAIN="smichub.org"

# ============================================================
# MOVE INTO THE LOCAL PROJECT DIRECTORY
# ============================================================

# This ensures the script works even when launched from another folder.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo
echo "=========================================="
echo "Deploying SMICHUB"
echo "=========================================="

# ============================================================
# 1. CHECK THE LOCAL PROJECT
# ============================================================

if [[ ! -f "manage.py" ]]; then
    echo "ERROR: manage.py was not found."
    echo "Place deploy.sh in the same folder as manage.py."
    exit 1
fi

echo
echo "1. Finding the local Python environment..."

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
    echo "ERROR: No local Python interpreter was found."
    exit 1
fi

echo "Using: $LOCAL_PYTHON"

echo
echo "2. Running local Django checks..."

"$LOCAL_PYTHON" manage.py check

echo
echo "3. Running local tests..."

"$LOCAL_PYTHON" manage.py test

# ============================================================
# 2. VERIFY THE VPS BEFORE CHANGING ANYTHING
# ============================================================

echo
echo "4. Checking the VPS configuration..."

ssh "$VPS" bash -s -- \
    "$PROJECT_DIR" \
    "$SERVICE_NAME" \
    "$ENV_FILE" \
    "$VENV_DIR" \
    "$DB_FILE" <<'REMOTE_CHECK'

set -Eeuo pipefail

PROJECT_DIR="$1"
SERVICE_NAME="$2"
ENV_FILE="$3"
VENV_DIR="$4"
DB_FILE="$5"

check_path() {
    local path="$1"
    local description="$2"

    if [[ ! -e "$path" ]]; then
        echo "ERROR: $description was not found:"
        echo "$path"
        exit 1
    fi
}

check_path "$PROJECT_DIR" "Project directory"
check_path "$PROJECT_DIR/manage.py" "manage.py"
check_path "$ENV_FILE" "Environment file"
check_path "$VENV_DIR/bin/python" "Virtual-environment Python"
check_path "$DB_FILE" "SQLite database"

if ! systemctl cat "$SERVICE_NAME" >/dev/null 2>&1; then
    echo "ERROR: systemd service was not found:"
    echo "$SERVICE_NAME"
    exit 1
fi

if ! command -v sqlite3 >/dev/null 2>&1; then
    echo "ERROR: sqlite3 is not installed on the VPS."
    echo "Install it once with:"
    echo "apt update && apt install -y sqlite3"
    exit 1
fi

echo "VPS configuration looks correct."
REMOTE_CHECK

# ============================================================
# 3. BACK UP THE PRODUCTION DATABASE
# ============================================================

echo
echo "5. Backing up the production database..."

ssh "$VPS" bash -s -- \
    "$DB_FILE" \
    "$BACKUP_DIR" <<'REMOTE_BACKUP'

set -Eeuo pipefail

DB_FILE="$1"
BACKUP_DIR="$2"

mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/db-before-deploy-$TIMESTAMP.sqlite3"

sqlite3 "$DB_FILE" ".backup '$BACKUP_FILE'"

RESULT="$(sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;")"

if [[ "$RESULT" != "ok" ]]; then
    echo "ERROR: The database backup failed its integrity check."
    rm -f "$BACKUP_FILE"
    exit 1
fi

echo "Database backup created:"
echo "$BACKUP_FILE"
REMOTE_BACKUP

# ============================================================
# 4. UPLOAD LOCAL CODE
# ============================================================

echo
echo "6. Uploading project files..."

rsync -avz \
    --exclude ".git/" \
    --exclude ".github/" \
    --exclude ".venv/" \
    --exclude "venv/" \
    --exclude "db.sqlite3" \
    --exclude "db.sqlite3-*" \
    --exclude "*.sqlite3" \
    --exclude "staticfiles/" \
    --exclude "media/" \
    --exclude "__pycache__/" \
    --exclude "*.pyc" \
    --exclude ".env" \
    --exclude ".env.*" \
    --exclude "*.env" \
    --exclude ".vscode/" \
    --exclude ".idea/" \
    --exclude ".DS_Store" \
    --exclude "settings.py" \
    ./ "$VPS:$PROJECT_DIR/"

# ============================================================
# 5. UPDATE DJANGO ON THE VPS
# ============================================================

echo
echo "7. Updating Django on the VPS..."

ssh "$VPS" bash -s -- \
    "$PROJECT_DIR" \
    "$SERVICE_NAME" \
    "$ENV_FILE" \
    "$VENV_DIR" <<'REMOTE_DEPLOY'

set -Eeuo pipefail

PROJECT_DIR="$1"
SERVICE_NAME="$2"
ENV_FILE="$3"
VENV_DIR="$4"

cd "$PROJECT_DIR"

set -a
source "$ENV_FILE"
set +a

PYTHON="$VENV_DIR/bin/python"

echo
echo "Installing dependencies..."

if [[ -f "requirements.txt" ]]; then
    "$PYTHON" -m pip install -r requirements.txt
else
    echo "No requirements.txt found; skipping dependency installation."
fi

echo
echo "Running production Django check..."

"$PYTHON" manage.py check

echo
echo "Applying database migrations..."

"$PYTHON" manage.py migrate --noinput

echo
echo "Collecting static files..."

"$PYTHON" manage.py collectstatic --noinput

echo
echo "Restarting $SERVICE_NAME..."

systemctl restart "$SERVICE_NAME"

if ! systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "ERROR: The service did not start successfully."
    echo
    systemctl status "$SERVICE_NAME" --no-pager || true
    echo
    journalctl -u "$SERVICE_NAME" -n 80 --no-pager || true
    exit 1
fi

echo "Service is running."
REMOTE_DEPLOY

# ============================================================
# 6. CHECK THE PUBLIC WEBSITE
# ============================================================

echo
echo "8. Checking the public website..."

# Wait briefly for Gunicorn to finish starting.
sleep 2

if ! curl \
    --fail \
    --silent \
    --show-error \
    --max-time 20 \
    "https://$DOMAIN/" \
    > /dev/null
then
    echo
    echo "ERROR: Deployment commands completed, but the website check failed."
    echo
    echo "Inspect the service with:"
    echo "ssh $VPS 'journalctl -u $SERVICE_NAME -n 100 --no-pager'"
    exit 1
fi

echo
echo "=========================================="
echo "Deployment completed successfully"
echo "https://$DOMAIN"
echo "=========================================="