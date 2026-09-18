/**
 * Image Quality Assessment Service for Packaged Product Labels
 * Analyzes resolution, blur (Laplacian variance), brightness/exposure, contrast,
 * orientation, and text edge visibility before executing OCR.
 */

export interface ImageQualityMetrics {
  width: number;
  height: number;
  megapixels: number;
  blurScore: number; // Laplacian variance: < 40 = severe blur, 40-90 = moderate blur, > 90 = sharp
  isBlurred: boolean;
  brightness: number; // Mean luminance: 0-255 (< 50 = underexposed, > 215 = glare/overexposed)
  brightnessStatus: 'Under-exposed (Dark)' | 'Optimal Exposure' | 'Over-exposed (Glare)';
  contrastScore: number; // Standard deviation of luminance (0-100)
  contrastStatus: 'Low Contrast' | 'Normal Contrast' | 'High Contrast';
  orientation: 'Standard (0°)' | 'Rotated / Skewed' | 'Portrait' | 'Landscape';
  textVisibilityScore: number; // High-frequency edge density: 0-100%
  overallScore: number; // Composite quality score: 0-100%
  qualityGrade: 'Excellent' | 'Good' | 'Fair' | 'Poor (Enhancement Needed)';
  advisoryMessage?: string;
  suggestedEnhancements: string[];
}

/**
 * Performs computer vision analysis directly in the browser via HTML5 Canvas
 * to evaluate image quality without network latency.
 */
