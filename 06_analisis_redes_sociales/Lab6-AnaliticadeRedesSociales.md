# Universidad del Valle de Guatemala
## Facultad de Ingeniería
### Departamento de Ciencias de la Computación
**CC3084 - Data Science**  
**Semestre II-2026**

---

# Laboratorio 6. Análisis de redes sociales

## INSTRUCCIONES

Se proporcionan dos conjuntos de datos obtenidos de YouTube: `youtube_videos.csv` y `youtube_comments.csv`. El primero contiene información de videos y canales; el segundo contiene comentarios publicados en una selección de videos. El objetivo del laboratorio es estudiar la estructura de participación de los usuarios, la relación entre canales y temas, y el contenido de las conversaciones observadas.

Debe resolver los ejercicios utilizando R o Python. La investigación debe ser reproducible: conserve el código, documente las decisiones metodológicas y permita reconstruir las tablas, redes, métricas y visualizaciones presentadas en el informe.

**Importante:** los datos no permiten identificar quién respondió a quién. La variable `reply_count` indica cuántas respuestas recibió un comentario, pero no identifica a los autores de esas respuestas. Por lo tanto, no debe interpretarse como una arista entre usuarios.

---

## DESCRIPCIÓN DE LOS CONJUNTOS DE DATOS

### 1. Dataset `youtube_videos.csv`

Cada fila representa un video de YouTube. El conjunto contiene 293 videos y 20 variables.

| Variable | Tipo observado | Descripción |
| :--- | :--- | :--- |
| `video_id` | Texto/identificador | Identificador único del video en YouTube. Es la llave primaria del conjunto y permite relacionarlo con `youtube_comments.csv`. |
| `title` | Texto | Título del video tal como aparece publicado en YouTube. Puede utilizarse para análisis de texto, tópicos, palabras frecuentes y clasificación temática. |
| `channel_name` | Texto/categórica | Nombre visible del canal que publicó el video. Puede cambiar o repetirse, por lo que no debe utilizarse como identificador único. |
| `channel_id` | Texto/identificador | Identificador único del canal de YouTube. Es preferible a `channel_name` para construir nodos correspondientes a canales. |
| `source_query` | Texto/categórica | Consulta de búsqueda o canal utilizado para encontrar el video durante la recolección. Ejemplos: `guatemala lluvias`, `guatemala noticias` o el handle de un canal. Describe el procedimiento de muestreo, no necesariamente el tema definitivo del video. |
| `source_group` | Categórica | Clasifica la procedencia del video según la estrategia de búsqueda. Presenta los valores `topic`, `official_gov` y `channel`. |
| `dataset_sources` | Texto/lista | Indica los archivos originales en los que apareció el video antes de integrar y eliminar duplicados. Puede contener varios nombres separados por \|. |
| `channel_handle` | Texto/identificador visible | Handle o nombre de usuario del canal, generalmente con la estructura `/@nombrecanal`. Es útil para mostrar etiquetas, pero `channel_id` continúa siendo el identificador más estable. |
| `published_time` | Texto temporal relativo | Tiempo transcurrido desde la publicación, expresado de forma relativa, por ejemplo, hace 2 días o hace 3 meses. Depende del momento de recolección y no debe tratarse directamente como una fecha exacta. |
| `view_count_text` | Texto numérico | Número de visualizaciones en el formato mostrado por YouTube, por ejemplo, 2,390 vistas. Se recomienda usar `view_count` para cálculos. |
| `description_snippet` | Texto | Fragmento abreviado de la descripción mostrado en los resultados de búsqueda. No siempre contiene la descripción completa. |
| `video_url` | Texto/URL | Dirección web completa del video. Puede utilizarse para verificar registros o proporcionar enlaces, pero no como identificador principal. |
| `query_hits` | Texto con estructura de lista | Lista de consultas de búsqueda mediante las cuales se recuperó el video. Un video puede coincidir con más de una consulta. Debe convertirse de texto a lista antes de analizarla. |
| `keywords` | Texto con estructura de lista | Palabras clave o etiquetas asociadas con el video. Puede contener una lista vacía []. Es útil para analizar temas, similitud y redes canal-tema. |
| `description` | Texto | Descripción completa del video. Puede contener texto narrativo, URL, hashtags, menciones, emojis y llamados a suscribirse. Es una de las principales fuentes para el análisis de tópicos. |
| `view_count` | Numérica entera | Número de visualizaciones observado durante la recolección. Es la variable recomendada para los análisis cuantitativos de popularidad. |
| `publish_date` | Fecha y hora | Fecha y hora de publicación en formato ISO 8601, incluyendo zona horaria. Ejemplo: 2026-08-28T22:00:20-07:00. |
| `upload_date` | Fecha y hora | Fecha y hora asociada con la carga del video. En este conjunto coincide con `publish_date` en el 100% de los registros. |
| `category` | Categórica | Categoría de YouTube asignada al video, como News & Politics, People & Blogs, Education o Entertainment. |
| `owner_handle` | Texto/identificador visible | Handle del propietario del video. En este conjunto coincide con `channel_handle` en todos los registros. |

