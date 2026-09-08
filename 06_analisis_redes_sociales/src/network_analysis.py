"""Construcción y análisis de las redes autor-video del Laboratorio 6."""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd

from config import (
    AUTHOR_PROJECTION_EDGES,
    DEGREE_DISTRIBUTIONS,
    NETWORK_EDGES,
    NETWORK_METRICS,
    NETWORK_NODES,
    NODE_CENTRALITIES,
    PROCESSED_DIR,
    VIDEO_COMMUNITIES,
    VIDEO_PROJECTION_EDGES,
)
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


def build_projections(graph: nx.Graph) -> tuple[nx.Graph, nx.Graph]:
    """Proyecta la red bipartita preservando también los nodos aislados.

    En la proyección de autores, ``weight`` cuenta videos compartidos. En la
    proyección de videos, cuenta autores compartidos. El número de comentarios
    de la arista bipartita no se usa para inflar estas coincidencias.
    """

    authors = [n for n, data in graph.nodes(data=True) if data["node_type"] == "author"]
    videos = [n for n, data in graph.nodes(data=True) if data["node_type"] == "video"]
    author_projection = nx.algorithms.bipartite.weighted_projected_graph(graph, authors)
    video_projection = nx.algorithms.bipartite.weighted_projected_graph(graph, videos)

    for projection in (author_projection, video_projection):
        for node in projection:
            projection.nodes[node].update(graph.nodes[node])
        assert_condition(
            all(data["weight"] >= 1 for _, _, data in projection.edges(data=True)),
            "La proyección contiene pesos no positivos",
        )
    return author_projection, video_projection


def projection_edge_table(graph: nx.Graph, projection_type: str) -> pd.DataFrame:
    """Convierte una proyección en una tabla auditable de aristas."""

    rows = [
        {"source": u, "target": v, "weight": int(data["weight"]), "projection": projection_type}
        for u, v, data in graph.edges(data=True)
    ]
    return pd.DataFrame(rows, columns=["source", "target", "weight", "projection"])


def _largest_component(graph: nx.Graph) -> nx.Graph:
    """Devuelve una copia de la componente más grande o un grafo vacío."""

    if graph.number_of_nodes() == 0:
        return graph.copy()
    members = max(nx.connected_components(graph), key=len)
    return graph.subgraph(members).copy()


def network_summary(graph: nx.Graph, network_name: str) -> dict[str, object]:
    """Resume topología, fragmentación, cohesión y transitividad."""

    n = graph.number_of_nodes()
    m = graph.number_of_edges()
    degrees = np.array([degree for _, degree in graph.degree()], dtype=float)
    components = list(nx.connected_components(graph)) if n else []
    largest = _largest_component(graph)
    largest_n = largest.number_of_nodes()
    global_connectivity = nx.node_connectivity(graph) if n > 1 else 0
    largest_connectivity = nx.node_connectivity(largest) if largest_n > 1 else 0
    articulation_count = (
        sum(1 for _ in nx.articulation_points(graph)) if n > 1 else 0
    )

    return {
        "network": network_name,
        "nodes": n,
        "edges": m,
        "density": nx.density(graph) if n > 1 else 0.0,
        "mean_degree": float(degrees.mean()) if n else 0.0,
        "median_degree": float(np.median(degrees)) if n else 0.0,
        "p90_degree": float(np.quantile(degrees, 0.90)) if n else 0.0,
        "max_degree": int(degrees.max()) if n else 0,
        "isolates": int(np.sum(degrees == 0)) if n else 0,
        "leaves": int(np.sum(degrees == 1)) if n else 0,
        "components": len(components),
        "largest_component_nodes": largest_n,
        "largest_component_share": largest_n / n if n else 0.0,
        "node_connectivity": global_connectivity,
        "largest_component_node_connectivity": largest_connectivity,
        "transitivity": nx.transitivity(graph) if n >= 3 else 0.0,
        "articulation_points": articulation_count,
    }


