"""Carga, diagnóstico, limpieza e integración de los dos CSV de YouTube.

Los datos de ``data/raw`` nunca se sobrescriben. Las funciones devuelven copias
y el orquestador guarda únicamente resultados reproducibles en
``data/processed``.
"""

from __future__ import annotations

import ast
import json
import re
import unicodedata
from collections import Counter

import emoji
import pandas as pd
from spacy.lang.en.stop_words import STOP_WORDS as STOP_WORDS_EN
from spacy.lang.es.stop_words import STOP_WORDS as STOP_WORDS_ES

from config import (
    COMMENT_COLUMNS,
    COMMENTS_CLEAN,
    COMMENTS_INTEGRATED,
    COMMENTS_RAW,
    PROCESSED_DIR,
    VIDEO_COLUMNS,
    VIDEOS_CLEAN,
    VIDEOS_RAW,
)


URL_RE = re.compile(r"(?:https?://|www\.)\S+", flags=re.IGNORECASE)
HASHTAG_RE = re.compile(r"(?<!\w)#([\wáéíóúüñÁÉÍÓÚÜÑ]+)", flags=re.UNICODE)
MENTION_RE = re.compile(r"(?<!\w)@([\w.-]+)", flags=re.UNICODE)
TOKEN_RE = re.compile(r"[^\W\d_]+", flags=re.UNICODE)

# Se preservan negaciones porque eliminarlas cambia el sentido del comentario.
NEGATIONS = {
    "no",
    "ni",
    "nunca",
    "jamás",
    "sin",
    "not",
    "never",
    "nor",
    "without",
}
STOP_WORDS = (set(STOP_WORDS_ES) | set(STOP_WORDS_EN)) - NEGATIONS


def assert_condition(condition: bool, message: str) -> None:
    """Detiene el flujo inmediatamente si no se cumple un contrato."""

    if not condition:
        raise ValueError(message)


