"""
GET /api/needs_setup

Devuelve true si el cliente todavía no completó el welcome wizard
(o sea, no hay responsables cargados en cfg_editors).

El index.html lo consulta al inicio; si true, redirige a /welcome.
"""

import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api._shared import read_db, json_response  # type: ignore


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            def _check(conn):
                # Existen las tablas cfg_*?
                tables = [r[0] for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='cfg_editors'"
                ).fetchall()]
                if "cfg_editors" not in tables:
                    return True  # DB sin schema = primera vez
                # ¿Hay editores activos?
                n = conn.execute(
                    "SELECT COUNT(*) FROM cfg_editors WHERE active=1"
                ).fetchone()[0]
                return n == 0

            needs = read_db(_check)
            return json_response(self, {"needs_setup": bool(needs)})
        except Exception as e:
            # En caso de error, asumir que NO necesita setup (no romper el dashboard)
            return json_response(self, {"needs_setup": False, "error": str(e)})
