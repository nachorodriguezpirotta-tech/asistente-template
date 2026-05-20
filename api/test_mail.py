"""
POST /api/test_mail

Manda un mail de test al admin para verificar que la cuenta de envío funciona.
Usa BRAND_NAME / ADMIN_EMAIL / MAIL_FROM_NAME del cliente (env vars).
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api._shared import json_response  # type: ignore


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        # Import perezoso: solo cuando se llama (sino el module-level falla en dev)
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from mail_client import send_mail  # type: ignore
            from branding_config import BRAND_NAME, ADMIN_EMAIL, MAIL_FROM_NAME, DASHBOARD_URL  # type: ignore
        except Exception as e:
            return json_response(self, {"error": f"Config: {e}"}, 500)

        if not ADMIN_EMAIL:
            return json_response(self, {"error": "ADMIN_EMAIL no seteado"}, 400)

        try:
            subject = f"✅ Test desde {BRAND_NAME}"
            text = f"""¡Hola!

Este es un mail de prueba de {BRAND_NAME}.

Si lo estás viendo, el sistema puede enviar notificaciones correctamente.
A partir de ahora, cuando tu equipo suba archivos a Drive, te llegará un mail
similar a este con los detalles del trabajo nuevo.

Dashboard: {DASHBOARD_URL}

— {BRAND_NAME}
"""
            html = f"""<html><body style="font-family:-apple-system,Segoe UI,sans-serif;max-width:600px;color:#222;line-height:1.6;">
<h2 style="color:#ff6b35;">✅ Test desde {BRAND_NAME}</h2>
<p>¡Hola!</p>
<p>Este es un mail de prueba de <strong>{BRAND_NAME}</strong>.</p>
<p>Si lo estás viendo, el sistema puede enviar notificaciones correctamente.</p>
<p>A partir de ahora, cuando tu equipo suba archivos a Drive, te llegará un mail
similar a este con los detalles del trabajo nuevo.</p>
<p style="margin-top:24px;"><a href="{DASHBOARD_URL}" style="background:#ff6b35;color:white;padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:600;">Ir al dashboard</a></p>
<hr style="border:none;border-top:1px solid #eee;margin:24px 0;">
<p style="color:#888;font-size:12px;">— {BRAND_NAME}</p>
</body></html>"""

            msg_id = send_mail(
                to=ADMIN_EMAIL,
                subject=subject,
                body_text=text,
                body_html=html,
                from_name=MAIL_FROM_NAME or BRAND_NAME,
                kind="test",
            )
            return json_response(self, {"ok": True, "msg_id": msg_id, "to": ADMIN_EMAIL})
        except Exception as e:
            return json_response(self, {"error": f"Falló envío: {e}"}, 500)
