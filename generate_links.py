"""
Genera URLs únicos por responsable para mandar por WhatsApp/mail.

Después del deploy:
    DASHBOARD_SECRET="..." VERCEL_URL="https://..." python3 generate_links.py

Los responsables salen de la env var EDITORS (separados por coma).
"""

import os
import sys
import hashlib
import hmac


def make_token(editor: str, secret: str) -> str:
    return hmac.new(
        secret.encode(),
        editor.lower().encode(),
        hashlib.sha256,
    ).hexdigest()[:16]


def main():
    secret = os.environ.get("DASHBOARD_SECRET", "")
    base_url = os.environ.get("DASHBOARD_URL") or os.environ.get("VERCEL_URL", "")
    editors_env = os.environ.get("EDITORS", "")
    editors = [e.strip() for e in editors_env.split(",") if e.strip()]

    if not secret:
        print("❌ Falta DASHBOARD_SECRET.")
        print("   Ejemplo: DASHBOARD_SECRET='...' python3 generate_links.py")
        sys.exit(1)

    if not base_url:
        base_url = "https://TU-PROYECTO.vercel.app"
        print("⚠️  DASHBOARD_URL no seteada. Reemplazá 'TU-PROYECTO' por tu dominio real.\n")

    if not editors:
        print("⚠️  EDITORS no seteado. Pasá lista separada por coma:")
        print("   EDITORS='Juan,Maria,Pedro' python3 generate_links.py\n")
        sys.exit(1)

    base_url = base_url.rstrip("/")
    print(f"🔗 Links únicos por responsable (base: {base_url})\n")
    print("-" * 70)
    print()

    for editor in editors:
        token = make_token(editor, secret)
        url = f"{base_url}/?editor={editor}&t={token}"
        print(f"  📩 {editor}")
        print(f"     {url}")
        print()

    admin_token = make_token("ADMIN", secret)
    admin_url = f"{base_url}/?admin=1&t={admin_token}"
    print("-" * 70)
    print(f"  👑 Admin")
    print(f"     {admin_url}")
    print()


if __name__ == "__main__":
    main()
