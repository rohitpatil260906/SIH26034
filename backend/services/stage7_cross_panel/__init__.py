"""
Stage 7: Cross-Panel Information Merging & Multi-Image Consolidation Engine
==========================================================================
Master Pipeline Orchestrator for Stage 7:
- Groups multi-image inputs by physical product using ProductMatcher.
- Consolidates fields across panels using FieldMerger and ConflictDetector.
- Links cross-panel entities and multi-panel addresses using PanelLinker.
- Computes panel completeness (available_panels vs missing_panels).
- Constructs cross-panel evidence graphs via EvidenceGraphBuilder.
- Manages multi-image sessions and late-arriving image updates via SessionManager.

Strict Zero-Hallucination & Legal Separation Policy:
- Does NOT perform legal compliance checks or violation generation.
- Never fabricates missing visible text.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from ...models import (
    Stage1Response,
    Stage2Response,
    Stage3Response,
    Stage4Response,
    Stage4ProductIdentity,
    Stage6Response,
    Stage6SingleProductProfile,
    Stage6ProductProfile,
    Stage7Session,
    Stage7SourceImage,
    Stage7ProductMatchEvidence,
    Stage7UnifiedProduct,
    Stage7Response
)
from .session_manager import SessionManager
from .product_matcher import ProductMatcher
from .panel_linker import PanelLinker
from .field_merger import FieldMerger
from .conflict_detector import ConflictDetector
from .evidence_graph import EvidenceGraphBuilder

logger = logging.getLogger(__name__)


class Stage7Pipeline:
    """Master pipeline for Stage 7 Cross-Panel Information Merging."""

    def __init__(self):
        self.session_manager = SessionManager()
        self.product_matcher = ProductMatcher()
        self.panel_linker = PanelLinker()
        self.field_merger = FieldMerger()
        self.conflict_detector = ConflictDetector()
        self.evidence_graph_builder = EvidenceGraphBuilder()

    def process_session(
        self,
        session_id: str = "session_001",
        image_inputs: List[Dict[str, Any]] = []
    ) -> Stage7Response:
        """
        Processes a multi-image scan session.
        Each item in image_inputs:
        {
            "image_id": "image_001",
            "panel": "FRONT",
            "stage1_output": Optional[Stage1Response],
            "stage2_output": Optional[Stage2Response],
            "stage3_output": Optional[Stage3Response],
            "stage4_output": Optional[Stage4Response],
            "stage6_output": Optional[Stage6Response] or Stage6SingleProductProfile,
            "product_identity": Optional[Stage4ProductIdentity],
            "extra_signals": Optional[Dict[str, Any]]
        }
        """
        if not image_inputs:
            return Stage7Response(
                session_id=session_id,
                status="COMPLETED",
                products=[],
                message="No image inputs provided"
            )

        # 1. Register session images
        for item in image_inputs:
            img_id = item.get("image_id", "img_unknown")
            p_role = item.get("panel", "UNKNOWN")
            self.session_manager.add_image_to_session(session_id, img_id, p_role)

        # 2. Extract Stage 4 identity & Stage 6 profile per image
        image_records: List[Dict[str, Any]] = []
        for item in image_inputs:
            img_id = item.get("image_id", "img_unknown")
            p_role = item.get("panel", "UNKNOWN")
            src_img = Stage7SourceImage(image_id=img_id, panel=p_role)

            # Stage 4 Identity
            s4_out = item.get("stage4_output")
            prod_id = item.get("product_identity")
            if not prod_id and s4_out and s4_out.products:
                prod_id = s4_out.products[0]
            elif not prod_id and s4_out:
                prod_id = s4_out.identity

            # Stage 6 Profile
            s6_out = item.get("stage6_output")
            s6_single: Optional[Stage6SingleProductProfile] = None
            if isinstance(s6_out, Stage6SingleProductProfile):
                s6_single = s6_out
            elif isinstance(s6_out, Stage6Response) and s6_out.products:
                s6_single = s6_out.products[0]

            image_records.append({
                "source_image": src_img,
                "identity": prod_id or Stage4ProductIdentity(),
                "profile": s6_single,
                "extra_signals": item.get("extra_signals", {})
            })

        # 3. Cluster images into physical products
        product_clusters: List[List[Dict[str, Any]]] = []
        match_evidences: List[Stage7ProductMatchEvidence] = []

        for rec in image_records:
            matched_cluster = None
            for cluster in product_clusters:
                # Compare rec with first item in cluster
                rep_rec = cluster[0]
                match_res = self.product_matcher.evaluate_match(
                    image_a=rep_rec["source_image"].image_id,
                    identity_a=rep_rec["identity"],
                    profile_a=rep_rec["profile"].product_profile if rep_rec["profile"] else None,
                    image_b=rec["source_image"].image_id,
                    identity_b=rec["identity"],
                    profile_b=rec["profile"].product_profile if rec["profile"] else None,
                    extra_signals_a=rep_rec["extra_signals"],
                    extra_signals_b=rec["extra_signals"]
                )
                match_evidences.append(match_res)
                if match_res.status in ("MATCHED", "POSSIBLE_MATCH"):
                    matched_cluster = cluster
                    break

            if matched_cluster is not None:
                matched_cluster.append(rec)
            else:
                product_clusters.append([rec])

        # 4. Consolidate each product cluster into Stage7UnifiedProduct
        unified_products: List[Stage7UnifiedProduct] = []

        for idx, cluster in enumerate(product_clusters, 1):
            product_id = f"product_{idx:03d}"
            cluster_src_images = [r["source_image"] for r in cluster]

            # Collect profiles for field merging
            profiles_for_merging: List[Tuple[Stage7SourceImage, Stage6SingleProductProfile]] = []
            identities_by_image: Dict[str, Tuple[Stage7SourceImage, Stage4ProductIdentity]] = {}

            for r in cluster:
                src_img = r["source_image"]
                identities_by_image[src_img.image_id] = (src_img, r["identity"])
                if r["profile"]:
                    profiles_for_merging.append((src_img, r["profile"]))

            # Field merging & conflict detection
            unified_fields, conflicts = self.field_merger.merge_product_fields(profiles_for_merging)

            # Panel linking & completeness
            panel_completeness = self.panel_linker.calculate_panel_completeness(cluster_src_images)
            cross_links = self.panel_linker.link_cross_panel_entities(identities_by_image)

            # Merged Product Identity & Category Profile
            primary_identity = cluster[0]["identity"]
            merged_identity = self._merge_identity_records([r["identity"] for r in cluster])

            primary_cat_profile = (
                cluster[0]["profile"].product_profile if cluster[0]["profile"] else Stage6ProductProfile()
            )

            # Build cross-panel evidence graph
            graph = self.evidence_graph_builder.build_graph(
                product_id=product_id,
                source_images=cluster_src_images,
                unified_fields=unified_fields,
                cross_panel_links=cross_links
            )

            # Merge confidence calculation
            merge_conf = 0.95 if len(cluster) > 1 else 0.90
            status = "NEEDS_REVIEW" if conflicts else "MERGED"

            unified_products.append(Stage7UnifiedProduct(
                product_id=product_id,
                source_images=cluster_src_images,
                identity=merged_identity,
                category_profile=primary_cat_profile,
                fields=unified_fields,
                conflicts=conflicts,
                cross_panel_links=cross_links,
                evidence_graph=graph,
                panel_completeness=panel_completeness,
                merge_confidence=merge_conf,
                status=status
            ))

        # 5. Update Session Manager state
        session_obj = self.session_manager.update_session_products(
            session_id=session_id,
            products=unified_products,
            matches=match_evidences
        )

        return Stage7Response(
            session_id=session_id,
            status="COMPLETED" if not any(p.status == "NEEDS_REVIEW" for p in unified_products) else "NEEDS_REVIEW",
            products=unified_products,
            session=session_obj
        )

    def _merge_identity_records(self, identities: List[Stage4ProductIdentity]) -> Stage4ProductIdentity:
        """Helper to combine Stage 4 identity signals across panels."""
        if not identities:
            return Stage4ProductIdentity()

        base = identities[0].model_copy(deep=True)
        # Collect unique entities across panels
        all_entities: List[Any] = list(base.entities)
        existing_keys = {(e.role.upper(), e.name.strip().lower()) for e in all_entities if e.name}

        for id_rec in identities[1:]:
            for ent in id_rec.entities:
                if not ent.name:
                    continue
                k = (ent.role.upper(), ent.name.strip().lower())
                if k not in existing_keys:
                    all_entities.append(ent)
                    existing_keys.add(k)

        base.entities = all_entities
        return base
