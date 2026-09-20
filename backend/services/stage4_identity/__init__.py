"""
LM-COMPASS Stage 4: Universal Product + Company + Entity Identification Pipeline
================================================================================
Master orchestrator for Stage 4:
- Identifies Brand, Product Name, Category, Variant, Model, SKU, Article Number,
  Batch Number, Lot Number, Serial Number, and Country of Origin.
- Resolves all commercial entities (Manufacturer, Packer, Marketer, Importer, Distributor, Seller)
  without merging their distinct legal roles.
- Back-Panel & Any-Panel Resilience: Functions reliably without requiring a front PDP.
- Multi-Product Segmentation: Produces separate product_001, product_002 identities if multiple items exist.
- Barcode / QR Code supporting evidence attachment.
- Traceable Identity Evidence Graph.
- Strictly adheres to NO-HALLUCINATION and NO-RULE-VALIDATION boundaries.
"""

import uuid
import re
from typing import Dict, Any, Optional, Tuple, List

from ...models import (
    Stage1Response,
    Stage2Response,
    Stage2TextRegion,
    Stage3Response,
    Stage3SemanticField,
    Stage4Response,
    Stage4ProductIdentity,
    Stage4Entity,
    Stage4ValueWithStatus,
    Stage4CategoryInfo
)
from ..stage3_semantic import Stage3Pipeline
from .role_detector import RoleDetectionService
from .company_resolver import CompanyResolverService
from .address_associator import AddressAssociatorService
from .brand_product_resolver import BrandProductResolverService
from .category_resolver import CategoryResolverService
from .identifier_resolver import IdentifierResolverService
from .evidence_graph import IdentityEvidenceGraphBuilder
from .multi_product_handler import MultiProductHandler
from .confidence_evaluator import IdentityConfidenceEvaluator


