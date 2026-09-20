"""
Service 6: Layout Analysis Service
==================================
Analyzes spatial and visual layout of packaging labels:
- Visual reading order sorting (top-to-bottom, left-to-right, column-aware)
- Line and paragraph grouping into coherent visual blocks
- Visual hierarchy estimation (relative font height, prominence, position on panel)
- Spatial neighborhood graphs (preceding label, succeeding value, same-line adjacency)
- Table understanding (Nutrition information, specification grids, tabular key-value pairs)
"""

from typing import List, Dict, Any, Tuple, Optional
import re
from ...models import ExtractedLine, BoundingBox


class LayoutBlock:
    """A visual block formed by grouping adjacent text lines."""
    def __init__(self, block_id: int, lines: List[ExtractedLine]):
        self.block_id = block_id
        self.lines = lines
        self.text = "\n".join(l.text for l in lines)
        self.bbox = self._compute_bounding_box()
        self.estimated_font_size = self._estimate_font_size()

    def _compute_bounding_box(self) -> Optional[BoundingBox]:
        boxes = [l.bbox for l in self.lines if l.bbox]
        if not boxes:
            return None
        min_x = min(b.x for b in boxes)
        min_y = min(b.y for b in boxes)
        max_x = max(b.x + b.width for b in boxes)
        max_y = max(b.y + b.height for b in boxes)
        return BoundingBox(
            x=min_x,
            y=min_y,
            width=max_x - min_x,
            height=max_y - min_y,
            label="LayoutBlock"
        )

    def _estimate_font_size(self) -> float:
        heights = [l.bbox.height for l in self.lines if l.bbox and l.bbox.height > 0]
        if heights:
            return sum(heights) / len(heights)
        return 4.0


class TableRow:
    """A row in a detected tabular section (e.g., nutrition facts or specifications)."""
    def __init__(self, header: str, value: str, raw_text: str, bbox: Optional[BoundingBox] = None):
        self.header = header.strip()
        self.value = value.strip()
        self.raw_text = raw_text.strip()
        self.bbox = bbox


class LayoutAnalysisService:
    """Understands visual hierarchy, reading order, and tabular structures."""

    def __init__(self):
        pass

    def sort_reading_order(self, lines: List[ExtractedLine]) -> List[ExtractedLine]:
        """Sorts extracted lines in visual reading order (top-to-bottom, primary; left-to-right, secondary)."""
        def sort_key(l: ExtractedLine):
            if l.bbox:
                # Snap y into 3% bands to group lines on approximately same horizontal level
                band = round(l.bbox.y / 3.0) * 3.0
                return (band, l.bbox.x)
            return (float(l.line_index), 0.0)

        return sorted(lines, key=sort_key)

    def group_into_blocks(
        self,
        lines: List[ExtractedLine],
        vertical_threshold_pct: float = 5.0
    ) -> List[LayoutBlock]:
        """Groups lines with small vertical separation and overlapping horizontal extents into blocks."""
        if not lines:
            return []

        sorted_lines = self.sort_reading_order(lines)
        blocks: List[LayoutBlock] = []
        current_group: List[ExtractedLine] = [sorted_lines[0]]

        for i in range(1, len(sorted_lines)):
            prev = sorted_lines[i - 1]
            curr = sorted_lines[i]

            is_adjacent = False
            if prev.bbox and curr.bbox:
                v_gap = curr.bbox.y - (prev.bbox.y + prev.bbox.height)
                # Check vertical proximity
                if 0.0 <= v_gap <= vertical_threshold_pct:
                    is_adjacent = True
            elif curr.line_index == prev.line_index + 1:
                is_adjacent = True

            if is_adjacent:
                current_group.append(curr)
            else:
                blocks.append(LayoutBlock(len(blocks) + 1, current_group))
                current_group = [curr]

        if current_group:
            blocks.append(LayoutBlock(len(blocks) + 1, current_group))

        return blocks

    def analyze_visual_hierarchy(
        self,
        line: ExtractedLine,
        all_lines: List[ExtractedLine]
    ) -> Dict[str, Any]:
        """Estimates visual prominence of a line (prominent hero title, body text, or micro stamp)."""
        if not line.bbox:
            # Fallback based on position in transcript
            pos_ratio = min(1.0, max(0.0, line.line_index / max(1, len(all_lines))))
            return {
                "relative_size": "medium",
                "vertical_zone": "top" if pos_ratio < 0.25 else ("bottom" if pos_ratio > 0.75 else "middle"),
                "is_prominent": pos_ratio < 0.20,
                "is_bottom_stamp": pos_ratio > 0.80
            }

        heights = [l.bbox.height for l in all_lines if l.bbox and l.bbox.height > 0]
        avg_height = (sum(heights) / len(heights)) if heights else 4.0
        line_height = line.bbox.height

        rel_size = "medium"
        if line_height >= avg_height * 1.5:
            rel_size = "large"
        elif line_height <= avg_height * 0.7:
            rel_size = "small"

        y_pos = line.bbox.y
        zone = "top" if y_pos < 30.0 else ("bottom" if y_pos > 70.0 else "middle")

        return {
            "relative_size": rel_size,
            "vertical_zone": zone,
            "is_prominent": rel_size == "large" and (zone in ["top", "middle"]),
            "is_bottom_stamp": zone == "bottom" or rel_size == "small",
            "bbox_height": line_height,
            "avg_height": avg_height
        }

    def detect_table_rows(self, lines: List[ExtractedLine]) -> List[TableRow]:
        """Detects key-value pairs formatted as tabular rows (e.g., 'Serving Size | 50 g' or 'Serving Size: 50 g')."""
        table_rows: List[TableRow] = []
        table_delims = [r'[:|–—\t]', r'\s{2,}']

        for line in lines:
            txt = line.text.strip()
            # Nutrition or specification table pattern
            for delim in table_delims:
                parts = re.split(delim, txt, maxsplit=1)
                if len(parts) == 2 and len(parts[0].strip()) > 1 and len(parts[1].strip()) > 0:
                    header = parts[0].strip()
                    val = parts[1].strip()
                    table_rows.append(TableRow(header=header, value=val, raw_text=txt, bbox=line.bbox))
                    break

        return table_rows
