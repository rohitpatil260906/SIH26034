"""
Stage 10: End-to-End Audit Trail Logger
=======================================
Records operational audit events for pipeline execution tracking:
- Records scan creation, image upload, stage execution, rule evaluation, violation generation, and finalization.
- Strictly operational audit logging (no hidden chain-of-thought or raw internal debug dumps).
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from .pipeline_models import Stage10AuditEvent


class AuditTrailLogger:
    """Manages operational audit events for a scan session."""

    def __init__(self, scan_id: str):
        self.scan_id = scan_id
        self._events: List[Stage10AuditEvent] = []

    def log_event(
        self,
        stage: str,
        event_type: str,
        status: str,
        product_id: Optional[str] = None,
        relevant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Stage10AuditEvent:
        """Logs an operational audit event."""
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        event = Stage10AuditEvent(
            event_id=event_id,
            scan_id=self.scan_id,
            product_id=product_id,
            stage=stage,
            event_type=event_type,
            status=status,
            relevant_id=relevant_id,
            details=details or {},
            timestamp=datetime.now().isoformat()
        )
        self._events.append(event)
        return event

    def get_events(self) -> List[Stage10AuditEvent]:
        """Returns all recorded audit events."""
        return list(self._events)
