"""
Seeds + helpers de matching: cómo identificar a qué proyecto/responsable
corresponde un archivo o carpeta.

Las constantes de abajo son SEED inicial vacío. Una vez deployado, el cliente
carga su data desde el dashboard /config (que escribe en tabla cfg_*).

Para implementar a un cliente nuevo:
  1. Dejá las constantes vacías (o cargá un seed mínimo si querés que arranque
     con algo).
  2. La primera corrida de tracker.init_db() crea las tablas cfg_* vacías.
  3. El cliente entra a /config y carga sus responsables, apodos, etc.
"""

import unicodedata


# ─── SEED inicial (vacío por defecto) ─────────────────────────────────────────
# Si querés que el cliente arranque con algo, cargalo acá. Si no, dejá vacío.

CLIENT_ALIASES = {
    # "nombre raro en drive": "Nombre Real Proyecto",
}

CLIENT_NICKNAMES = {
    # "apodo": "Nombre Real",
}

CLIENT_NICKNAMES_BY_EDITOR = {
    # ("apodo", "responsable"): "Nombre Real",
}

EDITOR_EMAILS = {
    # "Nombre": "email@cliente.com",
}

DAILY_SUMMARY_EDITORS = set()

EDITORS_LIST = []

CLIENT_DELIVERY_FOLDERS = {
    # "Nombre Real Proyecto": "drive_folder_id",
}


# ─── DB-backed runtime loaders ───────────────────────────────────────────────
# Estas funciones leen de las tablas cfg_* (fuente de verdad runtime).
# Si la DB no está disponible, fallback al SEED de arriba.

def _safe_db_call(fn, default):
    try:
        return fn()
    except Exception:
        return default


def get_editor_emails_runtime() -> dict:
    """Mails de TODOS los responsables activos. Usado para identificar por owner
    de archivo en Drive (clasificador). NO para mandar mails."""
    from tracker import cfg_get_editor_emails
    db = _safe_db_call(cfg_get_editor_emails, None)
    return db if db is not None else dict(EDITOR_EMAILS)


def get_notification_emails_runtime() -> dict:
    """Mails de responsables que SÍ reciben notificaciones."""
    from tracker import cfg_get_notification_emails
    db = _safe_db_call(cfg_get_notification_emails, None)
    if db is not None:
        return db
    out = {}
    for name in DAILY_SUMMARY_EDITORS:
        if name in EDITOR_EMAILS:
            out[name] = EDITOR_EMAILS[name]
    return out


def get_editor_email_for_notification(editor: str):
    if not editor:
        return None
    emails = get_notification_emails_runtime()
    for k, v in emails.items():
        if _normalize(k) == _normalize(editor):
            return v
    return None


def get_editors_list_runtime() -> list:
    from tracker import cfg_get_editors_list
    db = _safe_db_call(cfg_get_editors_list, None)
    return db if db else list(EDITORS_LIST)


def get_daily_summary_editors_runtime() -> set:
    from tracker import cfg_get_daily_summary_editors
    db = _safe_db_call(cfg_get_daily_summary_editors, None)
    return db if db is not None else set(DAILY_SUMMARY_EDITORS)


def get_nicknames_runtime() -> dict:
    from tracker import cfg_get_nicknames
    db = _safe_db_call(cfg_get_nicknames, None)
    return db if db else dict(CLIENT_NICKNAMES)


def get_nicknames_by_editor_runtime() -> dict:
    from tracker import cfg_get_nicknames_by_editor
    db = _safe_db_call(cfg_get_nicknames_by_editor, None)
    return db if db else dict(CLIENT_NICKNAMES_BY_EDITOR)


def get_aliases_runtime() -> dict:
    from tracker import cfg_get_aliases
    db = _safe_db_call(cfg_get_aliases, None)
    return db if db else dict(CLIENT_ALIASES)


def get_delivery_folders_runtime() -> dict:
    from tracker import cfg_get_delivery_folders
    db = _safe_db_call(cfg_get_delivery_folders, None)
    return db if db else dict(CLIENT_DELIVERY_FOLDERS)


def get_editor_email(editor: str):
    if not editor:
        return None
    emails = get_editor_emails_runtime()
    for k, v in emails.items():
        if _normalize(k) == _normalize(editor):
            return v
    return None


def resolve_nickname_static(text: str, editor: str = None) -> str:
    if not text:
        return text
    norm = _normalize(text)

    nicknames_by_editor = get_nicknames_by_editor_runtime()
    nicknames = get_nicknames_runtime()

    if editor:
        norm_editor = _normalize(editor)
        key = (norm, norm_editor)
        if key in nicknames_by_editor:
            return nicknames_by_editor[key]

    return nicknames.get(norm, text)


def _normalize(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(s.lower().split())


def resolve_alias(drive_folder_name: str) -> str:
    if not drive_folder_name:
        return drive_folder_name
    norm = _normalize(drive_folder_name)
    aliases = get_aliases_runtime()
    if norm in aliases:
        return aliases[norm]
    return drive_folder_name


def reverse_alias(cliente_real: str) -> list:
    target = _normalize(cliente_real)
    aliases = get_aliases_runtime()
    return [drive_name for drive_name, real in aliases.items()
            if _normalize(real) == target]
