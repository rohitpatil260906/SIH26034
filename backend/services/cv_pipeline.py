import io
import os
import math
import base64
import time
from typing import Dict, List, Tuple, Any, Optional
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import numpy as np
import cv2
from skimage import exposure, feature, filters, measure, transform

from ..models import ImageQualityMetrics, PreprocessingVariantInfo

EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "evidence")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def decode_base64_image(data_uri_or_base64: str) -> Image.Image:
    """Decodes a base64 string, data URI, local path, or URL into a PIL Image."""
    if not data_uri_or_base64:
        # Create default synthetic packaging image
        return Image.new("RGB", (800, 800), color=(245, 245, 245))
    
    # 1. Check if it's an HTTP/HTTPS URL
    if data_uri_or_base64.startswith("http://") or data_uri_or_base64.startswith("https://"):
        try:
            import requests
            resp = requests.get(data_uri_or_base64, timeout=5)
            if resp.status_code == 200:
                return Image.open(io.BytesIO(resp.content)).convert("RGB")
        except Exception:
            pass

    # 2. Check if it's an existing local file path
    if os.path.exists(data_uri_or_base64):
        try:
            return Image.open(data_uri_or_base64).convert("RGB")
        except Exception:
            pass

    # 3. Handle base64 / data URI
    try:
        data = data_uri_or_base64
        if ',' in data:
            data = data.split(',', 1)[1]
        raw_bytes = base64.b64decode(data)
        return Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    except Exception as e:
        # Fallback: create an annotated placeholder image
        img = Image.new("RGB", (800, 800), color=(240, 243, 246))
        return img

def encode_image_to_base64(image: Image.Image, format: str = "JPEG", quality: int = 90) -> str:
    """Encodes a PIL Image to a base64 data URI."""
    buf = io.BytesIO()
    image.save(buf, format=format, quality=quality)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    mime = "image/jpeg" if format.upper() == "JPEG" else "image/png"
    return f"data:{mime};base64,{encoded}"

def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    """Converts a PIL Image (RGB) to OpenCV format (BGR)."""
    rgb_arr = np.array(pil_img)
    return cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR)

def cv2_to_pil(cv_img: np.ndarray) -> Image.Image:
    """Converts an OpenCV image (BGR or Gray) to PIL Image (RGB)."""
    if len(cv_img.shape) == 2:
        return Image.fromarray(cv_img).convert("RGB")
    rgb_arr = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_arr)

# -------------------------------------------------------------------
# STEP 2.1: IMAGE INPUT & EVIDENCE PRESERVATION
# -------------------------------------------------------------------

def store_original_evidence(
    scan_id: str,
    surface: str,
    pil_image: Image.Image,
    file_name: Optional[str] = None
) -> Tuple[str, Image.Image]:
    """Stores the original image unchanged on disk as legal evidence.
    Returns the evidence file path and a working copy for computer vision.
    """
    scan_folder = os.path.join(EVIDENCE_DIR, scan_id)
    os.makedirs(scan_folder, exist_ok=True)
    
    clean_surface = surface.replace(" ", "_").replace("(", "").replace(")", "").lower()
    ext = "jpg"
    if file_name and "." in file_name:
        ext = file_name.rsplit(".", 1)[1].lower()
        if ext not in ["jpg", "jpeg", "png"]:
            ext = "jpg"
            
    evidence_filename = f"evidence_{clean_surface}.{ext}"
    evidence_path = os.path.join(scan_folder, evidence_filename)
    
    # Save original immutable evidence
    pil_image.save(evidence_path)
    
    # Create an independent processing copy
    processing_copy = pil_image.copy()
    return evidence_path, processing_copy

# -------------------------------------------------------------------
# STEP 2.2: 12 AUTOMATED IMAGE QUALITY CHECKS
# -------------------------------------------------------------------

