# Laboratorio 6 — Análisis de redes sociales

**Curso:** CC3084 · Data Science · Semestre II, 2026

Esta carpeta contiene el enunciado, los datos y el código del Laboratorio 6. La organización sigue la convención del repositorio guía del curso: cada laboratorio es autocontenido y reproducible.

El avance implementa los ejercicios **1 al 4**: carga e integración, diagnóstico y limpieza, análisis exploratorio y construcción de la red bipartita autor–video. El desarrollo principal, los resultados y las interpretaciones están en:

```text
notebooks/analisis_redes_sociales.ipynb
```

## Estructura

```text
06_analisis_redes_sociales/
├── data/
│   ├── raw/                  # datos originales; no se modifican
│   └── processed/            # datos derivados y reproducibles
├── notebooks/                # exploración, análisis e informe ejecutable
├── src/                      # funciones y scripts reutilizables
├── Lab6-AnaliticadeRedesSociales.md
├── codebook.md               # variables, transformaciones y limitaciones
├── requirements.txt          # dependencias de Python
└── README.md
```

## Convenciones de trabajo

- `data/raw/` es la fuente de verdad. Los CSV originales deben conservarse sin cambios.
- `data/processed/` contendrá tablas limpias, tablas de nodos y aristas, y demás resultados reconstruibles. Su contenido no se versiona.
- `notebooks/` contendrá el cuaderno principal con el desarrollo e interpretación del laboratorio.
- `src/` contendrá funciones o etapas que convenga separar del cuaderno.
- Las rutas del código deben ser relativas a esta carpeta para que el análisis funcione en otros equipos.
- No se traduce ningún texto: cada comentario, título y descripción se conserva en su idioma original.

## Preparar el entorno

Se recomienda Python 3.13. Desde esta carpeta:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

En macOS o Linux, la activación equivalente es `source .venv/bin/activate`.

## Ejecutar el avance

Para regenerar las tablas limpias y las tablas de red:

```powershell
python src/run_pipeline.py
```

Para abrir el cuaderno:

```powershell
jupyter notebook notebooks/analisis_redes_sociales.ipynb
```

El notebook ya se entrega ejecutado. Si se desea reproducir todas sus salidas desde cero:

```powershell
python -m nbconvert --to notebook --execute --inplace notebooks/analisis_redes_sociales.ipynb
```

## Datos disponibles

- `data/raw/youtube_videos.csv`
- `data/raw/youtube_comments.csv`

## Salidas reproducibles

El pipeline genera dentro de `data/processed/`:

- `youtube_videos_clean.csv`
- `youtube_comments_clean.csv`
- `youtube_comments_integrated.csv`
- `network_nodes.csv`
- `network_edges.csv`

Estas salidas no se versionan porque pueden reconstruirse a partir de los CSV originales. Consulte [`codebook.md`](codebook.md) para conocer la definición y el tratamiento de cada variable.
