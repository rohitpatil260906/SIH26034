"""
Stage 9: Non-Destructive Evidence Highlighter Engine
====================================================
Highlights evidence regions on images while strictly preserving originals:
- Takes original image + original bounding box coordinates [x1, y1, x2, y2].
- Draws highlighted bounding box overlays on a copy of the image.
- Preserves original image, dimensions, and unenhanced original coordinates.
- Supports single or multiple evidence bounding boxes per violation.
"""

from typing import List, Dict, Any, Optional, Union
import numpy as np
import cv2


class EvidenceHighlighter:
    """Non-destructive evidence region highlighter."""

    @staticmethod
    def highlight_evidence(
        image: np.ndarray,
        bboxes: List[List[float]],
        color: tuple = (0, 0, 255),  # Red BGR
        thickness: int = 2,
        label: Optional[str] = None
    ) -> np.ndarray:
        """
        Draws bounding box overlays on a COPY of the image.
        Returns the highlighted image array while preserving the input array.
        """
        if image is None or image.size == 0:
            return image

        # Make a copy to preserve original image
        highlighted = image.copy()
        h, w = highlighted.shape[:2]

        for bbox in bboxes:
            if not bbox or len(bbox) < 4:
                continue

            x1, y1, x2, y2 = [int(v) for v in bbox[:4]]

            # Clamp coordinates to image boundaries
            x1 = max(0, min(w - 1, x1))
            y1 = max(0, min(h - 1, y1))
            x2 = max(0, min(w - 1, x2))
            y2 = max(0, min(h - 1, y2))

            cv2.rectangle(highlighted, (x1, y1), (x2, y2), color, thickness)

            if label:
                cv2.putText(
                    highlighted,
                    label,
                    (x1, max(y1 - 5, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1,
                    cv2.LINE_AA
                )

        return highlighted