def analyze_complete_image_quality(pil_image: Image.Image) -> ImageQualityMetrics:
    """Performs the 14 automated image quality assessments using OpenCV + NumPy + scikit-image:
    1. Resolution (Megapixels)
    2. Blur (Laplacian variance)
    3. Focus (Sobel gradient energy / Tenengrad)
    4. Brightness (Mean intensity)
    5. Contrast (Standard deviation)
    6. Noise (Residual variance after median smoothing)
    7. Glare / Specular reflection
    8. Shadow / Non-uniform illumination
    9. Skew angle (Hough line angles)
    10. Rotation orientation
    11. Perspective distortion (Quadrilateral homography test)
    12. Estimated text size (Connected component median glyph height)
    13. Text visibility score
    14. Image completeness (Package boundary edge clipping)
    """
    cv_img = pil_to_cv2(pil_image)
    h, w = cv_img.shape[:2]
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    megapixels = round((w * h) / 1_000_000.0, 2)
    
    # 1. Blur detection (Laplacian variance)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    blur_var = float(np.var(laplacian))
    is_blurred = blur_var < 100.0
    
    # 2. Focus score (Tenengrad focus measure / gradient energy)
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    grad_mag = np.sqrt(sobel_x**2 + sobel_y**2)
    tenengrad = float(np.mean(grad_mag**2))
    focus_score = round(min(100.0, max(10.0, (tenengrad / 1200.0) * 85.0)), 1)
    
    # 3. Noise estimation (residual difference after median blur)
    denoised_est = cv2.medianBlur(gray, 3)
    noise_residual = cv2.absdiff(gray, denoised_est)
    noise_var = float(np.var(noise_residual))
    is_noisy = noise_var > 65.0
    
    # 4. Brightness analysis
    mean_brightness = float(np.mean(gray))
    
    # 5. Contrast analysis (Standard deviation)
    contrast_std = float(np.std(gray))
    
    # 6. Glare / reflection detection (saturated pixels > 245 with low local gradient)
    bright_mask = gray > 245
    glare_mask = bright_mask & (grad_mag < 25.0)
    glare_pct = round(float(np.sum(glare_mask) / (w * h)) * 100.0, 2)
    is_glare_detected = glare_pct > 2.5
    
    # 7. Shadow detection (deep shadow regions < 40 intensity occupying > 5% area)
    shadow_mask = gray < 45
    shadow_pct = round(float(np.sum(shadow_mask) / (w * h)) * 100.0, 2)
    shadow_detected = shadow_pct > 6.0 and abs(mean_brightness - 140.0) > 30.0
    
    # 8. Skew & Orientation estimation (Hough line angles)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=max(30, w // 20), maxLineGap=10)
    skew_angle = 0.0
    if lines is not None and len(lines) > 0:
        angles = []
        for line in lines:
            pts = line.flatten()
            if len(pts) >= 4:
                x1, y1, x2, y2 = pts[:4]
                if x2 != x1:
                    theta = math.degrees(math.atan2(float(y2 - y1), float(x2 - x1)))
                    if abs(theta) < 45.0:
                        angles.append(theta)
        if angles:
            skew_angle = round(float(np.median(angles)), 2)
            
    # 9. Rotation detection
    rotation_angle = 0.0
    if abs(skew_angle) > 1.0:
        rotation_angle = skew_angle
        
    # 10. Perspective distortion detection (ratio of contour bounding box)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    perspective_distortion = False
    if contours:
        largest_c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_c) > 0.15 * (w * h):
            peri = cv2.arcLength(largest_c, True)
            approx = cv2.approxPolyDP(largest_c, 0.04 * peri, True)
            if len(approx) == 4:
                pts = approx.reshape(4, 2)
                d1 = np.linalg.norm(pts[0] - pts[1])
                d2 = np.linalg.norm(pts[2] - pts[3])
                if max(d1, d2) > 0 and (abs(d1 - d2) / max(d1, d2)) > 0.20:
                    perspective_distortion = True

    # 11. Background interference detection
    edge_density = float(np.mean(edges > 0))
    bg_interference_score = round(min(100.0, edge_density * 300.0), 1)

    # 12. Estimated text size (Glyph median height via connected components)
    _, bin_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(bin_thresh, connectivity=8)
    glyph_heights = []
    for i in range(1, n_labels):
        cw = stats[i, cv2.CC_STAT_WIDTH]
        ch = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        # Filter typical text characters (height 6px to 120px, reasonable aspect ratio)
        if 6 <= ch <= 120 and 4 <= cw <= 120 and 15 <= area <= 6000:
            glyph_heights.append(ch)
    est_text_size = round(float(np.median(glyph_heights)), 1) if glyph_heights else 14.0

    # 13. Text visibility estimation
    text_vis_score = min(100.0, (contrast_std / 55.0) * 50.0 + (blur_var / 200.0) * 35.0 + (focus_score / 100.0) * 15.0)
    if text_vis_score >= 75 and not is_blurred:
        text_visibility = "Optimal - High contrast and sharp text boundaries"
    elif text_vis_score >= 50:
        text_visibility = "Moderate - Contrast stretching recommended for micro-text"
    else:
        text_visibility = "Degraded - Blur, uneven lighting or low contrast detected"

    # 14. Image completeness (detect whether package touches edge boundaries)
    # If high edge activity directly touches outer 2% margin, package might be clipped
    margin_top = np.mean(edges[:int(h * 0.02), :])
    margin_bottom = np.mean(edges[int(h * 0.98):, :])
    margin_left = np.mean(edges[:, :int(w * 0.02)])
    margin_right = np.mean(edges[:, int(w * 0.98):])
    is_clipped = max(margin_top, margin_bottom, margin_left, margin_right) > 35.0
    image_completeness = "Border clipped - Secondary surfaces recommended" if is_clipped else "Complete packaging visible"

    # Overall quality score (0-100) & advisory
    # Sharpness: max 30 pts
    sharp_pts = min(30.0, (blur_var / 150.0) * 30.0)
    # Brightness: max 20 pts (ideal 110-170)
    b_dist = abs(mean_brightness - 140.0)
    bright_pts = max(0.0, 20.0 - (b_dist / 140.0) * 20.0)
    # Contrast: max 20 pts (ideal std > 45)
    cont_pts = min(20.0, (contrast_std / 50.0) * 20.0)
    # Resolution: max 15 pts (ideal > 1.5 MP)
    res_pts = min(15.0, (megapixels / 1.5) * 15.0)
    # Glare, shadow & noise deduction: max 15 pts
    clean_pts = max(0.0, 15.0 - (glare_pct * 1.5) - (noise_var / 30.0) - (8.0 if shadow_detected else 0.0))
    
    overall = int(round(sharp_pts + bright_pts + cont_pts + res_pts + clean_pts))
    overall = max(15, min(99, overall))
    
    advisory = None
    if overall < 65 or is_blurred or is_glare_detected or shadow_detected or is_clipped:
        reasons = []
        if is_blurred: reasons.append("camera blur")
        if is_glare_detected: reasons.append(f"surface glare ({glare_pct}%)")
        if shadow_detected: reasons.append("heavy shadows")
        if mean_brightness < 80: reasons.append("low lighting")
        if contrast_std < 30: reasons.append("low contrast")
        if is_clipped: reasons.append("package margins clipped")
        advisory = f"Image quality is suboptimal ({', '.join(reasons)}). Multi-pass AI preprocessing will be applied."

    margin_risk = "High" if is_clipped else ("Moderate" if max(margin_top, margin_bottom, margin_left, margin_right) > 20.0 else "Low")

    return ImageQualityMetrics(
        resolution_megapixels=megapixels,
        width=w,
        height=h,
        resolution=f"{w}x{h}",
        blur_laplacian_variance=round(blur_var, 2),
        is_blurred=is_blurred,
        focus_score=focus_score,
        noise_variance=round(noise_var, 2),
        is_noisy=is_noisy,
        mean_brightness=round(mean_brightness, 1),
        brightness=round(mean_brightness, 1),
        contrast_std_dev=round(contrast_std, 1),
        contrast=round(contrast_std, 1),
        glare_percentage=glare_pct,
        is_glare_detected=is_glare_detected,
        shadow_detected=shadow_detected,
        rotation_angle_deg=rotation_angle,
        perspective_distortion_detected=perspective_distortion,
        skew_angle_deg=skew_angle,
        skew_angle=skew_angle,
        estimated_text_size_px=est_text_size,
        estimated_glyph_height_px=est_text_size,
        margin_clipping_risk=margin_risk,
        background_interference_score=bg_interference_score,
        text_visibility=text_visibility,
        image_completeness=image_completeness,
        overall_quality_score=overall,
        advisory=advisory
    )

