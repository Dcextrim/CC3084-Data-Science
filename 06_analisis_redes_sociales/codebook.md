# Codebook — Laboratorio 6: Análisis de redes sociales

## Alcance y procedencia

Los dos archivos fueron proporcionados para el curso CC3084. Cada fila de `youtube_videos.csv` representa un video y cada fila de `youtube_comments.csv` representa un comentario principal observado en uno de esos videos. Los datos crudos se conservan sin cambios en `data/raw/`; toda transformación se genera en `data/processed/`.

No se traduce el contenido. Los textos se conservan en el idioma en que fueron recolectados para evitar pérdida de contexto. Los nombres y handles se usan como etiquetas visibles, nunca como sustitutos de los identificadores.

## Modelo relacional

```text
canal (channel_id)
  └── publica → video (video_id)
                   └── recibe → comentario (comment_id)
                                      └── escrito por → autor (author_channel_id)

video ── clasificado en → category
video ── recuperado mediante → source_query / source_group
```

- `video_id` relaciona ambos archivos en una unión muchos-a-uno: varios comentarios pueden pertenecer a un video.
- El canal propietario del video (`channel_id`) es distinto del autor del comentario (`author_channel_id`).
- `reply_count` es un atributo del comentario. No identifica quién respondió y, por tanto, no crea una arista entre autores.

## `youtube_videos.csv`

**Unidad de observación:** un video.  
**Llave primaria:** `video_id`.

| Variable | Tipo esperado | Definición y tratamiento |
|---|---|---|
| `video_id` | identificador | ID único del video; se conserva como texto y solo se recortan espacios externos. |
| `title` | texto | Título visible; se conserva y se normalizan espacios externos. |
| `channel_name` | categórica | Nombre visible del canal; sirve como etiqueta, no como ID. |
| `channel_id` | identificador | ID estable del canal propietario del video. |
| `source_query` | categórica | Consulta o canal usado durante la recolección; describe el muestreo, no el tema definitivo. |
| `source_group` | categórica | Estrategia de origen: `topic`, `official_gov` o `channel`. |
| `dataset_sources` | texto/lista | Archivos originales en los que apareció el registro, separados por `|`. |
| `channel_handle` | texto | Handle visible del canal; puede cambiar. |
| `published_time` | texto relativo | Antigüedad mostrada por YouTube; no se convierte en fecha exacta. |
| `view_count_text` | texto numérico | Conteo mostrado por YouTube; se convierte en `view_count_text_num` para auditarlo. |
| `description_snippet` | texto | Fragmento abreviado de la descripción. |
| `video_url` | URL | Enlace al video; no se usa como identificador. |
| `query_hits` | lista serializada | Consultas que recuperaron el video; se convierte de forma segura en `query_hits_json`. |
| `keywords` | lista serializada | Etiquetas del video; se convierte de forma segura en `keywords_json`. |
| `description` | texto | Descripción completa en su idioma original. |
| `view_count` | entero | Visualizaciones observadas al momento de recolección. |
| `publish_date` | fecha-hora | Se analiza como UTC en `publish_datetime`. |
| `upload_date` | fecha-hora | Se analiza como UTC en `upload_datetime`; se audita su coincidencia con publicación. |
| `category` | categórica | Categoría asignada por YouTube. |
| `owner_handle` | texto | Handle del propietario; se compara con `channel_handle`. |

### Variables derivadas de videos

| Variable | Tipo | Definición |
|---|---|---|
| `view_count_text_num` | entero anulable | Conversión de `view_count_text`; elimina separadores y reconoce `k`, `mil`, `m` y `millón(es)`. |
| `publish_datetime` | fecha-hora UTC | Conversión reproducible de `publish_date`; los valores inválidos quedan faltantes. |
| `upload_datetime` | fecha-hora UTC | Conversión reproducible de `upload_date`. |
| `query_hits_json` | lista JSON | Versión estructurada de `query_hits`. |
| `keywords_json` | lista JSON | Versión estructurada de `keywords`. |

## `youtube_comments.csv`

**Unidad de observación:** un comentario principal.  
**Llave primaria:** `comment_id`.  
**Llave foránea:** `video_id`.