---

### 2. Dataset `youtube_comments.csv`

Cada fila representa un comentario principal publicado en un video. El conjunto contiene 406 comentarios y 17 variables.

| Variable | Tipo observado | Descripción |
| :--- | :--- | :--- |
| `video_id` | Texto/identificador | Identificador del video donde fue publicado el comentario. Es la llave foránea que permite relacionar el comentario con `youtube_videos.csv`. |
| `comment_id` | Texto/identificador | Identificador único del comentario en YouTube. Es la llave primaria del conjunto de comentarios. |
| `video_title` | Texto | Título del video en el que aparece el comentario. Es una variable descriptiva redundante porque puede obtenerse al unir ambos conjuntos mediante `video_id`. |
| `channel_name` | Texto/categórica | Nombre visible del canal propietario del video comentado. No corresponde al autor del comentario. |
| `channel_id` | Texto/identificador | Identificador único del canal que publicó el video comentado. Es diferente de `author_channel_id`. |
| `author_name` | Texto | Nombre visible del autor del comentario. Puede incluir un handle y puede cambiar, por lo que no debe utilizarse como identificador único. |
| `author_channel_id` | Texto/identificador | Identificador único del canal o cuenta del autor del comentario. Debe utilizarse para representar a los autores como nodos de la red. |
| `text` | Texto | Contenido completo del comentario. Es la variable principal para analizar tópicos, sentimiento, menciones, lenguaje y palabras frecuentes. |
| `source_query` | Texto/categórica | Consulta o canal mediante el cual se encontró el video o se obtuvieron sus comentarios. Describe el proceso de recolección. |
| `source_group` | Categórica | Tipo de fuente utilizada para obtener el contenido. En este conjunto presenta los valores topic y channel. |
| `dataset_sources` | Texto/lista | Archivos originales de comentarios en los que apareció el registro antes de integrar las fuentes. Puede contener varios nombres separados por \|. |
| `author_handle` | Texto/identificador visible | Handle del autor del comentario, generalmente con formato /@nombre. Es apropiado para etiquetas visuales, pero debe preferirse `author_channel_id` para identificar nodos. |
| `published_text` | Texto temporal relativo | Tiempo transcurrido desde la publicación del comentario, por ejemplo, hace 1 día, hace 2 semanas o hace 1 año. No es una fecha exacta. |
| `like_count_text` | Texto numérico | Cantidad de "me gusta" recibidos por el comentario. Aparece almacenada como texto y puede contener espacios o valores vacíos. Debe limpiarse y convertirse a entero. |
| `reply_count` | Numérica entera | Número de respuestas recibidas por el comentario principal. No identifica autores ni contiene el texto de las respuestas. |
| `is_pinned` | Lógica/booleana | Indica si el comentario fue fijado por el canal. En este conjunto todos los registros tienen el valor False, por lo que no aporta variabilidad. |
| `viewer_rating` | Numérica vacía | Variable destinada posiblemente a registrar una valoración del usuario. Está vacía en los 406 registros y no puede utilizarse en el análisis. |

---

## EJERCICIOS

### 1. Carga, comprensión e integración de los datos
* **1.1.** Cargue los archivos `youtube_videos.csv` y `youtube_comments.csv` en R o Python.
* **1.2.** Identifique la unidad de observación, la llave primaria y las variables relevantes de cada archivo.
* **1.3.** Explique la relación entre canal, video, autor del comentario, comentario, categoría y consulta de búsqueda.
* **1.4.** Integre los conjuntos de datos mediante `video_id`. Compruebe y reporte cuántos comentarios pudieron asociarse con un video.

