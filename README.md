# CC3084 - Data Science

Repositorio de ejercicios y proyectos del curso **CC3084 - Data Science** de la Universidad del Valle de Guatemala.

## Ejercicio de series de tiempo

Análisis de la temperatura mensual de Guatemala entre enero de 1950 y junio de 2026. El trabajo explora las temperaturas del aire, la superficie y cuatro capas del suelo; para el modelado utiliza `temperature_2m_c`, la temperatura del aire a dos metros.

El notebook cubre:

1. Exploración de datos, extremos y tendencias por capa.
2. Separación cronológica entre entrenamiento y los últimos 36 meses de prueba.
3. Descomposición en tendencia, estacionalidad y residuos.
4. Pruebas ADF, KPSS y Levene para evaluar estacionariedad en media y varianza.
5. Identificación y entrenamiento de tres modelos SARIMA mediante ACF y PACF.
6. Validación de coeficientes, raíces, residuos, AIC, BIC y Ljung-Box.
7. Pronóstico fuera de muestra y comparación con Holt-Winters, suavizamiento exponencial simple y naive estacional.
8. Evaluación de la capacidad del modelo para predecir valores recientes.

### Resultados principales

| Resultado | Valor |
|---|---:|
| Tendencia de la temperatura a 2 m | +0.171 °C por década |
| Periodo de entrenamiento | 1950-01 a 2023-06 |
| Periodo de prueba | 2023-07 a 2026-06 |
| Modelo seleccionado | SARIMA(1,0,1)(0,1,1)[12] |
| AIC / BIC | 1421.01 / 1440.01 |
| RMSE en prueba | 0.893 °C |
| MAPE en prueba | 2.69% |
| Cobertura del intervalo de 95% | 86.1% |

El SARIMA seleccionado obtuvo el menor RMSE entre los métodos comparados. Es útil para pronósticos mensuales centrales, aunque tiende a subestimar episodios extremos, como el máximo observado en mayo de 2024.

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| [`Series_de_Tiempo_Guatemal_Chet.ipynb`](./Series_de_Tiempo_Guatemal_Chet.ipynb) | Notebook completo y ejecutado, con código, resultados, tablas y nueve visualizaciones. |
| `guatemala_temperatura.csv` | Dataset requerido. No está versionado; debe colocarse junto al notebook. |

## Requisitos

- Python 3.11 o posterior
- Jupyter Notebook o JupyterLab
- NumPy
- pandas
- Matplotlib
- seaborn
- SciPy
- scikit-learn
- statsmodels

Instalación rápida:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install jupyter numpy pandas matplotlib seaborn scipy scikit-learn statsmodels
```

## Ejecución

1. Clona el repositorio y entra en su directorio.
2. Coloca `guatemala_temperatura.csv` en la raíz del repositorio, junto al notebook.
3. Activa el entorno virtual e inicia Jupyter:

```powershell
jupyter lab Series_de_Tiempo_Guatemal_Chet.ipynb
```

4. Ejecuta las celdas en orden mediante **Run All**.

El notebook ya incluye sus resultados y gráficas, pero puede ejecutarse nuevamente para reproducir todo el análisis. Los archivos derivados se guardan en `output/series_tiempo/`.

## Autor

**Daniel Chet**

Universidad del Valle de Guatemala
