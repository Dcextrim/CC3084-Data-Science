"""Ejecuta el procesamiento y reconstruye todas las tablas del avance 1–4."""

from config import COMMENTS_INTEGRATED, NETWORK_EDGES, NETWORK_NODES, VIDEOS_CLEAN
from data_processing import (
    integrate_data,
    load_raw_data,
    prepare_comments,
    prepare_videos,
    save_processed,
)
from network_analysis import build_network_tables, save_network_tables


def main() -> None:
    videos_raw, comments_raw = load_raw_data()
    videos = prepare_videos(videos_raw)
    comments = prepare_comments(comments_raw)
    integrated = integrate_data(comments, videos)
    nodes, edges = build_network_tables(comments, videos)

    save_processed(videos, comments, integrated)
    save_network_tables(nodes, edges)

    print(f"[ok] {len(videos):,} videos limpios -> {VIDEOS_CLEAN.name}")
    print(f"[ok] {len(comments):,} comentarios integrados -> {COMMENTS_INTEGRATED.name}")
    print(f"[ok] {len(nodes):,} nodos -> {NETWORK_NODES.name}")
    print(f"[ok] {len(edges):,} aristas -> {NETWORK_EDGES.name}")


if __name__ == "__main__":
    main()