### 2. Calidad, limpieza y preprocesamiento
* **2.1.** Elabore un diagnóstico inicial de calidad que incluya dimensiones, tipos de variables, valores faltantes, duplicados, variables constantes, valores atípicos y consistencia entre identificadores, nombres y handles.
* **2.2.** Identifique variables que no pueden utilizarse o que requieren precauciones especiales. Justifique su tratamiento.
* **2.3.** Normalice los identificadores y nombres sin sustituir los ID por nombres visibles. Utilice `channel_id`, `video_id`, `comment_id` y `author_channel_id` como identificadores cuando corresponda.
* **2.4.** Convierta a formato numérico las variables de conteo almacenadas como texto. Documente el tratamiento de separadores, abreviaturas y valores no válidos.
* **2.5.** Cree dos versiones del texto: `texto_original` y `texto_limpio`. El texto original debe conservarse para auditoría y análisis de sentimiento.
* **2.6.** Para `texto_limpio`, evalúe y documente: conversión a minúsculas, eliminación de URL, separación de hashtags y menciones, puntuación, números, stopwords en español, lematización y tratamiento de emojis.
* **2.7.** Cuantifique el efecto de la limpieza: registros eliminados o modificados, textos vacíos y duplicados antes y después.

### 3. Análisis exploratorio
* **3.1.** Describa como mínimo: número de videos, canales, comentarios y autores; videos por canal; comentarios y autores únicos por video; visualizaciones; respuestas; "me gusta"; categorías; consultas de búsqueda; hashtags; palabras y bigramas frecuentes.
* **3.2.** Analice la concentración de la participación. Determine qué proporción de comentarios corresponde a los videos y canales más activos.
* **3.3.** Compare popularidad y participación. Evalúe la relación entre visualizaciones y comentarios, indicando las limitaciones de ambos conteos.
* **3.4.** Genere visualizaciones pertinentes. Puede incluir una nube de palabras, pero esta no sustituye gráficos de frecuencia o comparaciones cuantitativas.
* **3.5.** Responda las siguientes preguntas:
  * ¿Qué videos y canales concentran la mayor participación observada?
  * ¿Existen audiencias compartidas entre videos, canales o temas?
  * ¿Qué autores funcionan como puentes entre contenidos que de otra forma permanecerían separados?
  * ¿Qué temas y sentimientos caracterizan a las principales comunidades de participación?
  * ¿La visibilidad medida mediante visualizaciones coincide con la participación observada?
  * ¿Qué conclusiones están limitadas por el procedimiento de recolección y la cobertura de los datos?
* **3.6.** Formule al menos tres preguntas adicionales que surjan del análisis exploratorio y respóndalas con evidencia obtenida de los datos.

### 4. Construcción de la red bipartita autor-video
* **4.1.** Construya una red bipartita no dirigida en la que un conjunto de nodos represente autores y el otro represente videos.
* **4.2.** Cree una arista cuando un autor haya comentado en un video. Asigne como peso el número de comentarios publicados por ese autor en ese video.
* **4.3.** Construya y entregue una tabla de nodos y una tabla de aristas. Incluya tipo de nodo y atributos relevantes.
* **4.4.** Visualice la red completa, evite eliminar estructuras relevantes únicamente para mejorar la apariencia.
* **4.5.** Explique con precisión qué significa una arista. No interprete la co-participación como amistad, conversación directa ni aprobación.

### 5. Proyecciones de la red
* **5.1.** Construya una proyección autor-autor: dos autores se conectan si comentaron en el mismo video. El peso debe representar el número de videos compartidos.
* **5.2.** Construya una proyección video-video: dos videos se conectan si comparten al menos un autor. El peso debe representar el número de autores compartidos.
* **5.3.** Compare las dos proyecciones y discuta qué fenómeno representa cada una.
* **5.4.** Visualice cada una de las proyecciones.

### 6. Topología y fragmentación
* **6.1.** Para la red bipartita y las proyecciones pertinentes, calcule y discuta: número de nodos y aristas, densidad, grado medio, distribución de grados para determinar si la mayoría tiene pocas conexiones o están concentradas en unos pocos, componentes conexos y tamaño de la componente más grande.
* **6.2.** Calcule cohesión y transitividad.
* **6.3.** Identifique autores, videos o grupos periféricos y aislados. Distinga entre aislamiento observado y ausencia de datos.
* **6.4.** Explique los hallazgos derivados de los análisis estructurales de las redes calculados anteriormente.

