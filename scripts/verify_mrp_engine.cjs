// Verification script for MRP Detection Engine

// In-line mirror of detection logic for isolated testing
function cleanOcrPriceDigits(raw) {
  let s = raw.trim();
  s = s.replace(/(\d)[Oo]/g, '$10').replace(/[Oo](\d)/g, '0$1');
  s = s.replace(/(\d)[Bb](\d)/g, '$18$2');
  s = s.replace(/(\d)[Ss]\b/g, '$15');
  s = s.replace(/(\d)[Il]/g, '$11').replace(/[Il](\d)/g, '1$1');
  return s;
}

function checkTaxInclusiveStatement(text) {
  const taxPatterns = [
    /inclusive\s*of\s*all\s*taxes/i,
    /incl\.?\s*of\s*all\s*taxes/i,
    /incl\.?\s*all\s*taxes/i,
    /incl\.?\s*taxes/i,
    /all\s*taxes\s*incl/i
  ];
  for (const p of taxPatterns) {
    const m = text.match(p);
    if (m) return { present: true, phrase: m[0] };
  }
  return { present: false };
}

function isDisqualifiedLine(text) {
  if (/\busp\b|unit\s*sale\s*price|\/g\b|\/ml\b|\/piece\b|\/kg\b|\/l\b/i.test(text)) return true;
  if (/\bnet\s*(?:wt\.?|qty|quantity)\b|\b\d+\s*(?:g|gm|gms|ml|kg|l)\b/i.test(text) && !/mrp|price|₹|rs/i.test(text)) return true;
  if (/nutri|energy|kcal|calorie|fat\b|protein/i.test(text)) return true;
  if (/\bspf\s*\d+\b/i.test(text)) return true;
  if (/^(?:mfd|pkd|mfg|exp|use\s*before|best\s*before)[\s:]*[0-9]{2}[/-][0-9]{2,4}$/i.test(text.trim())) return true;
  return false;
}

function normalizeMrpKeyword(line) {
  return line
    .replace(/\b(?:m8p|nr\s*p|mbp|wrp)\b/gi, 'MRP')
    .replace(/\bm\.r\.p\.?:?/gi, 'MRP')
    .replace(/\bmax(?:imum)?\s*retail\s*price\b/gi, 'MRP')
    .replace(/\bretail\s*price\b/gi, 'MRP');
}

function parsePriceNumber(rawNum) {
  const cleaned = cleanOcrPriceDigits(rawNum).replace(/,/g, '');
  const val = parseFloat(cleaned);
  if (!isNaN(val) && val > 0 && val < 500000) return val;
  return null;
}

function detectMrp(rawText, lines = []) {
  const allLines = lines.length > 0 ? lines : rawText.split('\n').map(l => l.trim()).filter(Boolean);
  const taxCheck = checkTaxInclusiveStatement(rawText);

  // Strategy 1: Direct unified regex
  const directPatterns = [
    /(?:m\.?r\.?p\.?|max(?:imum)?\s*retail\s*price|retail\s*price|m8p|nr\s*p)[\s:]*(?:\(?[^)]*taxes?[^)]*\)?[\s:]*)*(?:₹|rs\.?|inr)?[\s:]*([0-9]+(?:\.[0-9]{1,2})?|\b[0-9]{2,5}\b)[\s]*(?:\/\-|\/\=)?/i,
    /(?:m\.?r\.?p\.?|max(?:imum)?\s*retail\s*price|retail\s*price|m8p|nr\s*p)[\s:]*(?:₹|rs\.?|inr)?[\s:]*([0-9]+(?:\.[0-9]{1,2})?|\b[0-9]{2,5}\b)[\s]*(?:\/\-|\/\=)?/i,
    /(?:₹|rs\.?|inr)[\s:]*([0-9]+(?:\.[0-9]{1,2})?|\b[0-9]{2,5}\b)[\s]*(?:\/\-|\/\=)?/i
  ];

  for (let i = 0; i < allLines.length; i++) {
    const line = allLines[i];
    if (isDisqualifiedLine(line)) continue;
    const normalizedLine = normalizeMrpKeyword(line);

    if (/mrp|price/i.test(normalizedLine)) {
      for (const pat of directPatterns) {
        const m = normalizedLine.match(pat);
        if (m && m[1]) {
          const num = parsePriceNumber(m[1]);
          if (num !== null) {
            const hasTax = checkTaxInclusiveStatement(line).present || taxCheck.present;
            return {
              detected: true,
              numeric: num,
              currency: '₹',
              displayValue: `₹ ${num}/- ${hasTax ? '(INCL. OF ALL TAXES)' : ''}`.trim(),
              status: 'DETECTED',
              strategy: 'Direct Packaging MRP Pattern Scan'
            };
          }
        }
      }
    }
  }

  // Strategy 2: Multi-line spatial proximity
  for (let i = 0; i < allLines.length; i++) {
    const currentLine = allLines[i];
    const isMrpKeyword = /^(?:m\.?r\.?p\.?|max(?:imum)?\s*retail\s*price|retail\s*price|m8p|nr\s*p|price)[\s:]*$/i.test(currentLine.trim()) ||
      /mrp\b/i.test(currentLine);

    if (isMrpKeyword && !isDisqualifiedLine(currentLine)) {
      for (let offset = 1; offset <= 2; offset++) {
        if (i + offset < allLines.length) {
          const nextLine = allLines[i + offset].trim();
          if (isDisqualifiedLine(nextLine)) continue;
          const priceMatch = nextLine.match(/(?:₹|rs\.?|inr)?[\s:]*([0-9]+(?:\.[0-9]{1,2})?|\b[0-9]{2,5}\b)[\s]*(?:\/\-|\/\=)?/i);
          if (priceMatch && priceMatch[1]) {
            const num = parsePriceNumber(priceMatch[1]);
            if (num !== null) {
              const hasTax = checkTaxInclusiveStatement(currentLine + ' ' + nextLine).present || taxCheck.present;
              return {
                detected: true,
                numeric: num,
                currency: '₹',
                displayValue: `₹ ${num}/- ${hasTax ? '(INCL. OF ALL TAXES)' : ''}`.trim(),
                status: 'DETECTED',
                strategy: 'Multi-Line Spatial Proximity Stitching'
              };
            }
          }
        }
      }
    }
  }

  // Strategy 4: Currency-led standalone
  for (const line of allLines) {
    if (isDisqualifiedLine(line)) continue;
    const currencyMatch = line.match(/(?:₹|rs\.?|inr)[\s:]*([0-9]+(?:\.[0-9]{1,2})?|\b[0-9]{2,5}\b)[\s]*(?:\/\-|\/\=)?/i);
    if (currencyMatch && currencyMatch[1]) {
      const num = parsePriceNumber(currencyMatch[1]);
      if (num !== null) {
        const hasTax = checkTaxInclusiveStatement(line).present || taxCheck.present;
        return {
          detected: true,
          numeric: num,
          currency: '₹',
          displayValue: `₹ ${num}/- ${hasTax ? '(INCL. OF ALL TAXES)' : ''}`.trim(),
          status: 'DETECTED',
          strategy: 'Currency-Led Packaging Price Detection'
        };
      }
    }
  }

  // Strategy 5: Standalone slash-dash
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
          displayValue: `₹ ${num}/- ${hasTax ? '(INCL. OF ALL TAXES)' : ''}`.trim(),
          status: 'DETECTED',
          strategy: 'Indian Slash-Dash Suffix Price Match'
        };
      }
    }
  }

  return null;
}

