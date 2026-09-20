"""
Stage 5: Multi-Variant Enhancement & Color Channel Optimization Engine
======================================================================
Produces condition-tailored enhancement branches:
- original
- grayscale
- contrast_enhanced
- clahe
- sharpened
- denoised
- adaptive_threshold
- upscaled
- glare_reduced
- shadow_corrected
- channel_optimized (RGB / HSV / LAB channel isolation)
Executes selective variant generation to ensure high performance without redundant compute.
"""

from typing import Dict, Any, List, Tuple, Optional
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import numpy as np
import cv2

from ..cv_pipeline import pil_to_cv2, cv2_to_pil, encode_image_to_base64
from .coordinate_mapper import CoordinateTransformChain


class GeneratedVariant:
    """Encapsulates an image variant, its chain, and generation metadata."""

    def __init__(
        self,
        variant_id: str,
        variant_type: str,
        image: Image.Image,
        chain: CoordinateTransformChain,
        source_variant: str = "original",
        parameters: Optional[Dict[str, Any]] = None
    ):
        self.variant_id = variant_id
        self.variant_type = variant_type
        self.image = image
        self.chain = chain
        self.source_variant = source_variant
        self.parameters = parameters or {}


class EnhancementEngine:
    """Selectively generates enhanced variants based on detected distortions."""

    def __init__(self):
        pass

    def evaluate_optimal_color_channel(self, cv_img: np.ndarray) -> Tuple[np.ndarray, str]:
        """Evaluates RGB, HSV, and LAB channels to select the channel maximizing text stroke contrast."""
        if len(cv_img.shape) != 3:
            return cv_img, "grayscale"

        b, g, r = cv2.split(cv_img)
        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
        l_chan, a_chan, b_chan = cv2.split(lab)

        # Measure text edge contrast via Laplacian variance on each channel
        channels = {
            "green_channel": g,
            "blue_channel": b,
            "red_channel": r,
            "hsv_value": v,
            "lab_luminance": l_chan
        }

        best_name = "lab_luminance"
        best_score = -1.0
        best_arr = l_chan

        for name, arr in channels.items():
            score = float(cv2.Laplacian(arr, cv2.CV_64F).var())
            if score > best_score:
                best_score = score
                best_name = name
                best_arr = arr

        return best_arr, best_name

    def generate_variants(
        self,
        base_image: Image.Image,
        base_chain: CoordinateTransformChain,
        distortions: List[str]
    ) -> List[GeneratedVariant]:
        """Selectively builds relevant enhancement variants.
        
        Args:
            base_image: Currently rectified / unwarped image
            base_chain: CoordinateTransformChain corresponding to base_image
            distortions: List of detected distortion condition tags
        """
        variants: List[GeneratedVariant] = []
        w, h = base_image.size
        cv_img = pil_to_cv2(base_image)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img

        # 1. Base Image (original or primary rectified)
        variants.append(
            GeneratedVariant(
                variant_id="var_base",
                variant_type="BASE_INPUT",
                image=base_image,
                chain=base_chain.clone(),
                source_variant="original"
            )
        )

        # 2. Grayscale (standard baseline for OCR)
        gray_pil = Image.fromarray(gray)
        variants.append(
            GeneratedVariant(
                variant_id="var_grayscale",
                variant_type="GRAYSCALE",
                image=gray_pil,
                chain=base_chain.clone(),
                source_variant="var_base"
            )
        )

        # 3. CLAHE (Local Contrast Adaptive Equalization)
        # Highly effective for low contrast, uneven lighting, shadows, and packaging glare
        clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
        clahe_gray = clahe.apply(gray)
        variants.append(
            GeneratedVariant(
                variant_id="var_clahe",
                variant_type="CLAHE",
                image=Image.fromarray(clahe_gray),
                chain=base_chain.clone(),
                source_variant="var_base",
                parameters={"clip_limit": 2.2}
            )
        )

        # 4. Sharpened (for blur or micro-text)
        if any(d in distortions for d in ["BLUR", "MOTION_BLUR", "LOW_RESOLUTION", "COMPRESSION_ARTIFACT"]):
            sharp_pil = base_image.filter(ImageFilter.UnsharpMask(radius=2, percent=160, threshold=2))
            variants.append(
                GeneratedVariant(
                    variant_id="var_sharpened",
                    variant_type="SHARPENED",
                    image=sharp_pil,
                    chain=base_chain.clone(),
                    source_variant="var_base"
                )
            )

        # 5. Denoised (for compression artifacts or noisy camera sensors)
        if any(d in distortions for d in ["COMPRESSION_ARTIFACT", "LOW_RESOLUTION", "UNDEREXPOSURE"]):
            denoised_cv = cv2.bilateralFilter(cv_img, 5, 35, 35)
            variants.append(
                GeneratedVariant(
                    variant_id="var_denoised",
                    variant_type="DENOISED",
                    image=cv2_to_pil(denoised_cv),
                    chain=base_chain.clone(),
                    source_variant="var_base"
                )
            )

        # 6. Adaptive Threshold (Sauvola / Gaussian local binarization)
        # Essential for dot-matrix inkjet dates and debossed packaging text
        adaptive_cv = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 7
        )
        variants.append(
            GeneratedVariant(
                variant_id="var_adaptive_thresh",
                variant_type="ADAPTIVE_THRESHOLD",
                image=Image.fromarray(adaptive_cv),
                chain=base_chain.clone(),
                source_variant="var_base"
            )
        )

        # 7. Upscaled variant (if low resolution or small print)
        if any(d in distortions for d in ["LOW_RESOLUTION"]) or max(w, h) < 1100:
            scale = 1.6
            up_w, up_h = int(w * scale), int(h * scale)
            up_cv = cv2.resize(cv_img, (up_w, up_h), interpolation=cv2.INTER_LANCZOS4)
            up_chain = base_chain.clone()
            up_chain.add_scale(scale, scale)
            variants.append(
                GeneratedVariant(
                    variant_id="var_upscaled",
                    variant_type="UPSCALED",
                    image=cv2_to_pil(up_cv),
                    chain=up_chain,
                    source_variant="var_base",
                    parameters={"scale_factor": scale}
                )
            )

        # 8. Optimal Color Channel
        opt_chan, chan_name = self.evaluate_optimal_color_channel(cv_img)
        variants.append(
            GeneratedVariant(
                variant_id="var_channel_opt",
                variant_type="CHANNEL_OPTIMIZED",
                image=Image.fromarray(opt_chan),
                chain=base_chain.clone(),
                source_variant="var_base",
                parameters={"channel": chan_name}
            )
        )

        return variants