### 7. Comunidades
* **7.1.** Seleccione una red adecuada para detectar comunidades y justifique la elección.
* **7.2.** Investigue y aplique un algoritmo apropiado, por ejemplo Louvain, Leiden o un método específico para redes bipartitas. Explique sus supuestos y el tratamiento de los pesos.
* **7.3.** Reporte el número de comunidades, sus tamaños y una medida de calidad como la modularidad cuando sea aplicable.
* **7.4.** Visualice todas las comunidades y analice hasta tres comunidades principales. Si se detectan menos de tres comunidades, analice las disponibles y justifique.
* **7.5.** Caracterice cada comunidad mediante videos, canales, autores, intensidad de participación, temas frecuentes y sentimiento.

### 8. Nodos centrales y participantes puente
* **8.1.** Investigue y calcule las medidas apropiadas de centralidad. Puede complementar con cercanía, PageRank o centralidad de vectores propios, justificando su uso.
* **8.2.** Interprete por separado los resultados para autores y videos. Para los autores, considere recurrencia y diversidad de participación; para los videos, alcance dentro de la red y capacidad de conectar audiencias.
* **8.3.** Identifique participantes recurrentes y autores puente y videos articuladores (si los elimináramos de la red, esta se segmenta).

### 9. Análisis de contenido y sentimiento
* **9.1.** Realice análisis de sentimiento de los comentarios con una herramienta adecuada para español. Justifique el modelo o léxico utilizado, explique los resultados obtenidos.
* **9.2.** Compare el sentimiento por video, canal, tema o comunidad cuando el tamaño de muestra lo permita.
* **9.3.** Explique todos sus hallazgos.

### 10. Interpretación, limitaciones y conclusiones
* **10.1.** Explique los hallazgos en el contexto de participación y consumo de contenido en YouTube.
* **10.2.** Discuta como mínimo las siguientes limitaciones: cobertura de comentarios, selección por consultas, fechas relativas, conteos observados al momento de recolección, falta de relaciones explícitas entre autores y concentración de comentarios en pocos videos.
* **10.3.** Distinga claramente descripción, asociación e inferencia. No generalice los resultados a todos los usuarios de YouTube o a toda la población de Guatemala.
* **10.4.** Incluya una sección de conclusiones que integre redes, contenido, sentimiento y limitaciones.

---

## HERRAMIENTAS SUGERIDAS

*Nota: estas herramientas son sugeridas y su uso no es obligatorio. Puede utilizar otras herramientas siempre que se usen de manera correcta.*

### Python:
* **Análisis de la topología de la red:**
  * `networkx`: Biblioteca clave para el análisis de redes y grafos en Python. Permite construir, manipular y analizar redes, además de calcular métricas como centralidad, cohesión y detectar comunidades.
  * `igraph` (para Python): Similar a la versión de R, permite realizar análisis más rápidos y escalables en redes grandes.
  * `pygraphviz`: Para trabajar con grafos y visualizaciones de redes más complejas.
* **Análisis de influencers y nodos clave:**
  * `networkx`: Calcula métricas de centralidad (grado, intermediación, cercanía, etc.), ideal para identificar los nodos clave en la red (influencers).
* **Análisis de contenido y sentimiento:**
  * `nltk`: Biblioteca fundamental para procesamiento de lenguaje natural (NLP), con herramientas para tokenización, análisis de frecuencia y extracción de características de texto.
  * `TextBlob`: Proporciona una API simple para realizar análisis de sentimiento y análisis gramatical.
  * `VADER` (de `nltk.sentiment`): Especialmente diseñado para analizar sentimientos en redes sociales, tiene una alta precisión con textos cortos como tweets.
  * `spacy`: Un motor de NLP más avanzado y rápido, útil para análisis de contenido más profundos como detección de entidades nombradas (NER).
  * `transformers` (de Hugging Face): Si buscas aplicar modelos más complejos de análisis de texto, esta biblioteca incluye modelos de última generación como BERT para análisis de sentimientos y clasificación de texto.
