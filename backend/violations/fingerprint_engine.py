"""
Stage 9: Violation Fingerprint Engine
=====================================
Generates deterministic fingerprints for violations:
- Uniquely identifies violations using product_id + rule_id + violation_type + issue_identity.
- Prevents duplicate violation records when the same violation appears across multiple panels.
"""

import hashlib
from typing import Optional


class FingerprintEngine:
    """Generates deterministic hashes for violation deduplication."""

    @staticmethod
    def generate_fingerprint(
        product_id: str,
        rule_id: str,
        violation_type: str,
        issue_identity: Optional[str] = None
    ) -> str:
        """
        Creates a SHA-256 deterministic fingerprint string.
        Format: sha256(product_id:rule_id:violation_type:issue_identity)
        """
        raw_key = f"{product_id.strip()}:{rule_id.strip()}:{violation_type.strip()}:{(issue_identity or '').strip().lower()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:32]
