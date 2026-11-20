#!/bin/bash
# Deploy a self-contained demo instance (docker-compose.demo.yml), no prompts.
#
# First run writes .env.demo with a random SECRET_KEY and admin password;
# edit it afterwards to change hosts, HTTPS or credentials.
#
#   ./deploy_demo.sh             build and start (seeds data on first start)
#   ./deploy_demo.sh --wipe      drop the demo database first, then start fresh
#
# DEMO_PORT (default 8004) and DEMO_BIND (default 127.0.0.1; use 0.0.0.0 to
# expose it) are read from the calling environment.
set -euo pipefail

SCRIPT_ROOT=$(cd "$(dirname "$0")"; pwd)
ENV_FILE=$SCRIPT_ROOT/.env.demo
COMPOSE=(docker compose -f "$SCRIPT_ROOT/docker-compose.demo.yml")
WIPE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
    --wipe) WIPE=1;;
    *) echo "Unknown argument $1" >&2; exit 1;;
    esac
    shift
done

rand() { openssl rand -hex "$1" 2>/dev/null || head -c "$1" /dev/urandom | od -An -tx1 | tr -d ' \n'; }

if [[ ! -f $ENV_FILE ]]; then
    ADMIN_PASSWORD=$(rand 8)
    cat > "$ENV_FILE" <<EOF
DJANGO_SETTINGS_MODULE=finanze.settings.demo
SECRET_KEY=$(rand 32)
DEMO_MODE=1
RAPIDAPI_KEY=not_available

DEMO_USERNAME=demo
DEMO_PASSWORD=demo
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=$ADMIN_PASSWORD
DJANGO_SUPERUSER_EMAIL=

# For a public deployment behind an HTTPS proxy, e.g.:
# DEMO_ALLOWED_HOSTS=demo.example.com
# DEMO_CSRF_ORIGINS=https://demo.example.com
# DEMO_HTTPS=1
DEMO_ALLOWED_HOSTS=localhost,127.0.0.1
EOF
    echo "[INFO] Created $ENV_FILE (admin password: $ADMIN_PASSWORD)" >&2
else
    echo "[INFO] Using existing $ENV_FILE" >&2
fi

if [[ $WIPE == 1 ]]; then
    "${COMPOSE[@]}" down -v
fi

"${COMPOSE[@]}" up -d --build

echo "[INFO] Demo starting on http://${DEMO_BIND:-127.0.0.1}:${DEMO_PORT:-8004}/ - login: demo / demo (see $ENV_FILE)" >&2
