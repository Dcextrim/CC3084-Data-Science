"""Construcción de la red bipartita autor–video para el ejercicio 4."""

from __future__ import annotations

import networkx as nx
import pandas as pd

from config import NETWORK_EDGES, NETWORK_NODES, PROCESSED_DIR
from data_processing import assert_condition


def representative_label(series: pd.Series) -> object:
    """Elige la etiqueta visible más frecuente sin usarla como identificador."""

    values = series.dropna().astype("string").str.strip()
    values = values[values.ne("")]
    if values.empty:
        return pd.NA
    return values.value_counts().index[0]


def build_network_tables(
    comments: pd.DataFrame, videos: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Crea tablas de nodos y aristas de la red bipartita no dirigida.

    Se incluyen todos los videos del CSV, incluso los que no recibieron un
    comentario en la muestra. No existen autores observables sin comentarios.
    """

    usable = comments.dropna(subset=["author_channel_id", "video_id"]).copy()

    edges = (
        usable.groupby(["author_channel_id", "video_id"], as_index=False)
        .size()
        .rename(columns={"size": "weight"})
    )
    video_attributes = videos[
        ["video_id", "title", "channel_id", "channel_name"]
    ].drop_duplicates("video_id")
    edges = edges.merge(video_attributes, on="video_id", how="left", validate="many_to_one")
    edges.insert(0, "source", "author::" + edges["author_channel_id"].astype(str))
    edges.insert(1, "target", "video::" + edges["video_id"].astype(str))
    edges = edges[
        [
            "source",
            "target",
            "weight",
            "author_channel_id",
            "video_id",
            "title",
            "channel_id",
            "channel_name",
        ]
    ].rename(columns={"title": "video_title"})

    author_nodes = (
        usable.groupby("author_channel_id")
        .agg(
            author_name=("author_name", representative_label),
            author_handle=("author_handle", representative_label),
            comment_count=("comment_id", "size"),
            unique_videos=("video_id", "nunique"),
            unique_channels=("channel_id", "nunique"),
        )
        .reset_index()
    )
    author_nodes["node_id"] = "author::" + author_nodes["author_channel_id"].astype(str)
    author_nodes["node_type"] = "author"
    author_nodes["original_id"] = author_nodes["author_channel_id"]
    author_nodes["label"] = author_nodes["author_handle"].fillna(author_nodes["author_name"])
    author_nodes["channel_name"] = pd.NA
    author_nodes["title"] = pd.NA
    author_nodes["category"] = pd.NA
    author_nodes["view_count"] = pd.NA
    author_nodes["unique_neighbors"] = author_nodes["unique_videos"]

    video_participation = (
        usable.groupby("video_id")
        .agg(
            comment_count=("comment_id", "size"),
            unique_neighbors=("author_channel_id", "nunique"),
        )
        .reset_index()
    )
    video_nodes = videos[
        ["video_id", "title", "channel_id", "channel_name", "category", "view_count"]
    ].drop_duplicates("video_id")
    video_nodes = video_nodes.merge(video_participation, on="video_id", how="left")
    video_nodes[["comment_count", "unique_neighbors"]] = video_nodes[
        ["comment_count", "unique_neighbors"]
    ].fillna(0).astype(int)
    video_nodes["node_id"] = "video::" + video_nodes["video_id"].astype(str)
    video_nodes["node_type"] = "video"
    video_nodes["original_id"] = video_nodes["video_id"]
    video_nodes["label"] = video_nodes["title"]
    video_nodes["author_name"] = pd.NA
    video_nodes["author_handle"] = pd.NA
    video_nodes["unique_videos"] = pd.NA
    video_nodes["unique_channels"] = pd.NA

    node_columns = [
        "node_id",
        "node_type",
        "original_id",
        "label",
        "author_name",
        "author_handle",
        "channel_id",
        "channel_name",
        "title",
        "category",
        "view_count",
        "comment_count",
        "unique_neighbors",
        "unique_videos",
        "unique_channels",
    ]
    nodes = pd.concat(
        [author_nodes.reindex(columns=node_columns), video_nodes.reindex(columns=node_columns)],
        ignore_index=True,
    )

    assert_condition(edges["weight"].gt(0).all(), "Hay aristas con peso no positivo")
    assert_condition(
        int(edges["weight"].sum()) == len(usable),
        "La suma de pesos no coincide con los comentarios utilizables",
    )
    assert_condition(nodes["node_id"].is_unique, "La tabla de nodos contiene IDs repetidos")
    assert_condition(
        set(edges["source"]).issubset(set(nodes["node_id"])),
        "Hay autores de aristas ausentes en nodos",
    )
    assert_condition(
        set(edges["target"]).issubset(set(nodes["node_id"])),
        "Hay videos de aristas ausentes en nodos",
    )
    return nodes, edges


def build_bipartite_graph(nodes: pd.DataFrame, edges: pd.DataFrame) -> nx.Graph:
    """Convierte las tablas auditables en un grafo no dirigido de NetworkX."""

    graph = nx.Graph()
    for row in nodes.to_dict(orient="records"):
        node_id = row.pop("node_id")
        row["bipartite"] = 0 if row["node_type"] == "author" else 1
        graph.add_node(node_id, **row)
    for row in edges.to_dict(orient="records"):
        graph.add_edge(row["source"], row["target"], weight=int(row["weight"]))
    assert_condition(nx.algorithms.bipartite.is_bipartite(graph), "El grafo no es bipartito")
    return graph


def save_network_tables(nodes: pd.DataFrame, edges: pd.DataFrame) -> None:
    """Guarda tablas reconstruibles para auditoría o uso posterior."""

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    nodes.to_csv(NETWORK_NODES, index=False, encoding="utf-8")
    edges.to_csv(NETWORK_EDGES, index=False, encoding="utf-8")
