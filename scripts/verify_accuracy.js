// Direct verification of optical and AI extraction logic
import assert from 'node:assert';

// Import compiled dist or duplicate pure logic to verify regex behavior directly
const NUTRITIONAL_LINE_REGEX =
  /nutri|energy|kcal|fat\b|saturat|mufa|pufa|cholesterol|carbohydrate|sugar|protein|sodium|potassium|vitamin|mineral|approx\.\s*per|per\s*100|serving\s*size|\/100g|\/100ml|100g\)|100ml\)|table\s*1/i;

const QUANTITY_PATTERN =
  /(?:net\s*(?:quantity|content|weight|vol(?:\.|ume)?|wt\.?|mass|qty\.?)|contents?|volume|weight)\s*(?:is|:|-)?\s*([0-9]+(?:\.[0-9]+)?)\s*(kg|g|gm|gms|grams?|l|litre|litres?|liter|liters?|ml|millilitre|millilitres?|unit|units|n|pcs|pieces?|tablets?|capsules?)\b/i;

function cleanOcrText(text) {
  return text
    .replace(/\bnel\s*qty\b/gi, 'net qty')
    .replace(/\bnet\s*oty\b/gi, 'net qty')
    .replace(/\bnet\s*qly\b/gi, 'net qty')
    .replace(/\bnel\s*wt\b/gi, 'net wt')
    .replace(/\bnct\s*wt\b/gi, 'net wt')
    .replace(/\bnct\s*qty\b/gi, 'net qty')
    .replace(/\bnet\s*w[tl][.:;]?\s*/gi, 'net wt: ')
    .replace(/\bnet\s*(?:wt\.?|weight|qty\.?|quantity|vol\.?|volume|content|contents)?[:.\-\s]+(\d+(?:\.\d+)?)\s+(?:9|q)\b/gi, 'net qty: $1 g')
    .replace(/\bnet\s*(?:wt\.?|weight|qty\.?|quantity|vol\.?|volume|content|contents)?[:.\-\s]+(\d+(?:\.\d+)?)\s*m[1liI|]\b/gi, 'net qty: $1 ml');
}

const explicitNetPattern = /(?:net\s*(?:quantity|qty\.?|weight|wt\.?|vol\.?|volume|content|contents|mass|amount|pack\s*size)?[:.\-\s]*)\s*(\d+(?:\.\d+)?)\s*(kg|g|gm|gms|gram|grams|ml|mls|millilitre|milliliter|l|lt|ltr|litre|litres|liter|count|units?|pieces?|pcs|tabs?|caps?|n|u)\b/i;

function extractNetQuantity(rawText, lines) {
  const cleanLines = (lines && lines.length > 0 ? lines : rawText.split('\n'))
    .map(cleanOcrText)
    .filter(l => l.trim().length > 0);

  // Strategy 1: Explicit statutory label keywords across individual lines
  for (const line of cleanLines) {
    if (NUTRITIONAL_LINE_REGEX.test(line)) continue;
    const match = line.match(explicitNetPattern);
    if (match) {
      const numeric = parseFloat(match[1]);
      const unit = match[2].toLowerCase();
      if (!isNaN(numeric) && numeric > 0) {
        return { value: numeric, unit, display: `${numeric} ${unit}` };
      }
    }
  }

  // Strategy 2: Multi-line detection (Line 1: "NET WT.", Line 2: "56 g")
  for (let i = 0; i < cleanLines.length - 1; i++) {
    const l1 = cleanLines[i];
    const l2 = cleanLines[i + 1];
    if (NUTRITIONAL_LINE_REGEX.test(l1) || NUTRITIONAL_LINE_REGEX.test(l2)) continue;
    if (/\b(?:net\s*(?:wt\.?|weight|qty\.?|quantity|content))\b/i.test(l1)) {
      const standAloneMatch = l2.match(/^([0-9]+(?:\.[0-9]+)?)\s*(kg|g|gm|gms|l|ml|unit|n|pcs)\b/i);
      if (standAloneMatch) {
        const numeric = parseFloat(standAloneMatch[1]);
        const unit = standAloneMatch[2].toLowerCase();
        if (!isNaN(numeric) && numeric > 0) {
          return { value: numeric, unit, display: `${numeric} ${unit}` };
        }
      }
    }
  }

  return null;
}

// Test Case 1: Lakmé Sunscreen with 100g Nutrition Table
const lakmeSampleLines = [
  'LAKME SUN EXPERT SPF 50 PA+++ ULTRA MATTE GEL',
  'NET WT.: 56 g',
  'MRP: Rs. 499.00 (inclusive of all taxes)',
  'Mfg. Date: 02/2026',
  'Hindustan Unilever Ltd., B.D. Sawant Marg, Mumbai 400099',
  'NUTRITIONAL VALUES (Per 100g):',
  'Energy: 450 kcal',
  'Total Fat: 100g'
];

const result1 = extractNetQuantity(lakmeSampleLines.join('\n'), lakmeSampleLines);
console.log('Test 1 (Lakme Sunscreen 56g with 100g table):', result1);
assert.strictEqual(result1?.value, 56, 'Should extract 56g, NOT 100g!');
assert.strictEqual(result1?.display, '56 g');

// Test Case 2: Multi-line label (Line 1 = "NET WT.", Line 2 = "56 g")
const multiLine = [
  'LAKME SUN EXPERT',
  'NET WT.',
  '56 g',
  'Nutritional Information Approx. per 100g',
  'Fat 100g'
];
const result2 = extractNetQuantity(multiLine.join('\n'), multiLine);
console.log('Test 2 (Multi-line Net WT on line 1, 56g on line 2):', result2);
assert.strictEqual(result2?.value, 56, 'Multi-line must extract 56g!');

// Test Case 3: OCR typo (Nel Wt: 56 9)
const typoSample = [
  'Nel Wt: 56 9',
  'Per 100g serving',
  'Total Fat: 100g'
];
const result3 = extractNetQuantity(typoSample.join('\n'), typoSample);
console.log('Test 3 (OCR Typo Nel Wt: 56 9):', result3);
assert.strictEqual(result3?.value, 56, 'Typo normalized to 56 g!');

// Test Case 4: General snack with 42g Net Quantity and 100g Nutritional Table
const snackSample = [
  'CRUNCHY POTATO CHIPS',
  'Net Quantity: 42g',
  'NUTRITIONAL FACTS',
  'Approx. values per 100g:',
  'Carbohydrate: 55g',
  'Total Fat: 32g',
  'Energy per 100g: 540 kcal'
];
const result4 = extractNetQuantity(snackSample.join('\n'), snackSample);
console.log('Test 4 (Snack 42g with nutrition table):', result4);
assert.strictEqual(result4?.value, 42);

console.log('\n ALL 4 TESTS PASSED ACCURATELY! ZERO 100g FALSE POSITIVES!');
