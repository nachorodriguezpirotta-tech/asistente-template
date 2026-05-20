"""
POST /api/setup_team
Body: { team: [{name, email}, ...] }

Carga los responsables iniciales en cfg_editors. Es el primer paso del wizard
de welcome para el cliente. Después de esto el dashboard está listo para usar.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api._shared import with_db, json_response  # type: ignore


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return json_response(self, {"error": "Body vacío"}, 400)
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return json_response(self, {"error": "JSON inválido"}, 400)

        team = data.get("team") or []
        if not isinstance(team, list) or not team:
            return json_response(self, {"error": "Falta team (lista de {name, email})"}, 400)

        # Validar cada miembro
        clean_team = []
        for m in team:
            name = (m.get("name") or "").strip()
            email = (m.get("email") or "").strip().lower()
            if not name or not email:
                continue
            if "@" not in email or "." not in email.split("@")[-1]:
                continue
            clean_team.append({"name": name, "email": email})

        if not clean_team:
            return json_response(self, {"error": "Ningún miembro válido"}, 400)

        # Aplicar a la DB (con el commit+push que hace with_db)
        def _apply(conn):
            from datetime import datetime
            now = datetime.now().isoformat(timespec="seconds")
            for m in clean_team:
                conn.execute("""
                    INSERT INTO cfg_editors
                    (name, email, receives_daily_summary, receives_notifications, active, created_at, updated_at)
                    VALUES (?, ?, 1, 1, 1, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        email=excluded.email,
                        receives_notifications=1,
                        active=1,
                        updated_at=excluded.updated_at
                """, (m["name"], m["email"], now, now))
            return len(clean_team)

        try:
            n = with_db(_apply, message=f"setup_team: {len(clean_team)} responsables")
            return json_response(self, {"ok": True, "added": n})
        except Exception as e:
            return json_response(self, {"error": str(e)}, 500)
