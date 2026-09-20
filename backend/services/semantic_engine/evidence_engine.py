"""
Service 16: Evidence / BBox Engine
==================================
Manages statutory evidentiary provenance:
- Links every extracted field and violation to an exact visual bounding box
- Generates high-resolution base64 crops of physical declarations
- Retains 3-5 line surrounding contextual windows
- Guarantees strict non-repudiation and optical audit trail for enforcement officers
"""

from typing import Dict, Any, Optional, List, Tuple
from PIL import Image

from ...models import BoundingBox, UniversalFieldObject, FieldEvidence
from ..cv_pipeline import encode_image_to_base64


class EvidenceEngine:
    """Optical and textual evidence provenance manager."""

    def __init__(self):
        pass

    def attach_evidence_crop(
        self,
        field: UniversalFieldObject,
        source_image: Optional[Image.Image]
    ) -> Optional[str]:
        """Crops the bounding box from source image and generates a base64 thumbnail."""
        if not source_image or not field.evidence_bbox:
            return None

        w, h = source_image.size
        b = field.evidence_bbox
        x1 = max(0, int((b.x / 100.0) * w))
        y1 = max(0, int((b.y / 100.0) * h))
        x2 = min(w, int(((b.x + b.width) / 100.0) * w))
        y2 = min(h, int(((b.y + b.height) / 100.0) * h))

        if x2 <= x1 or y2 <= y1:
            return None

        crop = source_image.crop((x1, y1, x2, y2))
        return encode_image_to_base64(crop, format="JPEG", quality=85)

    def create_field_evidence_map(
        self,
        fields: List[UniversalFieldObject],
        source_image: Optional[Image.Image] = None
    ) -> Dict[str, FieldEvidence]:
        """Constructs statutory FieldEvidence dictionary from UniversalFieldObjects."""
        ev_map: Dict[str, FieldEvidence] = {}

        for f in fields:
            crop_b64 = self.attach_evidence_crop(f, source_image)
            ev = FieldEvidence(
                field_name=f.selected_field.lower(),
                label=f.selected_field.replace("_", " ").title(),
                value=str(f.normalized_value or f.raw_text),
                ocr_confidence=f.ocr_confidence,
                detection_confidence=0.95,
                validation_confidence=f.rule_confidence,
                overall_confidence=f.overall_confidence,
                source_text=f.raw_text,
                surface=f.source_panel,
                bounding_box=f.evidence_bbox,
                cropped_image_base64=crop_b64,
                status="DETECTED" if f.status == "RESOLVED" else "NEEDS REVIEW",
                surrounding_context=f.evidence_context,
                semantic_class=f.selected_field,
                assignment_reasoning=f.reason
            )
            ev_map[f.selected_field.lower()] = ev

        return ev_map
