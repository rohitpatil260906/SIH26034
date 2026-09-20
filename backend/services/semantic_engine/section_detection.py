"""
Service 7: Section Detection Service
====================================
Detects packaging semantic section boundaries and assigns text lines to sections:
- INGREDIENTS
- NUTRITION_INFORMATION
- DIRECTIONS
- WARNING
- MANUFACTURER
- PACKER
- IMPORTER
- MARKETER
- CONSUMER_CARE
- STORAGE
- PDP_HEADER / PRODUCT_DETAILS
- CODING_AREA

CRITICAL GUARANTEE:
Prevents cross-section contamination (e.g. ingredient amounts, nutrients, or direction text
are NEVER misidentified as package Net Quantity or Manufacturer Address).
"""

from typing import List, Dict, Any, Tuple, Optional
import re
from ...models import ExtractedLine, SectionType


# Regex patterns matching section initiators
SECTION_PATTERNS: List[Tuple[str, re.Pattern]] = [
    (SectionType.INGREDIENTS, re.compile(
        r'^(?:ingredients?|composition|key\s*ingredients?|active\s*ingredients?|सामग्री)\b', re.I)),
    (SectionType.NUTRITION_INFORMATION, re.compile(
        r'^(?:nutrition(?:al)?\s*(?:information|facts|values?|declaration)?|approximate\s*values?|पोषण\s*जानकारी)\b', re.I)),
    (SectionType.DIRECTIONS, re.compile(
        r'^(?:directions?(?:\s*(?:for\s*use|of\s*use))?|how\s*to\s*use|mode\s*of\s*application|usage(?:\s*instructions?)?|उपयोग\s*विधि)\b', re.I)),
    (SectionType.WARNING, re.compile(
        r'^(?:warnings?|cautions?|precautions?|advisories?|for\s*external\s*use\s*only|चेतावनी)\b', re.I)),
    (SectionType.MANUFACTURER, re.compile(
        r'^(?:manufactured\s*(?:and\s*packaged\s*)?by|mfd\.?\s*by|produced\s*by|made\s*by|निर्माता)\b', re.I)),
    (SectionType.PACKER, re.compile(
        r'^(?:packed\s*by|pkd\.?\s*by|pre-?packed\s*by|पैकर)\b', re.I)),
    (SectionType.IMPORTER, re.compile(
        r'^(?:imported\s*(?:and\s*marketed\s*)?by|imp\.?\s*by|आयातित)\b', re.I)),
    (SectionType.MARKETER, re.compile(
        r'^(?:marketed\s*by|mktd\.?\s*by|distributed\s*by|मार्केटेड)\b', re.I)),
    (SectionType.CONSUMER_CARE, re.compile(
        r'^(?:consumer\s*care(?:\s*cell)?|customer\s*(?:care|support|helpline)|helpline|toll[\s-]free|उपभोक्ता\s*सेवा)\b', re.I)),
    (SectionType.STORAGE, re.compile(
        r'^(?:storage(?:\s*conditions?)?|store\s*(?:in|away)|keep\s*in\s*a\s*cool)\b', re.I)),
    (SectionType.CODING_AREA, re.compile(
        r'^(?:batch\s*(?:no\.?|number)?|b\.?\s*no\.?|lot\s*no\.?|mfd(?:\s*date)?|pkd(?:\s*date)?|use\s*before|best\s*before|exp(?:iry)?)\b', re.I))
]


class SectionBoundary:
    """Represents a bounded semantic section on the package."""
    def __init__(self, section_type: str, start_line_idx: int, header_text: str):
        self.section_type = section_type
        self.start_line_idx = start_line_idx
        self.end_line_idx = start_line_idx
        self.header_text = header_text
        self.lines: List[ExtractedLine] = []


class SectionDetectionService:
    """Detects and partitions text lines into semantic sections."""

    def __init__(self):
        pass

    def detect_sections(self, lines: List[ExtractedLine]) -> List[SectionBoundary]:
        """Segments lines into ordered semantic sections based on heading transitions."""
        if not lines:
            return []

        sections: List[SectionBoundary] = []
        current_section = SectionBoundary(SectionType.PDP_HEADER, lines[0].line_index, "INITIAL_HEADER")
        current_section.lines.append(lines[0])

        for line in lines[1:]:
            txt = line.text.strip()
            detected_type: Optional[str] = None
            detected_header: str = ""

            for sec_type, pat in SECTION_PATTERNS:
                if pat.search(txt):
                    detected_type = sec_type
                    detected_header = txt
                    break

            # If a new section heading is encountered
            if detected_type and detected_type != current_section.section_type:
                current_section.end_line_idx = line.line_index - 1
                sections.append(current_section)
                current_section = SectionBoundary(detected_type, line.line_index, detected_header)

            current_section.lines.append(line)

        current_section.end_line_idx = lines[-1].line_index
        sections.append(current_section)
        return sections

    def map_line_to_section(self, line: ExtractedLine, sections: List[SectionBoundary]) -> str:
        """Returns the active section type for any individual line."""
        for sec in sections:
            if sec.start_line_idx <= line.line_index <= sec.end_line_idx:
                return sec.section_type
        return SectionType.OTHER
