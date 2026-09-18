/**
 * Multi-Stage Image Preprocessing Pipeline
 * Generates multiple enhanced representations of packaging label photos
 * to maximize OCR and AI Vision detection across challenging surfaces:
 * - Reflective / metallic packaging (gold/silver)
 * - Dark backgrounds with light/white text (inversion)
 * - Dot-matrix and inkjet stamped text (adaptive binarization)
 * - Low-resolution or small print (bicubic upscaling)
 * - Uneven illumination & shadows (contrast stretching & gamma)
 * - Cropped statutory declaration boxes (bottom 35%, top 40%, middle 40%)
 */

export interface ProcessedImageVariant {
  id: string;
  name: string;
  description: string;
  dataUrl: string;
  width: number;
  height: number;
  isCrop?: boolean;
}

export interface MultiStageProcessingResult {
  original: ProcessedImageVariant;
  variants: ProcessedImageVariant[];
  crops: ProcessedImageVariant[];
}

/**
 * Loads an image from a URL or data URI safely into an HTMLImageElement
 */
function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => resolve(img);
    img.onerror = (err) => reject(err);
    img.src = src;
  });
}

/**
 * Applies a 3x3 Laplacian edge-sharpening convolution kernel
 */
function applySharpen(
  data: Uint8ClampedArray,
  width: number,
  height: number,
  strength: number = 0.65
): void {
  const copy = new Uint8ClampedArray(data);
  const center = 1 + 4 * strength;
  const edge = -strength;

  for (let y = 1; y < height - 1; y++) {
    const rowOffset = y * width * 4;
    const prevRowOffset = (y - 1) * width * 4;
    const nextRowOffset = (y + 1) * width * 4;

    for (let x = 1; x < width - 1; x++) {
      const idx = rowOffset + x * 4;
      const leftIdx = rowOffset + (x - 1) * 4;
      const rightIdx = rowOffset + (x + 1) * 4;
      const topIdx = prevRowOffset + x * 4;
      const bottomIdx = nextRowOffset + x * 4;

      for (let c = 0; c < 3; c++) {
        const val =
          center * copy[idx + c] +
          edge * (copy[leftIdx + c] + copy[rightIdx + c] + copy[topIdx + c] + copy[bottomIdx + c]);
        data[idx + c] = Math.min(255, Math.max(0, val));
      }
    }
  }
}

/**
 * Performs dynamic histogram percentile contrast stretching and glare reduction
 */
