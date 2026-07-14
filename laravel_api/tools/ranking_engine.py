"""
Ranking engine utilities for computing authenticity, relationship,
semantic, time-decay and final feed score for posts.

Usage (basic):
  from tools.ranking_engine import compute_feed_score, compute_image_authenticity, caption_originality

  auth = compute_image_authenticity('images/photo.jpg', 'Nice hike with friends')
  score = compute_feed_score(auth['authenticity'], time_decay, relationship, semantic)

This module optionally uses `sentence_transformers` and `chromadb` when available.
It is written to be run independently from the Laravel app and can be used to precompute
scores for posts before returning the /api/feed response.
"""

import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional

try:
    import cv2
    import numpy as np
except Exception:
    cv2 = None
    np = None

try:
    from sentence_transformers import SentenceTransformer, util
    _DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
except Exception:
    SentenceTransformer = None
    util = None

try:
    import chromadb
    from chromadb.config import Settings
except Exception:
    chromadb = None


# -----------------------------
# Caption originality + spam/inappropriate heuristics
# -----------------------------
GENERIC_PHRASES = [
    "like share follow",
    "viral",
    "follow me",
    "check bio",
    "subscribe",
    "best post ever",
    "amazing",
    "click the link",
]

BAD_WORDS = {"hate", "stupid", "idiot", "kill", "damn"}
SPAM_WORDS = {"buy", "sale", "discount", "free", "offer", "limited", "click", "subscribe", "follow"}
FIRST_PERSON = {"i", "me", "my", "mine", "we", "our", "us"}


def _load_model(name: str = _DEFAULT_MODEL_NAME):
    if SentenceTransformer is None:
        raise RuntimeError("sentence_transformers is not installed")
    return SentenceTransformer(name)


_GLOBAL_MODEL = None
_GENERIC_EMB = None


def _ensure_model():
    global _GLOBAL_MODEL, _GENERIC_EMB
    if _GLOBAL_MODEL is None:
        _GLOBAL_MODEL = _load_model()
        if _GENERIC_EMB is None:
            _GENERIC_EMB = _GLOBAL_MODEL.encode(GENERIC_PHRASES, convert_to_tensor=True)
    return _GLOBAL_MODEL, _GENERIC_EMB


