import io
import math
import base64
from typing import Tuple, Dict, Any, Optional
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numpy as np

def decode_base64_image(data_uri_or_base64: str) -> Image.Image:
    """Decodes a base64 string or data URI into a PIL Image."""
    if ',' in data_uri_or_base64:
        data_uri_or_base64 = data_uri_or_base64.split(',', 1)[1]
    raw_bytes = base64.b64decode(data_uri_or_base64)
    return Image.open(io.BytesIO(raw_bytes)).convert("RGB")

def encode_image_to_base64(image: Image.Image, format: str = "JPEG") -> str:
    """Encodes a PIL Image to a base64 data URI."""
    buf = io.BytesIO()
    image.save(buf, format=format)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    mime = "image/jpeg" if format.upper() == "JPEG" else "image/png"
    return f"data:{mime};base64,{encoded}"

def calculate_laplacian_variance(gray_array: np.ndarray) -> float:
    """Computes the variance of the 3x3 Laplacian convolution for blur estimation."""
    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    # Simple discrete convolution
    from scipy.signal import convolve2d  # fallback if available
    try:
        lap = convolve2d(gray_array, kernel, mode='valid')
        return float(np.var(lap))
    except Exception:
        # Fast numpy slice approximation for Laplacian
        padded = np.pad(gray_array.astype(np.float32), 1, mode='edge')
        lap = (
            padded[:-2, 1:-1] +
            padded[2:, 1:-1] +
            padded[1:-1, :-2] +
            padded[1:-1, 2:] -
            4 * padded[1:-1, 1:-1]
        )
        return float(np.var(lap))

def analyze_image_quality(image: Image.Image) -> Dict[str, Any]:
    """Analyzes image sharpness, luminance, contrast, and overall OCR viability."""
    width, height = image.size
    megapixels = round((width * height) / 1_000_000, 2)
    
    gray = image.convert("L")
    arr = np.array(gray)
    
    mean_brightness = float(np.mean(arr))
    contrast_std = float(np.std(arr))
    laplacian_var = calculate_laplacian_variance(arr)
    
    is_blurred = laplacian_var < 100.0
    
    # Calculate weighted quality score (0-100)
    # Sharpness: optimal > 150 -> 40 pts
    sharpness_score = min(40.0, (laplacian_var / 150.0) * 40.0)
    # Brightness: optimal 100-180 -> 25 pts
    brightness_dist = abs(mean_brightness - 140.0)
    brightness_score = max(0.0, 25.0 - (brightness_dist / 140.0) * 25.0)
    # Contrast: optimal std > 45 -> 25 pts
    contrast_score = min(25.0, (contrast_std / 50.0) * 25.0)
    # Resolution: > 1.0 MP -> 10 pts
    res_score = min(10.0, (megapixels / 1.5) * 10.0)
    
    overall_score = int(round(sharpness_score + brightness_score + contrast_score + res_score))
    overall_score = max(10, min(99, overall_score))
    
    if overall_score >= 80:
        visibility = "Optimal - Clear text legibility across all panels"
    elif overall_score >= 60:
        visibility = "Moderate - Micro-text and crimp dates require multi-pass enhancement"
    else:
        visibility = "Degraded - Blur or uneven lighting detected"
        
    advisory = None
    if overall_score < 65 or is_blurred:
        advisory = "Image quality is low. AI enhancement will be attempted."
        
    return {
        "resolution_megapixels": megapixels,
        "blur_laplacian_variance": round(laplacian_var, 2),
        "is_blurred": is_blurred,
        "mean_brightness": round(mean_brightness, 1),
        "contrast_std_dev": round(contrast_std, 1),
        "text_visibility": visibility,
        "overall_quality_score": overall_score,
        "advisory": advisory
    }

def enhance_image_for_ocr(image: Image.Image) -> Dict[str, Image.Image]:
    """Generates enhanced transform passes for multi-pass OCR:
    1. Sharpened (Laplacian edge filter)
    2. Dynamic Contrast (Autocontrast + Percentile stretch)
    3. High-Contrast Binarized (Adaptive thresholding for dot-matrix/inkjet)
    """
    # 1. Edge sharpening
    sharpened = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    
    # 2. Dynamic Contrast Stretching
    gray = image.convert("L")
    contrasted_gray = ImageOps.autocontrast(gray, cutoff=2)
    enhancer = ImageEnhance.Contrast(image)
    dynamic_contrast = enhancer.enhance(1.4)
    
    # 3. High-contrast Sauvola / Adaptive Binarization simulation
    arr = np.array(contrasted_gray, dtype=np.float32)
    # Local window thresholding
    # Window size 25
    k = 0.2
    R = 128.0
    # Global Otsu-like fallback for speed & reliability
    threshold = np.mean(arr) - 0.2 * np.std(arr)
    binarized_arr = np.where(arr > threshold, 255, 0).astype(np.uint8)
    binarized = Image.fromarray(binarized_arr, mode="L")
    
    return {
        "original": image,
        "sharpened": sharpened,
        "contrast": dynamic_contrast,
        "binarized": binarized.convert("RGB")
    }
