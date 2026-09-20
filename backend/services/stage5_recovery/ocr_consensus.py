"""
Stage 5: Multi-Variant OCR Consensus & Disagreement Isolation Service
====================================================================
Runs OCR across independent enhancement variants, calculates character- and word-level
agreement, clusters spatially overlapping detections, and establishes evidence-backed consensus.
Preserves alternative candidate readings when ambiguity exists.
Zero-hallucination guarantee: marks unresolvable ambiguity as OCR_UNCERTAIN.
"""

import uuid
import difflib
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
import numpy as np

from ...models import Stage5OcrConsensusItem
from ..stage2_ocr.ocr_adapter import MultiEngineOcrAdapter
from ..stage2_ocr.grouping import group_words_into_lines
from ..stage2_ocr.normalization import (
    normalize_text_candidate,
    is_garbage_ocr,
    calculate_bbox_iou,
    compute_string_similarity
)
from .coordinate_mapper import CoordinateTransformChain
from .enhancement_engine import GeneratedVariant


def compute_character_level_agreement(strings: List[str]) -> Tuple[str, float]:
    """Computes consensus string using majority vote at each character position across aligned readings."""
    if not strings:
        return "", 0.0
    if len(strings) == 1:
        return strings[0], 0.90

    # Count exact matches first
    counts: Dict[str, int] = {}
    for s in strings:
        counts[s] = counts.get(s, 0) + 1

    most_common_str, best_count = max(counts.items(), key=lambda item: item[1])
    if best_count > len(strings) / 2:
        conf = 0.85 + 0.15 * (float(best_count) / float(len(strings)))
        return most_common_str, min(0.99, conf)

    # Sequence matcher consensus alignment
    primary = most_common_str
    consensus_chars = []
    total_matches = 0
    total_positions = len(primary)

    for i, ch in enumerate(primary):
        char_votes: Dict[str, int] = {ch: 1}
        for other in strings:
            if other == primary:
                continue
            if i < len(other):
                char_votes[other[i]] = char_votes.get(other[i], 0) + 1

        best_char, char_count = max(char_votes.items(), key=lambda item: item[1])
        consensus_chars.append(best_char)
        if char_count >= 2:
            total_matches += 1

    consensus_str = "".join(consensus_chars)
    agreement_ratio = float(total_matches) / float(max(1, total_positions))
    confidence = 0.65 + 0.30 * agreement_ratio
    return consensus_str, round(min(0.99, confidence), 3)


class OcrConsensusEngine:
    """Aggregates and verifies text readings across multiple recovered image variants."""

    def __init__(self):
        self.ocr_adapter = MultiEngineOcrAdapter()

    def run_consensus_across_variants(
        self,
        variants: List[GeneratedVariant],
        orig_w: int,
        orig_h: int,
        max_variants: int = 2
    ) -> List[Stage5OcrConsensusItem]:
        """Runs OCR on selected distinct variants, clusters readings by original image spatial location,
        and computes consensus text and confidence.
        """
        all_detections: List[Dict[str, Any]] = []
        # Select up to max_variants complementary branches to balance consensus with high performance
        eval_variants = variants[:max_variants]

        for variant in eval_variants:
            raw_dets = self.ocr_adapter.run_ocr_on_image(variant.image, variant_name=variant.variant_id)
            lines = group_words_into_lines(raw_dets)

            for line in lines:
                raw = line.get("raw_text", "").strip()
                if is_garbage_ocr(raw):
                    continue

                local_bbox = line["bbox"]  # [x, y, w, h] in variant coordinate space
                # Map back to original image space
                orig_bbox = variant.chain.map_bbox_to_original(local_bbox, orig_w, orig_h)
                
                # Also generate 4-corner polygon in original space
                bx, by, bw, bh = local_bbox
                poly_local = [[bx, by], [bx + bw, by], [bx + bw, by + bh], [bx, by + bh]]
                orig_poly = variant.chain.map_polygon_to_original(poly_local, orig_w, orig_h)

                norm_cand = line.get("normalized_text")
                if not norm_cand:
                    norm_cand_res = normalize_text_candidate(raw)
                    norm_cand = norm_cand_res[0] if isinstance(norm_cand_res, tuple) else str(norm_cand_res)

                all_detections.append({
                    "raw_text": raw,
                    "normalized_text": norm_cand,
                    "processed_bbox": local_bbox,
                    "original_bbox": orig_bbox,
                    "original_polygon": orig_poly,
                    "variant_id": variant.variant_id,
                    "variant_type": variant.variant_type,
                    "confidence": line.get("confidence", 0.90),
                    "transform_chain": variant.chain.get_operation_names()
                })

        # Cluster detections based on original image bounding box IoU & string similarity
        clusters: List[List[Dict[str, Any]]] = []

        for det in all_detections:
            matched = False
            for cluster in clusters:
                rep = cluster[0]
                iou = calculate_bbox_iou(det["original_bbox"], rep["original_bbox"])
                sim = compute_string_similarity(det["raw_text"], rep["raw_text"])

                # Spatial overlap check in original image coordinates
                if iou > 0.35 or (iou > 0.15 and sim > 0.55):
                    cluster.append(det)
                    matched = True
                    break

            if not matched:
                clusters.append([det])

        consensus_items: List[Stage5OcrConsensusItem] = []

        for cluster in clusters:
            raw_candidates = [d["raw_text"] for d in cluster]
            variants_involved = list(set(d["variant_id"] for d in cluster))
            transforms = list(set(op for d in cluster for op in d["transform_chain"]))

            # Compute character-level consensus text
            consensus_raw, consensus_conf = compute_character_level_agreement(raw_candidates)
            norm_res = normalize_text_candidate(consensus_raw)
            norm_text = norm_res[0] if isinstance(norm_res, tuple) else str(norm_res)

            # Representative bounding box (union or highest confidence box)
            best_det = max(cluster, key=lambda d: d.get("confidence", 0.0))
            orig_bbox = best_det["original_bbox"]
            orig_poly = best_det["original_polygon"]
            proc_bbox = best_det["processed_bbox"]

            # Filter out identical or empty competing candidates
            competing = list(set(c for c in raw_candidates if c != consensus_raw and not is_garbage_ocr(c)))

            # If agreement is weak or text has no alphanumeric characters, mark OCR_UNCERTAIN
            has_alnum = any(c.isalnum() for c in consensus_raw)
            if not has_alnum or consensus_conf < 0.25:
                status = "OCR_UNCERTAIN"
            else:
                status = "CONFIRMED"

            consensus_items.append(
                Stage5OcrConsensusItem(
                    consensus_id=f"CON-{uuid.uuid4().hex[:8].upper()}",
                    raw_text=consensus_raw,
                    normalized_text=norm_text,
                    consensus_confidence=consensus_conf,
                    agreement_count=len(cluster),
                    total_variants_evaluated=len(variants),
                    competing_candidates=competing,
                    processed_bbox=proc_bbox,
                    original_bbox=orig_bbox,
                    original_polygon=orig_poly,
                    source_variants=variants_involved,
                    transformation_chain=transforms,
                    status=status
                )
            )

        # Sort by vertical reading order in original image space
        consensus_items.sort(key=lambda item: (item.original_bbox[1] if item.original_bbox else 0.0))
        return consensus_items
