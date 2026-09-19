"""
Stage 3: Universal Text Meaning & Semantic Understanding Master Pipeline
========================================================================
Translates raw and normalized OCR text into rich, contextual, evidence-backed
Legal Metrology semantic fields and relationships:
1. Section Detection (Semantic domains & shielding, e.g. INGREDIENTS shield)
2. Heading Detection & Heading-to-Value Association
3. Contextual Quantity, Price, Date, and Entity Interpretation
4. Table Structure & Cell Semantic Interpretation (e.g. Serving Size vs Net Qty)
5. Product Category Signal Detection
6. Ambiguity Resolution & Conservative Safety Gating
7. Zero-Hallucination Evidence Tracking preserving coordinates & source region IDs
"""

import re
import uuid
from typing import Optional, Dict, Any, Tuple, List
from PIL import Image

from ...models import (
    Stage1Response,
    Stage2Response,
    Stage3Response,
    Stage3SemanticField,
    Stage3Section,
    Stage3Relationship,
    Stage3CategoryCandidate,
    Stage3Statistics,
    Stage3CandidateType
)
from ..stage2_ocr import Stage2Pipeline
from .section_detector import SectionDetectionService
from .heading_association import HeadingAssociationService
from .quantity_interpreter import QuantityInterpretationService
from .price_interpreter import PriceInterpretationService
from .date_interpreter import DateInterpretationService
from .entity_interpreter import EntityInterpretationService
from .table_interpreter import TableInterpretationService
from .category_detector import CategorySignalDetector
from .ambiguity_resolver import AmbiguityResolverService


