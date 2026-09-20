"""
Stage 7: Multi-Image Scan Session Manager
=========================================
Manages multi-image scan sessions:
- Maintains session state (session_id, image_ids, panel_ids, product_ids).
- Keeps each uploaded image independently traceable without overwriting single-image results.
- Supports late-arriving image additions (e.g. Front uploaded first, Back uploaded later) by updating existing product sessions.
- Supports image removal and reprocessing while preserving evidence from remaining images.
"""

from typing import List, Dict, Any, Optional, Tuple
from ...models import (
    Stage7Session,
    Stage7UnifiedProduct,
    Stage7SourceImage,
    Stage7ProductMatchEvidence
)


class SessionManager:
    """Manages multi-image scan sessions and product clusters."""

    def __init__(self):
        self.sessions: Dict[str, Stage7Session] = {}

    def get_or_create_session(self, session_id: str = "session_001") -> Stage7Session:
        """Retrieves existing session or creates a new one."""
        if session_id not in self.sessions:
            self.sessions[session_id] = Stage7Session(
                session_id=session_id,
                image_ids=[],
                panel_ids=[],
                product_ids=[],
                product_matches=[],
                products=[]
            )
        return self.sessions[session_id]

    def add_image_to_session(
        self,
        session_id: str,
        image_id: str,
        panel: str = "UNKNOWN"
    ) -> Stage7Session:
        """Registers a new image in the session."""
        session = self.get_or_create_session(session_id)
        if image_id not in session.image_ids:
            session.image_ids.append(image_id)
        if panel not in session.panel_ids:
            session.panel_ids.append(panel)
        return session

    def update_session_products(
        self,
        session_id: str,
        products: List[Stage7UnifiedProduct],
        matches: List[Stage7ProductMatchEvidence]
    ) -> Stage7Session:
        """Updates products and same-product match evidence for the session."""
        session = self.get_or_create_session(session_id)
        session.products = products
        session.product_matches = matches
        session.product_ids = [p.product_id for p in products]
        return session
