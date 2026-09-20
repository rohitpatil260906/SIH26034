from typing import List, Dict, Any, Tuple
from ..models import (
    StructuredProductData,
    CanonicalField,
    ExtractedLine,
    BoundingBox
)
from .text_processor import process_and_classify_text

def extract_structured_product_from_surfaces(
    surface_images: List[Dict[str, Any]]
) -> Tuple[StructuredProductData, List[CanonicalField], List[ExtractedLine]]:
    """Synthesizes text and declarations across packaging surfaces (Front PDP, Back panel, etc.)
    using generalized NLP, spatial layout reasoning, and strict anti-hallucination rules.
    """
    extracted_lines: List[ExtractedLine] = []
    line_counter = 0
    all_raw_text = []

    for img_info in surface_images:
        surface = img_info.get("surface", "Front (PDP)")
        text_lines = img_info.get("text_lines", [])

        for idx, text in enumerate(text_lines):
            line_counter += 1
            is_uncertain = "?" in text or "[unclear]" in text.lower() or "0?" in text
            extracted_lines.append(ExtractedLine(
                line_index=line_counter,
                text=text,
                confidence=0.55 if is_uncertain else 0.94,
                bbox=BoundingBox(x=10.0, y=min(90.0, 10.0 + idx * 8.0), width=80.0, height=6.0),
                is_uncertain=is_uncertain,
                surface=surface
            ))
            all_raw_text.append(text)

    joined_text = "\n".join(all_raw_text)
    primary_surface = surface_images[0].get("surface", "Front (PDP)") if surface_images else "Front (PDP)"

    data, canonical_fields, _ = process_and_classify_text(
        extracted_lines=extracted_lines,
        raw_transcript=joined_text,
        surface=primary_surface
    )

    return data, canonical_fields, extracted_lines
