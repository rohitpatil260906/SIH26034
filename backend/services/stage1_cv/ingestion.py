"""
Stage 1: Image Ingestion and Validation Service
===============================================
Handles ingestion of packaging label images from camera, upload, or drag-and-drop:
- Validates file format (JPEG, JPG, PNG, WEBP)
- Traps and handles corrupted, truncated, or invalid byte streams safely (no crash)
- Extracts rich input metadata (dimensions, aspect ratio, byte size, format, timestamp)
- Preserves the original image in memory/storage while generating an isolated working copy
"""

import io
import uuid
import base64
from typing import Tuple, Dict, Any, Optional
from datetime import datetime
from PIL import Image, ImageOps, UnidentifiedImageError

from ...models import Stage1InputMetadata


SUPPORTED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}


class ImageIngestionService:
    """Safe ingestion and metadata extraction for packaging label images."""

    def __init__(self):
        pass

    def ingest_from_bytes(
        self,
        image_bytes: bytes,
        original_filename: str = "package.jpg",
        source: str = "upload"
    ) -> Tuple[Optional[Image.Image], Optional[Image.Image], Stage1InputMetadata, Optional[str]]:
        """Safely ingests image bytes, validates format, and creates metadata.
        
        Returns:
            (original_image, working_copy, metadata, error_message)
        """
        image_id = f"IMG-{uuid.uuid4().hex[:8].upper()}"
        file_size = len(image_bytes)

        if file_size < 32:
            metadata = Stage1InputMetadata(
                image_id=image_id,
                source=source,
                original_filename=original_filename,
                file_type="UNKNOWN",
                file_size_bytes=file_size,
                processing_status="REJECTED"
            )
            return None, None, metadata, "Corrupted image: file size too small or empty."

        try:
            stream = io.BytesIO(image_bytes)
            pil_img = Image.open(stream)
            pil_img.load()  # Force reading entire raster to detect truncated data
            fmt = (pil_img.format or "JPEG").upper()
        except (UnidentifiedImageError, OSError, ValueError) as e:
            metadata = Stage1InputMetadata(
                image_id=image_id,
                source=source,
                original_filename=original_filename,
                file_type="UNKNOWN",
                file_size_bytes=file_size,
                processing_status="REJECTED"
            )
            return None, None, metadata, f"Corrupted or unsupported image file: {str(e)}"

        if fmt not in SUPPORTED_FORMATS and fmt != "MPO":
            metadata = Stage1InputMetadata(
                image_id=image_id,
                source=source,
                original_filename=original_filename,
                file_type=fmt,
                file_size_bytes=file_size,
                processing_status="REJECTED"
            )
            return None, None, metadata, f"Unsupported file format '{fmt}'. Supported formats: JPEG, PNG, WEBP."

        w, h = pil_img.size
        aspect_ratio = round(float(w) / float(h), 3) if h > 0 else 1.0

        # Preserve the original image unaltered
        original_image = pil_img.copy()
        # Create an independent working copy for subsequent transformations
        working_copy = pil_img.copy()

        metadata = Stage1InputMetadata(
            image_id=image_id,
            source=source,
            original_filename=original_filename,
            file_type=fmt,
            file_size_bytes=file_size,
            width=w,
            height=h,
            aspect_ratio=aspect_ratio,
            orientation="NORMAL",
            capture_timestamp=datetime.utcnow().isoformat(),
            processing_status="SUCCESS"
        )

        return original_image, working_copy, metadata, None

    def ingest_from_base64(
        self,
        b64_string: str,
        original_filename: str = "package.jpg",
        source: str = "upload"
    ) -> Tuple[Optional[Image.Image], Optional[Image.Image], Stage1InputMetadata, Optional[str]]:
        """Decodes base64 image data (with or without data URI header) and ingests."""
        if not b64_string:
            metadata = Stage1InputMetadata(
                image_id=f"IMG-{uuid.uuid4().hex[:8].upper()}",
                source=source,
                original_filename=original_filename,
                file_type="UNKNOWN",
                file_size_bytes=0,
                processing_status="REJECTED"
            )
            return None, None, metadata, "Empty image data provided."

        clean_b64 = b64_string
        if "," in b64_string:
            clean_b64 = b64_string.split(",", 1)[1]

        try:
            raw_bytes = base64.b64decode(clean_b64)
        except Exception as e:
            metadata = Stage1InputMetadata(
                image_id=f"IMG-{uuid.uuid4().hex[:8].upper()}",
                source=source,
                original_filename=original_filename,
                file_type="UNKNOWN",
                file_size_bytes=0,
                processing_status="REJECTED"
            )
            return None, None, metadata, f"Base64 decoding failed: {str(e)}"

        return self.ingest_from_bytes(raw_bytes, original_filename=original_filename, source=source)
