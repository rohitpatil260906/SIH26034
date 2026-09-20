"""
Stage 4: Company & Organization Resolver Service
================================================
Extracts and validates commercial corporate names:
- Corporate indicators (Pvt Ltd, Ltd, LLP, Inc, Corporation, Industries, Foods, etc.)
- Partial entity detection (e.g., "...Consumer Products Pvt Ltd" -> partial_entity = True, no hallucination)
- OCR garbage filter (e.g., "AKMI 0| HA", "- a — pe—— -", "Xx_9@@" are rejected)
"""

import re
from typing import Dict, Any, Optional, Tuple, List


class CompanyResolverService:
    """Extracts, validates, and normalizes company and corporate entity names."""

    # Corporate indicators
    CORP_INDICATOR_REGEX = re.compile(
        r'\b(?:p[uvt]+[\.\s]*ltd\.?|pvt\.?\s*ltd\.?|private\s+limited|ltd\.?|limited|llp|inc\.?|corp\.?|corporation|industries|enterprises|laboratories|labs|foods|pharmaceuticals|pharma|cosmetics|confectionery|beverages|products|manufacturing|mfg|international|company|co\.)\b',
        re.I
    )

    # Specific full corporate suffix for clean boundaries
    CORP_SUFFIX_REGEX = re.compile(
        r'\b(?:p[uvt]+[\.\s]*ltd\.?|pvt\.?\s*ltd\.?|private\s+limited|ltd\.?|limited|llp|inc\.?|corp\.?|corporation)\b',
        re.I
    )

    # Garbage / unreadable OCR patterns
    GARBAGE_PATTERNS = [
        re.compile(r'^[\W_]+$'),                       # Only non-alphanumeric punctuation/underscores
        re.compile(r'^[a-z0-9_]{1,3}[@|#]{1,3}', re.I), # Strange punctuation mixes like "Xx_9@@"
        re.compile(r'[|\\/_~—–]{2,}'),                 # Repeated slashes/bars/dashes
        re.compile(r'^(?:[a-z]\s+){3,}[a-z]$', re.I),   # Disjointed single letters like "a — pe—— -"
    ]

    def is_ocr_garbage(self, text: str) -> bool:
        """Determines if text is low-quality OCR noise or unreadable artifacts."""
        if not text or len(text.strip()) < 3:
            return True

        clean = text.strip()
        
        # Check against specific noise patterns
        for pat in self.GARBAGE_PATTERNS:
            if pat.search(clean):
                return True

        # Check alphanumeric ratio
        alnum_chars = sum(1 for c in clean if c.isalnum())
        total_chars = len(clean)
        if total_chars > 0 and (alnum_chars / total_chars) < 0.50:
            return True

        # Check if words are mostly unpronounceable gibberish with non-standard characters
        words = clean.split()
        if len(words) >= 2:
            # Check for strings like "AKMI 0| HA"
            pipe_or_symbols = sum(1 for w in words if any(c in "|_~@#$%^&*+=\\" for c in w))
            if pipe_or_symbols >= len(words) / 2:
                return True

        return False

    def is_partial_name(self, text: str) -> bool:
        """Checks if company name has an explicit truncation indicator (e.g. leading ellipsis)."""
        clean = text.strip()
        if clean.startswith("...") or clean.startswith("…") or clean.startswith(".."):
            return True
        return False

    def extract_company_candidate(self, text: str) -> Tuple[Optional[str], bool, bool, float]:
        """Extracts a company name candidate from text.
        
        Returns:
            (cleaned_name, is_partial, is_garbage, confidence)
        """
        if not text:
            return None, False, False, 0.0

        clean = text.strip()

        # 1. Check garbage
        if self.is_ocr_garbage(clean):
            return None, False, True, 0.0

        # 2. Check partial
        partial = self.is_partial_name(clean)
        clean_text = re.sub(r'^(?:\.{2,}|…)\s*', '', clean).strip()

        # 3. Check for corporate indicator
        has_corp = self.CORP_INDICATOR_REGEX.search(clean_text) is not None
        if not has_corp:
            return None, False, False, 0.0

        # Extract the company name substring up to and including the corporate indicator
        # e.g., "Golden Bake Foods Pvt Ltd"
        conf = 0.95 if self.CORP_SUFFIX_REGEX.search(clean_text) else 0.80
        if partial:
            conf = 0.75

        return clean_text, partial, False, conf