class Stage4Pipeline:
    """Master orchestrator for Stage 4 Universal Identity Resolution."""

    def __init__(self):
        self.stage3_pipeline = Stage3Pipeline()
        self.role_detector = RoleDetectionService()
        self.company_resolver = CompanyResolverService()
        self.address_associator = AddressAssociatorService()
        self.brand_product_resolver = BrandProductResolverService()
        self.category_resolver = CategoryResolverService()
        self.identifier_resolver = IdentifierResolverService()
        self.evidence_graph_builder = IdentityEvidenceGraphBuilder()
        self.multi_product_handler = MultiProductHandler()
        self.confidence_evaluator = IdentityConfidenceEvaluator()

    def _determine_panel(
        self,
        regions: List[Stage2TextRegion],
        stage1_output: Optional[Stage1Response] = None
    ) -> str:
        if stage1_output and getattr(stage1_output, "panel", None):
            return stage1_output.panel.type.upper()
        if stage1_output and getattr(stage1_output, "panels", None) and stage1_output.panels:
            return stage1_output.panels[0].type.upper()

        all_text = " ".join((r.normalized_text or r.raw_text or "").lower() for r in regions)
        # Statutory and back panel indicators
        back_signals = sum(1 for w in [
            "ingredients", "nutritional", "mfg by", "manufactured by", "packed by", "pkd by",
            "best before", "net qty", "mrp", "plot", "estate", "industrial area", "gidc", "midc"
        ] if w in all_text)
        if back_signals >= 2:
            return "BACK"
        
        # Side panel indicator: imported by, model, specs
        if "imported by" in all_text and ("model" in all_text or "country of origin" in all_text):
            return "SIDE"

        if any(w in all_text for w in ["glowcare", "deluxe", "serum", "tea", "biscuit", "shampoo"]) and back_signals < 2:
            return "FRONT"

        return "UNKNOWN"

    def process_stage3_output(
        self,
        stage3_output: Stage3Response,
        stage2_output: Optional[Stage2Response] = None,
        stage1_output: Optional[Stage1Response] = None
    ) -> Stage4Response:
        """Resolves complete product and entity identity from Stage 3 and supporting OCR outputs."""
        scan_id = stage3_output.scan_id.replace("STAGE3", "STAGE4")

        # 1. Quality check
        if stage3_output.semantic_status == "INSUFFICIENT_QUALITY":
            empty_id = Stage4ProductIdentity(
                product_name=Stage4ValueWithStatus(value="NOT_VISIBLE", status="UNCERTAIN", confidence=0.0),
                brand=Stage4ValueWithStatus(value="NOT_VISIBLE", status="UNCERTAIN", confidence=0.0)
            )
            return Stage4Response(
                scan_id=scan_id,
                identity_status="UNCERTAIN",
                identity=empty_id,
                products=[empty_id],
                message=stage3_output.message or "Image quality insufficient for identity resolution."
            )

        # Retrieve text regions and semantic fields
        regions = stage2_output.regions if stage2_output else []
        if not regions and stage3_output.uncertain_regions:
            regions = stage3_output.uncertain_regions

        semantic_fields = stage3_output.semantic_fields

        # 2. Multi-Product Partitioning
        partitions = self.multi_product_handler.detect_and_partition_products(
            regions=regions,
            semantic_fields=semantic_fields,
            stage1_output=stage1_output
        )

        resolved_products: List[Stage4ProductIdentity] = []
        any_garbage = False

        for prod_id, prod_regions, prod_fields, prod_bbox in partitions:
            source_panel = self._determine_panel(prod_regions, stage1_output)
            detected_company_names: List[str] = []
            entities: List[Stage4Entity] = []
            consumed_address_region_ids: set = set()

            # A. Entity and Role Extraction
            for idx, reg in enumerate(prod_regions):
                txt = (reg.normalized_text or reg.raw_text or "").strip()
                
                # Check for garbage
                if self.company_resolver.is_ocr_garbage(txt):
                    any_garbage = True
                    continue

                role, role_label, role_conf = self.role_detector.detect_role_from_text(txt)
                
                # Handle composite roles (e.g. Manufactured and Marketed By)
                target_roles = []
                if role == "MANUFACTURER_AND_MARKETER":
                    target_roles = ["MANUFACTURER", "MARKETER"]
                elif role == "MANUFACTURER_AND_PACKER":
                    target_roles = ["MANUFACTURER", "PACKER"]
                elif role == "IMPORTER_AND_DISTRIBUTOR":
                    target_roles = ["IMPORTER", "DISTRIBUTOR"]
                elif role:
                    target_roles = [role]

                company_name = None
                is_partial = False
                comp_conf = 0.90
                company_reg_idx = idx

                if role:
                    # Role is explicit on this line
                    stripped = self.role_detector.strip_role_prefix(txt)
                    if stripped and len(stripped) >= 3:
                        c_name, part, garb, c_conf = self.company_resolver.extract_company_candidate(stripped)
                        if garb:
                            any_garbage = True
                        elif c_name:
                            company_name = c_name
                            is_partial = part
                            comp_conf = c_conf
                        else:
                            # Use stripped text if reasonable length
                            company_name = stripped
                            is_partial = self.company_resolver.is_partial_name(stripped)
                    
                    # If company name wasn't on the same line, check next line
                    if not company_name and (idx + 1) < len(prod_regions):
                        next_txt = (prod_regions[idx+1].normalized_text or prod_regions[idx+1].raw_text or "").strip()
                        c_name, part, garb, c_conf = self.company_resolver.extract_company_candidate(next_txt)
                        if garb:
                            any_garbage = True
                        elif c_name:
                            company_name = c_name
                            is_partial = part
                            comp_conf = c_conf
                            company_reg_idx = idx + 1
                        elif not self.address_associator.is_address_text(next_txt) and len(next_txt) >= 3:
                            company_name = next_txt
                            is_partial = self.company_resolver.is_partial_name(next_txt)
                            company_reg_idx = idx + 1

                elif not role:
                    # Line without explicit role prefix: check if it's an organization name directly
                    c_name, part, garb, c_conf = self.company_resolver.extract_company_candidate(txt)
                    if garb:
                        any_garbage = True
                    elif c_name and not self.address_associator.is_address_text(txt):
                        # Default role if unspecified
                        target_roles = ["OTHER_ORGANIZATION"]
                        company_name = c_name
                        is_partial = part
                        comp_conf = c_conf

                if company_name and target_roles:
                    # Associate Address & PIN
                    addr_str, pin_val, addr_reg_ids, agg_bbox = self.address_associator.associate_address_block(
                        company_region_idx=company_reg_idx,
                        all_regions=prod_regions
                    )
                    consumed_address_region_ids.update(addr_reg_ids)
                    detected_company_names.append(company_name)

                    source_ids = [prod_regions[idx].region_id]
                    if company_reg_idx != idx:
                        source_ids.append(prod_regions[company_reg_idx].region_id)
                    source_ids.extend(addr_reg_ids)

                    if not pin_val:
                        for sf in prod_fields:
                            if sf.semantic_type in ("POSTAL_PIN", "MANUFACTURER_ADDRESS", "PACKER_ADDRESS", "MARKETER_ADDRESS", "ADDRESS"):
                                p_found = self.address_associator.extract_pin(sf.value)
                                if p_found:
                                    pin_val = p_found
                                    break

                    for r in target_roles:
                        entities.append(
                            Stage4Entity(
                                role=r,
                                name=company_name,
                                address=addr_str if addr_str else None,
                                pin=pin_val if pin_val else None,
                                confidence=round((role_conf + comp_conf) / 2.0, 2),
                                entity_confidence=comp_conf,
                                role_confidence=role_conf,
                                partial_entity=is_partial,
                                source_panel=source_panel,
                                source_region_ids=source_ids,
                                bbox=agg_bbox if agg_bbox else prod_regions[company_reg_idx].bbox,
                                original_bbox=prod_regions[company_reg_idx].original_bbox
                            )
                        )

            # Check Stage 3 semantic fields for any missed entities
            for sf in prod_fields:
                if sf.semantic_type in ("MANUFACTURER_NAME", "MARKETER_NAME", "PACKER_NAME", "IMPORTER_NAME"):
                    role_map = {
                        "MANUFACTURER_NAME": "MANUFACTURER",
                        "MARKETER_NAME": "MARKETER",
                        "PACKER_NAME": "PACKER",
                        "IMPORTER_NAME": "IMPORTER"
                    }
                    m_role = role_map[sf.semantic_type]
                    if not any(e.role == m_role for e in entities):
                        entities.append(
                            Stage4Entity(
                                role=m_role,
                                name=sf.value,
                                address=None,
                                pin=None,
                                confidence=sf.semantic_confidence,
                                entity_confidence=sf.semantic_confidence,
                                role_confidence=0.95,
                                partial_entity=self.company_resolver.is_partial_name(sf.value),
                                source_panel=source_panel,
                                source_region_ids=sf.source_region_ids,
                                bbox=sf.bbox,
                                original_bbox=sf.original_bbox
                            )
                        )
                        detected_company_names.append(sf.value)

            # B. Brand, Product Name, and Variant Resolution
            product_name, brand, variant = self.brand_product_resolver.resolve_brand_product_variant(
                regions=prod_regions,
                semantic_fields=prod_fields,
                detected_company_names=detected_company_names,
                source_panel=source_panel
            )

            # C. Category Resolution
            category = self.category_resolver.resolve_category(
                s3_candidates=stage3_output.category_candidates,
                product_name=product_name.value,
                regions=prod_regions
            )

            # D. Identifier and Country of Origin Resolution
            ident_data = self.identifier_resolver.extract_identifiers(
                regions=prod_regions,
                semantic_fields=prod_fields
            )

            # E. Barcode & QR Supporting Evidence
            barcode_val = None
            barcode_fmt = None
            qr_val = None
            decode_conf = 0.0

            if stage2_output:
                if stage2_output.barcode_regions:
                    bc = stage2_output.barcode_regions[0]
                    barcode_val = bc.decoded_data
                    barcode_fmt = bc.format
                    decode_conf = bc.confidence
                if stage2_output.qr_regions:
                    qr = stage2_output.qr_regions[0]
                    qr_val = qr.decoded_payload
                    decode_conf = max(decode_conf, qr.confidence)

            # F. Identity Evidence Graph
            graph = self.evidence_graph_builder.build_graph(
                entities=entities,
                brand=brand,
                product_name=product_name,
                model_number=ident_data.get("model_number")
            )

            product_identity = Stage4ProductIdentity(
                product_id=prod_id,
                product_name=product_name,
                brand=brand,
                category=category,
                variant=variant,
                entities=entities,
                model_number=ident_data.get("model_number"),
                sku=ident_data.get("sku"),
                article_number=ident_data.get("article_number"),
                batch_number=ident_data.get("batch_number"),
                lot_number=ident_data.get("lot_number"),
                serial_number=ident_data.get("serial_number"),
                country_of_origin=ident_data.get("country_of_origin"),
                barcode_value=barcode_val,
                barcode_type=barcode_fmt,
                qr_value=qr_val,
                decode_confidence=decode_conf,
                evidence_graph=graph,
                source_panel=source_panel,
                bbox=prod_bbox
            )
            resolved_products.append(product_identity)

        primary_product = resolved_products[0] if resolved_products else Stage4ProductIdentity()

        # Overall identity status
        overall_status = self.confidence_evaluator.evaluate_identity_status(
            product_name=primary_product.product_name,
            brand=primary_product.brand,
            category=primary_product.category,
            entities=primary_product.entities,
            is_garbage_detected=any_garbage and not primary_product.entities
        )

        status_msg = (
            f"Stage 4 Identity Resolution completed. Identified {len(resolved_products)} product(s), "
            f"{len(primary_product.entities)} commercial entity(s). Status: {overall_status}."
        )

        return Stage4Response(
            scan_id=scan_id,
            identity_status=overall_status,
            identity=primary_product,
            products=resolved_products,
            message=status_msg
        )

    def process_image_bytes(
        self,
        image_bytes: bytes,
        filename: str = "package.jpg",
        source: str = "upload"
    ) -> Stage4Response:
        """Executes full Stage 1 + Stage 2 + Stage 3 + Stage 4 pipeline from raw image bytes."""
        stage2_res = self.stage3_pipeline.stage2_pipeline.process_image_bytes(
            image_bytes, filename=filename, source=source
        )
        stage3_res = self.stage3_pipeline.process_stage2_output(stage2_res)
        return self.process_stage3_output(
            stage3_output=stage3_res,
            stage2_output=stage2_res
        )

    def process_base64_image(
        self,
        base64_str: str,
        filename: str = "package.jpg",
        source: str = "upload"
    ) -> Stage4Response:
        """Executes full Stage 1 + Stage 2 + Stage 3 + Stage 4 pipeline from base64 string."""
        import base64
        clean_b64 = base64_str.split(",", 1)[1] if "," in base64_str else base64_str
        raw_bytes = base64.b64decode(clean_b64)
        return self.process_image_bytes(raw_bytes, filename=filename, source=source)
