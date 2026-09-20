"""
Stage 4: Multi-Product Detection & Partitioning Handler
======================================================
Identifies if an image contains multiple side-by-side or distinct packaging items:
- Inspects Stage 1 packages or large horizontal bounding box clusters
- Partitions OCR regions and semantic fields per product
- Prevents cross-product contamination
- Emits separate product_001, product_002, etc.
"""

from typing import Dict, Any, Optional, Tuple, List
from ...models import Stage2TextRegion, Stage3SemanticField, Stage1Response


class MultiProductHandler:
    """Partitions inputs into independent product clusters when multiple products are present."""

    def detect_and_partition_products(
        self,
        regions: List[Stage2TextRegion],
        semantic_fields: List[Stage3SemanticField],
        stage1_output: Optional[Stage1Response] = None
    ) -> List[Tuple[str, List[Stage2TextRegion], List[Stage3SemanticField], List[float]]]:
        """Returns a list of (product_id, product_regions, product_semantic_fields, product_bbox)."""
        if not regions:
            return [("product_001", [], [], [])]

        # 1. Check if Stage 1 explicitly segmented multiple packages
        packages = getattr(stage1_output, "packages", None)
        if stage1_output and packages and len(packages) > 1:
            partitions = []
            for idx, pkg in enumerate(packages):
                pid = f"product_{idx+1:03d}"
                px, py, pw, ph = pkg.bbox if pkg.bbox and len(pkg.bbox) == 4 else [0, 0, 9999, 9999]
                
                # Assign regions overlapping this package
                pkg_regions = [
                    r for r in regions
                    if r.bbox and len(r.bbox) == 4 and (px <= r.bbox[0] + r.bbox[2]/2 <= px + pw)
                ]
                pkg_region_ids = {r.region_id for r in pkg_regions}
                pkg_fields = [
                    f for f in semantic_fields
                    if any(rid in pkg_region_ids for rid in f.source_region_ids)
                ]
                partitions.append((pid, pkg_regions, pkg_fields, pkg.bbox))
            if partitions:
                return partitions

        # 2. Check for two clear horizontal clusters in text regions
        # e.g., product on left (x < mid) and product on right (x > mid + gap)
        x_coords = [r.bbox[0] for r in regions if r.bbox and len(r.bbox) == 4]
        if len(x_coords) >= 4:
            min_x = min(x_coords)
            max_x = max(r.bbox[0] + r.bbox[2] for r in regions if r.bbox and len(r.bbox) == 4)
            span = max_x - min_x
            
            # Look for a wide empty vertical gap across the entire middle
            mid_start = min_x + span * 0.35
            mid_end = min_x + span * 0.65
            
            left_regions = [r for r in regions if r.bbox and (r.bbox[0] + r.bbox[2]) <= mid_start + span * 0.05]
            right_regions = [r for r in regions if r.bbox and r.bbox[0] >= mid_end - span * 0.05]

            # If both left and right have at least 2 distinct text lines and no regions straddling the center
            straddle_regions = [r for r in regions if r.bbox and (r.bbox[0] < mid_end and r.bbox[0] + r.bbox[2] > mid_start)]
            
            if len(left_regions) >= 2 and len(right_regions) >= 2 and len(straddle_regions) == 0:
                # We have 2 separate products!
                left_ids = {r.region_id for r in left_regions}
                right_ids = {r.region_id for r in right_regions}

                left_fields = [f for f in semantic_fields if any(rid in left_ids for rid in f.source_region_ids)]
                right_fields = [f for f in semantic_fields if any(rid in right_ids for rid in f.source_region_ids)]

                left_bbox = [
                    min(r.bbox[0] for r in left_regions),
                    min(r.bbox[1] for r in left_regions),
                    max(r.bbox[0] + r.bbox[2] for r in left_regions) - min(r.bbox[0] for r in left_regions),
                    max(r.bbox[1] + r.bbox[3] for r in left_regions) - min(r.bbox[1] for r in left_regions)
                ]
                right_bbox = [
                    min(r.bbox[0] for r in right_regions),
                    min(r.bbox[1] for r in right_regions),
                    max(r.bbox[0] + r.bbox[2] for r in right_regions) - min(r.bbox[0] for r in right_regions),
                    max(r.bbox[1] + r.bbox[3] for r in right_regions) - min(r.bbox[1] for r in right_regions)
                ]

                return [
                    ("product_001", left_regions, left_fields, left_bbox),
                    ("product_002", right_regions, right_fields, right_bbox)
                ]

        # Single product default
        overall_bbox = []
        if regions and regions[0].bbox:
            overall_bbox = [
                min(r.bbox[0] for r in regions if r.bbox),
                min(r.bbox[1] for r in regions if r.bbox),
                max(r.bbox[0] + r.bbox[2] for r in regions if r.bbox) - min(r.bbox[0] for r in regions if r.bbox),
                max(r.bbox[1] + r.bbox[3] for r in regions if r.bbox) - min(r.bbox[1] for r in regions if r.bbox)
            ]
        return [("product_001", regions, semantic_fields, overall_bbox)]
