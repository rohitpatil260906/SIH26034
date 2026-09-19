"""
Service 3: Panel Detection Service
==================================
Identifies package surfaces and panels:
- Principal Display Panel (Front/PDP)
- Back Panel (Information Panel)
- Side Panels
- Coding Area / Base / Flap / Crimp
- Estimates surface area in cm² for Rule 5 / Table 1 statutory font height checks.
"""

from typing import Dict, Any, Optional, List
from PIL import Image

from ...models import BoundingBox


class PanelDetectionService:
    """Detects and characterizes packaging panels."""

    PANEL_PDP = "Front (PDP)"
    PANEL_BACK = "Back Panel"
    PANEL_SIDE = "Side Panel"
    PANEL_CODING = "Coding Area"
    PANEL_TOP_BOTTOM = "Top/Bottom"
    PANEL_OUTER = "Outer Carton"

    def __init__(self, default_pdp_area_cm2: float = 120.0):
        self.default_pdp_area_cm2 = default_pdp_area_cm2

    def classify_panel(
        self,
        image: Optional[Image.Image] = None,
        surface_hint: Optional[str] = None,
        text_lines: Optional[List[str]] = None
    ) -> str:
        """Determines the packaging surface/panel from visual and textual cues."""
        if surface_hint:
            hint_lower = surface_hint.lower()
            if "pdp" in hint_lower or "front" in hint_lower:
                return self.PANEL_PDP
            if "back" in hint_lower:
                return self.PANEL_BACK
            if "side" in hint_lower:
                return self.PANEL_SIDE
            if "code" in hint_lower or "stamp" in hint_lower or "bottom" in hint_lower or "crimp" in hint_lower:
                return self.PANEL_CODING
            if "top" in hint_lower:
                return self.PANEL_TOP_BOTTOM
            if "outer" in hint_lower or "carton" in hint_lower:
                return self.PANEL_OUTER

        if text_lines:
            joined = " ".join(text_lines).lower()
            # If tiny text snippet with only batch, mfd, mrp
            if len(text_lines) <= 6 and ("b.no" in joined or "mrp" in joined or "mfd" in joined) and ("manufactured by" not in joined):
                return self.PANEL_CODING
            # If dense with ingredients, instructions, manufacturer
            if "ingredient" in joined or "manufactured by" in joined or "directions" in joined:
                return self.PANEL_BACK

        return self.PANEL_PDP

    def estimate_panel_area_cm2(
        self,
        image: Optional[Image.Image] = None,
        known_dpi: float = 300.0
    ) -> float:
        """Estimates panel surface area in cm² for Rule 5 / Table 1 calculation."""
        if image is None:
            return self.default_pdp_area_cm2

        width_px, height_px = image.size
        # Approximate assuming typical smartphone label capture (approx 150-300 dpi)
        # 1 inch = 2.54 cm
        width_cm = (width_px / known_dpi) * 2.54
        height_cm = (height_px / known_dpi) * 2.54
        area_cm2 = width_cm * height_cm
        return max(15.0, min(1500.0, round(area_cm2, 2)))
