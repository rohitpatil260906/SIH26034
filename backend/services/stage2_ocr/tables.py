"""
Stage 2: Table Structure Detection & Cell Extraction Service
============================================================
Detects tabular grids on packaging (nutrition facts, specification tables, mineral analysis):
1. Detects horizontal and vertical grid lines using morphological structuring elements
2. Identifies table boundaries, row count, column count, and individual cell coordinates
3. Extracts text inside each cell while preserving row/column indices
4. Generates structured Stage2TableInfo models with coordinate mappings
"""

import uuid
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image
import numpy as np
import cv2

from ...models import Stage2TableInfo, Stage2TableCell
from ..cv_pipeline import pil_to_cv2
from ..stage1_cv.geometry import map_bbox_to_original


class TableDetectionService:
    """Detects and parses grid tables on packaging labels."""

    def __init__(self):
        pass

    def detect_tables(
        self,
        image: Image.Image,
        text_regions: List[Dict[str, Any]],
        m_inv: Optional[np.ndarray] = None,
        orig_w: int = 1000,
        orig_h: int = 1000
    ) -> List[Stage2TableInfo]:
        """Identifies grid tables and associates detected text with specific cells.
        
        Returns:
            List[Stage2TableInfo]
        """
        cv_img = pil_to_cv2(image)
        h, w = cv_img.shape[:2]
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img

        # 1. Binarize
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 5
        )

        # 2. Extract horizontal and vertical lines
        h_scale = max(35, w // 10)
        v_scale = max(25, h // 12)
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_scale, 1))
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_scale))

        h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)
        v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)

        # 3. Table grid is the intersection/union of horizontal and vertical lines
        table_grid = cv2.add(h_lines, v_lines)
        grid_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        table_grid = cv2.morphologyEx(table_grid, cv2.MORPH_CLOSE, grid_kernel)

        # Find external contours of table grids
        contours, _ = cv2.findContours(table_grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detected_tables: List[Stage2TableInfo] = []

        min_table_area = (w * h) * 0.035  # Must occupy at least 3.5% of label

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_table_area:
                continue

            tx, ty, tw, th = cv2.boundingRect(cnt)
            # Table should have minimum dimensions
            if tw < w * 0.20 or th < h * 0.08:
                continue

            # Table should have at least 2 horizontal lines and 2 vertical lines
            roi_h = h_lines[ty : ty + th, tx : tx + tw]
            h_line_proj = np.sum(roi_h, axis=1)
            row_peaks = np.where(h_line_proj > (tw * 255 * 0.35))[0]

            roi_v = v_lines[ty : ty + th, tx : tx + tw]
            v_line_proj = np.sum(roi_v, axis=0)
            col_peaks = np.where(v_line_proj > (th * 255 * 0.35))[0]

            # Require minimum 2 horizontal lines (1 row) and 2 vertical lines (1 column)
            if len(row_peaks) >= 2 and len(col_peaks) >= 2:
                # Deduplicate close peaks
                row_coords = [row_peaks[0]]
                for rp in row_peaks[1:]:
                    if rp - row_coords[-1] > 12:
                        row_coords.append(rp)

                col_coords = [col_peaks[0]]
                for cp in col_peaks[1:]:
                    if cp - col_coords[-1] > 20:
                        col_coords.append(cp)

                rows_cnt = max(1, len(row_coords) - 1)
                cols_cnt = max(1, len(col_coords) - 1)

                table_bbox = [float(tx), float(ty), float(tw), float(th)]
                orig_tbl_bbox = map_bbox_to_original(table_bbox, m_inv, orig_w, orig_h) if m_inv is not None else table_bbox

                table_id = f"TBL-{uuid.uuid4().hex[:6].upper()}"
                cells: List[Stage2TableCell] = []

                # Build cells
                for r in range(rows_cnt):
                    r_top = ty + row_coords[r]
                    r_bot = ty + (row_coords[r + 1] if r + 1 < len(row_coords) else th)
                    for c in range(cols_cnt):
                        c_left = tx + col_coords[c]
                        c_right = tx + (col_coords[c + 1] if c + 1 < len(col_coords) else tw)

                        cell_w = max(1.0, float(c_right - c_left))
                        cell_h = max(1.0, float(r_bot - r_top))
                        cell_bbox = [float(c_left), float(r_top), cell_w, cell_h]
                        orig_cell_bbox = map_bbox_to_original(cell_bbox, m_inv, orig_w, orig_h) if m_inv is not None else cell_bbox

                        # Find matching text inside cell
                        cell_text_parts = []
                        for tr in text_regions:
                            rx, ry, rw, rh = tr["bbox"]
                            rc_x = rx + rw / 2.0
                            rc_y = ry + rh / 2.0
                            if c_left <= rc_x <= c_right and r_top <= rc_y <= r_bot:
                                cell_text_parts.append(tr.get("normalized_text", tr.get("raw_text", "")))

                        cell_text = " ".join(cell_text_parts).strip()
                        cells.append(
                            Stage2TableCell(
                                row_index=r,
                                col_index=c,
                                row_span=1,
                                col_span=1,
                                text=cell_text,
                                bbox=cell_bbox,
                                original_bbox=orig_cell_bbox
                            )
                        )

                detected_tables.append(
                    Stage2TableInfo(
                        table_id=table_id,
                        bbox=table_bbox,
                        original_bbox=orig_tbl_bbox,
                        rows_count=rows_cnt,
                        cols_count=cols_cnt,
                        cells=cells
                    )
                )

        return detected_tables
