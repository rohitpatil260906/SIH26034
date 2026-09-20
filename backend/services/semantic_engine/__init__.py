"""
LM-COMPASS UNIVERSAL FIELD SEMANTIC UNDERSTANDING ENGINE
========================================================
18-Service Modular Legal Metrology Vision & Semantic Architecture:
1. ImageQualityService
2. ImagePreprocessingService
3. PanelDetectionService
4. TextDetectionService
5. OcrEnsembleService
6. LayoutAnalysisService
7. SectionDetectionService
8. ProductClassificationService
9. EntityExtractionService
10. SemanticFieldClassificationService
11. ContextResolutionService
12. VlmVerificationService
13. CrossPanelMergeService
14. LegalMetrologyRuleEngine
15. ConfidenceEngine
16. EvidenceEngine
17. ComplianceDecisionEngine
18. AuditExplainabilityService
"""

from typing import List, Dict, Any, Tuple, Optional
from PIL import Image

from ...models import (
    UniversalFieldObject,
    UniversalSemanticField,
    ExtractedLine,
    StructuredProductData,
    ComplianceCheckItem,
    LmCompassResult,
    BoundingBox,
    SectionType
)

from .image_quality import ImageQualityService
from .preprocessing import ImagePreprocessingService
from .panel_detection import PanelDetectionService
from .text_detection import TextDetectionService
from .ocr_ensemble import OcrEnsembleService
from .layout_analysis import LayoutAnalysisService, TableRow, LayoutBlock
from .section_detection import SectionDetectionService, SectionBoundary
from .product_classification import ProductClassificationService
from .entity_extraction import EntityExtractionService, RawCandidateEntity
from .semantic_classifier import SemanticFieldClassificationService
from .context_resolution import ContextResolutionService, DecomposedAddress
from .vlm_verification import VlmVerificationService
from .cross_panel_merge import CrossPanelMergeService
from .rule_engine_adapter import LegalMetrologyRuleEngine
from .confidence_engine import ConfidenceEngine
from .evidence_engine import EvidenceEngine
from .compliance_decision import ComplianceDecisionEngine
from .audit_explainability import AuditExplainabilityService, AuditExplanationDossier


class UniversalFieldPipeline:
    """Master orchestrator integrating all 18 modular semantic services."""

    def __init__(self):
        self.image_quality_service = ImageQualityService()
        self.preprocessing_service = ImagePreprocessingService()
        self.panel_detection_service = PanelDetectionService()
        self.text_detection_service = TextDetectionService()
        self.ocr_ensemble_service = OcrEnsembleService()
        self.layout_analysis_service = LayoutAnalysisService()
        self.section_detection_service = SectionDetectionService()
        self.product_classification_service = ProductClassificationService()
        self.entity_extraction_service = EntityExtractionService()
        self.semantic_classifier_service = SemanticFieldClassificationService()
        self.context_resolution_service = ContextResolutionService()
        self.vlm_verification_service = VlmVerificationService()
        self.cross_panel_merge_service = CrossPanelMergeService()
        self.rule_engine_service = LegalMetrologyRuleEngine()
        self.confidence_engine_service = ConfidenceEngine()
        self.evidence_engine_service = EvidenceEngine()
        self.compliance_decision_service = ComplianceDecisionEngine()
        self.audit_explainability_service = AuditExplainabilityService()

    def process_surface_text(
        self,
        lines: List[ExtractedLine],
        raw_transcript: str,
        surface: str = "Front (PDP)",
        image: Optional[Image.Image] = None
    ) -> Tuple[List[UniversalFieldObject], List[AuditExplanationDossier]]:
        """Processes lines from a single surface through the complete semantic understanding pipeline."""
        if not lines:
            return [], []

        # 1. Layout: Reading order & Visual prominence
        sorted_lines = self.layout_analysis_service.sort_reading_order(lines)
        table_rows = self.layout_analysis_service.detect_table_rows(sorted_lines)

        # 2. Section Detection (Shielding ingredients & directions)
        sections = self.section_detection_service.detect_sections(sorted_lines)

        # 3. Product Classification
        prod_class = self.product_classification_service.classify_product(raw_transcript, [l.text for l in lines])
        cat_name = prod_class.product_type or "Other Packaged Commodity"

        # 4. Raw Candidate Entity Extraction (No premature classification!)
        raw_candidates = self.entity_extraction_service.extract_candidates_from_lines(sorted_lines)

        universal_fields: List[UniversalFieldObject] = []

        # 5. Semantic Classification with Checks A-F
        for cand in raw_candidates:
            # Map candidate's line to its active section
            target_line = next((l for l in sorted_lines if l.line_index == cand.line_index), None)
            active_section = SectionType.PDP_HEADER
            if target_line:
                active_section = self.section_detection_service.map_line_to_section(target_line, sections)

            # Check visual prominence
            vis_hier = {}
            if target_line:
                vis_hier = self.layout_analysis_service.analyze_visual_hierarchy(target_line, sorted_lines)

            # Classify candidate
            u_field = self.semantic_classifier_service.classify_candidate(
                candidate=cand,
                section=active_section,
                surface=surface,
                product_category=cat_name,
                visual_prominence=vis_hier
            )

            # 6. VLM Verification if ambiguous
            if u_field.status == "NEEDS_REVIEW" and len(u_field.candidate_fields) > 1:
                crop = None
                if image and u_field.evidence_bbox:
                    crop = self.text_detection_service.crop_region(image, u_field.evidence_bbox)
                v_field, v_conf, v_reason = self.vlm_verification_service.verify_field_ambiguity(
                    cropped_image=crop,
                    target_text=u_field.raw_text,
                    surrounding_context=u_field.evidence_context,
                    candidate_fields=u_field.candidate_fields
                )
                if v_field != UniversalSemanticField.UNKNOWN:
                    u_field.selected_field = v_field
                    u_field.semantic_confidence = v_conf
                    u_field.reason += f" | {v_reason}"
                    u_field.status = "RESOLVED"

            # 7. Confidence Calibration
            calibrated_field = self.confidence_engine_service.calibrate_field(u_field)
            universal_fields.append(calibrated_field)

        # 8. Table understanding fields (e.g. nutrition tables)
        table_fields = self.context_resolution_service.resolve_table_rows_to_fields(table_rows, surface)
        for tf in table_fields:
            calibrated_tf = self.confidence_engine_service.calibrate_field(tf)
            universal_fields.append(calibrated_tf)

        # 9. Audit Dossier Explainability
        dossiers = self.audit_explainability_service.generate_field_dossiers(universal_fields)

        return universal_fields, dossiers


# Global singleton pipeline instance
_GLOBAL_PIPELINE: Optional[UniversalFieldPipeline] = None


def get_universal_pipeline() -> UniversalFieldPipeline:
    """Returns the singleton instance of the UniversalFieldPipeline."""
    global _GLOBAL_PIPELINE
    if _GLOBAL_PIPELINE is None:
        _GLOBAL_PIPELINE = UniversalFieldPipeline()
    return _GLOBAL_PIPELINE
