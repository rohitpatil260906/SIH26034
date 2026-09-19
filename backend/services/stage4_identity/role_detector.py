"""
Stage 4: Role Detection Service
===============================
Recognizes explicit statutory corporate role labels on packaging:
- Manufactured By / At / For, Mfg By, Mfd By -> MANUFACTURER
- Packed By / At / For, Packer, Pkd By -> PACKER
- Marketed By / For, Mkt By -> MARKETER
- Imported By / For, Imp By -> IMPORTER
- Distributed By, Distributor -> DISTRIBUTOR
- Sold By -> SELLER
- Owned By -> OWNER
- License Holder / Licensed By -> LICENSE_HOLDER
- Composite roles (Manufactured & Marketed By, Manufactured/Packed By)

RULE: Use the exact visible wording as evidence.
Do NOT infer a legal role from the company name alone.
"""

import re
from typing import Dict, Any, Optional, Tuple, List


class RoleDetectionService:
    """Detects explicit commercial role indicators from text lines or headings."""

    # Role regex mapping (ordered by specificity)
    ROLE_PATTERNS = [
        # Composite roles
        (re.compile(r'\b(?:manufactured\s+(?:and|&)\s+marketed\s+by|mfg\s*(?:and|&)\s*mkt\s*by)\b', re.I), "MANUFACTURER_AND_MARKETER"),
        (re.compile(r'\b(?:manufactured\s*[\/\&]\s*packed\s+by|mfg\s*[\/\&]\s*pkd\s+by)\b', re.I), "MANUFACTURER_AND_PACKER"),
        (re.compile(r'\b(?:importer\s*[\/\&]\s*distributor|imported\s+(?:and|&)\s+distributed\s+by)\b', re.I), "IMPORTER_AND_DISTRIBUTOR"),
        
        # Single statutory roles
        (re.compile(r'\b(?:manufactured\s+by|manufactured\s+at|manufactured\s+for|mfg\.?\s*by|mfd\.?\s*by|mfg\s+at|mfd\s+at|(?:[il1]+[a-z]*anu[a-z]*|mfg|mfd|ilg|mfc)[a-z]*\s*(?:by|at|for|e|:)?)\b', re.I), "MANUFACTURER"),
        (re.compile(r'\b(?:packed\s+by|packed\s+at|packed\s+for|packer|pkd\.?\s*by|pkd\s+at|(?:pkd|pck)[a-z]*\s*(?:by|at)?)\b', re.I), "PACKER"),
        (re.compile(r'\b(?:marketed\s+by|marketed\s+for|mkt\.?\s*by|mktg\.?\s*by|(?:mkt|mktg)[a-z]*\s*(?:by|for)?)\b', re.I), "MARKETER"),
        (re.compile(r'\b(?:imported\s+by|imported\s+for|imp\.?\s*by|importer|(?:imp|impt)[a-z]*\s*(?:by|for)?)\b', re.I), "IMPORTER"),
        (re.compile(r'\b(?:distributed\s+by|distributor)\b', re.I), "DISTRIBUTOR"),
        (re.compile(r'\b(?:sold\s+by|seller)\b', re.I), "SELLER"),
        (re.compile(r'\b(?:owned\s+by|trademark\s+owned\s+by|brand\s+owned\s+by)\b', re.I), "OWNER"),
        (re.compile(r'\b(?:license\s+holder|licensed\s+by|under\s+licen[sc]e\s+(?:from|of))\b', re.I), "LICENSE_HOLDER")
    ]

    def detect_role_from_text(self, text: str) -> Tuple[Optional[str], Optional[str], float]:
        """Detects if a line or heading contains an explicit role label.
        
        Returns:
            (role, matched_label, confidence)
        """
        if not text:
            return None, None, 0.0

        for pattern, role in self.ROLE_PATTERNS:
            match = pattern.search(text)
            if match:
                matched_label = match.group(0).strip()
                return role, matched_label, 0.98

        return None, None, 0.0

    def strip_role_prefix(self, text: str) -> str:
        """Strips the statutory role prefix from a line leaving the organization name."""
        cleaned = text
        for pattern, _ in self.ROLE_PATTERNS:
            cleaned = pattern.sub('', cleaned)
        
        # Strip trailing colon, hyphens, and whitespace
        cleaned = re.sub(r'^[\s:\-–—]+', '', cleaned).strip()
        return cleaned
