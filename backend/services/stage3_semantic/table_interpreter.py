"""
Stage 3: Table Structure Semantic Interpreter
=============================================
Understands tabular key-value relationships in nutrition facts, specifications,
and analysis tables detected in Stage 2:
- "Serving Size | 50 g" -> field = SERVING_SIZE, value = "50 g" (NOT NET_QUANTITY)
- "Energy | 480 kcal" -> field = NUTRITION_INFORMATION
- Preserves cell coordinates and relationship confidence
"""

import re
import uuid
from typing import List, Tuple, Dict, Any, Optional
from ...models import (
    Stage2TableInfo,
    Stage3SemanticField,
    Stage3Relationship,
    Stage3CandidateType
)


class TableInterpretationService:
    """Interprets structural cells within detected tables into semantic fields."""

    def interpret_tables(
        self,
        tables: List[Stage2TableInfo]
    ) -> Tuple[List[Stage3SemanticField], List[Stage3Relationship]]:
        """Parses rows and columns of tables into semantic fields and relationships."""
        fields: List[Stage3SemanticField] = []
        relationships: List[Stage3Relationship] = []

        for tbl in tables:
            # Group cells by row_index
            rows: Dict[int, Dict[int, str]] = {}
            row_bboxes: Dict[int, List[float]] = {}
            row_orig_bboxes: Dict[int, List[float]] = {}

            for cell in tbl.cells:
                r, c = cell.row_index, cell.col_index
                if r not in rows:
                    rows[r] = {}
                rows[r][c] = (cell.text or "").strip()
                if r not in row_bboxes and cell.bbox:
                    row_bboxes[r] = cell.bbox
                if r not in row_orig_bboxes and cell.original_bbox:
                    row_orig_bboxes[r] = cell.original_bbox

            # Evaluate row pairs (e.g. Col 0 is Header, Col 1 is Value)
            for r, cols in sorted(rows.items()):
                if len(cols) < 2:
                    continue

                col0_text = cols.get(0, "")
                col1_text = cols.get(1, "")

                if not col0_text or not col1_text:
                    continue

                c0_lower = col0_text.lower()

                # A. Serving Size Row
                if "serving size" in c0_lower or "per serving" in c0_lower:
                    field_id = f"FLD-{uuid.uuid4().hex[:6].upper()}"
                    fields.append(
                        Stage3SemanticField(
                            field_id=field_id,
                            semantic_type="SERVING_SIZE",
                            value=col1_text,
                            normalized_value=col1_text,
                            heading_text=col0_text,
                            bbox=row_bboxes.get(r, tbl.bbox),
                            original_bbox=row_orig_bboxes.get(r, tbl.original_bbox),
                            ocr_confidence=0.95,
                            semantic_confidence=0.98,
                            relationship_confidence=0.99,
                            status="CONFIRMED",
                            candidate_types=[
                                Stage3CandidateType(type="SERVING_SIZE", confidence=0.98),
                                Stage3CandidateType(type="NET_QUANTITY", confidence=0.02)
                            ]
                        )
                    )
                    relationships.append(
                        Stage3Relationship(
                            relationship_id=f"REL-{uuid.uuid4().hex[:6].upper()}",
                            field_type="SERVING_SIZE",
                            heading_text=col0_text,
                            value_text=col1_text,
                            relationship_confidence=0.99,
                            association_type="TABLE_CELL"
                        )
                    )

                # B. Nutrition Row (e.g., Energy, Protein, Fat, Carbohydrate)
                elif any(k in c0_lower for k in ("energy", "protein", "carbohydrate", "fat", "sugar", "sodium", "nutrient")):
                    field_id = f"FLD-{uuid.uuid4().hex[:6].upper()}"
                    fields.append(
                        Stage3SemanticField(
                            field_id=field_id,
                            semantic_type="NUTRITION_INFORMATION",
                            value=f"{col0_text}: {col1_text}",
                            normalized_value=f"{col0_text}: {col1_text}",
                            heading_text=col0_text,
                            bbox=row_bboxes.get(r, tbl.bbox),
                            original_bbox=row_orig_bboxes.get(r, tbl.original_bbox),
                            ocr_confidence=0.95,
                            semantic_confidence=0.96,
                            relationship_confidence=0.98,
                            status="CONFIRMED",
                            candidate_types=[
                                Stage3CandidateType(type="NUTRITION_INFORMATION", confidence=0.96)
                            ]
                        )
                    )

        return fields, relationships