* **Visualización avanzada:**
  * `plotly`: Para crear gráficos interactivos y explorar los datos de manera dinámica.
  * `PyVis`: Para la visualización interactiva de redes.
  * `Bokeh`: Alternativa a plotly, permite generar gráficos interactivos y dashboards complejos.
  * `Gephi`: Aunque no es Python puro, puedes exportar los datos de networkx o igraph a Gephi para visualización avanzada de redes.
  * `igraph`: Permite hacer visualizaciones estáticas de comunidades y de grafos.

### R:
* **Análisis de la topología de la red:**
  * `igraph`: Uno de los paquetes más populares para el análisis de redes. Permite construir, manipular y visualizar grafos, además de calcular métricas de red como la densidad, el diámetro y el coeficiente de agrupamiento.
  * `network`: Similar a igraph, pero con un enfoque más en la visualización de redes y la integración con otros paquetes como statnet.
  * `ggraph`: Paquete para la visualización de redes usando la gramática de gráficos de ggplot2.
* **Identificación y análisis de comunidades:**
  * `igraph`: También incluye algoritmos de detección de comunidades como Louvain y Girvan-Newman.
  * `clustree`: Para visualizar y comparar estructuras de clusters o comunidades.
* **Análisis de influencers y nodos clave:**
  * `igraph`: Permite calcular métricas de centralidad como grado, intermediación, y cercanía.
  * `CINNA`: Un paquete más especializado en métricas de centralidad.
* **Análisis de contenido y sentimiento:**
  * `textclean`: Herramienta útil para limpiar y normalizar el texto.
  * `tidytext`: Paquete para el análisis de texto en un formato de datos ordenado, perfecto para trabajar con grandes conjuntos de tweets.
  * `syuzhet`: Para el análisis de sentimiento, que incluye métodos como análisis basado en léxicos de emociones.
  * `sentimentr`: Otro paquete para realizar análisis de sentimiento a nivel de oración o documento.
* **Visualización avanzada:**
  * `ggraph`: Potente herramienta de visualización de datos que permite generar gráficos avanzados de redes y análisis.
  * `plotly`: Para crear visualizaciones interactivas que los usuarios puedan explorar dinámicamente.
  * `visNetwork`: Un paquete para crear visualizaciones interactivas de redes.

---

## EVALUACIÓN

*NOTA: La evaluación de cada integrante del grupo será de acuerdo con sus contribuciones al trabajo grupal.*

* **(18 puntos) Calidad, limpieza y preprocesamiento**
  * (4 puntos) Presenta diagnóstico inicial de calidad: dimensiones, tipos, faltantes, duplicados, variables constantes, atípicos y consistencia de IDs/nombres/handles.
  * (2 puntos) Identifica variables problemáticas o de uso delicado y justifica su tratamiento.
  * (2 puntos) Normaliza correctamente identificadores y nombres, manteniendo `channel_id`, `video_id`, `comment_id` y `author_channel_id` como IDs.
  * (3 puntos) Convierte a numérico las variables de conteo en texto y documenta separadores, abreviaturas y valores inválidos.
  * (3 puntos) Crea y conserva `texto_original` y `texto_limpio` con justificación metodológica.
  * (2 puntos) Documenta claramente las decisiones de limpieza de `texto_limpio` (minúsculas, URL, hashtags, menciones, puntuación, números, stopwords, lematización, emojis).
  * (2 puntos) Cuantifica el efecto de la limpieza: registros eliminados/modificados, textos vacíos y duplicados antes y después.

* **(18 puntos) Análisis exploratorio**
  * (6 puntos) Describe los elementos mínimos requeridos: videos, canales, comentarios, autores, videos por canal, comentarios y autores por video, visualizaciones, respuestas, me gusta, categorías, consultas, hashtags, palabras y bigramas frecuentes.
  * (3 puntos) Analiza la concentración de la participación en videos y canales más activos.
  * (2 puntos) Compara popularidad y participación, discutiendo la relación entre visualizaciones y comentarios y sus limitaciones.
  * (3 puntos) Presenta visualizaciones pertinentes y bien interpretadas.
  * (2 puntos) Responde con evidencia las preguntas obligatorias del inciso 3.5.
  * (2 puntos) Formula al menos tres preguntas adicionales y las responde con evidencia.

