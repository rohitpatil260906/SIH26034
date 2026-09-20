"""
Stage 7: Cross-Panel Evidence Graph Builder
===========================================
Constructs a structured multi-panel evidence graph:
- Nodes: PRODUCT, PANEL, FIELD, ENTITY, REGION.
- Edges: HAS_PANEL, HAS_FIELD, LINKED_TO, OWNS.
- Links every unified field to its source panels, source images, bounding boxes, and region IDs.
"""

from typing import List, Dict, Any, Optional
from ...models import (
    Stage7CrossPanelEvidenceGraph,
    Stage7EvidenceGraphNode,
    Stage7EvidenceGraphEdge,
    Stage7SourceImage,
    Stage7UnifiedField,
    Stage7CrossPanelLink
)


class EvidenceGraphBuilder:
    """Constructs cross-panel evidence graphs for unified product profiles."""

    def build_graph(
        self,
        product_id: str,
        source_images: List[Stage7SourceImage],
        unified_fields: List[Stage7UnifiedField],
        cross_panel_links: List[Stage7CrossPanelLink]
    ) -> Stage7CrossPanelEvidenceGraph:
        """Builds node and edge graph representation of cross-panel evidence."""
        nodes: List[Stage7EvidenceGraphNode] = []
        edges: List[Stage7EvidenceGraphEdge] = []

        # 1. Root Product Node
        prod_node_id = f"node_prod_{product_id}"
        nodes.append(Stage7EvidenceGraphNode(
            node_id=prod_node_id,
            node_type="PRODUCT",
            label=f"Product: {product_id}"
        ))

        # 2. Panel Nodes & HAS_PANEL Edges
        panel_node_map: Dict[str, str] = {}
        for img in source_images:
            p_node_id = f"node_panel_{img.image_id}"
            nodes.append(Stage7EvidenceGraphNode(
                node_id=p_node_id,
                node_type="PANEL",
                label=f"Panel: {img.panel} ({img.image_id})",
                image_id=img.image_id,
                panel=img.panel
            ))
            edges.append(Stage7EvidenceGraphEdge(
                source_node_id=prod_node_id,
                target_node_id=p_node_id,
                relation="HAS_PANEL"
            ))
            panel_node_map[img.image_id] = p_node_id

        # 3. Field Nodes & HAS_FIELD Edges
        for f in unified_fields:
            if not f.value and f.status not in ("CONFIRMED", "NEEDS_REVIEW", "CONFLICT"):
                continue
            f_node_id = f"node_field_{f.field_name}"
            lbl = f"{f.field_name}: {f.value or 'CONFLICT'}"
            nodes.append(Stage7EvidenceGraphNode(
                node_id=f_node_id,
                node_type="FIELD",
                label=lbl
            ))
            edges.append(Stage7EvidenceGraphEdge(
                source_node_id=prod_node_id,
                target_node_id=f_node_id,
                relation="HAS_FIELD"
            ))

            # Connect field to panel sources
            for src in f.sources:
                p_node_id = panel_node_map.get(src.image_id)
                if p_node_id:
                    edges.append(Stage7EvidenceGraphEdge(
                        source_node_id=p_node_id,
                        target_node_id=f_node_id,
                        relation="OWNS"
                    ))

        # 4. Cross-Panel Link Edges
        for link in cross_panel_links:
            src_node = panel_node_map.get(link.source_image_id)
            tgt_node = panel_node_map.get(link.target_image_id)
            if src_node and tgt_node:
                edges.append(Stage7EvidenceGraphEdge(
                    source_node_id=src_node,
                    target_node_id=tgt_node,
                    relation="LINKED_TO"
                ))

        return Stage7CrossPanelEvidenceGraph(nodes=nodes, edges=edges)
