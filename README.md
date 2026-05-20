# Asistente Template

Sistema modular para tracking automático de proyectos con assets en Google Drive.

Detecta archivos nuevos en carpetas de Drive, los asigna al responsable que
corresponda según un Google Sheet, manda mail + push notification, y cierra
automáticamente las tareas cuando se entrega el output.

**Casos de uso:**
- Agencia de edición de video (input=crudo, output=editado, responsable=editor)
- Estudio fotográfico (input=shoot, output=foto retocada, responsable=retocador)
- Estudio contable (input=recibo, output=procesado, responsable=contador)
- Productora (input=brief, output=entregable, responsable=productor)
- Cualquier servicio con flujo "input archivo → output archivo"

Todo el vocabulario, branding, y matching es **configurable por env var** —
se implementa a un cliente nuevo en horas, no semanas.

---

## Arquitectura

```
GitHub Actions (cron cada 2 min)
    ↓
scan_incremental.py
    ↓
1. Lee cambios recientes de Google Drive (Drive Changes API)
2. Detecta archivos nuevos en carpetas de input
3. Lee Sheet → identifica responsable
4. Crea tarea en SQLite (committed al repo)
5. Manda mail (Gmail API) + push notification
    ↓
Cuando aparece output:
6. Cierra automáticamente la tarea pendiente más vieja del proyecto
7. Manda mail de cierre

Frontend (Vercel)
    ↓
Dashboard PWA (admin + vista por responsable)
API serverless (lee/escribe DB del repo vía GitHub Contents API)
```

---

## Setup de un cliente nuevo

### 1. Clonar y correr setup interactivo

```bash
cp -R asistente-template asistente-<cliente>
cd asistente-<cliente>
python3 setup.py
```

El setup pregunta branding, vocabulario, Drive folders, Sheet, etc., y genera:
- `.env` con todas las variables
- HTMLs con los placeholders reemplazados (`__BRAND_NAME__` → "Asistente Acme")

**Presets** disponibles para autocompletar vocabulario común (video edit, fotografía,
contabilidad, diseño, legal, UGC): ver [presets/README.md](presets/README.md).
El setup los ofrece como primera pregunta del bloque "Vocabulario".

### 2. Autorizar Google APIs

Necesitás dos cuentas Google del cliente:

**a. Cuenta del dueño** (acceso al Drive con los archivos):
```bash
python3 auth.py
```
Genera `token.json`. Imprime al final los valores OAUTH_* para Secrets.

**b. Cuenta dedicada** (desde la que se mandan mails — tipo `asistente@cliente.com`):
```bash
python3 auth_mail.py
```
Genera `token_mail.json`. Pide solo scope `gmail.send`.

### 3. Baseline inicial

Snapshot del estado actual del Drive — todo lo que ya existe HOY no genera tareas:

```bash
python3 baseline.py
```

### 4. Probar local

```bash
python3 scan_incremental.py    # debería decir "0 archivos nuevos"
python3 mail_client.py         # manda mail de test
```

### 5. Deploy

**a. Subir a GitHub:**
```bash
git init
git add .
git commit -m "init"
gh repo create $GITHUB_OWNER/$GITHUB_REPO --private --source=. --push
```

**b. GitHub Secrets** (Settings → Secrets → Actions, agregar):
- `OAUTH_REFRESH_TOKEN`, `OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET`
- `MAIL_OAUTH_REFRESH_TOKEN`, `MAIL_OAUTH_CLIENT_ID`, `MAIL_OAUTH_CLIENT_SECRET`
- `SHEET_ID`, `ADMIN_EMAIL`
- `BRAND_NAME`, `INPUT_SINGULAR`, `OUTPUT_SINGULAR`, etc. (todas las del .env)
- `VAPID_PRIVATE_KEY`
- `GITHUB_PAT` (token con permiso `contents:write`)

**c. Deploy a Vercel:**
```bash
vercel link
vercel env add BRAND_NAME
# … repetir para cada var del .env
vercel --prod
```

**d. Habilitar GitHub Actions** y verificar que el primer run pase.

### 6. Cargar datos del cliente

Entrar al dashboard `/config` y cargar lista de responsables, apodos, carpetas
de delivery custom, etc.

---

## Customización por cliente

