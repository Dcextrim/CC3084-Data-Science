"""Sentimiento multilingüe sin traducir los comentarios originales."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
LABELS = ("negative", "neutral", "positive")


def normalize_social_text(value: object) -> str:
    """Aplica únicamente la normalización recomendada para texto social.

    Se sustituyen menciones y URL por marcadores; no se traduce, elimina
    puntuación, cambia el idioma ni retira emojis o negaciones.
    """

    text = "" if pd.isna(value) else str(value)
    text = re.sub(r"(?i)https?://\S+|www\.\S+", "http", text)
    text = re.sub(r"(?<!\w)/?@[\w.-]+", "@user", text)
    return text.strip()


def analyze_sentiment(
    texts: pd.Series,
    cache_dir: Path,
    batch_size: int = 16,
    max_length: int = 128,
) -> pd.DataFrame:
    """Clasifica textos con XLM-R y devuelve probabilidades auditables."""

    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    cache_dir.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME, cache_dir=cache_dir, use_fast=False
    )
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, cache_dir=cache_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    normalized = texts.map(normalize_social_text).tolist()
    probability_batches: list[object] = []
    with torch.inference_mode():
        for start in range(0, len(normalized), batch_size):
            encoded = tokenizer(
                normalized[start : start + batch_size],
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors="pt",
            ).to(device)
            logits = model(**encoded).logits
            probability_batches.append(torch.softmax(logits, dim=1).cpu())

    probabilities = torch.cat(probability_batches).numpy()
    result = pd.DataFrame(probabilities, columns=[f"p_{label}" for label in LABELS], index=texts.index)
    result["sentiment_label"] = result[[f"p_{label}" for label in LABELS]].idxmax(axis=1).str.removeprefix("p_")
    result["sentiment_confidence"] = result[[f"p_{label}" for label in LABELS]].max(axis=1)
    result["sentiment_score"] = result["p_positive"] - result["p_negative"]
    result["sentiment_model"] = MODEL_NAME
    return result
