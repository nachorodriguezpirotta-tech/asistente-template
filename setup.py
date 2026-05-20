#!/usr/bin/env python3
"""
Setup interactivo para implementar el template a un cliente nuevo.

Hace dos cosas:
  1. Pregunta los valores de branding/dominio del cliente.
  2. Genera dos archivos:
       - .env             → variables de entorno para correr local
       - .env.deploy.txt  → resumen pegable en GitHub Secrets + Vercel env vars
  3. Reemplaza los placeholders __BRAND_NAME__, __DASHBOARD_URL__, etc. en
     los archivos HTML/JSON estáticos.

Uso:
    python3 setup.py
"""

import os
import sys
import secrets
from pathlib import Path

BASE = Path(__file__).parent
PRESETS_DIR = BASE / "presets"


def _load_preset(name: str) -> dict:
    """Lee un .env de presets/ y devuelve dict de var→value."""
    path = PRESETS_DIR / f"{name}.env"
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip()
    return out


def _pick_preset() -> dict:
    """Ofrece presets disponibles. Devuelve dict con overrides o vacío."""
    presets = sorted(p.stem for p in PRESETS_DIR.glob("*.env")) if PRESETS_DIR.exists() else []
    if not presets:
        return {}
    print("\n  Presets disponibles (autocompletan vocabulario + Drive):")
    for i, name in enumerate(presets, 1):
        print(f"    {i}. {name}")
    print(f"    0. ninguno (custom)")
    while True:
        choice = input("  Elegí preset [0]: ").strip() or "0"
        if choice == "0":
            return {}
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(presets):
                name = presets[idx]
                print(f"  ✓ Usando preset: {name}")
                return _load_preset(name)
        except ValueError:
            pass
        print("    (inválido)")


def ask(prompt: str, default: str = "", required: bool = False) -> str:
    suffix = f" [{default}]" if default else (" *" if required else "")
    while True:
        val = input(f"  {prompt}{suffix}: ").strip()
        if not val:
            val = default
        if required and not val:
            print("    (requerido — no puede ir vacío)")
            continue
        return val


def section(title: str):
    print(f"\n━━━ {title} ━━━")


