"""
Stage 4: Identity Evidence Graph Builder
========================================
Constructs a traceable relational graph linking entities, addresses, PINs, brands,
products, and model identifiers back to their exact source OCR regions:
- MANUFACTURER -> Company Name -> Address -> PIN
- BRAND -> Product Name
- IMPORTER -> Model Number
"""

import uuid
from typing import List, Optional
from ...models import (
    Stage4EvidenceNode,
    Stage4EvidenceEdge,
    Stage4EvidenceGraph,
    Stage4Entity,
    Stage4ValueWithStatus
)


class IdentityEvidenceGraphBuilder:
    """Builds a formal evidence graph connecting statutory identity declarations."""

    def build_graph(
        self,
        entities: List[Stage4Entity],
        brand: Stage4ValueWithStatus,
        product_name: Stage4ValueWithStatus,
        model_number: Optional[str] = None
    ) -> Stage4EvidenceGraph:
        """Constructs the nodes and edges of the identity evidence graph."""
        nodes: List[Stage4EvidenceNode] = []
        edges: List[Stage4EvidenceEdge] = []

        # 1. Brand and Product nodes
        brand_node_id = None
        if brand.status == "CONFIRMED":
            brand_node_id = f"NODE-BRAND-{uuid.uuid4().hex[:4].upper()}"
            nodes.append(
                Stage4EvidenceNode(
                    node_id=brand_node_id,
                    node_type="BRAND",
                    label=brand.value,
                    region_id=brand.source_region_ids[0] if brand.source_region_ids else None
                )
            )

        if product_name.status == "CONFIRMED":
            prod_node_id = f"NODE-PROD-{uuid.uuid4().hex[:4].upper()}"
            nodes.append(
                Stage4EvidenceNode(
                    node_id=prod_node_id,
                    node_type="PRODUCT",
                    label=product_name.value,
                    region_id=product_name.source_region_ids[0] if product_name.source_region_ids else None
                )
            )
            if brand_node_id:
                edges.append(
                    Stage4EvidenceEdge(
                        source_node_id=brand_node_id,
                        target_node_id=prod_node_id,
                        relation="OWNS_BRAND"
                    )
                )

        # 2. Entity nodes & address relationships
        for ent in entities:
            role_node_id = f"NODE-ROLE-{uuid.uuid4().hex[:4].upper()}"
            name_node_id = f"NODE-NAME-{uuid.uuid4().hex[:4].upper()}"

            nodes.append(
                Stage4EvidenceNode(
                    node_id=role_node_id,
                    node_type="ROLE",
                    label=ent.role,
                    region_id=ent.source_region_ids[0] if ent.source_region_ids else None
                )
            )
            nodes.append(
                Stage4EvidenceNode(
                    node_id=name_node_id,
                    node_type="ENTITY_NAME",
                    label=ent.name,
                    region_id=ent.source_region_ids[0] if ent.source_region_ids else None
                )
            )
            edges.append(
                Stage4EvidenceEdge(
                    source_node_id=role_node_id,
                    target_node_id=name_node_id,
                    relation="HAS_NAME"
                )
            )

            # Address link
            if ent.address:
                addr_node_id = f"NODE-ADDR-{uuid.uuid4().hex[:4].upper()}"
                nodes.append(
                    Stage4EvidenceNode(
                        node_id=addr_node_id,
                        node_type="ADDRESS",
                        label=ent.address,
                        region_id=ent.source_region_ids[1] if len(ent.source_region_ids) > 1 else None
                    )
                )
                edges.append(
                    Stage4EvidenceEdge(
                        source_node_id=name_node_id,
                        target_node_id=addr_node_id,
                        relation="LOCATED_AT"
                    )
                )

                # PIN link
                if ent.pin:
                    pin_node_id = f"NODE-PIN-{uuid.uuid4().hex[:4].upper()}"
                    nodes.append(
                        Stage4EvidenceNode(
                            node_id=pin_node_id,
                            node_type="PIN",
                            label=ent.pin,
                            region_id=None
                        )
                    )
                    edges.append(
                        Stage4EvidenceEdge(
                            source_node_id=addr_node_id,
                            target_node_id=pin_node_id,
                            relation="HAS_PIN"
                        )
                    )

            # Importer -> Model relationship
            if ent.role == "IMPORTER" and model_number:
                model_node_id = f"NODE-MODEL-{uuid.uuid4().hex[:4].upper()}"
                nodes.append(
                    Stage4EvidenceNode(
                        node_id=model_node_id,
                        node_type="MODEL",
                        label=model_number,
                        region_id=None
                    )
                )
                edges.append(
                    Stage4EvidenceEdge(
                        source_node_id=name_node_id,
                        target_node_id=model_node_id,
                        relation="HAS_MODEL"
                    )
                )

        return Stage4EvidenceGraph(nodes=nodes, edges=edges)