| Variable | Tipo esperado | Definición y tratamiento |
|---|---|---|
| `video_id` | identificador | Video donde apareció el comentario; llave de integración. |
| `comment_id` | identificador | ID único del comentario principal. |
| `video_title` | texto | Título redundante almacenado con el comentario; se compara con videos. |
| `channel_name` | categórica | Nombre del canal del video, no nombre del autor. |
| `channel_id` | identificador | ID del canal que publicó el video. |
| `author_name` | texto | Nombre visible del autor; puede cambiar. |
| `author_channel_id` | identificador | ID usado para representar al autor como nodo. |
| `text` | texto | Comentario crudo en su idioma original. |
| `source_query` | categórica | Consulta o canal que condujo al contenido durante la recolección. |
| `source_group` | categórica | Tipo de fuente (`topic` o `channel`). |
| `dataset_sources` | texto/lista | Archivos originales donde apareció el comentario. |
| `author_handle` | texto | Handle visible; se usa únicamente como etiqueta. |
| `published_text` | texto relativo | Antigüedad relativa; no equivale a una fecha exacta. |
| `like_count_text` | texto numérico | Me gusta mostrados; se convierte a `like_count`. Un texto vacío queda faltante, no cero. |
| `reply_count` | entero | Cantidad de respuestas, sin información de sus autores. |
| `is_pinned` | booleana | Indica comentario fijado; es constante en esta muestra. |
| `viewer_rating` | numérica | Campo totalmente vacío en esta muestra; no se usa analíticamente. |

### Variables derivadas de comentarios

| Variable | Tipo | Definición |
|---|---|---|
| `like_count` | entero anulable | Conversión de `like_count_text`. Un vacío se conserva como desconocido. |
| `texto_original` | texto | Copia exacta de `text` para auditoría y análisis posterior de sentimiento. |
| `texto_limpio` | texto | Versión en minúsculas, sin URL, menciones, emojis, puntuación, números ni stopwords españolas/inglesas; conserva el contenido de hashtags y las negaciones. No traduce ni lematiza. |
| `hashtags` | lista JSON | Hashtags extraídos, sin `#` y en minúsculas. |
| `menciones` | lista JSON | Handles extraídos antes de retirarlos del texto analítico. |
| `emojis` | lista JSON | Emojis extraídos antes de retirarlos de `texto_limpio`; permanecen en `texto_original`. |

La lematización española se evalúa en el notebook, pero no se aplica a todo el corpus: hay textos en varios idiomas y forzar un único modelo lingüístico podría deformar palabras y perder contexto. Esta decisión puede revisarse posteriormente si se identifica el idioma de cada observación con un método validado.

## Integración

`youtube_comments_integrated.csv` conserva las variables del comentario y agrega desde videos:

| Variable agregada | Definición |
|---|---|
| `video_title_ref` | título de referencia según `youtube_videos.csv`. |
| `video_channel_id_ref` | ID del canal según la tabla de videos. |
| `video_channel_name_ref` | nombre visible del canal según la tabla de videos. |
| `category` | categoría del video. |
| `video_source_query_ref` | consulta registrada en videos. |
| `video_source_group_ref` | grupo de origen registrado en videos. |
| `view_count` | visualizaciones observadas del video. |
| `publish_datetime` | fecha-hora de publicación normalizada a UTC. |

## Red bipartita autor–video

### `network_nodes.csv`

| Variable | Definición |
|---|---|
| `node_id` | ID interno con prefijo `author::` o `video::` para evitar colisiones. |
| `node_type` | `author` o `video`. |
| `original_id` | `author_channel_id` o `video_id` original. |
| `label` | handle/nombre para autores o título para videos; solo para presentación. |
| `comment_count` | comentarios observados asociados con el nodo. |
| `unique_neighbors` | videos únicos para un autor o autores únicos para un video. |
| demás atributos | handles del autor o canal, título, categoría y visualizaciones del video cuando aplican. |

Se incluyen todos los videos del archivo original. Un video con cero comentarios aparece como nodo aislado observado; esto muestra la cobertura de comentarios y no prueba ausencia total de audiencia en YouTube.

### `network_edges.csv`

| Variable | Definición |
|---|---|
| `source` | nodo autor (`author::<author_channel_id>`). |
| `target` | nodo video (`video::<video_id>`). |
| `weight` | número de comentarios de ese autor en ese video. |
| IDs y etiquetas auxiliares | IDs originales, título y canal para auditar la relación. |

Una arista significa únicamente **participación observada**: el autor publicó al menos un comentario principal en el video. No implica amistad, respuesta directa, conversación, aprobación ni exposición completa al contenido.

## Proyecciones

### `author_projection_edges.csv`

| Variable | Definición |
|---|---|
| `source`, `target` | nodos `author::<author_channel_id>` conectados por coparticipación. |
| `weight` | número de **videos distintos** comentados por ambos autores. |
| `projection` | constante `author-author`. |

### `video_projection_edges.csv`

| Variable | Definición |
|---|---|
| `source`, `target` | nodos `video::<video_id>` con audiencia compartida. |
| `weight` | número de **autores distintos** que comentaron ambos videos. |
| `projection` | constante `video-video`. |

Los pesos de la red bipartita no se suman al proyectar. Un vecino común cuenta
una sola vez, aunque el autor haya escrito varios comentarios en el video. Las
proyecciones conservan también los nodos aislados. Coparticipación no implica
amistad, conversación, acuerdo ni exposición completa.

