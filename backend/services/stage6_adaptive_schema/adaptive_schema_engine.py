"""
Stage 6: Adaptive Schema Engine & Field Status Builder
======================================================
Builds the dynamic adaptive schema for a product profile by mapping extracted Stage 3/4 evidence
to expected category fields and assigning explicit status:
- PRESENT: Value visibly present and extracted with high confidence
- NOT_VISIBLE: Field is relevant to product category but not present in current panel/image
- NOT_APPLICABLE: Field is irrelevant to product category (e.g. VOLTAGE for biscuits)
- UNKNOWN: Text exists but meaning cannot be determined
- NEEDS_REVIEW: Low confidence or conflicting values

Strict Zero-Hallucination Policy: Never invents missing values, ingredients, or specifications.
"""

from typing import List, Dict, Any, Optional, Set
from ...models import (
    Stage1Response,
    Stage2Response,
    Stage3Response,
    Stage3SemanticField,
    Stage4Response,
    Stage4ProductIdentity,
    Stage6ProductProfile,
    Stage6AdaptiveField,
    Stage6AdaptiveSchema,
    Stage6SingleProductProfile
)
from .field_relevance import FieldRelevanceEngine
from .schema_templates import UNIVERSAL_CORE_FIELDS, get_template_fields_for_category
from .semantic_differentiator import SemanticDifferentiator


