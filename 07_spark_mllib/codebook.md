# Codebook: conjunto analítico ENEIC (Personas)

Generado por el notebook `notebooks/laboratorio7-spark-mllib.ipynb` a partir
de las bases crudas de Personas de la ENEIC (`data/raw/Personas_ENEIC_*.xlsx`)
y sus diccionarios de datos oficiales. Ver `README.md` para el detalle del
proceso y `laboratorio7-spark-mllib-2026.md` para el enunciado completo.

## Identificación del período (derivadas de `archivo_origen`)

| Variable | Tipo | Descripción | Notas |
|---|---|---|---|
| `archivo_origen` | str | Nombre del archivo de procedencia | Trazabilidad; no se infiere del contenido |
| `periodo_archivo` | str | Período publicado, ej. `2025T1` | Asignado por archivo de origen, no por `TRIMESTRE` |
| `anio_archivo` | int | Año del archivo, ej. `2025` | Idem |
| `trimestre_calendario` | int | Trimestre calendario (1-4) del archivo | Idem; **no** es `TRIMESTRE - 1` |
| `TRIMESTRE` | original | Valor crudo de la encuesta | Se conserva sin modificar; no representa el trimestre calendario |

## Población y variable objetivo

| Variable analítica | Variable original | Tipo | Descripción | Filtro aplicado |
|---|---|---|---|---|
| `salario_mensual` | P05D01 | float | Sueldo/salario mensual sin descuentos, ocupación principal (Q) | Numérico finito y estrictamente positivo |
| `ocupado` | OCUPADOS | int | Indicador de ocupación | `OCUPADOS == 1` |
| `categoria_ocupacional` | P05C16 | str (categórica) | Categoría ocupacional | En {1,2,3,4}: 1 empleado de gobierno, 2 empleado de empresa privada, 3 empleado jornalero o peón, 4 servicio doméstico |

Población analítica: personas de 15+ años, `OCUPADOS = 1`, asalariadas según
`P05C16` ∈ {1,2,3,4}, con `salario_mensual` numérico finito y > 0.

## Predictores

| Variable analítica | Variable original | Tipo | Descripción | Uso |
|---|---|---|---|---|
| `edad` | P02A03 | int | Edad en años | Predictor numérico y clustering. Filtro: finita, ≥ 15 |
| `antiguedad_anios` | P05C07A | int | Años de antigüedad | Insumo de `antiguedad` |
| `antiguedad_meses` | P05C07B | int | Meses de antigüedad | Insumo de `antiguedad`; filtro: entero 0-11 |
| `antiguedad` | derivada | float | `antiguedad_anios + antiguedad_meses/12` | Predictor numérico y clustering. Filtro: ≥ 0 y ≤ `edad` |
| `horas_semanales` | P05H01A | float | Horas habituales, ocupación principal | Predictor y clustering. Filtro: > 0 y ≤ 168 |
| `nivel_educativo` | P03A03A | str (categórica) | Nivel educativo | Predictor categórico. Código 0 = "ninguno" (no es faltante) |
| `dominio` | DOMINIO | str (categórica) | Dominio geográfico/de diseño muestral | Predictor categórico |

Valores categóricos ausentes o no reconocidos en el diccionario se codifican
como `"DESCONOCIDO"` (nunca como 0).

Los seis predictores usados en los modelos supervisados son exactamente:
**edad, antiguedad, horas_semanales, nivel_educativo, categoria_ocupacional,
dominio**. No se usan identificadores, `FACTOR`, otros montos de ingreso, el
salario por hora derivado, ni la etiqueta de clúster.

## Variables de auditoría (se conservan, no son predictoras)

| Variable | Descripción |
|---|---|
| `NUM_HOGAR`, `NUM_PERSONA` | Identificadores para verificar unicidad y auditar duplicados |
| `FACTOR` | Factor de expansión del diseño muestral; se conserva y se documenta, no se usa (clustering/modelos/métricas no ponderados) |
| `ANIO`, `TRIMESTRE` | Campos originales de la encuesta, para auditoría de la fuente |

## Notas de alcance

- El clustering, los modelos supervisados y las métricas principales son **no
  ponderados**: describen los registros analizados, no estiman a la
  población guatemalteca.
- No se imputa `salario_mensual`; los registros sin salario positivo se
  excluyen y se cuentan.
- No se recortan outliers de salario en la comparación principal de modelos.
