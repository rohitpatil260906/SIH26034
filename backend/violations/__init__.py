"""
Stage 9: Violation & Evidence Engine Module
===========================================
Master entry point for LM-COMPASS Stage 9:
- Consumes Stage 8 verified rule evaluations.
- Generates auditable, evidence-backed violation records.
- Deduplicates violations via FingerprintEngine and DeduplicationEngine.
- Generates review queue items via ReviewQueueEngine.
- Highlights evidence regions via EvidenceHighlighter.
"""

from .violation_models import (
    Stage9EvidenceItem,
    Stage9Violation,
    Stage9ReviewItem,
    Stage9ViolationSummary,
    Stage9ProductViolationResult,
    Stage9Request,
    Stage9Response
)
from .violation_engine import Stage9ViolationEngine
from .fingerprint_engine import FingerprintEngine
from .evidence_highlighter import EvidenceHighlighter
from .deduplication_engine import DeduplicationEngine
from .review_queue_engine import ReviewQueueEngine

__all__ = [
    "Stage9ViolationEngine",
    "FingerprintEngine",
    "EvidenceHighlighter",
    "DeduplicationEngine",
    "ReviewQueueEngine",
    "Stage9EvidenceItem",
    "Stage9Violation",
    "Stage9ReviewItem",
    "Stage9ViolationSummary",
    "Stage9ProductViolationResult",
    "Stage9Request",
    "Stage9Response"
]