def caption_originality(text: str) -> Dict[str, float]:
    model, generic_embeddings = _ensure_model()
    t = text.lower().strip()

    # semantic originality
    emb = model.encode(t, convert_to_tensor=True)
    similarity = float(util.cos_sim(emb, generic_embeddings).max())
    originality = max(0.0, min(1.0, 1 - similarity))

    # repetition
    words = re.findall(r"\w+", t)
    unique_ratio = len(set(words)) / max(len(words), 1)

    # spam
    spam_count = sum(1 for w in words if w in SPAM_WORDS)
    spam_score = max(0.0, 1 - spam_count / 5)

    # inappropriate
    bad_count = sum(1 for w in words if w in BAD_WORDS)
    inappropriate_score = max(0.0, 1 - bad_count / 3)

    # personal storytelling
    personal_count = sum(1 for w in words if w in FIRST_PERSON)
    personal_score = min(personal_count / 3, 1.0)

    # length
    length = len(words)
    if length < 4:
        length_score = 0.4
    elif length < 10:
        length_score = 0.7
    elif length <= 60:
        length_score = 1.0
    else:
        length_score = 0.8

    # hashtag penalty
    hashtags = t.count("#")
    hashtag_score = max(0.0, 1 - hashtags / 10)

    # emoji penalty (basic range)
    emojis = len(re.findall(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]", t))
    emoji_score = max(0.5, 1 - emojis / 20)

    final = (
        originality * 0.30
        + unique_ratio * 0.15
        + spam_score * 0.15
        + inappropriate_score * 0.15
        + personal_score * 0.10
        + length_score * 0.05
        + hashtag_score * 0.05
        + emoji_score * 0.05
    )

    return {
        "originality": round(originality, 3),
        "repetition": round(unique_ratio, 3),
        "spam": round(spam_score, 3),
        "appropriate": round(inappropriate_score, 3),
        "personal": round(personal_score, 3),
        "length": round(length_score, 3),
        "hashtags": round(hashtag_score, 3),
        "emoji": round(emoji_score, 3),
        "final": round(final, 3),
    }


# -----------------------------
# Image-based authenticity
# -----------------------------
def _read_image(image_path: str):
    if cv2 is None:
        raise RuntimeError("OpenCV (cv2) is required for image scoring")
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    return img


def filter_score(image_path: str) -> float:
    img = _read_image(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    saturation = float(np.mean(hsv[:, :, 1]))
    score = 1 - (saturation / 255.0)
    return max(0.0, min(1.0, score))


def natural_image_score(image_path: str) -> float:
    img = _read_image(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian < 50:
        return 0.4
    elif laplacian < 150:
        return 0.8
    elif laplacian < 300:
        return 1.0
    else:
        return 0.6


def noise_score(image_path: str) -> float:
    img = _read_image(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    noise = float(np.mean(np.abs(gray.astype(float) - blur.astype(float))))
    return min(noise / 25.0, 1.0)


def brightness_score(image_path: str) -> float:
    img = _read_image(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    brightness = float(np.mean(hsv[:, :, 2]))
    ideal = 140.0
    diff = abs(brightness - ideal)
    score = 1 - (diff / 140.0)
    return max(0.0, min(1.0, score))


def hashtag_penalty(text: str) -> float:
    hashtags = text.count("#")
    if hashtags <= 2:
        return 1.0
    if hashtags <= 5:
        return 0.7
    return 0.3


def compute_image_authenticity(image_path: str, caption: str) -> Dict[str, float]:
    f = filter_score(image_path)
    n = natural_image_score(image_path)
    noise = noise_score(image_path)
    b = brightness_score(image_path)
    c = caption_originality(caption)["final"]
    h = hashtag_penalty(caption)

    final = 0.25 * f + 0.20 * n + 0.10 * noise + 0.15 * b + 0.20 * c + 0.10 * h

    return {
        "filter_score": round(f, 3),
        "natural_image": round(n, 3),
        "noise_score": round(noise, 3),
        "brightness": round(b, 3),
        "caption_originality": round(c, 3),
        "hashtag_score": round(h, 3),
        "authenticity": round(final, 3),
    }


# -----------------------------
# Relationship score
# -----------------------------
def relationship_score_for_post(current_user_id: Any, post_author_id: Any, interactions_by_user_on_author: Mapping[Any, int]) -> float:
    """
    interactions_by_user_on_author: mapping author_id -> count of interactions by current user with that author
    returns score in [0,1]
    """
    if current_user_id == post_author_id:
        return 0.2
    count = int(interactions_by_user_on_author.get(post_author_id, 0))
    score = min(1.0, 0.2 + 0.08 * count)
    return round(score, 4)


# -----------------------------
# Semantic scoring (Chroma optional)
# -----------------------------
def create_chroma_client(in_memory: bool = True):
    if chromadb is None:
        raise RuntimeError("chromadb is not installed")
    if in_memory:
        client = chromadb.Client(Settings(chroma_db_impl="chromadb.db.in_memory"))
    else:
        client = chromadb.Client()
    return client


def embed_text(text: str):
    model, _ = _ensure_model()
    return model.encode(text, convert_to_tensor=True)


def semantic_similarity_between_vectors(vec_a, vec_b) -> float:
    if util is None:
        raise RuntimeError("sentence_transformers util not available")
    sim = float(util.cos_sim(vec_a, vec_b).item())
    return max(0.0, min(1.0, sim))


def compute_semantic_score_with_chroma(client, collection_name: str, query_embedding, top_k: int = 5) -> float:
    """
    Query chroma collection and return best similarity (0..1). Requires collection to be populated.
    """
    coll = client.get_collection(name=collection_name)
    results = coll.query(query_embeddings=query_embedding.tolist() if hasattr(query_embedding, 'tolist') else query_embedding, n_results=top_k)
    # results['distances'] or 'metadatas' depends on client; conservatively fallback
    if not results or 'distances' not in results:
        return 0.0
    # distances are smaller for closer vectors; convert to similarity
    distances = results['distances'][0]
    if not distances:
        return 0.0
    best = 1.0 / (1.0 + distances[0])
    return float(max(0.0, min(1.0, best)))


# -----------------------------
# Time decay
# -----------------------------
def time_decay_score(created_at: datetime) -> float:
    """
    created_at: timezone-aware or naive UTC datetime
    """
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    age_hours = max(1.0, (datetime.now(timezone.utc) - created_at).total_seconds() / 3600.0)
    return round(1.0 / (1.0 + (age_hours / 36.0)), 4)


def compute_feed_score(authenticity: float, time_decay: float, relationship: float, semantic: float) -> float:
    final = (0.30 * authenticity) + (0.10 * time_decay) + (0.30 * relationship) + (0.30 * semantic)
    return round(max(0.0, min(1.0, final)), 4)


if __name__ == "__main__":
    print("ranking_engine module loaded. Use the functions to compute scores.")
