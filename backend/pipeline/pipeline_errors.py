"""
Stage 10: Custom Pipeline Exceptions
"""

class PipelineException(Exception):
    """Base exception for Stage 10 pipeline errors."""
    pass

class StageExecutionError(PipelineException):
    """Raised when an individual pipeline stage encounters an unrecoverable failure."""
    def __init__(self, stage_name: str, message: str):
        self.stage_name = stage_name
        self.message = message
        super().__init__(f"[{stage_name}] {message}")

class StateTransitionError(PipelineException):
    """Raised when an invalid pipeline state transition is attempted."""
    def __init__(self, from_state: str, to_state: str):
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(f"Invalid pipeline transition from '{from_state}' to '{to_state}'")

class ProductIsolationError(PipelineException):
    """Raised when product data boundary violation occurs."""
    pass