def degree_distribution(graph: nx.Graph, network_name: str) -> pd.DataFrame:
    """Cuenta nodos para cada grado observado."""

    distribution = (
        pd.Series(dict(graph.degree()), dtype="int64")
        .value_counts()
        .sort_index()
        .rename_axis("degree")
        .reset_index(name="nodes")
    )
    distribution.insert(0, "network", network_name)
    distribution["node_share"] = distribution["nodes"] / graph.number_of_nodes()
    return distribution


def detect_video_communities(
    video_projection: nx.Graph, seed: int = 42
) -> tuple[pd.DataFrame, list[set[str]], float, nx.Graph]:
    """Detecta comunidades Louvain en videos con audiencia compartida.

    Los videos aislados se excluyen del ajuste porque Louvain los convertiría
    en comunidades unitarias sin evidencia de coparticipación.
    """

    active_nodes = [node for node, degree in video_projection.degree() if degree > 0]
    active_graph = video_projection.subgraph(active_nodes).copy()
    if active_graph.number_of_edges() == 0:
        return (
            pd.DataFrame(columns=["node_id", "community_id", "community_size"]),
            [],
            float("nan"),
            active_graph,
        )

    communities = list(
        nx.community.louvain_communities(active_graph, weight="weight", seed=seed)
    )
    communities.sort(key=lambda group: (-len(group), sorted(group)[0]))
    rows = [
        {"node_id": node, "community_id": community_id, "community_size": len(group)}
        for community_id, group in enumerate(communities, start=1)
        for node in sorted(group)
    ]
    membership = pd.DataFrame(rows)
    modularity = nx.community.modularity(active_graph, communities, weight="weight")
    return membership, communities, float(modularity), active_graph


def centrality_table(graph: nx.Graph) -> pd.DataFrame:
    """Calcula centralidades comparables e identifica puntos de articulación."""

    authors = {n for n, data in graph.nodes(data=True) if data["node_type"] == "author"}
    normalized_degree = nx.algorithms.bipartite.degree_centrality(graph, authors)
    betweenness = nx.betweenness_centrality(graph, normalized=True, weight=None)
    pagerank = nx.pagerank(graph, alpha=0.85, weight="weight")
    articulation = set(nx.articulation_points(graph))

    rows = []
    for node, data in graph.nodes(data=True):
        rows.append(
            {
                "node_id": node,
                "node_type": data["node_type"],
                "original_id": data.get("original_id"),
                "label": data.get("label"),
                "degree": int(graph.degree(node)),
                "weighted_degree": int(graph.degree(node, weight="weight")),
                "normalized_degree": float(normalized_degree[node]),
                "betweenness": float(betweenness[node]),
                "pagerank": float(pagerank[node]),
                "is_articulation": node in articulation,
            }
        )
    result = pd.DataFrame(rows)
    result["betweenness_rank_within_type"] = result.groupby("node_type")["betweenness"].rank(
        method="min", ascending=False
    ).astype(int)
    return result


def save_advanced_network_tables(
    author_projection: nx.Graph,
    video_projection: nx.Graph,
    metrics: pd.DataFrame,
    distributions: pd.DataFrame,
    communities: pd.DataFrame,
    centralities: pd.DataFrame,
) -> None:
    """Guarda las tablas reconstruibles de los ejercicios 5–8."""

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    projection_edge_table(author_projection, "author-author").to_csv(
        AUTHOR_PROJECTION_EDGES, index=False, encoding="utf-8"
    )
    projection_edge_table(video_projection, "video-video").to_csv(
        VIDEO_PROJECTION_EDGES, index=False, encoding="utf-8"
    )
    metrics.to_csv(NETWORK_METRICS, index=False, encoding="utf-8")
    distributions.to_csv(DEGREE_DISTRIBUTIONS, index=False, encoding="utf-8")
    communities.to_csv(VIDEO_COMMUNITIES, index=False, encoding="utf-8")
    centralities.to_csv(NODE_CENTRALITIES, index=False, encoding="utf-8")