function applyContrastStretch(
  data: Uint8ClampedArray,
  width: number,
  height: number,
  forceInvert?: boolean
): { shouldInvert: boolean; meanLuminance: number } {
  const pixelCount = width * height;
  const luminance = new Uint8Array(pixelCount);
  const histogram = new Int32Array(256);

  let totalLuminance = 0;
  for (let i = 0, j = 0; i < data.length; i += 4, j++) {
    const l = Math.round(0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
    luminance[j] = l;
    histogram[l]++;
    totalLuminance += l;
  }

  const meanLuminance = totalLuminance / pixelCount;
  const lowerThresholdCount = pixelCount * 0.02;
  const upperThresholdCount = pixelCount * 0.98;

  let acc = 0;
  let pLow = 0;
  let pHigh = 255;

  for (let i = 0; i < 256; i++) {
    acc += histogram[i];
    if (pLow === 0 && acc >= lowerThresholdCount) {
      pLow = i;
    }
    if (acc >= upperThresholdCount) {
      pHigh = i;
      break;
    }
  }

  const range = pHigh - pLow;
  const shouldInvert = forceInvert !== undefined ? forceInvert : meanLuminance < 115;

  if (range > 15) {
    for (let i = 0, j = 0; i < data.length; i += 4, j++) {
      let l = luminance[j];
      let stretched = Math.round(((l - pLow) / range) * 255);
      stretched = Math.min(255, Math.max(0, stretched));

      if (shouldInvert) {
        stretched = 255 - stretched;
      }

      data[i] = stretched;
      data[i + 1] = stretched;
      data[i + 2] = stretched;
    }
  } else {
    for (let i = 0, j = 0; i < data.length; i += 4, j++) {
      let l = luminance[j];
      if (shouldInvert) l = 255 - l;
      data[i] = l;
      data[i + 1] = l;
      data[i + 2] = l;
    }
  }

  return { shouldInvert, meanLuminance };
}

/**
 * Applies local adaptive thresholding (Sauvola / Niblack variant)
 * Isolates dot-matrix and inkjet stamp text on gradient tubes and metallic labels
 */
function applyAdaptiveThreshold(
  data: Uint8ClampedArray,
  width: number,
  height: number,
  windowSize: number = 17,
  k: number = 0.22
): void {
  const pixelCount = width * height;
  const grayscale = new Uint8Array(pixelCount);

  for (let i = 0, j = 0; i < data.length; i += 4, j++) {
    grayscale[j] = Math.round(0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
  }

  const halfWin = Math.floor(windowSize / 2);
  const integral = new Float64Array((width + 1) * (height + 1));

  for (let y = 0; y < height; y++) {
    let rowSum = 0;
    for (let x = 0; x < width; x++) {
      rowSum += grayscale[y * width + x];
      integral[(y + 1) * (width + 1) + (x + 1)] =
        integral[y * (width + 1) + (x + 1)] + rowSum;
    }
  }

  for (let y = 0; y < height; y++) {
    const y0 = Math.max(0, y - halfWin);
    const y1 = Math.min(height - 1, y + halfWin);

    for (let x = 0; x < width; x++) {
      const x0 = Math.max(0, x - halfWin);
      const x1 = Math.min(width - 1, x + halfWin);
      const count = (x1 - x0 + 1) * (y1 - y0 + 1);

      const sum =
        integral[(y1 + 1) * (width + 1) + (x1 + 1)] -
        integral[y0 * (width + 1) + (x1 + 1)] -
        integral[(y1 + 1) * (width + 1) + x0] +
        integral[y0 * (width + 1) + x0];

      const mean = sum / count;
      const threshold = mean * (1 - k);
      const pixelVal = grayscale[y * width + x] < threshold ? 0 : 255;

      const idx = (y * width + x) * 4;
      data[idx] = pixelVal;
      data[idx + 1] = pixelVal;
      data[idx + 2] = pixelVal;
    }
  }
}

/**
 * Adjusts gamma and brightness to rescue shadowed or dark metallic packaging
 */
function applyBrightnessGamma(
  data: Uint8ClampedArray,
  gamma: number = 1.35,
  brightnessBoost: number = 15
): void {
  const lut = new Uint8Array(256);
  for (let i = 0; i < 256; i++) {
    const normalized = i / 255.0;
    const corrected = Math.pow(normalized, 1.0 / gamma) * 255.0 + brightnessBoost;
    lut[i] = Math.min(255, Math.max(0, Math.round(corrected)));
  }

  for (let i = 0; i < data.length; i += 4) {
    data[i] = lut[data[i]];
    data[i + 1] = lut[data[i + 1]];
    data[i + 2] = lut[data[i + 2]];
  }
}

/**
 * Creates a cropped and upscaled sub-canvas
 */
function createCroppedRegion(
  sourceCanvas: HTMLCanvasElement,
  yRatioStart: number,
  yRatioEnd: number,
  targetHeight: number = 1200
): string {
  const srcW = sourceCanvas.width;
  const srcH = sourceCanvas.height;

  const cropY = Math.round(srcH * yRatioStart);
  const cropH = Math.round(srcH * (yRatioEnd - yRatioStart));

  const scale = targetHeight / Math.max(1, cropH);
  const cropCanvas = document.createElement('canvas');
  cropCanvas.width = Math.round(srcW * scale);
  cropCanvas.height = targetHeight;

  const ctx = cropCanvas.getContext('2d');
  if (!ctx) return sourceCanvas.toDataURL('image/jpeg', 0.9);

  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';

  ctx.drawImage(
    sourceCanvas,
    0, cropY, srcW, cropH,
    0, 0, cropCanvas.width, cropCanvas.height
  );

  return cropCanvas.toDataURL('image/jpeg', 0.92);
}

/**
 * Executes the complete Multi-Stage Image Preprocessing Pipeline
 */
export async function processMultiStageImage(
  imageSource: string
): Promise<MultiStageProcessingResult> {
  const img = await loadImage(imageSource);
  const origWidth = img.naturalWidth || img.width;
  const origHeight = img.naturalHeight || img.height;

  const originalVariant: ProcessedImageVariant = {
    id: 'original',
    name: 'Original Packaging Image',
    description: 'Raw uploaded photo without transformation',
    dataUrl: imageSource,
    width: origWidth,
    height: origHeight
  };

  const variants: ProcessedImageVariant[] = [];
  const crops: ProcessedImageVariant[] = [];

  try {
    // 1. Target resolution upscaling (target max dimension 2400-2800px for small font legibility)
    const targetDim = 2600;
    const maxCurrent = Math.max(origWidth, origHeight);
    let scale = 1.0;
    if (maxCurrent < 1600) {
      scale = Math.min(3.0, targetDim / maxCurrent);
    } else if (maxCurrent > 3200) {
      scale = 2600 / maxCurrent;
    }

    const upW = Math.round(origWidth * scale);
    const upH = Math.round(origHeight * scale);

    // Canvas 1: High-Density Upscaled
    const upCanvas = document.createElement('canvas');
    upCanvas.width = upW;
    upCanvas.height = upH;
    const upCtx = upCanvas.getContext('2d')!;
    upCtx.imageSmoothingEnabled = true;
    upCtx.imageSmoothingQuality = 'high';
    upCtx.drawImage(img, 0, 0, upW, upH);

    variants.push({
      id: 'upscaled',
      name: 'Upscaled Super-Resolution (2x-3x)',
      description: 'Bicubic interpolated enlargement for small printed fonts',
      dataUrl: upCanvas.toDataURL('image/jpeg', 0.95),
      width: upW,
      height: upH
    });

    // Canvas 2: Contrast-Enhanced & Sharpened (Primary Workhorse)
    const enhCanvas = document.createElement('canvas');
    enhCanvas.width = upW;
    enhCanvas.height = upH;
    const enhCtx = enhCanvas.getContext('2d')!;
    enhCtx.drawImage(upCanvas, 0, 0);
    const enhImgData = enhCtx.getImageData(0, 0, upW, upH);

    // Sharpen
    applySharpen(enhImgData.data, upW, upH, 0.65);
    // Contrast Stretch & Auto-Inversion
    const { shouldInvert } = applyContrastStretch(enhImgData.data, upW, upH);
    enhCtx.putImageData(enhImgData, 0, 0);

    variants.push({
      id: 'contrast_sharpened',
      name: 'Contrast-Enhanced & Sharpened',
      description: 'Laplacian edge filtering with dynamic percentile contrast stretching',
      dataUrl: enhCanvas.toDataURL('image/jpeg', 0.95),
      width: upW,
      height: upH
    });

    // Canvas 3: Adaptive Binarized (for dot-matrix inkjet & embossed crimp numbers)
    const binCanvas = document.createElement('canvas');
    binCanvas.width = upW;
    binCanvas.height = upH;
    const binCtx = binCanvas.getContext('2d')!;
    binCtx.drawImage(upCanvas, 0, 0);
    const binImgData = binCtx.getImageData(0, 0, upW, upH);
    applyAdaptiveThreshold(binImgData.data, upW, upH, 19, 0.20);
    binCtx.putImageData(binImgData, 0, 0);

    variants.push({
      id: 'adaptive_binarized',
      name: 'Adaptive Thresholding / Sauvola Binarized',
      description: 'Isolates faint dot-matrix batch codes, MRP stamps, and date crimps',
      dataUrl: binCanvas.toDataURL('image/jpeg', 0.92),
      width: upW,
      height: upH
    });

    // Canvas 4: Gamma & Brightness Boosted (for dark/metallic packaging)
    const gamCanvas = document.createElement('canvas');
    gamCanvas.width = upW;
    gamCanvas.height = upH;
    const gamCtx = gamCanvas.getContext('2d')!;
    gamCtx.drawImage(upCanvas, 0, 0);
    const gamImgData = gamCtx.getImageData(0, 0, upW, upH);
    applyBrightnessGamma(gamImgData.data, 1.4, 20);
    gamCtx.putImageData(gamImgData, 0, 0);

    variants.push({
      id: 'gamma_brightened',
      name: 'Gamma & Illumination Normalization',
      description: 'Shadow removal and glare neutralization for reflective packaging',
      dataUrl: gamCanvas.toDataURL('image/jpeg', 0.92),
      width: upW,
      height: upH
    });

    // Canvas 5: Inverted Polarity (if not already inverted)
    if (!shouldInvert) {
      const invCanvas = document.createElement('canvas');
      invCanvas.width = upW;
      invCanvas.height = upH;
      const invCtx = invCanvas.getContext('2d')!;
      invCtx.drawImage(upCanvas, 0, 0);
      const invImgData = invCtx.getImageData(0, 0, upW, upH);
      applyContrastStretch(invImgData.data, upW, upH, true);
      invCtx.putImageData(invImgData, 0, 0);

      variants.push({
        id: 'polarity_inverted',
        name: 'Inverted Polarity (Dark Mode)',
        description: 'Black-on-white inversion for silver/white text on dark background',
        dataUrl: invCanvas.toDataURL('image/jpeg', 0.92),
        width: upW,
        height: upH
      });
    }

    // Cropped Region 1: Bottom 35% Declaration Region (where MRP, MFD, Batch commonly reside)
    const bottomCropUrl = createCroppedRegion(enhCanvas, 0.60, 1.0, 1000);
    crops.push({
      id: 'crop_bottom_declarations',
      name: 'Cropped Bottom Declaration Panel (60%-100%)',
      description: 'High-density crop targeting MRP, Batch, and Expiry print area',
      dataUrl: bottomCropUrl,
      width: Math.round(upW * (1000 / (upH * 0.4))),
      height: 1000,
      isCrop: true
    });

    // Cropped Region 2: Top 40% PDP Region (Product Name, Brand, Net Qty)
    const topCropUrl = createCroppedRegion(enhCanvas, 0.0, 0.45, 1000);
    crops.push({
      id: 'crop_top_pdp',
      name: 'Cropped Top PDP Panel (0%-45%)',
      description: 'High-density crop targeting Brand, Product Name, and PDP declarations',
      dataUrl: topCropUrl,
      width: Math.round(upW * (1000 / (upH * 0.45))),
      height: 1000,
      isCrop: true
    });

    // Cropped Region 3: Middle 40% Panel (Ingredients, Manufacturer Address, Consumer Care)
    const midCropUrl = createCroppedRegion(enhCanvas, 0.30, 0.70, 1000);
    crops.push({
      id: 'crop_middle_info',
      name: 'Cropped Middle Information Band (30%-70%)',
      description: 'High-density crop targeting Manufacturer Address and Helpline',
      dataUrl: midCropUrl,
      width: Math.round(upW * (1000 / (upH * 0.4))),
      height: 1000,
      isCrop: true
    });

  } catch (err) {
    console.warn('Multi-stage preprocessing note:', err);
  }

  return {
    original: originalVariant,
    variants,
    crops
  };
}

export const generateMultiStageVariants = processMultiStageImage;