def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carga los archivos originales y valida sus columnas y llaves."""

    videos = pd.read_csv(VIDEOS_RAW, low_memory=False)
    comments = pd.read_csv(COMMENTS_RAW, low_memory=False)

    missing_video_columns = set(VIDEO_COLUMNS) - set(videos.columns)
    missing_comment_columns = set(COMMENT_COLUMNS) - set(comments.columns)
    assert_condition(
        not missing_video_columns,
        f"Faltan columnas en videos: {sorted(missing_video_columns)}",
    )
    assert_condition(
        not missing_comment_columns,
        f"Faltan columnas en comentarios: {sorted(missing_comment_columns)}",
    )
    assert_condition(videos["video_id"].notna().all(), "video_id contiene nulos")
    assert_condition(comments["comment_id"].notna().all(), "comment_id contiene nulos")
    assert_condition(videos["video_id"].is_unique, "video_id no es llave primaria")
    assert_condition(comments["comment_id"].is_unique, "comment_id no es llave primaria")
    return videos, comments


def normalize_identifier(series: pd.Series) -> pd.Series:
    """Normaliza espacios en IDs sin reemplazarlos por nombres visibles."""

    result = series.astype("string").str.strip()
    return result.mask(result.eq(""), pd.NA)


def normalize_label(series: pd.Series) -> pd.Series:
    """Normaliza espacios accidentales en nombres o handles visibles."""

    result = series.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    return result.mask(result.eq(""), pd.NA)


def parse_count(value: object) -> int | pd._libs.missing.NAType:
    """Convierte conteos de texto con separadores y abreviaturas a enteros."""

    if pd.isna(value):
        return pd.NA
    text = unicodedata.normalize("NFKC", str(value)).casefold().strip()
    if not text or text in {"na", "n/a", "nan", "null", "-"}:
        return pd.NA

    match = re.search(
        r"([-+]?\d[\d.,\s]*?)\s*(k|mil|m|mm|mill[oó]n(?:es)?)?(?:\s|$)",
        text,
    )
    if not match:
        return pd.NA

    number_text = match.group(1).replace(" ", "")
    suffix = match.group(2)
    factor = 1
    if suffix in {"k", "mil"}:
        factor = 1_000
    elif suffix in {"m", "mm", "millón", "millon", "millones"}:
        factor = 1_000_000

    if factor == 1:
        number_text = number_text.replace(",", "").replace(".", "")
    else:
        # Con una abreviatura, el único separador se interpreta como decimal.
        if number_text.count(",") == 1 and "." not in number_text:
            number_text = number_text.replace(",", ".")
        elif number_text.count(".") > 1:
            number_text = number_text.replace(".", "")
        number_text = number_text.replace(",", "")

    try:
        return int(round(float(number_text) * factor))
    except ValueError:
        return pd.NA


def parse_list(value: object) -> list[str]:
    """Interpreta listas serializadas como texto sin ejecutar código."""

    if pd.isna(value) or not str(value).strip():
        return []
    try:
        parsed = ast.literal_eval(str(value))
    except (SyntaxError, ValueError):
        return []
    if not isinstance(parsed, (list, tuple, set)):
        return []
    return [str(item).strip() for item in parsed if str(item).strip()]


def _json_list(items: list[str]) -> str:
    return json.dumps(items, ensure_ascii=False)


def clean_text_record(value: object) -> dict[str, str]:
    """Crea una versión auditable y otra conservadora para análisis léxico.

    No traduce ni lematiza. La lematización española no se aplica al corpus
    completo porque hay comentarios en varios idiomas y podría deformarlos.
    """

    original = "" if pd.isna(value) else str(value)
    normalized = unicodedata.normalize("NFKC", original)
    hashtags = [match.casefold() for match in HASHTAG_RE.findall(normalized)]
    mentions = [match for match in MENTION_RE.findall(normalized)]
    emojis = [item["emoji"] for item in emoji.emoji_list(normalized)]

    cleaned = URL_RE.sub(" ", normalized)
    cleaned = HASHTAG_RE.sub(lambda match: f" {match.group(1)} ", cleaned)
    cleaned = MENTION_RE.sub(" ", cleaned)
    cleaned = emoji.replace_emoji(cleaned, replace=" ")
    cleaned = cleaned.casefold()
    cleaned = re.sub(r"\d+", " ", cleaned)
    tokens = TOKEN_RE.findall(cleaned)
    tokens = [
        token
        for token in tokens
        if token not in STOP_WORDS and (len(token) > 1 or token in NEGATIONS)
    ]

    return {
        "texto_original": original,
        "texto_limpio": " ".join(tokens),
        "hashtags": _json_list(hashtags),
        "menciones": _json_list(mentions),
        "emojis": _json_list(emojis),
    }


def prepare_videos(videos: pd.DataFrame) -> pd.DataFrame:
    """Normaliza identificadores, conteos, fechas y listas de videos."""

    clean = videos.copy()
    for column in ["video_id", "channel_id"]:
        clean[column] = normalize_identifier(clean[column])
    for column in ["title", "channel_name", "channel_handle", "owner_handle"]:
        clean[column] = normalize_label(clean[column])

    clean["view_count"] = pd.to_numeric(clean["view_count"], errors="coerce").astype("Int64")
    clean["view_count_text_num"] = clean["view_count_text"].map(parse_count).astype("Int64")
    clean["publish_datetime"] = pd.to_datetime(clean["publish_date"], errors="coerce", utc=True)
    clean["upload_datetime"] = pd.to_datetime(clean["upload_date"], errors="coerce", utc=True)
    clean["query_hits_json"] = clean["query_hits"].map(lambda value: _json_list(parse_list(value)))
    clean["keywords_json"] = clean["keywords"].map(lambda value: _json_list(parse_list(value)))

    assert_condition(clean["video_id"].notna().all(), "Hay video_id vacío tras normalizar")
    assert_condition(clean["video_id"].is_unique, "video_id dejó de ser único")
    return clean


def prepare_comments(comments: pd.DataFrame) -> pd.DataFrame:
    """Normaliza IDs, conteos y texto sin eliminar observaciones."""

    clean = comments.copy()
    for column in ["video_id", "comment_id", "channel_id", "author_channel_id"]:
        clean[column] = normalize_identifier(clean[column])
    for column in ["video_title", "channel_name", "author_name", "author_handle"]:
        clean[column] = normalize_label(clean[column])

    clean["like_count"] = clean["like_count_text"].map(parse_count).astype("Int64")
    clean["reply_count"] = pd.to_numeric(clean["reply_count"], errors="coerce").astype("Int64")
    text_fields = clean["text"].map(clean_text_record).apply(pd.Series)
    for column in text_fields.columns:
        clean[column] = text_fields[column]

    assert_condition(clean["comment_id"].notna().all(), "Hay comment_id vacío tras normalizar")
    assert_condition(clean["comment_id"].is_unique, "comment_id dejó de ser único")
    return clean


def integrate_data(comments: pd.DataFrame, videos: pd.DataFrame) -> pd.DataFrame:
    """Une cada comentario con su video mediante una relación muchos-a-uno."""

    video_attributes = videos[
        [
            "video_id",
            "title",
            "channel_id",
            "channel_name",
            "category",
            "source_query",
            "source_group",
            "view_count",
            "publish_datetime",
        ]
    ].rename(
        columns={
            "title": "video_title_ref",
            "channel_id": "video_channel_id_ref",
            "channel_name": "video_channel_name_ref",
            "source_query": "video_source_query_ref",
            "source_group": "video_source_group_ref",
        }
    )
    integrated = comments.merge(
        video_attributes,
        on="video_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    return integrated


def column_quality(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    """Resume tipos, faltantes, cardinalidad y variables constantes."""

    rows = []
    for column in df.columns:
        non_null_unique = int(df[column].nunique(dropna=True))
        missing = int(df[column].isna().sum())
        rows.append(
            {
                "dataset": dataset,
                "variable": column,
                "dtype": str(df[column].dtype),
                "faltantes": missing,
                "porcentaje_faltante": round(100 * missing / len(df), 2),
                "valores_unicos": non_null_unique,
                "constante": non_null_unique == 1,
                "totalmente_vacia": missing == len(df),
            }
        )
    return pd.DataFrame(rows)


def dataset_quality_summary(
    df: pd.DataFrame, dataset: str, primary_key: str
) -> pd.DataFrame:
    """Produce el diagnóstico general solicitado para un conjunto."""

    constants = [
        column for column in df.columns if df[column].nunique(dropna=True) == 1
    ]
    all_missing = [column for column in df.columns if df[column].isna().all()]
    return pd.DataFrame(
        [
            {
                "dataset": dataset,
                "filas": len(df),
                "columnas": len(df.columns),
                "filas_duplicadas": int(df.duplicated().sum()),
                "llave_duplicada": int(df[primary_key].duplicated().sum()),
                "variables_constantes": ", ".join(constants) or "ninguna",
                "variables_totalmente_vacias": ", ".join(all_missing) or "ninguna",
            }
        ]
    )


def outlier_summary(df: pd.DataFrame, columns: list[str], dataset: str) -> pd.DataFrame:
    """Marca atípicos con 1.5 veces el rango intercuartílico, sin borrarlos."""

    rows = []
    for column in columns:
        values = pd.to_numeric(df[column], errors="coerce").dropna()
        if values.empty:
            continue
        q1, q3 = values.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = ((values < lower) | (values > upper)).sum()
        rows.append(
            {
                "dataset": dataset,
                "variable": column,
                "minimo": values.min(),
                "q1": q1,
                "mediana": values.median(),
                "q3": q3,
                "maximo": values.max(),
                "limite_inferior_iqr": lower,
                "limite_superior_iqr": upper,
                "atipicos_iqr": int(outliers),
            }
        )
    return pd.DataFrame(rows)


def mapping_ambiguities(
    df: pd.DataFrame, dataset: str, id_column: str, label_column: str
) -> pd.DataFrame:
    """Cuenta IDs asociados con más de una etiqueta visible."""

    pairs = df[[id_column, label_column]].dropna().drop_duplicates()
    counts = pairs.groupby(id_column)[label_column].nunique()
    return pd.DataFrame(
        [
            {
                "dataset": dataset,
                "id": id_column,
                "etiqueta": label_column,
                "ids_con_multiples_etiquetas": int((counts > 1).sum()),
                "maximo_etiquetas_por_id": int(counts.max()) if len(counts) else 0,
            }
        ]
    )


def cross_dataset_consistency(
    comments: pd.DataFrame, videos: pd.DataFrame
) -> pd.DataFrame:
    """Compara títulos y datos de canal redundantes después del join por ID."""

    reference = videos[
        ["video_id", "title", "channel_id", "channel_name"]
    ].rename(
        columns={
            "title": "title_ref",
            "channel_id": "channel_id_ref",
            "channel_name": "channel_name_ref",
        }
    )
    compared = comments.merge(reference, on="video_id", how="left", validate="many_to_one")
    checks = [
        ("video_title", "title_ref"),
        ("channel_id", "channel_id_ref"),
        ("channel_name", "channel_name_ref"),
    ]
    rows = []
    for observed, expected in checks:
        comparable = compared[observed].notna() & compared[expected].notna()
        mismatches = (
            compared.loc[comparable, observed].astype("string").str.strip()
            != compared.loc[comparable, expected].astype("string").str.strip()
        ).sum()
        rows.append(
            {
                "variable_comentarios": observed,
                "variable_referencia_videos": expected,
                "comparables": int(comparable.sum()),
                "diferencias": int(mismatches),
            }
        )
    return pd.DataFrame(rows)


def cleaning_effect(comments: pd.DataFrame) -> pd.DataFrame:
    """Cuantifica registros modificados, vacíos y duplicados por la limpieza."""

    original = comments["texto_original"].fillna("").astype(str)
    cleaned = comments["texto_limpio"].fillna("").astype(str)
    original_nonempty = original.str.strip().ne("")
    cleaned_nonempty = cleaned.str.strip().ne("")
    return pd.DataFrame(
        [
            {"metrica": "registros_totales", "valor": len(comments)},
            {"metrica": "registros_eliminados", "valor": 0},
            {
                "metrica": "registros_modificados",
                "valor": int((original.str.strip() != cleaned.str.strip()).sum()),
            },
            {
                "metrica": "textos_vacios_antes",
                "valor": int((~original_nonempty).sum()),
            },
            {
                "metrica": "textos_vacios_despues",
                "valor": int((~cleaned_nonempty).sum()),
            },
            {
                "metrica": "duplicados_texto_antes",
                "valor": int(original[original_nonempty].duplicated().sum()),
            },
            {
                "metrica": "duplicados_texto_despues",
                "valor": int(cleaned[cleaned_nonempty].duplicated().sum()),
            },
        ]
    )


def decode_json_list(value: object) -> list[str]:
    """Decodifica una lista JSON generada por este módulo."""

    if pd.isna(value) or not str(value).strip():
        return []
    try:
        decoded = json.loads(str(value))
    except json.JSONDecodeError:
        return []
    return decoded if isinstance(decoded, list) else []


def frequency_table(texts: pd.Series, ngram: int = 1, top_n: int = 15) -> pd.DataFrame:
    """Cuenta palabras o n-gramas sobre ``texto_limpio``."""

    counter: Counter[str] = Counter()
    for text in texts.fillna("").astype(str):
        tokens = text.split()
        if ngram == 1:
            counter.update(tokens)
        else:
            counter.update(" ".join(tokens[i : i + ngram]) for i in range(len(tokens) - ngram + 1))
    label = "palabra" if ngram == 1 else f"{ngram}-grama"
    return pd.DataFrame(counter.most_common(top_n), columns=[label, "frecuencia"])


def list_frequency_table(series: pd.Series, label: str, top_n: int = 15) -> pd.DataFrame:
    """Cuenta elementos de columnas que contienen listas JSON."""

    counter: Counter[str] = Counter()
    for value in series:
        counter.update(decode_json_list(value))
    return pd.DataFrame(counter.most_common(top_n), columns=[label, "frecuencia"])


def save_processed(
    videos: pd.DataFrame,
    comments: pd.DataFrame,
    integrated: pd.DataFrame,
) -> None:
    """Guarda las tres tablas limpias sin modificar los archivos originales."""

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    videos.to_csv(VIDEOS_CLEAN, index=False, encoding="utf-8")
    comments.to_csv(COMMENTS_CLEAN, index=False, encoding="utf-8")
    integrated.drop(columns=["_merge"], errors="ignore").to_csv(
        COMMENTS_INTEGRATED, index=False, encoding="utf-8"
    )