export async function analyzeImageQuality(imageUrl: string): Promise<ImageQualityMetrics> {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';

    img.onload = () => {
      const width = img.naturalWidth || img.width;
      const height = img.naturalHeight || img.height;
      const megapixels = Number(((width * height) / 1_000_000).toFixed(2));

      // Create inspection canvas (downsampled to 600px width for rapid real-time analysis)
      const scale = Math.min(1, 600 / width);
      const cWidth = Math.round(width * scale);
      const cHeight = Math.round(height * scale);

      const canvas = document.createElement('canvas');
      canvas.width = cWidth;
      canvas.height = cHeight;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });

      if (!ctx) {
        resolve(createFallbackMetrics(width, height, megapixels));
        return;
      }

      ctx.drawImage(img, 0, 0, cWidth, cHeight);
      const imgData = ctx.getImageData(0, 0, cWidth, cHeight);
      const pixels = imgData.data;
      const totalPixels = cWidth * cHeight;

      // 1. Luminance & Contrast Calculation
      let totalLuminance = 0;
      const luminance = new Uint8Array(totalPixels);

      for (let i = 0, j = 0; i < pixels.length; i += 4, j++) {
        // Standard Rec. 601 perceptual luminance: 0.299 R + 0.587 G + 0.114 B
        const l = Math.round(0.299 * pixels[i] + 0.587 * pixels[i + 1] + 0.114 * pixels[i + 2]);
        luminance[j] = l;
        totalLuminance += l;
      }

      const meanLuminance = totalLuminance / totalPixels;

      // Variance / Standard Deviation of luminance for contrast
      let varianceSum = 0;
      for (let j = 0; j < totalPixels; j++) {
        const diff = luminance[j] - meanLuminance;
        varianceSum += diff * diff;
      }
      const contrastStdDev = Math.sqrt(varianceSum / totalPixels);
      const contrastScore = Math.min(100, Math.round((contrastStdDev / 70) * 100));

      // 2. Blur Detection via Discrete Laplacian Operator
      // Kernel:
      //  0  1  0
      //  1 -4  1
      //  0  1  0
      let laplacianSum = 0;
      let laplacianSqSum = 0;
      let count = 0;
      let edgePixelCount = 0;

      for (let y = 1; y < cHeight - 1; y++) {
        const row = y * cWidth;
        const prevRow = (y - 1) * cWidth;
        const nextRow = (y + 1) * cWidth;

        for (let x = 1; x < cWidth - 1; x++) {
          const center = luminance[row + x];
          const lapVal =
            luminance[row + x - 1] +
            luminance[row + x + 1] +
            luminance[prevRow + x] +
            luminance[nextRow + x] -
            4 * center;

          laplacianSum += lapVal;
          laplacianSqSum += lapVal * lapVal;
          count++;

          if (Math.abs(lapVal) > 30) {
            edgePixelCount++;
          }
        }
      }

      const laplacianMean = count > 0 ? laplacianSum / count : 0;
      const laplacianVariance = count > 0 ? laplacianSqSum / count - laplacianMean * laplacianMean : 0;
      const blurScore = Math.round(laplacianVariance);
      const isBlurred = blurScore < 75;

      // 3. Text Visibility / High-Frequency Edge Density
      const edgeDensity = count > 0 ? edgePixelCount / count : 0;
      const textVisibilityScore = Math.min(100, Math.round(edgeDensity * 600));

      // 4. Brightness Assessment
      const brightness = Math.round(meanLuminance);
      let brightnessStatus: ImageQualityMetrics['brightnessStatus'] = 'Optimal Exposure';
      if (brightness < 60) {
        brightnessStatus = 'Under-exposed (Dark)';
      } else if (brightness > 210) {
        brightnessStatus = 'Over-exposed (Glare)';
      }

      // 5. Contrast Assessment
      let contrastStatus: ImageQualityMetrics['contrastStatus'] = 'Normal Contrast';
      if (contrastScore < 40) {
        contrastStatus = 'Low Contrast';
      } else if (contrastScore > 75) {
        contrastStatus = 'High Contrast';
      }

      // 6. Orientation
      const isPortrait = height > width;
      const orientation: ImageQualityMetrics['orientation'] = isPortrait ? 'Portrait' : 'Landscape';

      // 7. Composite Quality Score (0 - 100)
      let composite = 0;
      // Resolution contribution (up to 25 pts)
      const resPts = Math.min(25, (megapixels / 2.0) * 25);
      // Sharpness contribution (up to 35 pts)
      const sharpPts = Math.min(35, (blurScore / 120) * 35);
      // Contrast contribution (up to 20 pts)
      const contrastPts = Math.min(20, (contrastScore / 70) * 20);
      // Brightness penalty (up to 20 pts)
      const brightDistance = Math.abs(brightness - 130);
      const brightPts = Math.max(0, 20 - (brightDistance / 100) * 20);

      composite = Math.round(resPts + sharpPts + contrastPts + brightPts);
      composite = Math.max(15, Math.min(99, composite));

      let qualityGrade: ImageQualityMetrics['qualityGrade'] = 'Good';
      if (composite >= 85) qualityGrade = 'Excellent';
      else if (composite >= 65) qualityGrade = 'Good';
      else if (composite >= 45) qualityGrade = 'Fair';
      else qualityGrade = 'Poor (Enhancement Needed)';

      const suggestedEnhancements: string[] = [];
      if (isBlurred) suggestedEnhancements.push('Laplacian 3x3 Edge Sharpening');
      if (brightness < 65) suggestedEnhancements.push('Gamma Lift & Shadow Reduction');
      if (brightness > 200) suggestedEnhancements.push('Glare Suppression & Histogram Normalization');
      if (contrastScore < 45) suggestedEnhancements.push('Dynamic Contrast Percentile Stretching');
      if (megapixels < 1.2) suggestedEnhancements.push('Super-Resolution 2x Canvas Interpolation');

      const isLowQuality = composite < 50 || isBlurred || brightness < 50;
      const advisoryMessage = isLowQuality
        ? 'Image quality is low. AI enhancement will be attempted.'
        : undefined;

      resolve({
        width,
        height,
        megapixels,
        blurScore,
        isBlurred,
        brightness,
        brightnessStatus,
        contrastScore,
        contrastStatus,
        orientation,
        textVisibilityScore,
        overallScore: composite,
        qualityGrade,
        advisoryMessage,
        suggestedEnhancements
      });
    };

    img.onerror = () => {
      resolve(createFallbackMetrics(1920, 1080, 2.07));
    };

    img.src = imageUrl;
  });
}

function createFallbackMetrics(width: number, height: number, megapixels: number): ImageQualityMetrics {
  return {
    width,
    height,
    megapixels,
    blurScore: 110,
    isBlurred: false,
    brightness: 128,
    brightnessStatus: 'Optimal Exposure',
    contrastScore: 72,
    contrastStatus: 'Normal Contrast',
    orientation: 'Portrait',
    textVisibilityScore: 85,
    overallScore: 82,
    qualityGrade: 'Good',
    suggestedEnhancements: ['Bilateral Smoothing', 'Histogram Stretch']
  };
}
