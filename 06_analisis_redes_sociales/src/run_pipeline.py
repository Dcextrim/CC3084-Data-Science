"""Ejecuta el procesamiento y reconstruye las tablas de los ejercicios 1–8."""

import pandas as pd

from config import COMMENTS_INTEGRATED, NETWORK_EDGES, NETWORK_NODES, VIDEOS_CLEAN
from data_processing import (
    integrate_data,
    load_raw_data,
    prepare_comments,
    prepare_videos,
    save_processed,
)
from network_analysis import (
    build_bipartite_graph,
    build_network_tables,
    build_projections,
    centrality_table,
    degree_distribution,
    detect_video_communities,
    network_summary,
    save_advanced_network_tables,
    save_network_tables,
)


def main() -> None:
    videos_raw, comments_raw = load_raw_data()
    videos = prepare_videos(videos_raw)
    comments = prepare_comments(comments_raw)
    integrated = integrate_data(comments, videos)
    nodes, edges = build_network_tables(comments, videos)
    graph = build_bipartite_graph(nodes, edges)
    author_projection, video_projection = build_projections(graph)
    metrics = pd.DataFrame(
        [
            network_summary(graph, "bipartite"),
            network_summary(author_projection, "author-author"),
            network_summary(video_projection, "video-video"),
        ]
    )
    distributions = pd.concat(
        [
            degree_distribution(graph, "bipartite"),
            degree_distribution(author_projection, "author-author"),
            degree_distribution(video_projection, "video-video"),
        ],
        ignore_index=True,
    )
    communities, _, _, _ = detect_video_communities(video_projection)
    centralities = centrality_table(graph)

    save_processed(videos, comments, integrated)
    save_network_tables(nodes, edges)
    save_advanced_network_tables(
        author_projection,
        video_projection,
        metrics,
        distributions,
        communities,
        centralities,
    )

    print(f"[ok] {len(videos):,} videos limpios -> {VIDEOS_CLEAN.name}")
    print(f"[ok] {len(comments):,} comentarios integrados -> {COMMENTS_INTEGRATED.name}")
    print(f"[ok] {len(nodes):,} nodos -> {NETWORK_NODES.name}")
    print(f"[ok] {len(edges):,} aristas -> {NETWORK_EDGES.name}")
    print(f"[ok] {author_projection.number_of_edges():,} aristas autor-autor")
    print(f"[ok] {video_projection.number_of_edges():,} aristas video-video")


if __name__ == "__main__":
    main()
