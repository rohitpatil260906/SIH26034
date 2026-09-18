/**
 * Advanced Legal Metrology MRP Detection & Spatial Pattern Engine
 * 
 * Implements context-aware, fault-tolerant Maximum Retail Price (MRP) extraction
 * under Rule 6(1)(e) of the Legal Metrology (Packaged Commodities) Rules, 2011.
 * 
 * Features:
 * 1. Multi-strategy pattern matching (compound phrases, intervening tax clauses)
 * 2. Multi-line spatial proximity analysis (keyword on line N, price on line N+1)
 * 3. 2D Bounding-box spatial clustering
 * 4. Typo-tolerant normalization (M8P, NR P, WRP, digit confusions 4B9->489)
 * 5. Standalone currency-led detection (₹489/-, Rs 489)
 * 6. Slash-dash notation (489/-, 489.00/-)
 * 7. Contextual anti-confusion guards (strictly rejects Net Qty 56g, USP ₹8.91/g, Calories 489 kcal)
 */

export interface MrpTokenWord {
  text: string;
  confidence?: number;
  bbox?: {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
  };
}

export interface MrpDetectionResult {
  detected: boolean;
  numeric: number;
  currency: string;
  displayValue: string;
  rawMatch: string;
  hasTaxStatement: boolean;
  taxPhraseDetected?: string;
  isDefective: boolean;
  confidence: number;
  strategy: string;
  status: 'DETECTED' | 'REVIEW' | 'NOT DETECTED';
  reviewReason?: string;
  source: 'Direct Pattern' | 'Multi-Line Proximity' | 'Spatial Bounding Box' | 'Currency Price Scan' | 'Typo-Tolerant Engine' | 'AI Vision';
  boundingBox?: { x: number; y: number; width: number; height: number; label?: string };
}

/**
 * Normalizes common optical character substitutions in price strings
 */
function cleanOcrPriceDigits(raw: string): string {
  let s = raw.trim();
  // Replace letter 'O' or 'o' with '0' if surrounded by digits or decimal
  s = s.replace(/(\d)[Oo]/g, '$10').replace(/[Oo](\d)/g, '0$1');
  // Replace letter 'B' with '8' if between digits (e.g. 4B9 -> 489)
  s = s.replace(/(\d)[Bb](\d)/g, '$18$2');
  // Replace letter 'S' with '5' in numeric sequence (e.g. 48S -> 485)
  s = s.replace(/(\d)[Ss]\b/g, '$15');
  // Replace uppercase 'I' or lowercase 'l' with '1' if in digits
  s = s.replace(/(\d)[Il]/g, '$11').replace(/[Il](\d)/g, '1$1');
  return s;
}

/**
 * Checks if a string contains statutory tax inclusivity statement
 */
function checkTaxInclusiveStatement(text: string): { present: boolean; phrase?: string } {
  const lower = text.toLowerCase();
  const taxPatterns = [
    /inclusive\s*of\s*all\s*taxes/i,
    /incl\.?\s*of\s*all\s*taxes/i,
    /incl\.?\s*all\s*taxes/i,
    /incl\.?\s*taxes/i,
    /incl\s*taxes/i,
    /all\s*taxes\s*incl/i,
    /inclusive\s*all\s*taxes/i,
    /incl\.\s*of\s*taxes/i
  ];

  for (const p of taxPatterns) {
    const m = text.match(p);
    if (m) {
      return { present: true, phrase: m[0] };
    }
  }

  // Also check normalized lowercase text
  if (
    lower.includes('incl. of all taxes') ||
    lower.includes('inclusive of all taxes') ||
    lower.includes('incl of all taxes') ||
    lower.includes('incl all taxes') ||
    lower.includes('incl. taxes') ||
    lower.includes('incl taxes')
  ) {
    return { present: true, phrase: 'incl. of all taxes' };
  }

  return { present: false };
}

/**
 * Checks if a line or text snippet is clearly a NON-MRP entity
 * (Net quantity, USP, Batch, Expiry, Calories, Nutrition, Dimensions, SPF)
 */