class Stage3Pipeline:
    """Master orchestrator for Stage 3 Universal Semantic Understanding."""

    def __init__(self):
        self.stage2_pipeline = Stage2Pipeline()
        self.section_detector = SectionDetectionService()
        self.heading_associator = HeadingAssociationService()
        self.quantity_interpreter = QuantityInterpretationService()
        self.price_interpreter = PriceInterpretationService()
        self.date_interpreter = DateInterpretationService()
        self.entity_interpreter = EntityInterpretationService()
        self.table_interpreter = TableInterpretationService()
        self.category_detector = CategorySignalDetector()
        self.ambiguity_resolver = AmbiguityResolverService()

    def process_stage2_output(
        self,
        stage2_output: Stage2Response,
        stage1_output: Optional[Stage1Response] = None
    ) -> Stage3Response:
        """Translates Stage 2 text detections into semantic fields and relationships."""
        scan_id = stage2_output.scan_id.replace("STAGE2", "STAGE3")

        # 1. Quality / Pre-condition check
        if stage2_output.text_detection_status == "INSUFFICIENT_QUALITY":
            return Stage3Response(
                scan_id=scan_id,
                semantic_status="INSUFFICIENT_QUALITY",
                message=stage2_output.message or "Image quality insufficient for semantic understanding."
            )

        regions = stage2_output.regions
        uncertain_regions = stage2_output.uncertain_regions
        tables = stage2_output.tables

        # 2. Section Detection & Domain Shielding
        sections, region_to_section = self.section_detector.detect_sections(regions)

        # 3. Heading Detection & Explicit Relationships
        relationships, region_associations = self.heading_associator.extract_heading_associations(regions)

        # 4. Contextual Region Interpretation
        all_semantic_fields: List[Stage3SemanticField] = []
        handled_region_ids = set()

        for reg in regions:
            reg_id = reg.region_id
            text = reg.normalized_text or reg.raw_text or ""
            sec_type = region_to_section.get(reg_id, "OTHER")
            assoc = region_associations.get(reg_id)

            heading_type = assoc.get("field_type") if assoc else None
            heading_text = assoc.get("heading_text") if assoc else None
            value_text = assoc.get("value_text", text) if assoc else text

            # A. Quantity Check
            q_type, q_val, q_conf, q_cands = self.quantity_interpreter.interpret_quantity(
                text=text,
                section_type=sec_type,
                heading_type=heading_type,
                heading_text=heading_text
            )
            if q_val:
                actual_type = heading_type if (assoc and assoc.get("field_type") in ("NET_QUANTITY", "SERVING_SIZE")) else q_type
                actual_val = value_text if (assoc and heading_type) else (q_val or text)
                all_semantic_fields.append(
                    Stage3SemanticField(
                        field_id=f"FLD-{uuid.uuid4().hex[:6].upper()}",
                        semantic_type=actual_type,
                        value=actual_val,
                        normalized_value=actual_val,
                        heading_text=heading_text,
                        source_region_ids=[reg_id],
                        heading_region_ids=[reg_id] if heading_text else [],
                        bbox=reg.bbox,
                        original_bbox=reg.original_bbox,
                        ocr_confidence=reg.ocr_confidence,
                        semantic_confidence=q_conf if q_conf > 0 else 0.50,
                        relationship_confidence=assoc.get("confidence", 0.90) if assoc else 0.50,
                        status="CONFIRMED" if (q_conf >= 0.70 and actual_type not in ("UNKNOWN", "OTHER_QUANTITY")) else "NEEDS_REVIEW",
                        candidate_types=q_cands
                    )
                )
                handled_region_ids.add(reg_id)
                continue

            # B. Price Check
            p_type, p_val, p_conf, p_cands = self.price_interpreter.interpret_price(
                text=text,
                section_type=sec_type,
                heading_type=heading_type
            )
            if p_val:
                actual_type = heading_type if (assoc and assoc.get("field_type") in ("MRP", "PRICE", "SALE_PRICE")) else p_type
                actual_val = value_text if (assoc and heading_type) else (p_val or text)
                all_semantic_fields.append(
                    Stage3SemanticField(
                        field_id=f"FLD-{uuid.uuid4().hex[:6].upper()}",
                        semantic_type=actual_type,
                        value=actual_val,
                        normalized_value=actual_val,
                        heading_text=heading_text,
                        source_region_ids=[reg_id],
                        heading_region_ids=[reg_id] if heading_text else [],
                        bbox=reg.bbox,
                        original_bbox=reg.original_bbox,
                        ocr_confidence=reg.ocr_confidence,
                        semantic_confidence=p_conf if p_conf > 0 else 0.50,
                        relationship_confidence=assoc.get("confidence", 0.90) if assoc else 0.50,
                        status="CONFIRMED" if (p_conf >= 0.70 and actual_type not in ("UNKNOWN", "PRICE_CANDIDATE")) else "NEEDS_REVIEW",
                        candidate_types=p_cands
                    )
                )
                handled_region_ids.add(reg_id)
                continue

            # C. Date Check
            d_type, d_val, d_conf, d_cands = self.date_interpreter.interpret_date(
                text=text,
                section_type=sec_type,
                heading_type=heading_type
            )
            if d_type != "UNKNOWN" or (assoc and assoc.get("field_type") in ("MANUFACTURING_DATE", "PACKING_DATE", "EXPIRY_DATE", "BEST_BEFORE_DATE")):
                actual_type = heading_type if (assoc and assoc.get("field_type") in ("MANUFACTURING_DATE", "PACKING_DATE", "EXPIRY_DATE", "BEST_BEFORE_DATE")) else d_type
                actual_val = value_text if assoc else (d_val or text)
                all_semantic_fields.append(
                    Stage3SemanticField(
                        field_id=f"FLD-{uuid.uuid4().hex[:6].upper()}",
                        semantic_type=actual_type,
                        value=actual_val,
                        normalized_value=actual_val,
                        heading_text=heading_text,
                        source_region_ids=[reg_id],
                        heading_region_ids=[reg_id] if heading_text else [],
                        bbox=reg.bbox,
                        original_bbox=reg.original_bbox,
                        ocr_confidence=reg.ocr_confidence,
                        semantic_confidence=d_conf if d_conf > 0 else 0.95,
                        relationship_confidence=assoc.get("confidence", 0.90) if assoc else 0.85,
                        status="CONFIRMED" if (d_conf >= 0.60 and actual_type != "UNKNOWN") else "NEEDS_REVIEW",
                        candidate_types=d_cands
                    )
                )
                handled_region_ids.add(reg_id)
                continue

            # D. Entity, Brand, & Address Check
            e_type, e_val, e_conf, e_cands = self.entity_interpreter.interpret_entity_or_address(
                text=text,
                section_type=sec_type,
                heading_type=heading_type
            )
            if e_type != "UNKNOWN" or (assoc and assoc.get("field_type") in ("MANUFACTURER_NAME", "MARKETER_NAME", "PACKER_NAME", "IMPORTER_NAME", "DISTRIBUTOR_NAME")):
                actual_type = heading_type if (assoc and assoc.get("field_type") in ("MANUFACTURER_NAME", "MARKETER_NAME", "PACKER_NAME", "IMPORTER_NAME", "DISTRIBUTOR_NAME")) else e_type
                actual_val = value_text if assoc else (e_val or text)
                all_semantic_fields.append(
                    Stage3SemanticField(
                        field_id=f"FLD-{uuid.uuid4().hex[:6].upper()}",
                        semantic_type=actual_type,
                        value=actual_val,
                        normalized_value=actual_val,
                        heading_text=heading_text,
                        source_region_ids=[reg_id],
                        heading_region_ids=[reg_id] if heading_text else [],
                        bbox=reg.bbox,
                        original_bbox=reg.original_bbox,
                        ocr_confidence=reg.ocr_confidence,
                        semantic_confidence=e_conf if e_conf > 0 else 0.95,
                        relationship_confidence=assoc.get("confidence", 0.90) if assoc else 0.85,
                        status="CONFIRMED" if e_conf >= 0.60 else "NEEDS_REVIEW",
                        candidate_types=e_cands
                    )
                )
                handled_region_ids.add(reg_id)
                continue

            # E. Identifiers (Batch No, Lot No)
            if assoc and assoc.get("field_type") in ("BATCH_NUMBER", "LOT_NUMBER", "MODEL_NUMBER", "SERIAL_NUMBER"):
                all_semantic_fields.append(
                    Stage3SemanticField(
                        field_id=f"FLD-{uuid.uuid4().hex[:6].upper()}",
                        semantic_type=assoc["field_type"],
                        value=value_text,
                        normalized_value=value_text,
                        heading_text=heading_text,
                        source_region_ids=[reg_id],
                        heading_region_ids=[reg_id],
                        bbox=reg.bbox,
                        original_bbox=reg.original_bbox,
                        ocr_confidence=reg.ocr_confidence,
                        semantic_confidence=0.96,
                        relationship_confidence=assoc.get("confidence", 0.95),
                        status="CONFIRMED",
                        candidate_types=[Stage3CandidateType(type=assoc["field_type"], confidence=0.96)]
                    )
                )
                handled_region_ids.add(reg_id)
                continue

            # F. Consumer Care / Contact
            if assoc and assoc.get("field_type") == "CONSUMER_CARE":
                all_semantic_fields.append(
                    Stage3SemanticField(
                        field_id=f"FLD-{uuid.uuid4().hex[:6].upper()}",
                        semantic_type="CONSUMER_CARE",
                        value=value_text,
                        normalized_value=value_text,
                        heading_text=heading_text,
                        source_region_ids=[reg_id],
                        heading_region_ids=[reg_id],
                        bbox=reg.bbox,
                        original_bbox=reg.original_bbox,
                        ocr_confidence=reg.ocr_confidence,
                        semantic_confidence=0.95,
                        relationship_confidence=assoc.get("confidence", 0.95),
                        status="CONFIRMED",
                        candidate_types=[Stage3CandidateType(type="CONSUMER_CARE", confidence=0.95)]
                    )
                )
                handled_region_ids.add(reg_id)
                continue

            # G. Section-level Declarations (e.g. INGREDIENTS paragraph)
            if sec_type == "INGREDIENTS":
                all_semantic_fields.append(
                    Stage3SemanticField(
                        field_id=f"FLD-{uuid.uuid4().hex[:6].upper()}",
                        semantic_type="INGREDIENTS",
                        value=text,
                        normalized_value=text,
                        heading_text="Ingredients",
                        source_region_ids=[reg_id],
                        bbox=reg.bbox,
                        original_bbox=reg.original_bbox,
                        ocr_confidence=reg.ocr_confidence,
                        semantic_confidence=0.96,
                        relationship_confidence=0.95,
                        status="CONFIRMED",
                        candidate_types=[Stage3CandidateType(type="INGREDIENTS", confidence=0.96)]
                    )
                )
                handled_region_ids.add(reg_id)
                continue

            # H. Product Name / Title Candidate (Prominent top banner without legal heading)
            words = text.split()
            has_title_word = any(w.isalpha() and len(w) >= 3 for w in words)
            is_number_or_price = bool(re.search(r'^[₹$€0-9]', text.strip()))
            if reg.reading_order_index in (1, 2) and sec_type == "OTHER" and len(words) <= 6 and has_title_word and not is_number_or_price:
                all_semantic_fields.append(
                    Stage3SemanticField(
                        field_id=f"FLD-{uuid.uuid4().hex[:6].upper()}",
                        semantic_type="PRODUCT_NAME",
                        value=text,
                        normalized_value=text,
                        heading_text=None,
                        source_region_ids=[reg_id],
                        bbox=reg.bbox,
                        original_bbox=reg.original_bbox,
                        ocr_confidence=reg.ocr_confidence,
                        semantic_confidence=0.88,
                        relationship_confidence=0.85,
                        status="CONFIRMED",
                        candidate_types=[
                            Stage3CandidateType(type="PRODUCT_NAME", confidence=0.88),
                            Stage3CandidateType(type="BRAND_NAME", confidence=0.80)
                        ]
                    )
                )
                handled_region_ids.add(reg_id)
                continue

            # Default: UNKNOWN field with conservative confidence
            all_semantic_fields.append(
                Stage3SemanticField(
                    field_id=f"FLD-{uuid.uuid4().hex[:6].upper()}",
                    semantic_type="UNKNOWN",
                    value=text,
                    normalized_value=text,
                    heading_text=None,
                    source_region_ids=[reg_id],
                    bbox=reg.bbox,
                    original_bbox=reg.original_bbox,
                    ocr_confidence=reg.ocr_confidence,
                    semantic_confidence=0.30,
                    relationship_confidence=0.20,
                    status="NEEDS_REVIEW",
                    candidate_types=[Stage3CandidateType(type="OTHER_DECLARATION", confidence=0.30)]
                )
            )

        # 5. Table Understanding
        table_fields, table_rels = self.table_interpreter.interpret_tables(tables)
        all_semantic_fields.extend(table_fields)
        relationships.extend(table_rels)

        # 6. Category Signal Detection
        category_candidates = self.category_detector.detect_category_signals(regions)

        # 7. Ambiguity Resolution & Statistics
        confirmed_fields, ambiguous_fields = self.ambiguity_resolver.resolve_ambiguity(all_semantic_fields)

        total_regions = len(regions)
        semantic_count = len(confirmed_fields)
        unknown_count = sum(1 for f in all_semantic_fields if f.semantic_type == "UNKNOWN")
        needs_review_count = len(ambiguous_fields)

        stats = Stage3Statistics(
            total_ocr_regions=total_regions,
            semantic_regions=semantic_count,
            unknown_regions=unknown_count,
            needs_review_regions=needs_review_count
        )

        status_msg = (
            f"Stage 3 semantic understanding complete. Extracted {len(confirmed_fields)} confirmed semantic field(s), "
            f"{len(relationships)} relationship(s), and {len(sections)} section(s). "
            f"Ambiguous fields flagged for review: {len(ambiguous_fields)}."
        )

        return Stage3Response(
            scan_id=scan_id,
            semantic_status="COMPLETED",
            sections=sections,
            semantic_fields=confirmed_fields,
            relationships=relationships,
            category_candidates=category_candidates,
            ambiguous_fields=ambiguous_fields,
            uncertain_regions=uncertain_regions,
            statistics=stats,
            message=status_msg
        )

    def process_image_bytes(
        self,
        image_bytes: bytes,
        filename: str = "package.jpg",
        source: str = "upload"
    ) -> Stage3Response:
        """Executes full Stage 1 + Stage 2 + Stage 3 end-to-end pipeline."""
        stage2_res = self.stage2_pipeline.process_image_bytes(
            image_bytes, filename=filename, source=source
        )
        return self.process_stage2_output(stage2_res)

    def process_base64_image(
        self,
        base64_str: str,
        filename: str = "package.jpg",
        source: str = "upload"
    ) -> Stage3Response:
        """Executes full Stage 1 + Stage 2 + Stage 3 from base64 string."""
        import base64
        clean_b64 = base64_str.split(",", 1)[1] if "," in base64_str else base64_str
        raw_bytes = base64.b64decode(clean_b64)
        return self.process_image_bytes(raw_bytes, filename=filename, source=source)