def main():
    print("=" * 60)
    print(" Setup de instancia nueva")
    print("=" * 60)

    section("1. Branding (cómo se llama y se ve)")
    brand_name = ask("Nombre comercial (ej. Asistente Acme)", required=True)
    brand_short = ask("Nombre corto para PWA (ej. Acme)", default=brand_name.split()[0])
    brand_tagline = ask("Tagline / subtítulo", default="Sistema de seguimiento de proyectos")
    primary_color = ask("Color primario (hex)", default="#000000")
    accent_color = ask("Color de acento (hex)", default="#3b82f6")

    section("2. Contacto")
    admin_email = ask("Email del admin (recibe resúmenes globales)", required=True)
    mail_from_name = ask("Nombre de remitente en mails", default=brand_name)
    mail_from_address = ask("Cuenta Gmail desde la que se envían mails (ej. asistente@acme.com)", required=True)

    section("3. Vocabulario del negocio")
    preset = _pick_preset()
    if preset:
        input_singular = preset.get("INPUT_SINGULAR", "archivo")
        input_plural = preset.get("INPUT_PLURAL", input_singular + "s")
        output_singular = preset.get("OUTPUT_SINGULAR", "entrega")
        output_plural = preset.get("OUTPUT_PLURAL", output_singular + "s")
        assignee_singular = preset.get("ASSIGNEE_SINGULAR", "responsable")
        assignee_plural = preset.get("ASSIGNEE_PLURAL", assignee_singular + "s")
        project_singular = preset.get("PROJECT_SINGULAR", "proyecto")
        project_plural = preset.get("PROJECT_PLURAL", project_singular + "s")
        input_folders = preset.get("INPUT_FOLDER_NAMES", "material,raw,crudos,input")
        input_exts = preset.get("INPUT_EXTS", ".mp4,.mov,.avi,.mkv,.m4v,.webm")
    else:
        print("  Cómo se llaman las cosas en este negocio.")
        input_singular = ask("Input singular", default="archivo")
        input_plural = ask("Input plural", default=input_singular + "s")
        output_singular = ask("Output singular", default="entrega")
        output_plural = ask("Output plural", default=output_singular + "s")
        assignee_singular = ask("Responsable singular", default="responsable")
        assignee_plural = ask("Responsable plural", default=assignee_singular + "s")
        project_singular = ask("Proyecto singular", default="proyecto")
        project_plural = ask("Proyecto plural", default=project_singular + "s")

        section("4. Drive")
        print("  Carpetas donde se suben los inputs (separar con coma).")
        input_folders = ask("Nombres de carpetas de input", default="material,raw,crudos,input")
        print("  Extensiones de archivo válidas (con punto, separadas con coma).")
        input_exts = ask("Extensiones válidas", default=".mp4,.mov,.avi,.mkv,.m4v,.webm")

    section("5. Google Sheet (matching proyecto → responsable)")
    sheet_id = ask("Google Sheet ID (de la URL: /d/<ESTE>/edit)", required=True)
    sheet_tab = ask("Nombre de la pestaña", default="Sheet1")
    sheet_header_row = ask("Número de fila del header", default="1")
    sheet_col_project = ask("Nombre de columna del proyecto/cliente", default="cliente")
    sheet_col_assignee = ask("Nombre de columna del responsable", default="responsable")

    section("6. Deploy (Vercel + GitHub)")
    dashboard_url = ask("URL pública del dashboard (ej. https://asistente-acme.vercel.app)", required=True)
    github_owner = ask("GitHub owner (usuario u org del repo)", required=True)
    github_repo = ask("Nombre del repo en GitHub", required=True)

    section("7. Secrets (se generan automáticamente)")
    dashboard_secret = secrets.token_urlsafe(32)
    print(f"  ✓ DASHBOARD_SECRET generado")

    # ─── Generar .env ──────────────────────────────────────────────────────
    env_lines = [
        "# ─── Branding ────────────────────────────────────────────",
        f"BRAND_NAME={brand_name}",
        f"BRAND_TAGLINE={brand_tagline}",
        f"PRIMARY_COLOR={primary_color}",
        f"ACCENT_COLOR={accent_color}",
        "",
        "# ─── Contacto ────────────────────────────────────────────",
        f"ADMIN_EMAIL={admin_email}",
        f"MAIL_FROM_NAME={mail_from_name}",
        f"MAIL_FROM_ADDRESS={mail_from_address}",
        "",
        "# ─── Vocabulario ─────────────────────────────────────────",
        f"INPUT_SINGULAR={input_singular}",
        f"INPUT_PLURAL={input_plural}",
        f"OUTPUT_SINGULAR={output_singular}",
        f"OUTPUT_PLURAL={output_plural}",
        f"ASSIGNEE_SINGULAR={assignee_singular}",
        f"ASSIGNEE_PLURAL={assignee_plural}",
        f"PROJECT_SINGULAR={project_singular}",
        f"PROJECT_PLURAL={project_plural}",
        "",
        "# ─── Drive ───────────────────────────────────────────────",
        f"INPUT_FOLDER_NAMES={input_folders}",
        f"INPUT_EXTS={input_exts}",
        "",
        "# ─── Sheet ───────────────────────────────────────────────",
        f"SHEET_ID={sheet_id}",
        f"SHEET_TAB={sheet_tab}",
        f"SHEET_HEADER_ROW={sheet_header_row}",
        f"SHEET_COL_PROJECT={sheet_col_project}",
        f"SHEET_COL_ASSIGNEE={sheet_col_assignee}",
        "",
        "# ─── Deploy ──────────────────────────────────────────────",
        f"DASHBOARD_URL={dashboard_url}",
        f"GITHUB_OWNER={github_owner}",
        f"GITHUB_REPO={github_repo}",
        f"GITHUB_REPO_FULL={github_owner}/{github_repo}",
        "",
        "# ─── Secrets ─────────────────────────────────────────────",
        f"DASHBOARD_SECRET={dashboard_secret}",
        f"VAPID_SUBJECT=mailto:{admin_email}",
        "",
        "# ─── Por completar después del OAuth y key generation ────",
        "# OAUTH_REFRESH_TOKEN=...   (de python3 auth.py)",
        "# OAUTH_CLIENT_ID=...",
        "# OAUTH_CLIENT_SECRET=...",
        "# VAPID_PRIVATE_KEY=...     (generar con web-push CLI)",
        "# GITHUB_PAT=...            (token con permiso 'contents:write')",
    ]

    env_file = BASE / ".env"
    env_file.write_text("\n".join(env_lines) + "\n", encoding="utf-8")
    print(f"\n✅ .env generado en {env_file}")

    # ─── Reemplazar placeholders en HTMLs ──────────────────────────────────
    print("\n→ Reemplazando placeholders en archivos estáticos…")
    replacements = {
        "__BRAND_NAME__": brand_name,
        "__BRAND_SHORT__": brand_short,
        "__DASHBOARD_URL__": dashboard_url.rstrip("/"),
    }
    static_files = list(BASE.glob("*.html")) + [BASE / "manifest.json"]
    for f in static_files:
        if not f.exists():
            continue
        content = f.read_text(encoding="utf-8")
        original = content
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        if content != original:
            f.write_text(content, encoding="utf-8")
            print(f"   ✓ {f.name}")

    # ─── Resumen ───────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(" Próximos pasos")
    print("=" * 60)
    print("""
  1. Configurar Google OAuth para este cliente:
       python3 auth.py
       (esto genera token.json + imprime los valores OAuth_*)

  2. Configurar Gmail OAuth para enviar mails desde la cuenta del cliente:
       python3 auth_mail.py

  3. Hacer baseline inicial (snapshot del estado HOY = ya conocido):
       python3 baseline.py

  4. Probar el scan local:
       python3 scan_incremental.py

  5. Deploy:
       a. Crear repo en GitHub: {owner}/{repo}
       b. git init && git add . && git commit -m "init" && git push
       c. Subir secrets a GitHub: cat .env (los valores OAUTH_*, VAPID_*, GITHUB_PAT)
       d. Deploy a Vercel apuntando al repo
       e. Setear las mismas env vars en Vercel project settings

  6. Cargar responsables del cliente en /config del dashboard.

  Toda la guía detallada está en README.md.
""".format(owner=github_owner, repo=github_repo))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelado.")
        sys.exit(1)
