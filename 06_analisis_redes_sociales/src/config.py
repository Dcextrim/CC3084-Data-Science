"""Rutas y contratos compartidos por el avance del Laboratorio 6."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

VIDEOS_RAW = RAW_DIR / "youtube_videos.csv"
COMMENTS_RAW = RAW_DIR / "youtube_comments.csv"

VIDEOS_CLEAN = PROCESSED_DIR / "youtube_videos_clean.csv"
COMMENTS_CLEAN = PROCESSED_DIR / "youtube_comments_clean.csv"
COMMENTS_INTEGRATED = PROCESSED_DIR / "youtube_comments_integrated.csv"
NETWORK_NODES = PROCESSED_DIR / "network_nodes.csv"
NETWORK_EDGES = PROCESSED_DIR / "network_edges.csv"

VIDEO_COLUMNS = [
    "video_id",
    "title",
    "channel_name",
    "channel_id",
    "source_query",
    "source_group",
    "dataset_sources",
    "channel_handle",
    "published_time",
    "view_count_text",
    "description_snippet",
    "video_url",
    "query_hits",
    "keywords",
    "description",
    "view_count",
    "publish_date",
    "upload_date",
    "category",
    "owner_handle",
]

COMMENT_COLUMNS = [
    "video_id",
    "comment_id",
    "video_title",
    "channel_name",
    "channel_id",
    "author_name",
    "author_channel_id",
    "text",
    "source_query",
    "source_group",
    "dataset_sources",
    "author_handle",
    "published_text",
    "like_count_text",
    "reply_count",
    "is_pinned",
    "viewer_rating",
]
