"""
Configuración central — agnóstica del cliente.

Lee de env vars con defaults seguros. Funciona local Y en GitHub Actions.
Branding y vocabulario viven en módulos separados (branding_config / domain_config).
"""

import os

from branding_config import (  # noqa: F401  (re-exportadas para imports legacy)
    BRAND_NAME, BRAND_TAGLINE, ADMIN_EMAIL, MAIL_FROM_NAME, MAIL_FROM_ADDRESS,
    DASHBOARD_URL, PRIMARY_COLOR, ACCENT_COLOR, LOGO_URL,
    mail_footer_text, mail_footer_html,
)
from domain_config import (  # noqa: F401
    INPUT_SINGULAR, INPUT_PLURAL, OUTPUT_SINGULAR, OUTPUT_PLURAL,
    ASSIGNEE_SINGULAR, ASSIGNEE_PLURAL, PROJECT_SINGULAR, PROJECT_PLURAL,
    ACTION_VERB, ACTION_DONE, INPUT_FOLDER_NAMES, INPUT_EXTS,
    n_inputs, n_outputs, n_projects,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# OAuth (modo local). En cloud todo viene por env vars.
CLIENT_SECRETS_FILE = os.environ.get(
    "CLIENT_SECRETS_FILE",
    os.path.join(BASE_DIR, "client_secrets.json"),
)
TOKEN_FILE = os.environ.get(
    "TOKEN_FILE",
    os.path.join(BASE_DIR, "token.json"),
)

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

# ─── Google Sheet de matching (proyecto → responsable) ────────────────────────
# Sheet donde está la tabla "qué proyecto le toca a quién".
SHEET_ID = os.environ.get("SHEET_ID", "")
SHEET_TAB = os.environ.get("SHEET_TAB", "Sheet1")
SHEET_HEADER_ROW = int(os.environ.get("SHEET_HEADER_ROW", "1"))

# ─── Aliases de compatibilidad ────────────────────────────────────────────────
# Nombres legacy que el scanner/closer todavía usan internamente.
PACKS_TAB = SHEET_TAB
PACKS_HEADER_ROW = SHEET_HEADER_ROW
VIDEO_EXTS = INPUT_EXTS
RAW_SUBFOLDER_NAMES = INPUT_FOLDER_NAMES

# ─── Notificaciones ───────────────────────────────────────────────────────────
# Modo prueba: redirigir TODOS los mails a esta dirección.
TEST_EMAIL = os.environ.get("TEST_EMAIL", "")

# ─── DB ───────────────────────────────────────────────────────────────────────
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "tracker.db"))
