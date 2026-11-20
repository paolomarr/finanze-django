"""
Settings for a self-hosted demo instance (see deploy_demo.sh / docker-compose.demo.yml).

Same as production (Postgres on host `db`, DEBUG off) but host and HTTPS
settings come from env, so the demo runs both on plain http://localhost and
behind an HTTPS reverse proxy.

  DEMO_ALLOWED_HOSTS   comma-separated, default "localhost,127.0.0.1"
  DEMO_CSRF_ORIGINS    comma-separated full origins, e.g. "https://demo.example.com"
  DEMO_HTTPS           "1" when served over HTTPS (secure cookies + redirect)
"""
from .production import *  # noqa: F401,F403
import os


def _csv(name, default=""):
    return [v.strip() for v in os.environ.get(name, default).split(",") if v.strip()]


ALLOWED_HOSTS = _csv("DEMO_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = CSRF_TRUSTED_ORIGINS + _csv("DEMO_CSRF_ORIGINS")  # noqa: F405

_https = os.environ.get("DEMO_HTTPS") == "1"
SECURE_SSL_REDIRECT = _https
SESSION_COOKIE_SECURE = _https
CSRF_COOKIE_SECURE = _https

# Offline fictional market (tradinglog/demo): no RapidAPI key needed.
FINANCE_PROVIDER = "demo"