function isDisqualifiedLine(text: string): boolean {
  const lower = text.toLowerCase();

  // Unit Sale Price is governed under Rule 6(1)(ea), not MRP
  if (/\busp\b|unit\s*sale\s*price|\/g\b|\/ml\b|\/piece\b|\/kg\b|\/l\b|\/unit\b/i.test(text)) {
    return true;
  }

  // Net Quantity declarations (e.g. "Net Wt. 56 g", "56g", "100ml")
  if (/\bnet\s*(?:wt\.?|qty|quantity)\b|\b\d+\s*(?:g|gm|gms|ml|kg|l|ltr)\b/i.test(text) && !/mrp|price|₹|rs/i.test(text)) {
    return true;
  }

  // Nutritional table energy or calories (e.g. "Energy 489 kcal", "Protein 12g")
  if (/nutri|energy|kcal|calorie|fat\b|carbohydrate|sugar|protein|sodium/i.test(lower)) {
    return true;
  }

  // Cosmetic SPF ratings (e.g. "SPF 50", "PA+++")
  if (/\bspf\s*\d+\b|\bpa\+{1,4}\b/i.test(text)) {
    return true;
  }

  // Date stamps without price (e.g. "02/2026", "MFD 02/26")
  if (/^(?:mfd|pkd|mfg|exp|use\s*before|best\s*before)[\s:]*[0-9]{2}[/-][0-9]{2,4}$/i.test(text.trim())) {
    return true;
  }

  return false;
}

/**
 * Normalizes keyword variants of "MRP"
 */
function normalizeMrpKeyword(line: string): string {
  return line
    .replace(/\b(?:m8p|nr\s*p|mbp|wrp|m\s*r\s*p)\b/gi, 'MRP')
    .replace(/\bm\.r\.p\.?:?/gi, 'MRP')
    .replace(/\bmax(?:imum)?\s*retail\s*price\b/gi, 'MRP')
    .replace(/\bmax\s*price\b/gi, 'MRP')
    .replace(/\bretail\s*price\b/gi, 'MRP');
}

/**
 * Extracts numeric value from a candidate price token
 */
function parsePriceNumber(rawNum: string): number | null {
  const cleaned = cleanOcrPriceDigits(rawNum).replace(/,/g, '');
  const val = parseFloat(cleaned);
  // Rational packaging price range check (₹1 to ₹1,00,000)
  if (!isNaN(val) && val > 0 && val < 500000) {
    return val;
  }
  return null;
}

/**
 * Master MRP Detection Engine
 */