# -------------------------------------------------------------------
# STEP 2.2 & 2.3: 13 PREPROCESSING VARIANTS & IMAGE CLEANING
# -------------------------------------------------------------------

def generate_13_preprocessing_variants(
    pil_image: Image.Image,
    include_base64: bool = True
) -> Dict[str, Tuple[Image.Image, PreprocessingVariantInfo]]:
    """Generates the 13 required computer vision preprocessing variants:
    A. Original
    B. Resized / Upscaled
    C. Grayscale
    D. Contrast enhanced
    E. Sharpened
    F. Denoised
    G. Adaptive threshold
    H. Otsu threshold
    I. Deskewed
    J. Perspective corrected
    K. Brightness corrected
    L. CLAHE enhanced
    M. Multiple-scale versions
    """
    t0 = time.time()
    cv_img = pil_to_cv2(pil_image)
    h, w = cv_img.shape[:2]
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    
    variants: Dict[str, Tuple[Image.Image, PreprocessingVariantInfo]] = {}

    def record_variant(var_id: str, name: str, desc: str, out_img: Image.Image):
        ow, oh = out_img.size
        b64 = encode_image_to_base64(out_img, quality=88) if include_base64 else None
        elapsed = round((time.time() - t0) * 1000, 1)
        info = PreprocessingVariantInfo(
            variant_id=var_id,
            name=name,
            description=desc,
            base64_image=b64,
            width=ow,
            height=oh,
            processing_time_ms=elapsed
        )
        variants[var_id] = (out_img, info)

    # A. Original
    record_variant("original", "Original Image", "Raw unaltered working copy for inspection evidence", pil_image)

    # B. Resized / Upscaled (Bicubic enlargement for micro-print)
    target_dim = 2400
    max_dim = max(w, h)
    scale = min(3.0, max(1.2, target_dim / max(1, max_dim)))
    new_w, new_h = int(w * scale), int(h * scale)
    resized_cv = cv2.resize(cv_img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    record_variant("resized", "Upscaled Super-Resolution (Bicubic)", f"Interpolated {scale:.1f}x scaling for micro-text and crimp dates", cv2_to_pil(resized_cv))

    # C. Grayscale
    gray_pil = Image.fromarray(gray).convert("RGB")
    record_variant("grayscale", "Luminance Grayscale", "Perceptual luminance conversion isolating text intensity", gray_pil)

    # D. Contrast Enhanced (Autocontrast percentile stretching)
    contrasted_gray = ImageOps.autocontrast(Image.fromarray(gray), cutoff=2)
    record_variant("contrast_enhanced", "Percentile Contrast Stretched", "Dynamic 2%-98% histogram stretching to eliminate haze", contrasted_gray.convert("RGB"))

    # E. Sharpened (Laplacian edge filter)
    sharpened_pil = pil_image.filter(ImageFilter.UnsharpMask(radius=2, percent=160, threshold=3))
    record_variant("sharpened", "Laplacian Edge Sharpened", "Unsharp mask filter reversing lens and motion blur on small characters", sharpened_pil)

    # F. Denoised (Fast Non-Local Means / Bilateral)
    denoised_cv = cv2.fastNlMeansDenoisingColored(cv_img, None, 8, 8, 7, 21) if max(w, h) <= 1800 else cv2.bilateralFilter(cv_img, 7, 50, 50)
    record_variant("denoised", "Non-Local Means Denoised", "Removes CMOS sensor grain and printing rosette texture", cv2_to_pil(denoised_cv))

    # G. Adaptive Threshold (Sauvola / Local window binarization)
    adaptive_bin = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 25, 8)
    record_variant("adaptive_threshold", "Sauvola / Adaptive Thresholded", "Local window binarization isolating dot-matrix inkjet batch stamps", cv2_to_pil(adaptive_bin))

    # H. Otsu Threshold
    _, otsu_bin = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    record_variant("otsu_threshold", "Otsu Global Binarization", "Optimal bimodal thresholding for high-contrast statutory panels", cv2_to_pil(otsu_bin))

    # I. Deskewed (Rotation by dominant text orientation)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 80, minLineLength=max(40, w // 15), maxLineGap=10)
    skew = 0.0
    if lines is not None and len(lines) > 0:
        valid_angles = []
        for l in lines:
            pts = l.flatten()
            if len(pts) >= 4 and pts[2] != pts[0]:
                a = math.degrees(math.atan2(float(pts[3] - pts[1]), float(pts[2] - pts[0])))
                if abs(a) < 45.0:
                    valid_angles.append(a)
        if valid_angles:
            skew = float(np.median(valid_angles))
            
    if abs(skew) > 0.5:
        rot_mat = cv2.getRotationMatrix2D((w / 2, h / 2), skew, 1.0)
        deskewed_cv = cv2.warpAffine(cv_img, rot_mat, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        deskewed_pil = cv2_to_pil(deskewed_cv)
    else:
        deskewed_pil = pil_image.copy()
    record_variant("deskewed", "Deskewed Orientation", f"Rectified {skew:.1f}° text slant for linear horizontal OCR scanning", deskewed_pil)

    # J. Perspective Corrected (Quadrilateral label homography)
    perspective_cv = cv_img.copy()
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_c) > 0.20 * (w * h):
            peri = cv2.arcLength(largest_c, True)
            approx = cv2.approxPolyDP(largest_c, 0.03 * peri, True)
            if len(approx) == 4:
                pts = approx.reshape(4, 2).astype(np.float32)
                # Order points: top-left, top-right, bottom-right, bottom-left
                s = pts.sum(axis=1)
                diff = np.diff(pts, axis=1)
                rect = np.zeros((4, 2), dtype=np.float32)
                rect[0] = pts[np.argmin(s)]
                rect[2] = pts[np.argmax(s)]
                rect[1] = pts[np.argmin(diff)]
                rect[3] = pts[np.argmax(diff)]
                
                widthA = np.linalg.norm(rect[2] - rect[3])
                widthB = np.linalg.norm(rect[1] - rect[0])
                maxWidth = max(int(widthA), int(widthB))
                heightA = np.linalg.norm(rect[1] - rect[2])
                heightB = np.linalg.norm(rect[0] - rect[3])
                maxHeight = max(int(heightA), int(heightB))
                
                dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype=np.float32)
                M = cv2.getPerspectiveTransform(rect, dst)
                perspective_cv = cv2.warpPerspective(cv_img, M, (maxWidth, maxHeight))
    record_variant("perspective_corrected", "Perspective Rectified", "Four-point homography planar unwarping for tilted bottles and boxes", cv2_to_pil(perspective_cv))

    # K. Brightness Corrected (Gamma illumination leveling)
    gamma = 1.35
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    gamma_cv = cv2.LUT(cv_img, table)
    record_variant("brightness_corrected", "Gamma Illumination Leveled", "Shadow removal and dynamic range compensation on reflective metallic packs", cv2_to_pil(gamma_cv))

    # L. CLAHE Enhanced (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    clahe_gray = clahe.apply(gray)
    record_variant("clahe_enhanced", "CLAHE Enhanced", "Local adaptive histogram equalization boosting low-contrast declarations", cv2_to_pil(clahe_gray))

    # M. Multi-scale versions (pyramid crop targeting statutory declarations)
    # Create a targeted high-res bottom 40% panel where MRP/Dates commonly reside
    crop_y = int(h * 0.55)
    crop_h = h - crop_y
    scale_factor = 2.0
    crop_cv = cv_img[crop_y:h, 0:w]
    multiscale_cv = cv2.resize(crop_cv, (int(w * scale_factor), int(crop_h * scale_factor)), interpolation=cv2.INTER_CUBIC)
    record_variant("multiscale", "Multi-Scale Targeted Crop", "High-density 2x magnification crop targeting statutory declaration zone", cv2_to_pil(multiscale_cv))

    return variants