## Topología y fragmentación

### `network_metrics.csv`

Cada fila resume la red bipartita o una proyección.

| Variable | Definición |
|---|---|
| `nodes`, `edges` | número de nodos y aristas. |
| `density` | aristas observadas como proporción de las posibles en una red simple no dirigida. |
| `mean_degree`, `median_degree`, `p90_degree`, `max_degree` | resumen de la distribución de vecinos distintos. |
| `isolates`, `leaves` | nodos de grado 0 y grado 1. |
| `components` | número de componentes conexas. |
| `largest_component_nodes`, `largest_component_share` | tamaño absoluto y relativo de la componente mayor. |
| `node_connectivity` | mínimo de nodos cuya eliminación desconecta la red completa; es 0 si ya está desconectada. |
| `largest_component_node_connectivity` | misma medida sobre la componente mayor. |
| `transitivity` | proporción global de triadas cerradas; en la bipartita es 0 por construcción. |
| `articulation_points` | nodos cuya eliminación aumenta el número de componentes. |

`degree_distributions.csv` contiene `network`, `degree`, `nodes` y
`node_share`, para auditar cuántos nodos presentan cada grado.

## Comunidades de videos

### `video_communities.csv`

| Variable | Definición |
|---|---|
| `node_id` | ID interno del video. |
| `community_id` | comunidad Louvain numerada desde 1, ordenada por tamaño. |
| `community_size` | videos incluidos en la comunidad. |

Louvain se ajusta con semilla 42 y pesos de autores compartidos sobre la
proyección video-video activa. Los videos de grado 0 se excluyen del ajuste
porque no aportan evidencia relacional y solo formarían grupos unitarios. La
modularidad y la caracterización completa se reportan en el notebook.

## Centralidades

### `node_centralities.csv`

| Variable | Definición |
|---|---|
| `degree` | videos distintos por autor o autores distintos por video. |
| `weighted_degree` | comentarios asociados con el nodo en la red bipartita. |
| `normalized_degree` | grado dividido entre el tamaño del conjunto opuesto. |
| `betweenness` | intermediación normalizada sobre caminos mínimos no ponderados. |
| `pagerank` | PageRank que utiliza el número de comentarios como peso. |
| `is_articulation` | indica si eliminar el nodo aumenta los componentes. |
| `betweenness_rank_within_type` | posición de intermediación comparada únicamente con nodos del mismo tipo. |

El peso representa intensidad, no distancia; por ello la intermediación se
calcula sin pasar `weight` como longitud. Estas medidas describen posición en
la red observada y no prueban influencia causal.

## Sentimiento

### `youtube_comments_sentiment.csv`

El texto de entrada es `texto_original`, sin traducción. Solo se sustituyen URL
y menciones por los marcadores recomendados por el modelo; se conservan
negaciones, puntuación, mayúsculas, hashtags y emojis.

| Variable | Definición |
|---|---|
| `p_negative`, `p_neutral`, `p_positive` | probabilidades producidas por el modelo. |
| `sentiment_label` | clase de probabilidad máxima. |
| `sentiment_confidence` | probabilidad máxima, usada como indicador de incertidumbre. |
| `sentiment_score` | `p_positive - p_negative`, entre -1 y 1. |
| `sentiment_model` | modelo exacto usado para reproducibilidad. |

Se utiliza [CardiffNLP XLM-R sentiment](https://huggingface.co/cardiffnlp/twitter-xlm-roberta-base-sentiment),
un modelo multilingüe de texto social ajustado con ocho idiomas, incluido
español. Sus etiquetas son estimaciones automáticas. No hay verdad de terreno
local y existe cambio de dominio entre tuits y comentarios de YouTube.

## Limitaciones que afectan la lectura

- Solo se observan los comentarios recolectados; cero comentarios en el archivo no equivale a cero comentarios en YouTube.
- La selección depende de consultas y canales usados durante la recolección.
- Las fechas relativas (`published_time`, `published_text`) dependen del momento de captura.
- Visualizaciones, me gusta y respuestas son conteos observados en un momento particular.
- Los vacíos de `like_count_text` se tratan como desconocidos, no como cero.
- No se conoce quién respondió a quién y `reply_count` no permite crear relaciones entre autores.
- Los nombres y handles pueden cambiar o repetirse; las redes utilizan IDs.
- Asociación, coparticipación y centralidad descriptiva no demuestran causalidad ni representan a toda Guatemala o a todos los usuarios de YouTube.
- Las comunidades dependen del algoritmo, los pesos, la semilla y la cobertura de comentarios; no son grupos sociales verificados.
- El sentimiento puede equivocarse con sarcasmo, modismos, texto mixto o contexto externo y no se validó con etiquetas humanas de esta muestra.
