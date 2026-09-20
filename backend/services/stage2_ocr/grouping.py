"""
Stage 2: Word-to-Line Grouping, Block Clustering, & Reading Order Service
========================================================================
Provides:
1. Groups adjacent word-level tokens into unified horizontal text lines
2. Groups lines into logical paragraph blocks without merging distinct declarations
3. Sorts detected text regions into natural reading order (top -> bottom, left -> right)
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from ...models import Stage2WordBox, Stage2TextRegion


def group_words_into_lines(
    words: List[Dict[str, Any]],
    y_threshold_ratio: float = 0.55,
    x_gap_ratio: float = 2.5
) -> List[Dict[str, Any]]:
    """Groups individual word tokens into cohesive text lines.
    
    Each word dict has: {"text": str, "bbox": [x, y, w, h], "confidence": float}
    Returns list of line dicts containing grouped text, line bbox, and word boxes.
    """
    if not words:
        return []

    # Sort words primarily by vertical coordinate (y), then by horizontal (x)
    sorted_words = sorted(words, key=lambda w: (w["bbox"][1], w["bbox"][0]))
    lines: List[List[Dict[str, Any]]] = []

    for word in sorted_words:
        wx, wy, ww, wh = word["bbox"]
        word_center_y = wy + wh / 2.0
        placed = False

        for line in lines:
            # Calculate average line height and center y
            line_heights = [w["bbox"][3] for w in line]
            avg_h = float(np.mean(line_heights))
            line_center_ys = [w["bbox"][1] + w["bbox"][3] / 2.0 for w in line]
            avg_center_y = float(np.mean(line_center_ys))

            # Vertical proximity check
            if abs(word_center_y - avg_center_y) <= (avg_h * y_threshold_ratio):
                line.append(word)
                placed = True
                break

        if not placed:
            lines.append([word])

    # Within each vertical band, split if horizontal gap between consecutive words is too large
    # (e.g. separate columns or distinct side-by-side products)
    split_lines: List[List[Dict[str, Any]]] = []
    for line in lines:
        line_sorted = sorted(line, key=lambda w: w["bbox"][0])
        current_subline = [line_sorted[0]]
        for w in line_sorted[1:]:
            prev_w = current_subline[-1]
            prev_right = prev_w["bbox"][0] + prev_w["bbox"][2]
            curr_left = w["bbox"][0]
            gap = curr_left - prev_right
            avg_h = (prev_w["bbox"][3] + w["bbox"][3]) / 2.0

            # If gap > max(45.0, avg_h * 3.5), it's a distinct column / product block
            if gap > max(45.0, avg_h * 3.5):
                split_lines.append(current_subline)
                current_subline = [w]
            else:
                current_subline.append(w)
        if current_subline:
            split_lines.append(current_subline)

    grouped_lines: List[Dict[str, Any]] = []
    for line_sorted in split_lines:
        full_text = " ".join(w.get("raw_text") or w.get("text", "") for w in line_sorted if (w.get("raw_text") or w.get("text"))).strip()
        if not full_text:
            continue
        
        # Calculate unified bounding box [min_x, min_y, max_w, max_h]
        min_x = min(w["bbox"][0] for w in line_sorted)
        min_y = min(w["bbox"][1] for w in line_sorted)
        max_x = max(w["bbox"][0] + w["bbox"][2] for w in line_sorted)
        max_y = max(w["bbox"][1] + w["bbox"][3] for w in line_sorted)

        confs = [w.get("confidence", 0.90) for w in line_sorted]
        avg_conf = float(np.mean(confs)) if confs else 0.90

        word_boxes = [
            Stage2WordBox(
                text=w.get("raw_text") or w.get("text", ""),
                bbox=w["bbox"],
                confidence=round(w.get("confidence", 0.90), 2)
            ) for w in line_sorted
        ]

        from .normalization import normalize_text_candidate
        norm_line, _ = normalize_text_candidate(full_text)
        grouped_lines.append({
            "raw_text": full_text,
            "normalized_text": norm_line,
            "text": full_text,
            "bbox": [round(min_x, 1), round(min_y, 1), round(max_x - min_x, 1), round(max_y - min_y, 1)],
            "confidence": round(avg_conf, 2),
            "words": word_boxes
        })

    # Sort lines by y-coordinate
    grouped_lines = sorted(grouped_lines, key=lambda l: (l["bbox"][1], l["bbox"][0]))
    return grouped_lines


def cluster_lines_into_blocks(
    lines: List[Dict[str, Any]],
    line_spacing_threshold_multiplier: float = 1.6
) -> List[List[Dict[str, Any]]]:
    """Clusters spatially adjacent lines into logical paragraph blocks
    (e.g., multi-line ingredient paragraphs or multi-line manufacturer address).
    """
    if not lines:
        return []

    # Sort top-to-bottom
    sorted_lines = sorted(lines, key=lambda l: l["bbox"][1])
    blocks: List[List[Dict[str, Any]]] = []
    current_block: List[Dict[str, Any]] = [sorted_lines[0]]

    for i in range(1, len(sorted_lines)):
        prev_line = current_block[-1]
        curr_line = sorted_lines[i]

        prev_y2 = prev_line["bbox"][1] + prev_line["bbox"][3]
        curr_y1 = curr_line["bbox"][1]
        line_gap = curr_y1 - prev_y2

        prev_h = prev_line["bbox"][3]
        curr_h = curr_line["bbox"][3]
        avg_h = (prev_h + curr_h) / 2.0

        # Check horizontal alignment overlap
        prev_x1 = prev_line["bbox"][0]
        prev_x2 = prev_x1 + prev_line["bbox"][2]
        curr_x1 = curr_line["bbox"][0]
        curr_x2 = curr_x1 + curr_line["bbox"][2]
        h_overlap = max(0.0, min(prev_x2, curr_x2) - max(prev_x1, curr_x1))

        # Check if lines have comparable height and moderate vertical gap
        if line_gap <= (avg_h * line_spacing_threshold_multiplier) and (h_overlap > 0.2 * min(prev_line["bbox"][2], curr_line["bbox"][2])):
            current_block.append(curr_line)
        else:
            blocks.append(current_block)
            current_block = [curr_line]

    if current_block:
        blocks.append(current_block)

    return blocks


def assign_natural_reading_order(
    regions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Assigns reading_order_index based on visual reading flow (top-to-bottom, left-to-right)."""
    # Sort with primary weight on Y (top to bottom) with bucketed bands, then X (left to right)
    # Banding lines within ~15px vertically ensures left-to-right columns sort logically
    if not regions:
        return []

    # Sort primarily by Y, secondarily by X
    sorted_regions = sorted(regions, key=lambda r: (round(r["bbox"][1] / 15.0), r["bbox"][0]))
    for idx, r in enumerate(sorted_regions):
        r["reading_order_index"] = idx + 1

    return sorted_regions
