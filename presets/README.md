# Presets

Vocabularios pre-armados para verticals comunes. Cada `.env` es un set de
variables que reemplaza la sección "Vocabulario" y "Drive" del `.env` principal.

## Disponibles

| Preset | Vertical | Input → Output |
|---|---|---|
| `video_edit.env` | Agencia de edición de video | crudo → editado |
| `photo_studio.env` | Estudio fotográfico | shoot → foto retocada |
| `ugc.env` | Agencia UGC | material → edit |
| `design_agency.env` | Diseño gráfico | brief → diseño |
| `accounting.env` | Estudio contable | recibo → procesado |
| `legal.env` | Estudio jurídico | documento → revisado |

## Cómo usar

**Opción A** — Aplicar al .env durante el setup:
```bash
python3 setup.py
# Cuando llegue a "Vocabulario", podés cancelar y aplicar un preset:
cat presets/video_edit.env >> .env
```

**Opción B** — Cargar como overrides de env:
```bash
set -a && source presets/photo_studio.env && set +a
python3 scan_incremental.py
```

**Opción C** — Combinar con setup interactivo:
Editá `setup.py` para ofrecer presets como primera pregunta. (TODO)

## Agregar un preset nuevo

Copiá uno existente, ajustá vocabulario + carpetas + extensiones. Mantenelo
genérico (sin nombres de cliente reales).