| Cambio | Esfuerzo | Cómo |
|---|---|---|
| Branding (nombre, colores, logo) | 5 min | Env vars + setup.py |
| Vocabulario (crudo→shoot, editor→retocador) | 5 min | Env vars |
| Carpetas de Drive monitoreadas | 5 min | `INPUT_FOLDER_NAMES` env |
| Extensiones válidas (video→foto→doc) | 2 min | `INPUT_EXTS` env |
| Cambiar Sheet de matching | 5 min | Env vars `SHEET_*` |
| Frecuencia del cron | 2 min | Editar `.github/workflows/scan.yml` |
| Reglas de nicknames específicas | 30 min | Cargar en `/config` desde dashboard |
| **Cambios que requieren código:** | | |
| Lógica de matching distinta (no Sheet) | 1-2h | Editar `scan_incremental.py` |
| Integración con Slack/WhatsApp | 2-4h | Agregar en `notifier.py` |
| Múltiples niveles de aprobación | 1d | Cambios en tracker schema |
| Workflows multi-stage (input→draft→final) | 1-2d | Refactor del closer |

---

## Comandos útiles

```bash
# Estado del sistema
python3 -c "from tracker import stats; print(stats())"

# Ver tareas pendientes
sqlite3 tracker.db "SELECT cliente, editor, file_name, detected_at FROM tasks WHERE status='pending'"

# Forzar resumen diario manual
python3 daily_summary.py --dry-run

# Forzar reminders
python3 reminders.py

# Health check
python3 health_check.py
```

---

## Estructura

```
.
├── branding_config.py    # Nombre, colores, emails (env vars)
├── domain_config.py      # Vocabulario del negocio (env vars)
├── config.py             # Config central
├── setup.py              # Setup interactivo para clientes nuevos
│
├── auth.py               # OAuth Drive + Sheets
├── auth_mail.py          # OAuth Gmail send
│
├── drive_client.py       # API Drive
├── sheets_client.py      # API Sheets
├── mail_client.py        # API Gmail
│
├── tracker.py            # DB SQLite (estado del sistema)
├── aliases.py            # Helpers de matching (DB-backed)
│
├── scan_incremental.py   # Scanner principal (Drive Changes API)
├── classifier.py         # Identifica si un archivo es input u output
├── closer.py             # Cierra tareas cuando aparece output
├── notifier.py           # Manda mails de input nuevo + cierre
├── push_sender.py        # Web Push notifications
│
├── daily_summary.py      # Mail diario 8am
├── weekly_summary.py     # Mail lunes 9am
├── monthly_summary.py    # Mail día 1 9am
├── reminders.py          # Recordatorios a responsables atrasados
├── health_check.py       # Alerta si el sistema dejó de correr
│
├── api/                  # Vercel serverless functions
│   ├── _shared.py
│   ├── data.py           # GET /api/data
│   ├── task.py           # CRUD de tareas
│   ├── stats.py
│   ├── config.py         # CRUD de cfg_* tablas
│   └── push.py
│
├── index.html / config.html / stats.html / mistats.html
├── manifest.json / sw.js / icon-*.png
│
├── .github/workflows/    # Crons de GitHub Actions
└── vercel.json
```

---

## Notas de implementación

- **DB en el repo:** `tracker.db` se commitea al repo. Cada workflow hace pull, ejecuta, y push. Race conditions están manejadas con `INSERT OR IGNORE` + retries con sha conflicts.
- **Cron cada 2 min:** GitHub Actions tiene 2000 min/mes free para repos privados. Ajustar el cron si superás el tier o si el cliente tiene cuenta paga.
- **Vercel serverless:** las API functions hacen pull/push de la DB en cada request. Para >100 escrituras/día considerar migrar a Postgres.
- **Modo prueba:** seteando `TEST_EMAIL` todos los mails van a esa dirección en vez de los responsables reales.

---

## Próximos pasos del template (TODO)

- [ ] Refactor de tablas DB a nombres genéricos (`known_files` → `known_inputs`)
- [ ] Endpoint REST de health (`/api/health`) con estado del último scan
- [ ] Setup de Slack como notification channel alternativo
- [ ] Modo "multi-stage" (input → draft → final, con dos cierres)
- [ ] CLI `python -m asistente status / scan / notify` (consolidar entry points)