class AdaptiveSchemaEngine:
    """Generates product-specific adaptive schema with strict zero-hallucination guarantees."""

    def __init__(self):
        self.relevance_engine = FieldRelevanceEngine()
        self.differentiator = SemanticDifferentiator()

    def build_adaptive_schema(
        self,
        product_id: str,
        profile: Stage6ProductProfile,
        stage4_output: Optional[Stage4Response] = None,
        stage3_output: Optional[Stage3Response] = None,
        stage2_output: Optional[Stage2Response] = None,
        stage1_output: Optional[Stage1Response] = None,
        product_identity: Optional[Stage4ProductIdentity] = None
    ) -> Stage6SingleProductProfile:
        """Constructs complete Stage 6 single product profile with adaptive schema."""

        category = profile.category
        expected_fields = get_template_fields_for_category(category)

        # Collect extracted values from Stage 4 & Stage 3
        extracted_map: Dict[str, Stage6AdaptiveField] = {}

        # 1. Map Stage 4 Identity fields
        target_identity = product_identity or (stage4_output.identity if stage4_output else None)
        if target_identity:
            if target_identity.product_name and target_identity.product_name.value != "NOT_VISIBLE":
                extracted_map["PRODUCT_NAME"] = Stage6AdaptiveField(
                    field_name="PRODUCT_NAME",
                    value=target_identity.product_name.value,
                    status="PRESENT" if target_identity.product_name.status == "CONFIRMED" else "NEEDS_REVIEW",
                    relevance=1.0,
                    confidence=target_identity.product_name.confidence,
                    source_region_ids=target_identity.product_name.source_region_ids
                )

            if target_identity.brand and target_identity.brand.value != "NOT_VISIBLE":
                extracted_map["BRAND"] = Stage6AdaptiveField(
                    field_name="BRAND",
                    value=target_identity.brand.value,
                    status="PRESENT" if target_identity.brand.status == "CONFIRMED" else "NEEDS_REVIEW",
                    relevance=0.98,
                    confidence=target_identity.brand.confidence,
                    source_region_ids=target_identity.brand.source_region_ids
                )

            if target_identity.model_number:
                val = target_identity.model_number.value if hasattr(target_identity.model_number, "value") else str(target_identity.model_number)
                if val and val != "NOT_VISIBLE":
                    extracted_map["MODEL_NUMBER"] = Stage6AdaptiveField(
                        field_name="MODEL_NUMBER",
                        value=val,
                        status="PRESENT",
                        relevance=self.relevance_engine.get_field_relevance("MODEL_NUMBER", category),
                        confidence=getattr(target_identity.model_number, "confidence", 0.90),
                        source_region_ids=getattr(target_identity.model_number, "source_region_ids", [])
                    )

            if target_identity.country_of_origin:
                val = target_identity.country_of_origin.value if hasattr(target_identity.country_of_origin, "value") else str(target_identity.country_of_origin)
                if val and val != "NOT_VISIBLE":
                    extracted_map["COUNTRY_OF_ORIGIN"] = Stage6AdaptiveField(
                        field_name="COUNTRY_OF_ORIGIN",
                        value=val,
                        status="PRESENT",
                        relevance=0.95,
                        confidence=getattr(target_identity.country_of_origin, "confidence", 0.95),
                        source_region_ids=getattr(target_identity.country_of_origin, "source_region_ids", [])
                    )

            # Stage 4 entities (Manufacturer, Packer, Marketer, Importer)
            for entity in target_identity.entities:
                if not entity.name or entity.name == "NOT_VISIBLE":
                    continue
                role_field = f"{entity.role.upper()}"
                extracted_map[role_field] = Stage6AdaptiveField(
                    field_name=role_field,
                    value=entity.name,
                    status="PRESENT" if not entity.partial_entity else "NEEDS_REVIEW",
                    relevance=0.95,
                    confidence=entity.confidence,
                    source_region_ids=entity.source_region_ids,
                    evidence=entity.address
                )
                if entity.address:
                    addr_field = f"{entity.role.upper()}_ADDRESS"
                    extracted_map[addr_field] = Stage6AdaptiveField(
                        field_name=addr_field,
                        value=entity.address,
                        status="PRESENT",
                        relevance=0.95,
                        confidence=entity.confidence,
                        source_region_ids=entity.source_region_ids
                    )

        # 2. Map Stage 3 Semantic Fields
        if stage3_output and stage3_output.semantic_fields:
            for sf in stage3_output.semantic_fields:
                stype = sf.semantic_type.upper()
                sf_unit = getattr(sf, "unit", None)
                sf_raw = getattr(sf, "raw_text", getattr(sf, "value", ""))

                # Semantic differentiation check for quantities
                if sf_unit or any(term in (sf_raw or "").lower() for term in ["g", "kg", "ml", "l", "mm", "cm", "weight", "serving"]):
                    diff = self.differentiator.differentiate_quantity(
                        raw_text=sf_raw or "",
                        value=sf.value,
                        unit=sf_unit,
                        semantic_type=stype,
                        category=category
                    )
                    d_type = diff["differentiated_type"]
                    if d_type != stype:
                        stype = d_type

                rel = self.relevance_engine.get_field_relevance(stype, category)
                status = "PRESENT" if sf.status == "CONFIRMED" else ("NEEDS_REVIEW" if sf.status == "AMBIGUOUS" else "UNKNOWN")

                extracted_map[stype] = Stage6AdaptiveField(
                    field_name=stype,
                    value=sf.value,
                    status=status,
                    relevance=rel,
                    confidence=sf.semantic_confidence,
                    source_region_ids=sf.source_region_ids,
                    evidence=getattr(sf, "evidence_text", getattr(sf, "heading_text", None)),
                    unit=sf_unit
                )

        # 3. Assemble Schema Lists
        all_fields: List[Stage6AdaptiveField] = []
        universal_fields: List[Stage6AdaptiveField] = []
        category_fields: List[Stage6AdaptiveField] = []

        uncertain_list: List[Stage6AdaptiveField] = []
        not_visible_list: List[Stage6AdaptiveField] = []
        not_applicable_list: List[Stage6AdaptiveField] = []

        # Process expected fields for category
        processed_field_names: Set[str] = set()

        for fname in expected_fields:
            processed_field_names.add(fname)
            rel = self.relevance_engine.get_field_relevance(fname, category)
            is_core = fname in UNIVERSAL_CORE_FIELDS

            if fname in extracted_map:
                field_obj = extracted_map[fname]
                field_obj.relevance = rel
            else:
                # Field not extracted -> assign NOT_VISIBLE or NOT_APPLICABLE
                if rel >= 0.15:
                    field_obj = Stage6AdaptiveField(
                        field_name=fname,
                        value=None,
                        status="NOT_VISIBLE",
                        relevance=rel,
                        confidence=0.0
                    )
                else:
                    field_obj = Stage6AdaptiveField(
                        field_name=fname,
                        value=None,
                        status="NOT_APPLICABLE",
                        relevance=rel,
                        confidence=0.0
                    )

            all_fields.append(field_obj)
            if is_core:
                universal_fields.append(field_obj)
            else:
                category_fields.append(field_obj)

            # Categorize status lists
            if field_obj.status in ("UNKNOWN", "NEEDS_REVIEW"):
                uncertain_list.append(field_obj)
            elif field_obj.status == "NOT_VISIBLE":
                not_visible_list.append(field_obj)
            elif field_obj.status == "NOT_APPLICABLE":
                not_applicable_list.append(field_obj)

        # Include any extra extracted fields not in template list
        for fname, fobj in extracted_map.items():
            if fname not in processed_field_names:
                all_fields.append(fobj)
                category_fields.append(fobj)
                if fobj.status in ("UNKNOWN", "NEEDS_REVIEW"):
                    uncertain_list.append(fobj)

        adaptive_schema = Stage6AdaptiveSchema(
            fields=all_fields,
            universal_core_fields=universal_fields,
            category_specific_fields=category_fields
        )

        return Stage6SingleProductProfile(
            product_id=product_id,
            product_profile=profile,
            adaptive_schema=adaptive_schema,
            uncertain_fields=uncertain_list,
            not_visible_fields=not_visible_list,
            not_applicable_fields=not_applicable_list
        )
