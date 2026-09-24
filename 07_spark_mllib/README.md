# Laboratorio 7: Spark MLlib — Salarios ENEIC

Práctica grupal de análisis exploratorio, segmentación (KMeans) y regresión
(Regresión Lineal y Random Forest) con Apache Spark MLlib sobre las bases de
Personas de la ENEIC (INE Guatemala). Se estima el salario mensual de
personas asalariadas a partir de características personales y laborales.
Ver el enunciado completo en
[`laboratorio7-spark-mllib-2026.md`](laboratorio7-spark-mllib-2026.md).

## Datos

Los archivos crudos (`data/raw/`) se descargan directamente del INE y **no se
versionan** (son grandes y reproducibles):

| Archivo | Período | Uso |
|---|---|---|
| `Personas_ENEIC_2025T1.xlsx` | I 2025 | Entrenamiento |
| `Personas_ENEIC_2025T2.xlsx` | II 2025 | Entrenamiento |
| `Personas_ENEIC_2025T3.xlsx` | III 2025 | Entrenamiento |
| `Personas_ENEIC_2025T4.xlsx` | IV 2025 | Validación |
| `Personas_ENEIC_2026T1.xlsx` | I 2026 | Prueba final |
| `Diccionario_Personas_*.xlsx` | — | Diccionario de datos por trimestre |

Fuente: <https://www.ine.gob.gt/encuesta-nacional-de-empleo-e-ingresos/>

Para volver a descargarlos:

```bash
python src/download_dataset.py
```

`data/processed/` guarda las salidas en Parquet generadas por el notebook
(conjunto 2025 preparado, 2026 preparado); tampoco se versiona, se regenera
al correr el notebook.

## Cómo correrlo

El ambiente es Docker Compose con Python 3.11, OpenJDK 17 y PySpark 3.5.1
(mismo esquema que la práctica `PasaporteSpark`):

```bash
docker compose up -d
```

Abre <http://localhost:8888> y ejecuta
[`notebooks/laboratorio7-spark-mllib.ipynb`](notebooks/laboratorio7-spark-mllib.ipynb)
de principio a fin. El notebook no depende de variables creadas en
ejecuciones previas.

Dentro del contenedor, los datos crudos quedan montados en
`/opt/app/working_dir/data/raw/`.

## Estructura

```
07_spark_mllib/
├── data/
│   ├── raw/            # bases y diccionarios ENEIC (no versionado)
│   └── processed/      # Parquet 2025/2026 preparados (no versionado)
├── docker/              # Dockerfile + requirements del contenedor
├── docker-compose.yml
├── notebooks/
│   └── laboratorio7-spark-mllib.ipynb
├── src/
│   └── download_dataset.py
├── codebook.md
└── laboratorio7-spark-mllib-2026.md   # enunciado
```

## Avance vs. entrega final

- **Avance (jueves 24 sep):** sección de Análisis Exploratorio Avanzado y
  Segmentación (carga/calidad de datos, estadística descriptiva,
  correlaciones, KMeans).
- **Entrega final (domingo 27 sep):** pipelines de Regresión Lineal y Random
  Forest, evaluación final sobre 2026T1, visualización y análisis de errores.

Ver `codebook.md` para la definición de las variables analíticas derivadas.
