"""
Health check — verifica que el sistema esté corriendo.

Lógica:
  - Mira el último 'first_seen_at' o 'last_scan_at' en la DB
  - Si pasaron más de 90 minutos sin actividad → manda mail de alerta
  - Si no hay nada en la DB, asume primer run → no alerta

Diseñado para correr cada 1 hora vía GitHub Actions.
"""

import os
import sys
from datetime import datetime, timedelta

from config import TEST_EMAIL, ADMIN_EMAIL, BRAND_NAME
from tracker import get_conn
from mail_client import send_mail


_ADMIN_EMAIL = TEST_EMAIL or ADMIN_EMAIL
_GH_REPO = os.environ.get("GITHUB_REPO_FULL", "")  # ej. "user/asistente-cliente"

ALERT_THRESHOLD_MIN = 90  # > 90 minutos sin actividad = alerta


def _parse_iso(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "").split(".")[0])
    except Exception:
        return None


def run():
    print("🩺 Health check del sistema")
    conn = get_conn()

    # El indicador más confiable: cuándo se vio el último cambio de drive page_token
    # (se actualiza en cada scan incremental).
    row = conn.execute(
        "SELECT value, updated_at FROM meta WHERE key='drive_changes_page_token'"
    ).fetchone()

    last_activity = None
    if row and row["updated_at"]:
        last_activity = _parse_iso(row["updated_at"])

    # Backup: último known_file insertado
    if not last_activity:
        row = conn.execute("SELECT MAX(first_seen_at) as ts FROM known_files").fetchone()
        if row and row["ts"]:
            last_activity = _parse_iso(row["ts"])

    conn.close()

    if not last_activity:
        print("   (Sin actividad registrada, sistema nuevo. Skip alerta.)")
        return

    now = datetime.now()
    minutes_since = (now - last_activity).total_seconds() / 60
    print(f"   Última actividad: {last_activity.isoformat()} ({minutes_since:.0f} min atrás)")

    if minutes_since < ALERT_THRESHOLD_MIN:
        print(f"   ✅ OK (< {ALERT_THRESHOLD_MIN} min)")
        return

    # ALERTA
    hours = minutes_since / 60
    subject = f"🚨 {BRAND_NAME}: sin actividad hace {hours:.1f} horas"
    actions_link = f"https://github.com/{_GH_REPO}/actions" if _GH_REPO else "(repo de GitHub Actions)"
    text = f"""ALERTA del sistema:

{BRAND_NAME} no registra actividad desde hace {hours:.1f} horas.

Última actividad detectada: {last_activity.isoformat()}

Posibles causas:
- Workflows de GitHub Actions fallando ({actions_link})
- Credenciales OAuth expiradas
- API de Drive caída

— {BRAND_NAME} Health Check
"""
    html = f"""<html><body style="font-family:-apple-system,Segoe UI,sans-serif;max-width:600px;color:#222;">
<h2 style="color:#dc2626;">🚨 Sistema sin actividad</h2>
<p>{BRAND_NAME} no registra actividad desde hace <strong>{hours:.1f} horas</strong>.</p>
<p>Última actividad detectada: <code>{last_activity.isoformat()}</code></p>
<h3>Posibles causas:</h3>
<ul>
<li>Workflows de GitHub Actions fallando</li>
<li>Credenciales OAuth expiradas</li>
<li>API de Drive caída</li>
</ul>
<p><a href="{actions_link}">Ver Actions</a></p>
</body></html>"""

    try:
        msg_id = send_mail(to=_ADMIN_EMAIL, subject=subject, body_text=text, body_html=html)
        print(f"   📧 Alerta enviada: {msg_id}")
    except Exception as e:
        print(f"   ❌ Falló envío alerta: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
