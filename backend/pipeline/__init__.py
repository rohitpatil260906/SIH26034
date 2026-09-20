"""
Stage 10: Master Pipeline Orchestration Module
==============================================
Master entry point for LM-COMPASS Stage 10:
- Orchestrates end-to-end 10-stage execution pipeline.
- Manages scan creation, image registration, pipeline execution, and final result synthesis.
- Enforces pipeline state transitions, error isolation, retries, and operational audit trail.
"""

from .pipeline_models import (
    Stage10StageProgress,
    Stage10ProcessingMetadata,
    Stage10AuditEvent,
    Stage10FinalResult,
    Stage10ScanStatusResponse,
    Stage10RunRequest,
    Stage10RunResponse
)
from .pipeline_state import PipelineState, PipelineStateValidator
from .pipeline_errors import (
    PipelineException,
    StageExecutionError,
    StateTransitionError,
    ProductIsolationError
)
from .pipeline_events import AuditTrailLogger
from .pipeline_runner import PipelineRunner
from .orchestrator import Stage10PipelineOrchestrator

__all__ = [
    "Stage10PipelineOrchestrator",
    "PipelineRunner",
    "AuditTrailLogger",
    "PipelineState",
    "PipelineStateValidator",
    "PipelineException",
    "StageExecutionError",
    "StateTransitionError",
    "ProductIsolationError",
    "Stage10StageProgress",
    "Stage10ProcessingMetadata",
    "Stage10AuditEvent",
    "Stage10FinalResult",
    "Stage10ScanStatusResponse",
    "Stage10RunRequest",
    "Stage10RunResponse"
]
