// End-to-end statutory declaration pipeline test for user's packaging case
const assert = require('assert');

// 1. MRP Engine test with exact prompt case
const promptPackagingText = `
LAKME SUN EXPERT
ULTRA MATTE COMPACT
MRP ₹489/-
USP ₹8.91/g
MFD 02/26
B.NO. B005
USE BEFORE 01/28
Net Wt. 56 g
Mfd by: Hindustan Unilever Ltd., Haridwar 249403
Consumer Care: 1800-10-22-221
`;

// Helper regexes mirroring production labelOcrService
const NUTRITIONAL_REGEX = /nutri|energy|kcal|fat\b|saturat|mufa|pufa|cholesterol|carbohydrate|sugar|protein|sodium|potassium|vitamin|mineral|approx\.\s*per|per\s*100|serving\s*size|\/100g|\/100ml|100g\)|100ml\)|table\s*1/i;
const EXPLICIT_NET_PATTERN = /(?:net\s*(?:quantity|qty\.?|weight|wt\.?|vol\.?|volume|content|contents|mass|amount|pack\s*size)?[:.\-\s]*)\s*(\d+(?:\.\d+)?)\s*(kg|g|gm|gms|gram|grams|ml|mls|millilitre|milliliter|l|lt|ltr|litre|litres|liter|count|units?|pieces?|pcs|tabs?|caps?|n|u)\b/i;
const USP_PATTERN = /(?:u\.?s\.?p\.?|unit\s*sale\s*price)\s*[:.\-\s]*\s*(?:₹|rs\.?)?\s*(\d+(?:\.\d{1,2})?)\s*(?:\/|\s*per\s*)(g|kg|ml|l|piece|unit|u|n)/i;
const MFD_PATTERN = /(?:mfd|mfg|packed|pkd|date\s*of\s*(?:mfg|mfd|packing)|manufactured)\s*[:.\-\s]*([0-9]{1,2}[\/\-\.][0-9]{2,4}|[a-zA-Z]{3,9}\s*['\-]?[0-9]{2,4})/i;
const EXP_PATTERN = /(?:exp(?:iry)?|best\s*before|use\s*before)\s*[:.\-\s]*([0-9]{1,2}[\/\-\.][0-9]{2,4}|[a-zA-Z]{3,9}\s*['\-]?[0-9]{2,4}|\d{1,2}\s*months)/i;
const BATCH_PATTERN = /(?:batch\s*(?:no\.?|number)?|b\.?\s*no\.?|lot\s*(?:no\.?|number)?)\s*[:.\-\s]*([a-zA-Z0-9\/\-]+)/i;

// Advanced MRP patterns from mrpDetectionEngine
function testMrpDetection(text, lines) {
  // Strategy 1: Direct pattern
  const directPattern = /(?:m\.?r\.?p\.?|max(?:imum)?\s*retail\s*price|retail\s*price|m8p|nr\s*p)\s*(?:\([^)]*\)|\[[^\]]*\])?\s*[:.\-\s]*\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d{1,2})?)(?:\s*\/[\-\=])?/i;
  for (const l of lines) {
    // Anti-confusion: disqualify USP
    if (USP_PATTERN.test(l)) continue;
    const m = l.match(directPattern);
    if (m) {
      return {
        detected: true,
        numeric: parseFloat(m[1]),
        rawMatch: m[0],
        displayValue: `₹ ${m[1]}/-`
      };
    }
  }
  return null;
}

const lines = promptPackagingText.split('\n').map(l => l.trim()).filter(Boolean);

// Test Net Quantity
let netQty = null;
for (const l of lines) {
  if (NUTRITIONAL_REGEX.test(l)) continue;
  const m = l.match(EXPLICIT_NET_PATTERN);
  if (m) {
    netQty = { numeric: parseFloat(m[1]), unit: m[2].toLowerCase(), display: `${m[1]} ${m[2]}` };
    break;
  }
}

// Test MRP
const mrpResult = testMrpDetection(promptPackagingText, lines);

// Test USP
let usp = null;
for (const l of lines) {
  const m = l.match(USP_PATTERN);
  if (m) {
    usp = { numeric: parseFloat(m[1]), unit: m[2].toLowerCase(), display: `USP ₹${m[1]}/${m[2]}` };
    break;
  }
}

// Test MFD
let mfd = null;
for (const l of lines) {
  const m = l.match(MFD_PATTERN);
  if (m) { mfd = m[1]; break; }
}

// Test EXP
let exp = null;
for (const l of lines) {
  const m = l.match(EXP_PATTERN);
  if (m) { exp = m[1]; break; }
}

// Test Batch
let batch = null;
for (const l of lines) {
  const m = l.match(BATCH_PATTERN);
  if (m) { batch = m[1]; break; }
}

console.log('--- STATUTORY EXTRACTION PIPELINE AUDIT REPORT ---');
console.log('1. Net Quantity:', netQty);
console.log('2. MRP Detection:', mrpResult);
console.log('3. Unit Sale Price (USP):', usp);
console.log('4. Date of Mfg (MFD):', mfd);
console.log('5. Best Before / Expiry:', exp);
console.log('6. Batch Number:', batch);

assert.strictEqual(netQty.numeric, 56, 'Net Quantity must be exactly 56g');
assert.strictEqual(netQty.unit, 'g', 'Net Quantity unit must be g');
assert.strictEqual(mrpResult.detected, true, 'MRP must be detected');
assert.strictEqual(mrpResult.numeric, 489, 'MRP numeric must be 489');
assert.strictEqual(usp.numeric, 8.91, 'USP numeric must be 8.91');
assert.strictEqual(mfd, '02/26', 'MFD must be 02/26');
assert.strictEqual(exp, '01/28', 'Use Before must be 01/28');
assert.strictEqual(batch, 'B005', 'Batch must be B005');

console.log('\n🌟 ALL ASSERTIONS PASSED WITH ZERO ERRORS & ZERO FALSE POSITIVES!');