console.log('====================================================');
console.log('TEST CASE 1: Primary User Prompt Test Case');
console.log('====================================================');
const promptText = `
MRP ₹489/-
USP ₹8.91/g
MFD 02/26
B.NO. B005
USE BEFORE 01/28
Net Wt. 56 g
`;

const res1 = detectMrp(promptText);
console.log('Result 1:', res1);
if (!res1 || res1.numeric !== 489) {
  throw new Error(`Test 1 Failed: Expected MRP 489, got ${JSON.stringify(res1)}`);
}
console.log('✓ TEST 1 PASSED: MRP detected as ₹489/-\n');

console.log('====================================================');
console.log('TEST CASE 2: Multi-line Split (MRP on Line 1, ₹489/- on Line 2)');
console.log('====================================================');
const multilineText = `
MRP
₹489/- (INCL. OF ALL TAXES)
Net Qty: 56g
`;
const res2 = detectMrp(multilineText);
console.log('Result 2:', res2);
if (!res2 || res2.numeric !== 489) {
  throw new Error(`Test 2 Failed: Expected MRP 489, got ${JSON.stringify(res2)}`);
}
console.log('✓ TEST 2 PASSED: Multi-line proximity stitching detected ₹489/-\n');

console.log('====================================================');
console.log('TEST CASE 3: Intervening Tax Phrase');
console.log('====================================================');
const interveningText = `
M.R.P. (INCLUSIVE OF ALL TAXES) ₹489.00
Net Wt: 56 g
`;
const res3 = detectMrp(interveningText);
console.log('Result 3:', res3);
if (!res3 || res3.numeric !== 489) {
  throw new Error(`Test 3 Failed: Expected MRP 489, got ${JSON.stringify(res3)}`);
}
console.log('✓ TEST 3 PASSED: Intervening tax phrase pattern detected ₹489/-\n');

console.log('====================================================');
console.log('TEST CASE 4: Broken OCR Typo (M8P Rs. 489/-)');
console.log('====================================================');
const typoText = `
M8P Rs. 489/-
B.No. 102
`;
const res4 = detectMrp(typoText);
console.log('Result 4:', res4);
if (!res4 || res4.numeric !== 489) {
  throw new Error(`Test 4 Failed: Expected MRP 489, got ${JSON.stringify(res4)}`);
}
console.log('✓ TEST 4 PASSED: Broken OCR normalized detected ₹489/-\n');

console.log('====================================================');
console.log('TEST CASE 5: Standalone Slash-Dash Price Notation (489/-)');
console.log('====================================================');
const slashText = `
Batch: B005
MFD: 02/2026
489/-
incl. of all taxes
`;
const res5 = detectMrp(slashText);
console.log('Result 5:', res5);
if (!res5 || res5.numeric !== 489) {
  throw new Error(`Test 5 Failed: Expected MRP 489, got ${JSON.stringify(res5)}`);
}
console.log('✓ TEST 5 PASSED: Slash-dash notation detected ₹489/-\n');

console.log('====================================================');
console.log('TEST CASE 6: Anti-Confusion Guard (USP not treated as MRP)');
console.log('====================================================');
const uspOnlyText = `
USP ₹8.91/g
Net Wt: 56 g
MFD: 02/26
`;
const res6 = detectMrp(uspOnlyText);
console.log('Result 6 (USP only):', res6);
if (res6 && res6.numeric === 8.91) {
  throw new Error('Test 6 Failed: USP was incorrectly captured as MRP!');
}
console.log('✓ TEST 6 PASSED: USP successfully disqualified from MRP\n');

console.log('🎉 ALL 6 MRP DETECTION TESTS PASSED WITH 100% ACCURACY!');
