# CC3084---Data-Science
Labs y Proyectos de Data Science

## PasaporteSpark

Practica individual de Machine Learning distribuido con Apache Spark MLlib.
El notebook utiliza el dataset de estadisticas de jugadores de la NBA para
predecir los puntos anotados (`PTS`) mediante regresion lineal y comparar el
resultado con otros enfoques.

### Entrega

- [Spark_03_SparkML_Daniel_Chet.ipynb](Spark_03_SparkML_Daniel_Chet.ipynb)

El notebook incluye:

- Limpieza y transformacion distribuida de los datos.
- Analisis exploratorio con muestreo seguro.
- Prevencion de data leakage.
- Regresion lineal con Spark ML.
- Feature engineering, StandardScaler y Random Forest.
- Evaluacion por metricas y por segmento de minutos jugados.

### Ejecucion local

El proyecto esta preparado para ejecutarse con Docker Compose, Python 3.11,
OpenJDK 17 y PySpark 3.5.1.

```bash
docker compose up -d
```

Luego abre [http://localhost:8888](http://localhost:8888) y ejecuta el
notebook desde JupyterLab.
