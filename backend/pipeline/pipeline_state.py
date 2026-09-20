"""
Stage 10: Explicit Pipeline State Machine
=========================================
Manages pipeline state transitions and state validation:
States:
- CREATED
- IMAGE_RECEIVED
- QUALITY_ANALYZED
- IMAGE_RECOVERED
- OCR_COMPLETED
- SEMANTIC_ANALYSIS_COMPLETED
- PRODUCT_IDENTIFIED
- PRODUCT_SCHEMA_COMPLETED
- PANELS_MERGED
- RULES_EVALUATED
- VIOLATIONS_EVALUATED
- FINALIZED
- FAILED
- PARTIAL
- NEEDS_REVIEW
"""

from enum import Enum
from typing import List, Set


class PipelineState(str, Enum):
    CREATED = "CREATED"
    IMAGE_RECEIVED = "IMAGE_RECEIVED"
    QUALITY_ANALYZED = "QUALITY_ANALYZED"
    IMAGE_RECOVERED = "IMAGE_RECOVERED"
    OCR_COMPLETED = "OCR_COMPLETED"
    SEMANTIC_ANALYSIS_COMPLETED = "SEMANTIC_ANALYSIS_COMPLETED"
    PRODUCT_IDENTIFIED = "PRODUCT_IDENTIFIED"
    PRODUCT_SCHEMA_COMPLETED = "PRODUCT_SCHEMA_COMPLETED"
    PANELS_MERGED = "PANELS_MERGED"
    RULES_EVALUATED = "RULES_EVALUATED"
    VIOLATIONS_EVALUATED = "VIOLATIONS_EVALUATED"
    FINALIZED = "FINALIZED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class PipelineStateValidator:
    """Validates state transitions to prevent invalid pipeline skips."""

    VALID_TRANSITIONS: Set[tuple] = {
        (PipelineState.CREATED, PipelineState.IMAGE_RECEIVED),
        (PipelineState.IMAGE_RECEIVED, PipelineState.QUALITY_ANALYZED),
        (PipelineState.QUALITY_ANALYZED, PipelineState.IMAGE_RECOVERED),
        (PipelineState.IMAGE_RECOVERED, PipelineState.OCR_COMPLETED),
        (PipelineState.OCR_COMPLETED, PipelineState.SEMANTIC_ANALYSIS_COMPLETED),
        (PipelineState.SEMANTIC_ANALYSIS_COMPLETED, PipelineState.PRODUCT_IDENTIFIED),
        (PipelineState.PRODUCT_IDENTIFIED, PipelineState.PRODUCT_SCHEMA_COMPLETED),
        (PipelineState.PRODUCT_SCHEMA_COMPLETED, PipelineState.PANELS_MERGED),
        (PipelineState.PANELS_MERGED, PipelineState.RULES_EVALUATED),
        (PipelineState.RULES_EVALUATED, PipelineState.VIOLATIONS_EVALUATED),
        (PipelineState.VIOLATIONS_EVALUATED, PipelineState.FINALIZED),
        (PipelineState.VIOLATIONS_EVALUATED, PipelineState.NEEDS_REVIEW),
        (PipelineState.VIOLATIONS_EVALUATED, PipelineState.PARTIAL),

        # Transitions to failure/partial states from any active state
        (PipelineState.CREATED, PipelineState.FAILED),
        (PipelineState.IMAGE_RECEIVED, PipelineState.FAILED),
        (PipelineState.QUALITY_ANALYZED, PipelineState.FAILED),
        (PipelineState.IMAGE_RECOVERED, PipelineState.FAILED),
        (PipelineState.OCR_COMPLETED, PipelineState.FAILED),
        (PipelineState.SEMANTIC_ANALYSIS_COMPLETED, PipelineState.FAILED),
        (PipelineState.PRODUCT_IDENTIFIED, PipelineState.FAILED),
        (PipelineState.PRODUCT_SCHEMA_COMPLETED, PipelineState.FAILED),
        (PipelineState.PANELS_MERGED, PipelineState.FAILED),
        (PipelineState.RULES_EVALUATED, PipelineState.FAILED),

        (PipelineState.QUALITY_ANALYZED, PipelineState.PARTIAL),
        (PipelineState.OCR_COMPLETED, PipelineState.PARTIAL),
        (PipelineState.PRODUCT_IDENTIFIED, PipelineState.PARTIAL),
        (PipelineState.PANELS_MERGED, PipelineState.PARTIAL),
        (PipelineState.RULES_EVALUATED, PipelineState.NEEDS_REVIEW),
    }

    @classmethod
    def can_transition(cls, from_state: PipelineState, to_state: PipelineState) -> bool:
        if from_state == to_state:
            return True
        return (from_state, to_state) in cls.VALID_TRANSITIONS
