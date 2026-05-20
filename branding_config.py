"""
Branding del cliente — todo lo que es marca/identidad visual/contacto.
Cada cliente setea estas vars en su .env (local) o en GitHub Actions Secrets (cloud).

Si una var no está definida, usa el default (que es genérico).
"""

import os

# ─── Marca ─────────────────────────────────────────────────────────────────────
BRAND_NAME = os.environ.get("BRAND_NAME", "Asistente")
# Aparece en subjects de mail, headers del dashboard, footers, etc.

BRAND_TAGLINE = os.environ.get("BRAND_TAGLINE", "Sistema de seguimiento de proyectos")
# Subtitle del dashboard.

# ─── Contacto ──────────────────────────────────────────────────────────────────
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")
# Dueño del sistema. Recibe resúmenes globales, errores, aprobaciones.

MAIL_FROM_NAME = os.environ.get("MAIL_FROM_NAME", BRAND_NAME)
# Nombre que aparece como remitente.

MAIL_FROM_ADDRESS = os.environ.get("MAIL_FROM_ADDRESS", "")
# Dirección desde la que se envían los mails (Gmail autorizado vía OAuth).

# ─── URL pública del dashboard ─────────────────────────────────────────────────
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://localhost:3000")
# Ej: https://asistente-cliente.vercel.app

# ─── Visual (opcional) ─────────────────────────────────────────────────────────
PRIMARY_COLOR = os.environ.get("PRIMARY_COLOR", "#000000")
ACCENT_COLOR = os.environ.get("ACCENT_COLOR", "#3b82f6")
LOGO_URL = os.environ.get("LOGO_URL", "")


def mail_footer_text() -> str:
    return f"— {BRAND_NAME}"


def mail_footer_html() -> str:
    return f'<p style="color:#888;font-size:12px;">— {BRAND_NAME}</p>'
