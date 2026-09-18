import { SurfaceType, ExtractedDeclaration, InspectionViolation } from '../types';

export interface SamplePackageItem {
  id: string;
  name: string;
  brand: string;
  category: string;
  manufacturer: string;
  packerImporter: string;
  barcode: string;
  batchNumber: string;
  simulatedStatus: 'Compliant' | 'Non-Compliant' | 'Under Review';
  summaryDescription: string;
  images: Array<{
    id: string;
    surface: SurfaceType;
    name: string;
    svgMock: string;
    dimensions: string;
    qualityStatus: 'Good' | 'Fair' | 'Poor';
  }>;
  declarations: ExtractedDeclaration[];
  violations: InspectionViolation[];
  officerNotes: string;
}

export const SAMPLE_PACKAGES: SamplePackageItem[] = [
  // 1. COMPLIANT PRODUCT
  {
    id: 'SAMPLE-COMPLIANT-01',
    name: 'Lakmé Sun Expert Aqua Sun Gel SPF 50',
    brand: 'Lakmé',
    category: 'Personal Care / Sunscreen Gel',
    manufacturer: 'Aero Care Personal Products LLP, Survey 284/2, Naroli, D&NH - 396235',
    packerImporter: 'Hindustan Unilever Limited, Unilever House, Andheri (E), Mumbai - 400099',
    barcode: '8909106031241',
    batchNumber: 'B005',
    simulatedStatus: 'Compliant',
    summaryDescription: 'Fully compliant retail cosmetic formulation. Satisfies all statutory declarations under Legal Metrology Rules, 2011 including Table I font heights and USP exemption.',
    images: [
      {
        id: 'IMG-LK-01',
        surface: 'Front (PDP)',
        name: 'Lakme_AquaGel_Front_PDP.jpg',
        svgMock: 'front-lakme-sunscreen',
        dimensions: '1920 x 1080 px',
        qualityStatus: 'Good'
      },
      {
        id: 'IMG-LK-02',
        surface: 'Back Panel',
        name: 'Lakme_AquaGel_Back_Panel.jpg',
        svgMock: 'back-lakme-sunscreen',
        dimensions: '1920 x 1080 px',
        qualityStatus: 'Good'
      }
    ],
    declarations: [
      {
        id: 'DEC-LK-1',
        declarationType: 'Common or Generic Name',
        extractedValue: 'Sunscreen Skin Gel',
        expectedRequirement: 'Generic commercial name on PDP under Rule 6(1)(b)',
        ruleReference: 'Rule 6(1)(b)',
        surface: 'Front (PDP)',
        status: 'Found',
        confidence: 'High',
        confidenceScore: 0.98,
        officerStatus: 'Verified',
        boundingBox: { x: 15, y: 35, width: 70, height: 12, label: 'Generic Name: Sunscreen Gel' }
      },
      {
        id: 'DEC-LK-2',
        declarationType: 'Net Quantity',
        extractedValue: 'Net Wt.: 56 g',
        expectedRequirement: 'Standard metric SI unit (g) complying with Rule 6(1)(c) and Rule 13',
        ruleReference: 'Rule 6(1)(c) & Rule 13',
        surface: 'Front (PDP)',
        status: 'Found',
        confidence: 'High',
        confidenceScore: 0.99,
        officerStatus: 'Verified',
        boundingBox: { x: 25, y: 84, width: 50, height: 8, label: 'Net Quantity: 56 g' }
      },
      {
        id: 'DEC-LK-3',
        declarationType: 'Retail Sale Price (MRP)',
        extractedValue: 'MRP ₹ 499.00 (INCL. OF ALL TAXES)',
        expectedRequirement: 'Maximum Retail Price with mandatory tax statement under Rule 6(1)(e)',
        ruleReference: 'Rule 6(1)(e)',
        surface: 'Back Panel',
        status: 'Found',
        confidence: 'High',
        confidenceScore: 0.97,
        officerStatus: 'Verified',
        boundingBox: { x: 20, y: 55, width: 60, height: 10, label: 'MRP ₹ 499 (INCL. TAXES)' }
      },
      {
        id: 'DEC-LK-4',
        declarationType: 'Unit Sale Price (USP)',
        extractedValue: 'USP ₹ 8.91/g (Statutory Rule 6(2) Exemption Applied for ≤ 100g)',
        expectedRequirement: 'Unit Sale Price declaration or statutory exemption for packages ≤ 100g',
        ruleReference: 'Rule 6(11) / Rule 6(2)',
        surface: 'Back Panel',
        status: 'Found',
        confidence: 'High',
        confidenceScore: 0.96,
        officerStatus: 'Verified',
        boundingBox: { x: 20, y: 64, width: 60, height: 8, label: 'USP: ₹ 8.91/g' }
      },
      {
        id: 'DEC-LK-5',
        declarationType: 'Date of Packing / Manufacture',
        extractedValue: 'MFD: 02/2026 | USE BEFORE: 01/2028',
        expectedRequirement: 'Month and year of manufacture & expiry under Rule 6(1)(d)',
        ruleReference: 'Rule 6(1)(d) & Rule 6(1)(da)',
        surface: 'Back Panel',
        status: 'Found',
        confidence: 'High',
        confidenceScore: 0.95,
        officerStatus: 'Verified',
        boundingBox: { x: 20, y: 72, width: 60, height: 8, label: 'MFD: 02/26 EXP: 01/28' }
      },
      {
        id: 'DEC-LK-6',
        declarationType: 'Manufacturer Name & Address',
        extractedValue: 'Aero Care Personal Products LLP, Survey 284/2, Naroli, D&NH - 396235',
        expectedRequirement: 'Full postal address with 6-digit PIN code under Rule 6(1)(a) & Rule 10',
        ruleReference: 'Rule 6(1)(a) & Rule 10',
        surface: 'Back Panel',
        status: 'Found',
        confidence: 'High',
        confidenceScore: 0.96,
        officerStatus: 'Verified',
        boundingBox: { x: 10, y: 18, width: 80, height: 12, label: 'Manufacturer with PIN 396235' }
      },
      {
        id: 'DEC-LK-7',
        declarationType: 'Consumer Care / Grievance Redressal',
        extractedValue: 'Toll-Free: 1800-10-22-221 | Email: lever.care@unilever.com',
        expectedRequirement: 'Toll-free helpline and email address under Rule 6(1)(f)',
        ruleReference: 'Rule 6(1)(f)',
        surface: 'Back Panel',
        status: 'Found',
        confidence: 'High',
        confidenceScore: 0.98,
        officerStatus: 'Verified',
        boundingBox: { x: 10, y: 25, width: 80, height: 8, label: 'Consumer Care 1800-10-22-221' }
      },
      {
        id: 'DEC-LK-8',
        declarationType: 'Country of Origin',
        extractedValue: 'Country of Origin: India',
        expectedRequirement: 'Mandatory country of origin under Rule 6(1)(a)',
        ruleReference: 'Rule 6(1)(a)',
        surface: 'Back Panel',
        status: 'Found',
        confidence: 'High',
        confidenceScore: 0.99,
        officerStatus: 'Verified',
        boundingBox: { x: 10, y: 14, width: 40, height: 6, label: 'Origin: India' }
      }
    ],
    violations: [],
    officerNotes: 'Full compliance verified on packaging. All Table I font height thresholds satisfied.'
  },

  // 2. NON-COMPLIANT PRODUCT
  {
    id: 'SAMPLE-VIOLATION-02',
    name: 'Heritage Kacchi Ghani Pure Mustard Oil (1 Litre)',
    brand: 'Heritage Agro',
    category: 'Edible Oils / Agricultural Produce',
    manufacturer: 'Heritage Agro Oil Mills, Alwar, Rajasthan',
    packerImporter: 'Heritage Agro Oil Mills Pvt. Ltd.',
    barcode: '8901234567890',
    batchNumber: 'MOL-2026/08-B',
    simulatedStatus: 'Non-Compliant',
    summaryDescription: 'Edible oil pouch displaying multiple statutory infractions: omission of mandatory tax phrase on MRP, non-standard unit symbols, and incomplete manufacturer postal address without PIN code.',
    images: [
      {
        id: 'IMG-HG-01',
        surface: 'Front (PDP)',
        name: 'Heritage_Mustard_Pouch_Front.jpg',
        svgMock: 'front-mustard',
        dimensions: '1920 x 1080 px',
        qualityStatus: 'Good'
      },
      {
        id: 'IMG-HG-02',
        surface: 'Back Panel',
        name: 'Heritage_Mustard_Pouch_Back.jpg',
        svgMock: 'back-mustard',
        dimensions: '1920 x 1080 px',
        qualityStatus: 'Good'
      }
    ],
    declarations: [
      {
        id: 'DEC-HG-1',
        declarationType: 'Retail Sale Price (MRP)',
        extractedValue: 'MRP ₹ 165.00',
        expectedRequirement: 'Mandatory phrase "(inclusive of all taxes)" under Rule 6(1)(e)',
        ruleReference: 'Rule 6(1)(e)',
        surface: 'Front (PDP)',
        status: 'Defective',
        confidence: 'High',
        confidenceScore: 0.97,
        officerStatus: 'Flagged',
        correctionNotes: 'Violation: Mandatory phrase "(inclusive of all taxes)" omitted next to MRP.',
        boundingBox: { x: 15, y: 85, width: 70, height: 8, label: 'MRP Missing Tax Phrase' }
      },
      {
        id: 'DEC-HG-2',
        declarationType: 'Net Quantity',
        extractedValue: 'Net Quantity: 1 Litre (910 gms)',
        expectedRequirement: 'Standard SI metric symbol "g" without plural "s" under Rule 13',
        ruleReference: 'Rule 13(1)',
        surface: 'Front (PDP)',
        status: 'Defective',
        confidence: 'High',
        confidenceScore: 0.96,
        officerStatus: 'Flagged',
        correctionNotes: 'Violation: Non-standard unit symbol "gms" used. SI metric standards mandate "g".',
        boundingBox: { x: 20, y: 77, width: 60, height: 8, label: 'Non-Standard Unit (gms)' }
      },
      {
        id: 'DEC-HG-3',
        declarationType: 'Manufacturer Name & Address',
        extractedValue: 'Heritage Agro Oil Mills, Matsya Industrial Area, Alwar, Rajasthan',
        expectedRequirement: 'Complete geographical postal address including 6-digit PIN code under Rule 10(1)',
        ruleReference: 'Rule 6(1)(a) & Rule 10',
        surface: 'Back Panel',
        status: 'Defective',
        confidence: 'High',
        confidenceScore: 0.94,
        officerStatus: 'Flagged',
        correctionNotes: 'Violation: Manufacturer address declared without mandatory 6-digit postal PIN code.',
        boundingBox: { x: 10, y: 15, width: 80, height: 12, label: 'Missing Postal PIN Code' }
      }
    ],
    violations: [
      {
        id: 'VIO-HG-01',
        violationType: 'Omission of Mandatory Tax Declaration on MRP',
        ruleReference: 'Rule 6(1)(e) of Legal Metrology Rules',
        statutoryActClause: 'Rule 6(1)(e) read with Section 36(1) of Legal Metrology Act, 2009',
        product: 'Heritage Kacchi Ghani Pure Mustard Oil',
        surface: 'Front (PDP)',
        description: "Retail Sale Price declared as 'MRP ₹ 165.00' without the mandatory statutory phrase '(inclusive of all taxes)'.",
        severity: 'High',
        officerStatus: 'Accepted',
        evidenceImage: '',
        evidenceBoundingBox: { x: 15, y: 85, width: 70, height: 8, label: 'Rule 6(1)(e) Tax Omission' },
        recommendedPenalty: 'Issue statutory compounding notice under Section 36(1) (Compoundable fee up to ₹25,000 under Rule 32A).',
        reportedDate: new Date().toISOString().slice(0, 10)
      },
      {
        id: 'VIO-HG-02',
        violationType: 'Non-Standard Metric Unit in Net Quantity',
        ruleReference: 'Rule 13 of Legal Metrology Rules',
        statutoryActClause: 'Rule 13(1) read with Section 36(1)',
        product: 'Heritage Kacchi Ghani Pure Mustard Oil',
        surface: 'Front (PDP)',
        description: "Secondary mass declared as '910 gms'. Rule 13 prohibits plural 's' on metric units; mandatory symbol is 'g'.",
        severity: 'Low',
        officerStatus: 'Accepted',
        evidenceImage: '',
        evidenceBoundingBox: { x: 20, y: 77, width: 60, height: 8, label: 'Rule 13 Unit Breach' },
        recommendedPenalty: 'Direct manufacturer to modify packaging gravure cylinder to comply with SI symbol conventions.',
        reportedDate: new Date().toISOString().slice(0, 10)
      },
      {
        id: 'VIO-HG-03',
        violationType: 'Incomplete Manufacturer Address (Missing PIN Code)',
        ruleReference: 'Rule 6(1)(a) read with Rule 10',
        statutoryActClause: 'Rule 10(1) read with Section 36(1)',
        product: 'Heritage Kacchi Ghani Pure Mustard Oil',
        surface: 'Back Panel',
        description: 'Manufacturer address declared as Alwar, Rajasthan without the mandatory 6-digit Indian postal PIN code.',
        severity: 'Medium',
        officerStatus: 'Accepted',
        evidenceImage: '',
        evidenceBoundingBox: { x: 10, y: 15, width: 80, height: 12, label: 'Rule 10 Missing PIN' },
        recommendedPenalty: 'Issue notice to furnish registered premises certification under Rule 10 / Rule 27.',
        reportedDate: new Date().toISOString().slice(0, 10)
      }
    ],
    officerNotes: 'Notice issued to manufacturer under Section 36(1). Compounding sum calculated at ₹25,000 under Rule 32A.'
  },

  // 3. NEEDS-REVIEW PRODUCT
  {
    id: 'SAMPLE-REVIEW-03',
    name: 'Swachh Bharat Concentrated Washing Powder (1.0 kg)',
    brand: 'Swachh Bharat',
    category: 'Household Detergents',
    manufacturer: 'Hindustan Homecare Products, Indore, MP - 452015',
    packerImporter: 'Hindustan Homecare Products',
    barcode: '8904455667788',
    batchNumber: 'BATCH-2026/09',
    simulatedStatus: 'Under Review',
    summaryDescription: 'Detergent pack with partially smeared thermal inkjet stamp. Demonstrates optical blur detection, confidence scoring, uncertain character tagging (0?/2026), and strict anti-hallucination safeguards.',
    images: [
      {
        id: 'IMG-SB-01',
        surface: 'Front (PDP)',
        name: 'Swachh_Bharat_Detergent_Front.jpg',
        svgMock: 'front-detergent',
        dimensions: '1920 x 1080 px',
        qualityStatus: 'Fair'
      }
    ],
    declarations: [
      {
        id: 'DEC-SB-1',
        declarationType: 'Date of Packing / Manufacture',
        extractedValue: 'Pkd: 0? / 2026 (Smeared Inkjet Stamp)',
        expectedRequirement: 'Legible month and year of pre-packing under Rule 6(1)(d)',
        ruleReference: 'Rule 6(1)(d)',
        surface: 'Front (PDP)',
        status: 'Under Review',
        confidence: 'Low',
        confidenceScore: 0.48,
        officerStatus: 'Pending',
        correctionNotes: 'Unclear text detected: Month character obscured by ink smudge. System anti-hallucination safeguard triggered; requires physical officer verification.',
        boundingBox: { x: 20, y: 68, width: 60, height: 12, label: 'Smeared Date: Pkd 0?/2026' }
      },
      {
        id: 'DEC-SB-2',
        declarationType: 'Retail Sale Price (MRP)',
        extractedValue: 'MRP ₹ 135.00 (incl. of all taxes)',
        expectedRequirement: 'Maximum Retail Price with tax declaration',
        ruleReference: 'Rule 6(1)(e)',
        surface: 'Front (PDP)',
        status: 'Found',
        confidence: 'High',
        confidenceScore: 0.94,
        officerStatus: 'Verified',
        boundingBox: { x: 20, y: 58, width: 60, height: 8, label: 'MRP ₹ 135 (incl. taxes)' }
      },
      {
        id: 'DEC-SB-3',
        declarationType: 'Net Quantity',
        extractedValue: 'Net Weight: 1.0 kg',
        expectedRequirement: 'Standard metric SI units under Rule 6(1)(c)',
        ruleReference: 'Rule 6(1)(c)',
        surface: 'Front (PDP)',
        status: 'Found',
        confidence: 'High',
        confidenceScore: 0.96,
        officerStatus: 'Verified',
        boundingBox: { x: 20, y: 48, width: 60, height: 8, label: 'Net Weight: 1.0 kg' }
      }
    ],
    violations: [],
    officerNotes: 'Thermal inkjet print head appears defective on manufacturing line. Physical lot sample inspected to confirm packing month.'
  }
];
