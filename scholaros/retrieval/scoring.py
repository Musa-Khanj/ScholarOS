"""
ScholarOS Retrieval Scoring and Fusion Algorithms.

Provides mathematical ranking algorithms including Reciprocal Rank Fusion (RRF),
min-max score normalization, linear score blending, and deduplication with
full provenance and metadata preservation.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

from scholaros.retrieval.result import RetrievalResult


def _build_result_key(res: RetrievalResult, key_func: str = "identity") -> str:
    """Build a stable unique identity key for a retrieval result."""
    if key_func == "chunk" and res.chunk_id:
        return f"chunk:{res.chunk_id}"
    if res.chunk_id:
        return f"chunk:{res.chunk_id}"
    if res.document_id:
        return f"doc:{res.document_id}"
    col = res.collection or "default"
    return f"{col}:{res.source}:{hash(res.content)}"


def deduplicate_results(
    results: Sequence[RetrievalResult],
    key_func: str = "identity",
) -> list[RetrievalResult]:
    """
    Deduplicate a list of retrieval results preserving the highest score,
    while merging metadata and preserving provenance.
    """
    best_by_key: dict[str, RetrievalResult] = {}

    for res in results:
        k = _build_result_key(res, key_func=key_func)

        if k not in best_by_key:
            best_by_key[k] = res
        else:
            existing = best_by_key[k]
            higher_score = max(existing.score, res.score)
            raw_score = max(existing.raw_score, res.raw_score)

            # Deep merge metadata
            merged_meta: dict[str, Any] = dict(existing.metadata)
            for mk, mv in res.metadata.items():
                if mk == "provenance" and isinstance(mv, dict) and "provenance" in merged_meta:
                    orig_prov = dict(merged_meta["provenance"]) if isinstance(merged_meta["provenance"], dict) else {}
                    # Merge streams
                    streams = set(orig_prov.get("streams", []))
                    if "streams" in mv:
                        streams.update(mv["streams"])
                    orig_prov.update(mv)
                    orig_prov["streams"] = sorted(streams)
                    merged_meta["provenance"] = orig_prov
                elif mk not in merged_meta:
                    merged_meta[mk] = mv

            # Choose base result (the one with higher score or richer content)
            base = res if res.score >= existing.score else existing
            updated = base.with_score(higher_score).with_metadata(merged_meta)
            if updated.raw_score != raw_score:
                updated._raw_score = raw_score
            best_by_key[k] = updated

    return sorted(best_by_key.values(), key=lambda r: r.score, reverse=True)


def min_max_normalize(
    results: Sequence[RetrievalResult],
) -> list[RetrievalResult]:
    """
    Normalize result scores into the [0.0, 1.0] interval.
    If all scores are equal or empty, returns scores of 1.0.
    """
    if not results:
        return []

    scores = [r.score for r in results]
    min_val = min(scores)
    max_val = max(scores)

    if math.isclose(max_val, min_val):
        return [r.with_score(1.0) for r in results]

    range_val = max_val - min_val
    return [
        r.with_score((r.score - min_val) / range_val)
        for r in results
    ]


def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[RetrievalResult]],
    k: int = 60,
    weights: Sequence[float] | None = None,
    stream_names: Sequence[str] | None = None,
) -> list[RetrievalResult]:
    """
    Combine multiple ranked result lists using Reciprocal Rank Fusion:
    RRF(d) = sum( weight_i * 1.0 / (k + rank_i) )

    Maintains stream rank provenance and merged metadata across streams.
    """
    if not ranked_lists:
        return []

    num_lists = len(ranked_lists)
    norm_weights: list[float]
    if weights is not None and len(weights) == num_lists:
        norm_weights = [float(w) for w in weights]
    else:
        norm_weights = [1.0] * num_lists

    s_names: list[str]
    if stream_names is not None and len(stream_names) == num_lists:
        s_names = list(stream_names)
    else:
        s_names = [f"stream_{i}" for i in range(num_lists)]

    rrf_scores: dict[str, float] = {}
    item_map: dict[str, RetrievalResult] = {}
    provenance_map: dict[str, dict[str, Any]] = {}

    for list_idx, ranked_list in enumerate(ranked_lists):
        w = norm_weights[list_idx]
        stream_name = s_names[list_idx]

        for rank, res in enumerate(ranked_list, start=1):
            key = _build_result_key(res)
            rrf_term = w * (1.0 / (k + rank))
            rrf_scores[key] = rrf_scores.get(key, 0.0) + rrf_term

            if key not in provenance_map:
                provenance_map[key] = {
                    "streams": [stream_name],
                    f"{stream_name}_rank": rank,
                    f"{stream_name}_raw_score": res.score,
                }
            else:
                prov = provenance_map[key]
                if stream_name not in prov["streams"]:
                    prov["streams"].append(stream_name)
                prov[f"{stream_name}_rank"] = rank
                prov[f"{stream_name}_raw_score"] = res.score

            if key not in item_map or res.score > item_map[key].score:
                item_map[key] = res

    fused_results: list[RetrievalResult] = []
    for key, score in rrf_scores.items():
        base_item = item_map[key]
        prov = provenance_map[key]
        prov["streams"].sort()
        updated_meta = dict(base_item.metadata)
        updated_meta["provenance"] = prov
        fused_results.append(base_item.with_score(round(score, 6)).with_metadata(updated_meta))

    fused_results.sort(key=lambda r: r.score, reverse=True)
    return fused_results


def blend_scores(
    list_a: Sequence[RetrievalResult],
    list_b: Sequence[RetrievalResult],
    weight_a: float = 0.5,
    weight_b: float = 0.5,
    name_a: str = "keyword",
    name_b: str = "semantic",
) -> list[RetrievalResult]:
    """
    Linearly combine normalized scores from two retrieval lists:
    Score(d) = (w_a * norm_a) + (w_b * norm_b)
    """
    total_w = weight_a + weight_b
    if total_w > 0:
        w_a = weight_a / total_w
        w_b = weight_b / total_w
    else:
        w_a, w_b = 0.5, 0.5

    norm_a_list = min_max_normalize(list_a)
    norm_b_list = min_max_normalize(list_b)

    norm_a = {
        _build_result_key(r): r
        for r in norm_a_list
    }
    norm_b = {
        _build_result_key(r): r
        for r in norm_b_list
    }

    all_keys = set(norm_a.keys()).union(norm_b.keys())
    blended: list[RetrievalResult] = []

    for key in all_keys:
        item_a = norm_a.get(key)
        item_b = norm_b.get(key)

        score_a = item_a.score if item_a is not None else 0.0
        score_b = item_b.score if item_b is not None else 0.0

        final_score = (score_a * w_a) + (score_b * w_b)
        base_item = item_a if item_a is not None else item_b
        assert base_item is not None

        # Build provenance
        streams: list[str] = []
        if item_a is not None:
            streams.append(name_a)
        if item_b is not None:
            streams.append(name_b)

        prov = {
            "streams": streams,
            f"{name_a}_score": round(score_a, 4) if item_a is not None else None,
            f"{name_b}_score": round(score_b, 4) if item_b is not None else None,
        }

        # Merge metadata
        merged_meta: dict[str, Any] = dict(base_item.metadata)
        if item_a is not None and item_b is not None:
            merged_meta.update(item_a.metadata)
            merged_meta.update(item_b.metadata)
        merged_meta["provenance"] = prov

        blended.append(base_item.with_score(round(final_score, 4)).with_metadata(merged_meta))

    blended.sort(key=lambda r: r.score, reverse=True)
    return blended


__all__ = [
    "deduplicate_results",
    "min_max_normalize",
    "reciprocal_rank_fusion",
    "blend_scores",
]