* **(10 puntos) Construcción de la red bipartita autor-video**
  * (2 puntos) Construye correctamente la red bipartita no dirigida autor-video.
  * (2 puntos) Define correctamente la arista y el peso como número de comentarios del autor en ese video.
  * (3 puntos) Entrega tabla de nodos y tabla de aristas con tipo de nodo y atributos relevantes.
  * (2 puntos) Visualiza la red completa sin eliminar estructuras relevantes solo por estética.
  * (1 punto) Explica con precisión el significado de la arista sin sobreinterpretarla.

* **(8 puntos) Proyecciones de la red**
  * (3 puntos) Construye correctamente la proyección autor-autor con peso por videos compartidos.
  * (3 puntos) Construye correctamente la proyección video-video con peso por autores compartidos.
  * (1 punto) Compara ambas proyecciones y discute qué fenómeno representa cada una.
  * (1 punto) Visualiza ambas proyecciones.

* **(12 puntos) Topología y fragmentación**
  * (5 puntos) Calcula y reporta correctamente número de nodos, aristas, densidad, grado medio, distribución de grados, componentes conexos y tamaño de la componente más grande. Calcula cohesión y transitividad. Identifica autores, videos o grupos periféricos y aislados, distinguiendo aislamiento observado de ausencia de datos.
  * (7 puntos) Interpreta correctamente los hallazgos estructurales, explicando basado en los gráficos y análisis realizados.

* **(10 puntos) Comunidades**
  * (2 puntos) Selecciona una red adecuada para detección de comunidades y justifica la elección.
  * (3 puntos) Investiga y aplica correctamente un algoritmo apropiado, por ejemplo Louvain, Leiden o un método específico para redes bipartitas. Explica supuestos y tratamiento de pesos.
  * (2 puntos) Reporta número de comunidades, tamaños y modularidad u otra medida de calidad cuando aplique.
  * (1 punto) Visualiza todas las comunidades.
  * (2 puntos) Analiza hasta tres comunidades principales en términos de videos, canales, autores, intensidad, temas y sentimiento.

* **(7 puntos) Nodos centrales y participantes puente**
  * (3 puntos) Investiga y calcula medidas apropiadas de centralidad, justificando su uso.
  * (2 puntos) Interpreta por separado resultados para autores y videos.
  * (2 puntos) Identifica participantes recurrentes, autores puente y videos articuladores. Explica hallazgos.

* **(5 puntos) Análisis de contenido y sentimiento**
  * (2 puntos) Realiza análisis de sentimiento con la herramienta adecuada para español y justifica el método.
  * (1 punto) Compara sentimiento por video, canal, tema o comunidad cuando el tamaño lo permita.
  * (2 puntos) Explica claramente los hallazgos de contenido y sentimiento.

* **(12 puntos) Interpretación, limitaciones y conclusiones**
  * (3 puntos) Explica los hallazgos en el contexto de participación y consumo de contenido en YouTube.
  * (4 puntos) Discute claramente las limitaciones mínimas exigidas.
  * (2 puntos) Distingue entre descripción, asociación e inferencia y evita generalizaciones indebidas.
  * (3 puntos) Presenta conclusiones integradas que conectan redes, contenido, sentimiento y limitaciones.

---

## MATERIAL A ENTREGAR

* Informe en formato PDF con resultados, visualizaciones, interpretación y conclusiones.
* Script reproducible de R (`.R` o `.Rmd`) o Python (`.py` o notebook).
* Enlace al espacio colaborativo del grupo.
* Enlace al repositorio utilizado para versionar el código.
* Archivo README con instrucciones para ejecutar el análisis y dependencias requeridas.

---

## FECHAS DE ENTREGA

* **AVANCE:** jueves 3 de septiembre de 2026: Actividades de la 1 a la 4 de la sección de ejercicios
* **DOCUMENTO FINAL COMPLETO:** domingo 6 de septiembre de 2026 a las 23:59.

**NOTA:** Para poder tener nota completa debe entregar las asignaciones en el tiempo adecuado. No se calificará el avance del laboratorio si no fue entregado en tiempo, aunque esté en el repositorio.

**Sugerencia:** El segundo día de clase de la semana tendrá un tiempo de aclaración de dudas con el profesor, se le sugiere que avance en la resolución del laboratorio en los pasos del contenido teórico visto en la clase presencial para que aclare todas sus dudas al respecto en dicho espacio.