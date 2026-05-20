"""
Vocabulario del negocio — cómo se llaman las cosas en este cliente.

El motor del sistema es agnóstico: detecta archivos en Drive, los asigna a un
responsable, manda mail, cierra cuando aparece el output. Pero los textos que ven
el usuario y los miembros del equipo dependen del negocio:

  Agencia de edición → input="crudo", output="editado", assignee="editor"
  Estudio fotográfico → input="shoot", output="foto retocada", assignee="retocador"
  Estudio contable → input="recibo", output="procesado", assignee="contador"
  Productora → input="brief", output="entregable", assignee="productor"

Setear estas vars en .env. Defaults son genéricos ("archivo nuevo" / "completado").
"""

import os


# ─── Vocabulario ──────────────────────────────────────────────────────────────
INPUT_SINGULAR = os.environ.get("INPUT_SINGULAR", "archivo")
INPUT_PLURAL = os.environ.get("INPUT_PLURAL", "archivos")
# Cómo se llama lo que entra. Ej: "crudo" / "shoot" / "recibo" / "brief".

OUTPUT_SINGULAR = os.environ.get("OUTPUT_SINGULAR", "entrega")
OUTPUT_PLURAL = os.environ.get("OUTPUT_PLURAL", "entregas")
# Cómo se llama lo que sale. Ej: "editado" / "foto retocada" / "procesado".

ASSIGNEE_SINGULAR = os.environ.get("ASSIGNEE_SINGULAR", "responsable")
ASSIGNEE_PLURAL = os.environ.get("ASSIGNEE_PLURAL", "responsables")
# Quién hace el trabajo. Ej: "editor" / "retocador" / "contador" / "productor".

PROJECT_SINGULAR = os.environ.get("PROJECT_SINGULAR", "proyecto")
PROJECT_PLURAL = os.environ.get("PROJECT_PLURAL", "proyectos")
# Unidad de agrupación. Ej: "cliente" / "shoot" / "expediente" / "campaña".

ACTION_VERB = os.environ.get("ACTION_VERB", "completar")
# Verbo de la acción que hace el responsable. Ej: "editar" / "retocar" / "procesar".

ACTION_DONE = os.environ.get("ACTION_DONE", "completado")
# Participio. Ej: "editado" / "retocado" / "procesado".


# ─── Estructura de Drive ──────────────────────────────────────────────────────
# Nombres aceptados de la subcarpeta donde se suben los INPUTS dentro de cada proyecto.
# Si el cliente sube fotos en una carpeta llamada "Material" o "Raw" o "Crudos",
# el watcher las detecta. Si tu cliente usa otro nombre, agregalo acá.
INPUT_FOLDER_NAMES = set(
    n.strip().lower()
    for n in os.environ.get(
        "INPUT_FOLDER_NAMES",
        "material,raw,crudos,material crudo,input,inputs"
    ).split(",")
    if n.strip()
)

# Extensiones de archivo que el watcher considera válidas como INPUT.
# Defaults = video. Para fotos: jpg,jpeg,png,raw,cr2,arw,nef,dng
# Para docs: pdf,doc,docx,xls,xlsx
INPUT_EXTS = set(
    "." + e.strip().lower().lstrip(".")
    for e in os.environ.get(
        "INPUT_EXTS",
        ".mp4,.mov,.avi,.mkv,.m4v,.webm,.mxf"
    ).split(",")
    if e.strip()
)


# ─── Helpers de formateo (para mails y UI) ────────────────────────────────────

def n_inputs(n: int) -> str:
    """'1 crudo' / '5 crudos'"""
    return f"{n} {INPUT_SINGULAR}" if n == 1 else f"{n} {INPUT_PLURAL}"


def n_outputs(n: int) -> str:
    return f"{n} {OUTPUT_SINGULAR}" if n == 1 else f"{n} {OUTPUT_PLURAL}"


def n_projects(n: int) -> str:
    return f"{n} {PROJECT_SINGULAR}" if n == 1 else f"{n} {PROJECT_PLURAL}"