export function detectMrp(
  rawText: string,
  lines: string[] = [],
  words: MrpTokenWord[] = []
): MrpDetectionResult | null {
  const allLines = lines.length > 0 ? lines : rawText.split('\n').map(l => l.trim()).filter(Boolean);
  const taxCheck = checkTaxInclusiveStatement(rawText);

  // =========================================================================
  // STRATEGY 1: DIRECT UNIFIED REGEX ON EACH LINE & JOINED TEXT
  // Handles:
  // - "MRP ₹489/-"
  // - "MRP Rs. 489.00"
  // - "MRP: 489/-"
  // - "MRP (INCL. OF ALL TAXES) ₹ 489"
  // - "MAX RETAIL PRICE ₹489/-"
  // =========================================================================
  const directPatterns = [
    // Pattern 1A: MRP with intervening tax phrase e.g. "MRP (INCL. OF ALL TAXES) ₹ 489"
    /(?:m\.?r\.?p\.?|max(?:imum)?\s*retail\s*price|retail\s*price|m8p|nr\s*p)[\s:]*(?:\(?[^)]*taxes?[^)]*\)?[\s:]*)*(?:₹|rs\.?|inr)?[\s:]*([0-9]+(?:\.[0-9]{1,2})?|\b[0-9]{2,5}\b)[\s]*(?:\/\-|\/\=)?/i,

    // Pattern 1B: Standard MRP with currency e.g. "MRP ₹489/-" or "MRP Rs. 489/-"
    /(?:m\.?r\.?p\.?|max(?:imum)?\s*retail\s*price|retail\s*price|m8p|nr\s*p)[\s:]*(?:₹|rs\.?|inr)?[\s:]*([0-9]+(?:\.[0-9]{1,2})?|\b[0-9]{2,5}\b)[\s]*(?:\/\-|\/\=)?/i,

    // Pattern 1C: "₹489/-" or "Rs. 489/-" on a line mentioning MRP or Price
    /(?:₹|rs\.?|inr)[\s:]*([0-9]+(?:\.[0-9]{1,2})?|\b[0-9]{2,5}\b)[\s]*(?:\/\-|\/\=)?/i
  ];

  for (let i = 0; i < allLines.length; i++) {
    const line = allLines[i];
    if (isDisqualifiedLine(line)) continue;

    const normalizedLine = normalizeMrpKeyword(line);

    // Test 1A & 1B: Explicit MRP keyword present on line
    if (/mrp|price/i.test(normalizedLine)) {
      for (const pat of directPatterns) {
        const m = normalizedLine.match(pat);
        if (m && m[1]) {
          const num = parsePriceNumber(m[1]);
          if (num !== null) {
            const hasLineTax = checkTaxInclusiveStatement(line).present || taxCheck.present;
            return {
              detected: true,
              numeric: num,
              currency: '₹',
              displayValue: `₹ ${num.toFixed(2).replace(/\.00$/, '')}/- ${hasLineTax ? '(INCL. OF ALL TAXES)' : ''}`.trim(),
              rawMatch: m[0],
              hasTaxStatement: hasLineTax,
              taxPhraseDetected: taxCheck.phrase,
              isDefective: !hasLineTax,
              confidence: 0.98,
              strategy: 'Direct Packaging MRP Pattern Scan',
              status: 'DETECTED',
              source: 'Direct Pattern',
              boundingBox: { x: 15, y: 60, width: 70, height: 10, label: `MRP ₹${num}` }
            };
          }
        }
      }
    }
  }

  // =========================================================================
  // STRATEGY 2: MULTI-LINE SPATIAL PROXIMITY
  // When "MRP" is on Line N, and the price "₹489/-" or "489.00" is on Line N+1 or N+2
  // =========================================================================
  for (let i = 0; i < allLines.length; i++) {
    const currentLine = allLines[i];
    const isMrpKeywordLine = /^(?:m\.?r\.?p\.?|max(?:imum)?\s*retail\s*price|retail\s*price|m8p|nr\s*p|price)[\s:]*$/i.test(currentLine.trim()) ||
      /mrp\b/i.test(currentLine);

    if (isMrpKeywordLine && !isDisqualifiedLine(currentLine)) {
      // Look ahead up to 2 lines
      for (let offset = 1; offset <= 2; offset++) {
        if (i + offset < allLines.length) {
          const nextLine = allLines[i + offset].trim();
          if (isDisqualifiedLine(nextLine)) continue;

          // Check if next line contains currency or price digits e.g. "₹489/-" or "Rs 489" or "489.00"
          const priceMatch = nextLine.match(/(?:₹|rs\.?|inr)?[\s:]*([0-9]+(?:\.[0-9]{1,2})?|\b[0-9]{2,5}\b)[\s]*(?:\/\-|\/\=)?/i);
          if (priceMatch && priceMatch[1]) {
            const num = parsePriceNumber(priceMatch[1]);
            if (num !== null) {
              const combinedText = `${currentLine} ${nextLine}`;
              const hasLineTax = checkTaxInclusiveStatement(combinedText).present || taxCheck.present;
              return {
                detected: true,
                numeric: num,
                currency: '₹',
                displayValue: `₹ ${num.toFixed(2).replace(/\.00$/, '')}/- ${hasLineTax ? '(INCL. OF ALL TAXES)' : ''}`.trim(),
                rawMatch: `${currentLine} -> ${nextLine}`,
                hasTaxStatement: hasLineTax,
                taxPhraseDetected: taxCheck.phrase,
                isDefective: !hasLineTax,
                confidence: 0.95,
                strategy: 'Multi-Line Spatial Proximity Stitching',
                status: 'DETECTED',
                source: 'Multi-Line Proximity',
                boundingBox: { x: 15, y: 60, width: 70, height: 12, label: `MRP ₹${num} (Multi-line)` }
              };
            }
          }
        }
      }
    }
  }

  // =========================================================================
  // STRATEGY 3: 2D WORD BOUNDING BOX PROXIMITY
  // If OCR word tokens are provided, find words near "MRP"
  // =========================================================================
  if (words && words.length > 1) {
    const mrpWords = words.filter(w => /mrp|m\.r\.p|m8p|price/i.test(w.text) && w.bbox);
    const candidateNumberWords = words.filter(w => /(?:₹|rs\.?)?[0-9]{2,5}(?:\.[0-9]{2})?(?:\/\-)?/i.test(w.text) && w.bbox);

    for (const mw of mrpWords) {
      if (!mw.bbox) continue;
      for (const nw of candidateNumberWords) {
        if (!nw.bbox) continue;
        const dx = Math.abs(nw.bbox.x0 - mw.bbox.x1);
        const dy = Math.abs(nw.bbox.y0 - mw.bbox.y0);

        // Within 250px horizontally or 100px vertically
        if (dx < 250 && dy < 100) {
          const numMatch = nw.text.match(/([0-9]+(?:\.[0-9]{1,2})?)/);
          if (numMatch) {
            const num = parsePriceNumber(numMatch[1]);
            if (num !== null) {
              const hasTax = taxCheck.present;
              return {
                detected: true,
                numeric: num,
                currency: '₹',
                displayValue: `₹ ${num.toFixed(2).replace(/\.00$/, '')}/- ${hasTax ? '(INCL. OF ALL TAXES)' : ''}`.trim(),
                rawMatch: `${mw.text} ${nw.text}`,
                hasTaxStatement: hasTax,
                taxPhraseDetected: taxCheck.phrase,
                isDefective: !hasTax,
                confidence: 0.94,
                strategy: '2D Spatial Bounding-Box Clustering',
                status: 'DETECTED',
                source: 'Spatial Bounding Box',
                boundingBox: {
                  x: Math.min(mw.bbox.x0, nw.bbox.x0),
                  y: Math.min(mw.bbox.y0, nw.bbox.y0),
                  width: Math.max(mw.bbox.x1, nw.bbox.x1) - Math.min(mw.bbox.x0, nw.bbox.x0),
                  height: Math.max(mw.bbox.y1, nw.bbox.y1) - Math.min(mw.bbox.y0, nw.bbox.y0),
                  label: `MRP ₹${num}`
                }
              };
            }
          }
        }
      }
    }
  }

  // =========================================================================
  // STRATEGY 4: CURRENCY-LED STANDALONE DETECTION (₹489/- or Rs. 489)
  // When the word "MRP" was missed by OCR, but the Rupee price is clearly visible
  // =========================================================================
  for (const line of allLines) {
    if (isDisqualifiedLine(line)) continue;

    // Matches "₹489/-", "₹ 489.00", "Rs. 489/-", "Rs 489"
    const currencyMatch = line.match(/(?:₹|rs\.?|inr)[\s:]*([0-9]+(?:\.[0-9]{1,2})?|\b[0-9]{2,5}\b)[\s]*(?:\/\-|\/\=)?/i);
    if (currencyMatch && currencyMatch[1]) {
      const num = parsePriceNumber(currencyMatch[1]);
      if (num !== null) {
        const hasTax = checkTaxInclusiveStatement(line).present || taxCheck.present;
        return {
          detected: true,
          numeric: num,
          currency: '₹',
          displayValue: `₹ ${num.toFixed(2).replace(/\.00$/, '')}/- ${hasTax ? '(INCL. OF ALL TAXES)' : ''}`.trim(),
          rawMatch: currencyMatch[0],
          hasTaxStatement: hasTax,
          taxPhraseDetected: taxCheck.phrase,
          isDefective: !hasTax,
          confidence: 0.90,
          strategy: 'Currency-Led Packaging Price Detection (₹/Rs)',
          status: 'DETECTED',
          source: 'Currency Price Scan',
          boundingBox: { x: 20, y: 62, width: 60, height: 10, label: `₹${num}` }
        };
      }
    }
  }

  // =========================================================================
  // STRATEGY 5: STANDALONE SLASH-DASH NOTATION ("489/-" or "489.00/-")
  // Extremely common in Indian retail printing
  // =========================================================================
  for (const line of allLines) {
    if (isDisqualifiedLine(line)) continue;

    const slashDashMatch = line.match(/(?:^|[\s:₹])([0-9]{2,5}(?:\.[0-9]{2})?)\s*(?:\/\-|\/\=)/i);
    if (slashDashMatch && slashDashMatch[1]) {
      const num = parsePriceNumber(slashDashMatch[1]);
      if (num !== null) {
        const hasTax = taxCheck.present;
        return {
          detected: true,
          numeric: num,
          currency: '₹',
          displayValue: `₹ ${num.toFixed(2).replace(/\.00$/, '')}/- ${hasTax ? '(INCL. OF ALL TAXES)' : ''}`.trim(),
          rawMatch: slashDashMatch[0],
          hasTaxStatement: hasTax,
          taxPhraseDetected: taxCheck.phrase,
          isDefective: !hasTax,
          confidence: 0.88,
          strategy: 'Indian Slash-Dash Suffix Price Match (/-)',
          status: 'DETECTED',
          source: 'Currency Price Scan',
          boundingBox: { x: 20, y: 65, width: 60, height: 10, label: `₹${num}/-` }
        };
      }
    }
  }

  // =========================================================================
  // STRATEGY 6: OPTICAL DEGRADATION & AMBIGUOUS TEXT (REVIEW, NOT MISSING!)
  // If words like "MRP" or currency were detected, but the digits were illegible
  // =========================================================================
  for (const line of allLines) {
    if (/mrp|m\.r\.p|m8p|retail\s*price/i.test(line)) {
      return {
        detected: false,
        numeric: 0,
        currency: '₹',
        displayValue: 'MRP text detected but numeric value partially illegible',
        rawMatch: line,
        hasTaxStatement: taxCheck.present,
        isDefective: true,
        confidence: 0.60,
        strategy: 'Ambiguity Guard: Optical verification required',
        status: 'REVIEW',
        reviewReason: `Packaging displays MRP indicator ('${line.trim()}'), but numeral requires inspection on secondary surface or stereomicroscope.`,
        source: 'Typo-Tolerant Engine',
        boundingBox: { x: 20, y: 60, width: 60, height: 8, label: 'MRP (Under Review)' }
      };
    }
  }

  // If completely absent after all strategies:
  return null;
}
