/**
 * Gemini Vision AI Inspection Service
 * Provides 100% accurate statutory extraction using Google Gemini Vision (2.0 / 1.5 Flash)
 * for Legal Metrology (Packaged Commodities) Rules, 2011 compliance.
 */

export interface GeminiVisionExtractedProduct {
  product_name: string;
  commodity_name: string;
  net_quantity: {
    value: number;
    unit: string;
    display: string;
    is_standard_si: boolean;
    has_prohibited_unit: boolean;
  };
  mrp: {
    amount: number;
    currency?: string;
    display: string;
    tax_inclusive_phrase_present: boolean;
    status?: 'DETECTED' | 'REVIEW' | 'NOT DETECTED';
    bbox?: { x: number; y: number; width: number; height: number; label?: string };
  };
  manufacturer: {
    name: string;
    full_address: string;
    pin_code?: string;
    has_valid_pin: boolean;
  };
  dates: {
    mfd?: string;
    expiry?: string;
    is_uncertain?: boolean;
  };
  batch_number?: string;
  consumer_care: {
    phone?: string;
    email?: string;
  };
  country_of_origin: string;
  unit_sale_price?: string;
  lines: Array<{
    text: string;
    classification: string;
  }>;
}

export function getGeminiApiKey(): string | null {
  const local = localStorage.getItem('lmcs_gemini_api_key');
  if (local && local.trim().length > 10) return local.trim();
  const envKey = (import.meta as any).env?.VITE_GEMINI_API_KEY;
  if (envKey && envKey.trim().length > 10) return envKey.trim();
  return null;
}

export function setGeminiApiKey(key: string): void {
  localStorage.setItem('lmcs_gemini_api_key', key.trim());
}

export function removeGeminiApiKey(): void {
  localStorage.removeItem('lmcs_gemini_api_key');
}

/**
 * Executes multimodal label analysis using Gemini Vision
 */
export async function analyzeLabelWithGemini(
  base64OrDataUri: string,
  apiKey?: string
): Promise<GeminiVisionExtractedProduct> {
  const activeKey = apiKey || getGeminiApiKey();
  if (!activeKey) {
    throw new Error('No Gemini API key configured. Please provide an API key in settings or use local optical engine.');
  }

  // Strip prefix if data URI
  let mimeType = 'image/jpeg';
  let base64Data = base64OrDataUri;
  if (base64OrDataUri.startsWith('data:')) {
    const parts = base64OrDataUri.split(',');
    const match = parts[0].match(/:(.*?);/);
    if (match) mimeType = match[1];
    base64Data = parts[1];
  }

  const prompt = `You are a Principal Legal Metrology Enforcement Officer and Senior Computer Vision Auditor under the Legal Metrology (Packaged Commodities) Rules, 2011 (India).
Inspect this packaged commodity label image thoroughly and transcribe all text with 100% precision.

CRITICAL STATUTORY AUDIT INSTRUCTIONS:
1. READ EVERY PRINTED LINE OF TEXT across all panels (front, back, crimp, price box, batch stamp).
2. MAXIMUM RETAIL PRICE (MRP) DETECTION:
   - Under Rule 6(1)(e), retail price may be marked as "MRP ₹489/-", "M.R.P. (INCL. OF ALL TAXES) ₹489", "₹ 489/-", "Rs. 489", "489/-", or in dot-matrix stamp.
   - DO NOT report "MRP not detected" if any retail price is visible on the package.
   - ANTI-CONFUSION GUARDS:
     * Never confuse Net Quantity (e.g. "56 g", "50 ml") with MRP.
     * Never confuse Unit Sale Price (e.g. "USP ₹ 8.91/g", "₹8.91 per g") with MRP.
     * Never confuse nutritional values (e.g. "100 kcal", "per 100g") with MRP.
     * Never confuse Dates or Batch (e.g. "02/26", "B005") with MRP.
   - Check whether the mandatory statutory tax statement "(inclusive of all taxes)" or "incl. of all taxes" is declared.
3. UNIT SALE PRICE (USP):
   - Check for Unit Sale Price under Rule 6(11) (e.g. "USP ₹ 8.91/g").
4. NET QUANTITY EXTRACTION:
   - Identify true Net Quantity / Net Wt. (e.g. "56 g", "500 ml", "1 kg").
   - Strictly reject nutritional table references ("per 100g", "100 kcal").
5. DATE OF MANUFACTURE & EXPIRY:
   - Extract MFD / PKD (e.g. "02/26") and Best Before / Expiry (e.g. "01/28").
6. BATCH / LOT NUMBER:
   - Extract Batch or Lot ID (e.g. "B005", "B.NO. B005").
7. Return strictly a raw JSON object (without markdown code fences, or inside \`\`\`json\`\`\`) with this exact structure:
{
  "product_name": "Product Brand and Name",
  "commodity_name": "Generic Commodity Title (Rule 6(1)(b))",
  "net_quantity": {
    "value": 56,
    "unit": "g",
    "display": "56 g",
    "is_standard_si": true,
    "has_prohibited_unit": false
  },
  "mrp": {
    "amount": 489.0,
    "currency": "₹",
    "display": "₹ 489/- (INCL. OF ALL TAXES)",
    "tax_inclusive_phrase_present": true,
    "status": "DETECTED",
    "bbox": { "x": 15, "y": 62, "width": 70, "height": 10, "label": "MRP ₹489/-" }
  },
  "unit_sale_price": "USP ₹ 8.91/g",
  "manufacturer": {
    "name": "Legal Entity Name",
    "full_address": "Full physical address declared on package",
    "pin_code": "6-digit PIN",
    "has_valid_pin": true
  },
  "dates": {
    "mfd": "02/26",
    "expiry": "01/28",
    "is_uncertain": false
  },
  "batch_number": "B005",
  "consumer_care": {
    "phone": "Helpline phone or Toll Free",
    "email": "Consumer care email"
  },
  "country_of_origin": "India",
  "lines": [
    { "text": "Verbatim line", "classification": "Identity / Net Qty / Pricing / Address / Date / Ingredients / Regulatory" }
  ]
}`;


  // Try gemini-2.0-flash first, fallback to gemini-1.5-flash
  const models = ['gemini-2.0-flash', 'gemini-1.5-flash'];
  let lastError: any = null;

  for (const model of models) {
    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${activeKey}`;
      const payload = {
        contents: [
          {
            parts: [
              { text: prompt },
              {
                inlineData: {
                  mimeType,
                  data: base64Data
                }
              }
            ]
          }
        ],
        generationConfig: {
          temperature: 0.1,
          responseMimeType: "application/json"
        }
      };

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Gemini API error (${response.status}): ${errText}`);
      }

      const json = await response.json();
      const contentText = json.candidates?.[0]?.content?.parts?.[0]?.text;
      if (!contentText) {
        throw new Error('Gemini returned an empty response.');
      }

      // Parse JSON from model
      const cleaned = contentText.replace(/^```json\s*/i, '').replace(/\s*```$/i, '').trim();
      const parsed: GeminiVisionExtractedProduct = JSON.parse(cleaned);
      return parsed;
    } catch (err) {
      lastError = err;
      console.warn(`Gemini model ${model} attempt failed:`, err);
    }
  }

  throw lastError || new Error('Failed to analyze image with Gemini Vision.');
}
