# Laboratorio 6 — Análisis de redes sociales

**Curso:** CC3084 · Data Science · Semestre II, 2026

Esta carpeta contiene el enunciado, los datos y el código del Laboratorio 6. La organización sigue la convención del repositorio guía del curso: cada laboratorio es autocontenido y reproducible.

## Estructura

```text
06_analisis_redes_sociales/
├── data/
│   ├── raw/                  # datos originales; no se modifican
│   └── processed/            # datos derivados y reproducibles
├── notebooks/                # exploración, análisis e informe ejecutable
├── src/                      # funciones y scripts reutilizables
├── Lab6-AnaliticadeRedesSociales.md
├── requirements.txt          # dependencias de Python
└── README.md
```

## Convenciones de trabajo

- `data/raw/` es la fuente de verdad. Los CSV originales deben conservarse sin cambios.
- `data/processed/` contendrá tablas limpias, tablas de nodos y aristas, y demás resultados reconstruibles. Su contenido no se versiona.
- `notebooks/` contendrá el cuaderno principal con el desarrollo e interpretación del laboratorio.
- `src/` contendrá funciones o etapas que convenga separar del cuaderno.
- Las rutas del código deben ser relativas a esta carpeta para que el análisis funcione en otros equipos.

## Preparar el entorno

Desde esta carpeta:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

En macOS o Linux, la activación equivalente es `source .venv/bin/activate`.

## Datos disponibles

- `data/raw/youtube_videos.csv`
- `data/raw/youtube_comments.csv`
