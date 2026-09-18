import { LegalRuleItem } from '../types';

export const LEGAL_RULES: LegalRuleItem[] = [
  {
    id: 'RULE-1',
    ruleNo: 'Rule 1',
    subRule: 'Sub-rule (1)–(2)',
    title: 'Short Title and Commencement',
    requirement: '(1) These rules may be called the Legal Metrology (Packaged Commodities) Rules, 2011. (2) They shall come into force on the 1st day of April, 2011.',
    applicableDeclaration: 'Statutory Authority & Title',
    category: 'Preliminary & Governance',
    prescribedParameters: 'All pre-packaged commodities manufactured, packed, imported or sold across India on or after April 1, 2011 fall under these rules.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011, Ministry of Consumer Affairs, Food & Public Distribution',
    penalProvision: 'Enforcement under Section 18 and Section 36 of Legal Metrology Act, 2009',
    lastUpdated: '2011-04-01',
    officerGuidance: 'Establishes jurisdiction for inspecting, testing, and seizing non-compliant packaged commodities.'
  },
  {
    id: 'RULE-2',
    ruleNo: 'Rule 2',
    subRule: 'Clauses (a)–(s)',
    title: 'Definitions and Statutory Interpretations',
    requirement: 'Defines statutory terms including: Act, consumer, dealer, industrial consumer, institutional consumer, e-commerce, e-commerce entity, marketplace based model of e-commerce, manufacturer, maximum permissible error, net quantity, packer, principal display panel, quantity, retail dealer, retail package, wholesale dealer, and wholesale package.',
    applicableDeclaration: 'Statutory Definitions & Classifications',
    category: 'Preliminary & Governance',
    prescribedParameters: 'Defines Principal Display Panel (PDP), Net Quantity, Retail Package, Maximum Permissible Error (MPE), and E-Commerce requirements.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Standard definitions applicable to all contraventions under the Act',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Check package classification (Retail vs Wholesale vs Institutional) to determine applicable statutory clauses.'
  },
  {
    id: 'RULE-3',
    ruleNo: 'Rule 3',
    subRule: 'Clauses (a)–(c)',
    title: 'Application of Chapter II (Scope & Non-Applicability Thresholds)',
    requirement: 'The provisions of Chapter II do not apply to: (a) packages containing a quantity of more than 25 kilogram or 25 litre; (b) cement, fertilizer and agricultural farm produce sold in bags above 50 kilogram; and (c) packaged commodities meant for industrial consumers or institutional consumers.',
    applicableDeclaration: 'Commercial Package Scope & Bulk Exemptions',
    category: 'Scope & Exemptions',
    prescribedParameters: 'Retail consumer protection rules apply to packages <= 25 kg / 25 L (or <= 50 kg for cement/fertilizer). Bulk and institutional sales are exempt from Chapter II requirements.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Non-applicability clause for bulk commercial shipments',
    lastUpdated: '2023-01-01',
    officerGuidance: 'If package exceeds 25 kg/25 L, or is marked "For Industrial / Institutional Use Only", verify buyer status before booking violation.'
  },
  {
    id: 'RULE-4',
    ruleNo: 'Rule 4',
    subRule: 'Rule 4',
    title: 'Regulation for Pre-packing and Sale of Commodities in Packaged Form',
    requirement: 'No person shall pre-pack or cause or permit to be pre-packed any commodity for sale, distribution or delivery unless the package in which the commodity is pre-packed bears, or has a securely affixed label bearing, the declarations required under these Rules. Packages kept within the manufacturer\'s premises without the retail sale price are not by themselves a violation, but packages leaving the premises for their destination must carry all declarations.',
    applicableDeclaration: 'Mandatory Secure Affixing of Statutory Labels',
    category: 'General Packaging Regulations',
    prescribedParameters: 'All pre-packed items leaving premises must bear securely affixed labels with full statutory declarations.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011, Rule 4',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009: Penalty up to ₹25,000 for first offence.',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Ensure labels cannot be easily detached or swapped. Loose tags or missing labels constitute a direct Rule 4 infraction.'
  },
  {
    id: 'RULE-5',
    ruleNo: 'Rule 5',
    subRule: 'Sub-rules (1)–(3)',
    title: 'Specific Commodities to be Packed in Recommended Standard Packages',
    requirement: 'Commodities specified in the Second Schedule shall be packed for sale, distribution or delivery in the standard quantities specified in that Schedule. The competent authority\'s notified standard quantity for an essential commodity prevails where applicable. Promotional groups of retail packages must comply with Rule 6.',
    applicableDeclaration: 'Second Schedule Standard Pack Sizes',
    category: 'Measurement & Quantity',
    prescribedParameters: 'Goods like baby foods, tea, coffee, edible oils, pulses, wheat flour, and biscuits must adhere to rationalized standard pack sizes specified in Second Schedule.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011, Second Schedule',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2022-07-14',
    officerGuidance: 'Check whether the commodity falls under Second Schedule and verify whether net quantity conforms to the prescribed standard sizes.'
  },
  {
    id: 'RULE-6-1-A',
    ruleNo: 'Rule 6',
    subRule: 'Sub-rule (1), Clause (a)',
    title: 'Name and Complete Address of Manufacturer, Packer, Importer & Country of Origin',
    requirement: 'Every package must bear definite, plain and conspicuous declarations of: (a) the name and complete address of the manufacturer, or where manufacturer is not the packer, the manufacturer and packer; for imported products, the importer; and the country of origin for imported products.',
    applicableDeclaration: 'Manufacturer / Packer / Importer Name, Address & Country of Origin',
    category: 'Mandatory Declarations',
    prescribedParameters: 'Must include full geographical address with postal PIN code, state, and clear prefixes ("Mfg by", "Packed by", "Imported by"). Country of origin is mandatory.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011 & Rule 10',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009: Fine up to ₹25,000 (first offence), up to ₹50,000 (second), or up to ₹1,00,000 / 1 year imprisonment (subsequent).',
    lastUpdated: '2024-04-01',
    officerGuidance: 'Check for postal PIN code. A website alone or city without street/industrial area is a violation under Rule 6(1)(a) read with Rule 10.'
  },
  {
    id: 'RULE-6-1-B',
    ruleNo: 'Rule 6',
    subRule: 'Sub-rule (1), Clause (b)',
    title: 'Common or Generic Name of the Commodity',
    requirement: 'The common or generic names of the commodity contained in the package, and in case of packages with more than one product, the name and number or quantity of each product shall be mentioned on the Principal Display Panel.',
    applicableDeclaration: 'Common or Generic Name of Commodity',
    category: 'Mandatory Declarations',
    prescribedParameters: 'Must use recognizable statutory or commercial generic term (e.g. "Sunscreen Lotion", "Mustard Oil", "Basmati Rice") on PDP, not proprietary trademark alone.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Verify generic name appears prominently on the front PDP, not hidden in the fine back-panel ingredients.'
  },
  {
    id: 'RULE-6-1-C',
    ruleNo: 'Rule 6',
    subRule: 'Sub-rule (1), Clause (c)',
    title: 'Net Quantity in Standard SI Metric Units',
    requirement: 'The net quantity in terms of standard unit of weight, measure or number of the commodity contained in the package shall be declared on the Principal Display Panel. Packaging and wrapping materials must be excluded.',
    applicableDeclaration: 'Net Quantity (Mass, Volume, Length, Area, or Number)',
    category: 'Mandatory Declarations',
    prescribedParameters: 'Expressed in metric SI units: g, kg, ml, l/L, m, cm, mm, or N/U for count. Must comply with font height and clear spacing around declaration.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011, Rules 11, 12, 13',
    penalProvision: 'Section 36(1) and Section 39 of Legal Metrology Act, 2009',
    lastUpdated: '2024-01-01',
    officerGuidance: 'Prohibits non-standard units (dozen, score, gross, lbs, oz, kgs, gms). Quantity must correspond to actual consumer contents.'
  },
  {
    id: 'RULE-6-1-D',
    ruleNo: 'Rule 6',
    subRule: 'Sub-rule (1), Clause (d)',
    title: 'Month and Year of Manufacture, Pre-packing or Import',
    requirement: 'The month and year in which the commodity is manufactured or pre-packed or imported shall be declared in clear, indelible characters.',
    applicableDeclaration: 'Date of Manufacture / Pre-packing / Import',
    category: 'Mandatory Declarations',
    prescribedParameters: 'Format: MM/YYYY or Month Year (e.g., "08/2026" or "August 2026"). Indelibly printed, embossed or laser-etched.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-07-01',
    officerGuidance: 'Smudged or illegible thermal batch prints violate Rule 6(1)(d) and Rule 9 (Manner of Declaration).'
  },
  {
    id: 'RULE-6-1-DA',
    ruleNo: 'Rule 6',
    subRule: 'Sub-rule (1), Clause (da)',
    title: 'Best-Before or Use-By Date for Limited Shelf-Life Commodities',
    requirement: 'Best-before or use-by information where applicable shall be declared on every package containing commodities liable to spoilage or limited shelf life.',
    applicableDeclaration: 'Best-Before / Expiry / Use-By Date',
    category: 'Mandatory Declarations',
    prescribedParameters: 'Clear phrasing: "Best before [X] months from packaging" or explicit expiry date DD/MM/YYYY.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Mandatory on food, cosmetics, medicines, and chemical formulations.'
  },
  {
    id: 'RULE-6-1-E',
    ruleNo: 'Rule 6',
    subRule: 'Sub-rule (1), Clause (e)',
    title: 'Retail Sale Price (MRP) Inclusive of All Taxes',
    requirement: 'The retail sale price of the package shall be clearly declared in the form of "Maximum or Max. Retail Price ₹... inclusive of all taxes" or "MRP ₹... incl. of all taxes".',
    applicableDeclaration: 'Retail Sale Price (MRP)',
    category: 'Mandatory Declarations',
    prescribedParameters: 'Must include currency symbol (₹ or Rs.), numerical value, and the statutory phrase "(inclusive of all taxes)" or "(incl. of all taxes)".',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011 & Rule 18',
    penalProvision: 'Section 36(1) & Section 52 of Legal Metrology Act, 2009',
    lastUpdated: '2024-01-01',
    officerGuidance: 'Omission of "(inclusive of all taxes)" is a direct statutory offence. Over-stickering is prohibited under Rule 18(2).'
  },
  {
    id: 'RULE-6-1-F',
    ruleNo: 'Rule 6',
    subRule: 'Sub-rule (1), Clause (f)',
    title: 'Consumer Care & Grievance Redressal Mechanism',
    requirement: 'Name, address, telephone number, and email address of the person or office that can be contacted in case of consumer complaints shall be conspicuously declared on every package.',
    applicableDeclaration: 'Consumer Care Contact Details',
    category: 'Mandatory Declarations',
    prescribedParameters: 'Must include: 1) Officer title/designation, 2) Complete address, 3) Working telephone number/helpline, 4) Valid email address.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-11-01',
    officerGuidance: 'Telephone AND email are both statutory requisites. Mentioning a website alone does not satisfy Rule 6(1)(f).'
  },
  {
    id: 'RULE-6-1-G',
    ruleNo: 'Rule 6',
    subRule: 'Sub-rule (1), Clause (g)',
    title: 'Batch or Lot Number',
    requirement: 'Every package shall bear the batch number or lot number or code number identifying the pre-packing manufacturing run.',
    applicableDeclaration: 'Batch / Lot / Code Number',
    category: 'Mandatory Declarations',
    prescribedParameters: 'Prefixed by "Batch No.", "B.No.", "Lot No.", or indelible manufacturing alphanumeric tracking code.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Essential for product traceability, lot recall, and establishing liability.'
  },
  {
    id: 'RULE-6-11',
    ruleNo: 'Rule 6',
    subRule: 'Sub-rule (11) / Rule 6(2)',
    title: 'Unit Sale Price (USP) Declaration',
    requirement: 'On packages containing more than 1 kg or 1 litre, or packages where unit pricing is mandated, the Unit Sale Price rounded off to nearest rupee or fifty paise shall be declared (e.g., ₹ 0.45 per g, or ₹ 120.00 per kg).',
    applicableDeclaration: 'Unit Sale Price (USP)',
    category: 'Mandatory Declarations',
    prescribedParameters: 'Expressed as ₹ per g, per kg, per ml, per l/L, or per piece/number, clearly declared adjacent to the MRP.',
    source: 'Legal Metrology (Packaged Commodities) Amendment Rules, 2022',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2024-01-01',
    officerGuidance: 'Enables consumers to cross-compare value across different brand package sizes.'
  },
  {
    id: 'RULE-7',
    ruleNo: 'Rule 7',
    subRule: 'Sub-rules (1)–(5)',
    title: 'Principal Display Panel (PDP), Area, Letter & Numeral Height Standards',
    requirement: 'Principal display panel area is calculated based on packaging geometry (rectangular: height x width; cylindrical: 40% of height x circumference; other shapes: 40% of total surface). Height of numerals and letters must strictly comply with Table I, and letter/numeral width must generally be at least one-third of height.',
    applicableDeclaration: 'Principal Display Panel (PDP) & Table I Font Height',
    category: 'Display & Legibility Standards',
    prescribedParameters: 'Area <= 50 cm²: min 1.0mm; 50-100 cm²: min 1.5mm; 100-500 cm²: min 2.5mm; 500-2500 cm²: min 4.0mm; > 2500 cm²: min 6.0mm. Width >= 1/3 of height (except numeral 1 and letter I).',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011, Table I',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Measure font height of Net Quantity and MRP using optical calibration grid against PDP area threshold.',
    fontTable: [
      { area: 'Not exceeding 50 cm²', minHeightNormal: '1.0 mm', minHeightBlowMoulded: '1.5 mm' },
      { area: 'Exceeding 50 cm² but not 100 cm²', minHeightNormal: '1.5 mm', minHeightBlowMoulded: '2.0 mm' },
      { area: 'Exceeding 100 cm² but not 500 cm²', minHeightNormal: '2.5 mm', minHeightBlowMoulded: '4.0 mm' },
      { area: 'Exceeding 500 cm² but not 2500 cm²', minHeightNormal: '4.0 mm', minHeightBlowMoulded: '6.0 mm' },
      { area: 'Exceeding 2500 cm²', minHeightNormal: '6.0 mm', minHeightBlowMoulded: '8.0 mm' }
    ]
  },
  {
    id: 'RULE-8',
    ruleNo: 'Rule 8',
    subRule: 'Sub-rules (1)–(2)',
    title: 'Declaration Where to Appear & Clear Space Surrounding Quantity',
    requirement: 'Every declaration required under the Rules shall appear on the Principal Display Panel. The area surrounding the quantity declaration must be free from printed information, with specified minimum spacing above/below and left/right.',
    applicableDeclaration: 'PDP Placement & Quantity Clear Zone',
    category: 'Display & Legibility Standards',
    prescribedParameters: 'Area surrounding net quantity declaration must maintain clear spacing equal to the height of the numeral above/below and twice the width left/right.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Check that graphics or promotional slogans do not crowd or obscure the net quantity declaration.'
  },
  {
    id: 'RULE-9',
    ruleNo: 'Rule 9',
    subRule: 'Sub-rules (1)–(4)',
    title: 'Manner in which Declaration Shall be Made (Legibility, Contrast & Wrappers)',
    requirement: 'Declarations must be legible and prominent. Numerals of retail sale price and net quantity must be printed, painted or inscribed in a colour contrasting conspicuously with the label background. Declarations must not require reading through a liquid commodity. An outside container or wrapper must also carry declarations unless transparent.',
    applicableDeclaration: 'Visual Contrast, Legibility & Outer Containers',
    category: 'Display & Legibility Standards',
    prescribedParameters: 'High optical contrast (e.g. dark text on light background or reverse). No low-contrast camouflage printing.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Light silver text on white background or faded thermal ink constitutes an infraction under Rule 9.'
  },
  {
    id: 'RULE-10',
    ruleNo: 'Rule 10',
    subRule: 'Sub-rules (1)–(2)',
    title: 'Declaration of Name and Complete Address of Manufacturer, Packer & Importer',
    requirement: 'Every package kept, offered, exposed for sale or sold must conspicuously bear the name and complete address of the manufacturer; where the manufacturer is not the packer, the manufacturer and packer; and for imported packages, the importer. Where a commodity manufactured outside India is packed in India, the PDP must also contain the name and complete address of the Indian packer.',
    applicableDeclaration: 'Manufacturer / Packer / Importer Geographical Address with PIN',
    category: 'Mandatory Declarations',
    prescribedParameters: 'Must include postal PIN code. For packages of capacity 10 cm³ or less, an approved identifying mark is sufficient.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Verify domestic packing address if imported commodity is bottled or repackaged in India.'
  },
  {
    id: 'RULE-11',
    ruleNo: 'Rule 11',
    subRule: 'Sub-rules (1)–(4)',
    title: 'General Provisions Relating to Declaration of Quantity (Tare & Environmental Rules)',
    requirement: 'Packaging and wrapping materials must be excluded when declaring net quantity. Where environmental conditions are not likely to change the quantity, the declared quantity must correspond to what the consumer receives and must not be qualified by words such as "when packed". Where significant environmental variation is permitted, qualifications must strictly follow First Schedule guidelines.',
    applicableDeclaration: 'Exclusion of Tare & Prohibition of "When Packed"',
    category: 'Measurement & Quantity',
    prescribedParameters: 'Gross weight cannot be declared as net quantity. Words like "when packed" or "approximate weight" are prohibited for standard goods.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) and Section 39 of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Detect and penalize phrases like "Net Wt: 500g When Packed" unless the commodity is specifically notified under First Schedule.'
  },
  {
    id: 'RULE-12',
    ruleNo: 'Rule 12',
    subRule: 'Sub-rules (1)–(7)',
    title: 'Manner in which Declaration of Quantity Shall be Made (Physical State Mapping)',
    requirement: 'Quantity must be declared in appropriate units: mass for solid/semi-solid/viscous or solid-liquid mixtures; length for linear measure; area for area measure; volume for liquids/cubic measure; and number for commodities sold by count. Unit conventions prohibit expressions such as dozen, score, gross.',
    applicableDeclaration: 'Physical State to Unit Mapping (Mass vs Volume vs Number)',
    category: 'Measurement & Quantity',
    prescribedParameters: 'Solids: weight (g, kg); Liquids: volume (ml, L); Count: N or U. Semi-solid products cannot arbitrarily use volume if standard trade practice requires mass.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Check if liquids like shampoo/syrup or solids like butter are declared in legally correct units.'
  },
  {
    id: 'RULE-13',
    ruleNo: 'Rule 13',
    subRule: 'Sub-rules (1)–(6)',
    title: 'Statement of Units of Weight, Measure or Number & Symbol Conventions',
    requirement: 'Units must be stated in accordance with prescribed sub-rules. For quantities below 1 kg/metre/litre, specified smaller units apply (g, cm, ml). For quantities >= 1 kg/metre/litre, corresponding SI units apply (kg, m, l/L). Dozen, score, gross and similar number expressions are prohibited. Only SI units may be used for net quantity, with N or U for items sold by number.',
    applicableDeclaration: 'SI Metric Symbols & Threshold Conventions',
    category: 'Measurement & Quantity',
    prescribedParameters: 'Quantities < 1 kg must use "g" (e.g. "500 g", not "0.5 kg"); quantities < 1 L must use "ml". No plural "s" (e.g. "kg" not "kgs", "g" not "gms"). No "dozen".',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Check for illegal unit symbols like "gms", "kgs", "ml.", "1 Dozen", "1 Pair".'
  },
  {
    id: 'RULE-14',
    ruleNo: 'Rule 14',
    subRule: 'Rule 14',
    title: 'Declarations with Regard to Dimensions of Certain Commodities (Textiles & Fabrics)',
    requirement: 'Packages containing bed-sheets, hemmed fabric materials, dhoties, sarees, napkins, pillow-covers, towels, table cloths or similar commodities must declare the number and finished dimensions. Where pieces have different dimensions, the dimensions and retail sale price of each piece must be declared.',
    applicableDeclaration: 'Finished Dimensions & Piece Counts for Textile Products',
    category: 'Specialized Commodity Requirements',
    prescribedParameters: 'Expressed in metric units (cm or m) along with count (e.g. "1 N Bedsheet: 220 cm x 240 cm").',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Inspect textile and linen packaging for finished dimensions in metric centimeters/meters.'
  },
  {
    id: 'RULE-15',
    ruleNo: 'Rule 15',
    subRule: 'Rule 15',
    title: 'Declaration with Regard to Dimensions and Weight on Packages in Certain Cases',
    requirement: 'Where the dimensions and/or weight of a commodity have a relationship to its price, the package\'s quantity declaration must state the relevant dimensions, weight, or a combination thereof.',
    applicableDeclaration: 'Price-to-Dimension / Price-to-Weight Relationship Declarations',
    category: 'Specialized Commodity Requirements',
    prescribedParameters: 'Requires simultaneous declaration of dimensions (length x width x thickness) and mass where both determine market value.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Applies to items such as foam sheets, construction boards, metal foils, and industrial insulation rolls.'
  },
  {
    id: 'RULE-16',
    ruleNo: 'Rule 16',
    subRule: 'Rule 16',
    title: 'Declarations with Regard to Number of Usable Sheets & Dimensions',
    requirement: 'Packages containing sheets such as aluminium foil, facial tissues, waxed paper, toilet paper or similar sheets must declare the number of usable sheets and the dimensions of each sheet, in addition to the quantity.',
    applicableDeclaration: 'Usable Sheet Count & Sheet Dimensions (Foils, Tissues, Papers)',
    category: 'Specialized Commodity Requirements',
    prescribedParameters: 'Mandatory: 1) Number of usable sheets (e.g. "100 Pulls / Sheets"), 2) Length and width of individual sheet (e.g. "20 cm x 20 cm"), 3) Total length/weight for foils.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Verify facial tissue, kitchen roll, and foil packaging for usable sheet count and individual sheet dimensions.'
  },
  {
    id: 'RULE-17',
    ruleNo: 'Rule 17',
    subRule: 'Clauses (i)–(iv)',
    title: 'Declarations with Regard to Dimensions of Container Type Commodities',
    requirement: 'Container-type commodities such as bags, boxes, cups and pans must be labelled according to their type: bag-type commodities require number of bags and linear dimensions; rectangular containers require number, length, width, and depth; circular containers require number, diameter, and depth.',
    applicableDeclaration: 'Container Type Geometry Declarations (Bags, Boxes, Cups, Pans)',
    category: 'Specialized Commodity Requirements',
    prescribedParameters: 'Linear dimensions (L x W x D), diameter, and capacity volume must accompany number of items.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Check disposable cups, garbage bags, storage boxes, and food containers for complete geometric dimensions.'
  },
  {
    id: 'RULE-18',
    ruleNo: 'Rule 18',
    subRule: 'Sub-rules (1)–(8)',
    title: 'Provisions Relating to Wholesale & Retail Dealers (No Overcharging or Dual MRP)',
    requirement: 'Wholesale dealers, retail dealers and importers must not sell, distribute, deliver, display or store packaged commodities unless packages comply with the Act and Rules. No person may sell a packaged commodity above its retail sale price (MRP), and restrictive/unfair trade practices must not be used to declare different MRPs for identical pre-packaged commodities. Unauthorized price alteration stickers are prohibited.',
    applicableDeclaration: 'Price Integrity, Anti-Overcharging & Anti-Dual-MRP',
    category: 'Market Enforcement',
    prescribedParameters: 'Sale above MRP is strictly illegal. Dual pricing for identical commodities is prohibited under Rule 18(2A). Sticker alterations prohibited under Rule 18(2).',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011, Rule 18',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009: Fine up to ₹50,000 for selling above MRP.',
    lastUpdated: '2024-01-01',
    officerGuidance: 'Inspect airport/mall/multiplex retail for dual MRP violations. Verify absence of price-hiking secondary stickers.'
  },
  {
    id: 'RULE-19',
    ruleNo: 'Rule 19',
    subRule: 'Sub-rules (1)–(8)',
    title: 'Inspection of Quantity and Error in Packages at Premises of Manufacturer or Packer',
    requirement: 'An authorised person may inspect packages/lots at the manufacturer\'s or packer\'s premises, draw samples according to the Fifth Schedule and conduct tests according to the Sixth Schedule. Results are entered in the Seventh Schedule and signed by the manufacturer/packer or authorised witness.',
    applicableDeclaration: 'Factory Premises Sampling & Seventh Schedule Audit',
    category: 'Inspection & Sampling Protocols',
    prescribedParameters: 'Statutory sampling according to batch lot size (Fifth Schedule) and net content determination (Sixth Schedule).',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011, Schedules 5, 6, 7',
    penalProvision: 'Section 15, Section 29, and Section 36 of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Follow statistical sample tables. Complete Seventh Schedule inspection sheet with authorized witness signature.'
  },
  {
    id: 'RULE-20',
    ruleNo: 'Rule 20',
    subRule: 'Sub-rules (1)–(2)',
    title: 'Action on Completion of Inspection at Manufacturer / Packer Premises',
    requirement: 'Where corrected average is deficient, excessive individual-package errors occur, or required declarations are missing, the officer can require a 100% check and permit sale only of compliant packages, with non-compliant packages to be repacked/relabelled. If errors exceed statutory limits, Director/Controller/Legal Metrology Officer shall seize sampled packages and initiate prosecution.',
    applicableDeclaration: 'Seizure, Relabelling & Factory Remediation Order',
    category: 'Inspection & Sampling Protocols',
    prescribedParameters: '100% lot screening order, detention of defective lots, compounding or prosecution under Section 36.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) and Section 39 of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Issue formal Panchnama and detention memo if average net quantity is below declared quantity.'
  },
  {
    id: 'RULE-21',
    ruleNo: 'Rule 21',
    subRule: 'Sub-rules (1)–(5)',
    title: 'Inspection of Quantity and Error at Wholesale or Retail Premises',
    requirement: 'Normally quantity testing is not carried out at retail/wholesale premises unless a complaint is received, there is reason to suspect tampering/pilferage/leakage, or required declarations are suspected to be missing. When testing is done, the officer verifies the declared quantity and maximum permissible error. Packages exceeding permissible error may be seized.',
    applicableDeclaration: 'Retail Surveillance, Consumer Complaint & Dealer Inspection',
    category: 'Inspection & Sampling Protocols',
    prescribedParameters: 'Retail checks triggered by complaints, visible tampering, or missing declarations. Dealer protected if deficiency is due to environmental variations under "when packed" rule.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Check shelf displays for missing declarations (MRP, Net Qty, Consumer Care) or price tampering.'
  },
  {
    id: 'RULE-22',
    ruleNo: 'Rule 22',
    subRule: 'Sub-rules (1)–(3)',
    title: 'Establishment of Maximum Permissible Error (MPE) on Packages',
    requirement: 'The maximum permissible error for commodities is as specified in the First Schedule. In establishing it, account is taken of unavoidable deviations in weighing/measuring/counting under good manufacturing practice, climate/transport variations, and container tolerances.',
    applicableDeclaration: 'First Schedule Maximum Permissible Error (MPE)',
    category: 'Measurement & Quantity',
    prescribedParameters: 'Defines allowable negative error tolerances: e.g., 50g-100g: 4.5g; 100g-200g: 4.5%; 200g-300g: 9g; 300g-500g: 3%; 500g-1kg: 15g; 1kg-10kg: 1.5%. No package may exceed 2x MPE.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011, First Schedule',
    penalProvision: 'Section 36(1) and Section 39 of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Calculate individual sample errors against First Schedule table. Any single package exceeding 2x MPE triggers immediate lot rejection.'
  },
  {
    id: 'RULE-23',
    ruleNo: 'Rule 23',
    subRule: 'Sub-rules (1)–(2)',
    title: 'Deceptive Packages to be Repacked or in Default to be Seized',
    requirement: 'A deceptive package is one designed to deliberately give the consumer an exaggerated or misleading impression about quantity, except where larger dimensions are justified for product protection. Where found deceptive, the manufacturer/packer may be required to repack and relabel it, failing which it shall be seized.',
    applicableDeclaration: 'Anti-Deceptive Packaging & Slack Fill Limits',
    category: 'Consumer Protection & Anti-Deception',
    prescribedParameters: 'Prohibits excessive slack fill, hollow bottoms, oversized cartons, or false cavities designed to mislead consumers on volume.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009 and Seizure Orders',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Inspect oversized outer cartons containing small inner pouches without protective structural necessity.'
  },
  {
    id: 'RULE-24',
    ruleNo: 'Rule 24',
    subRule: 'Rule 24',
    title: 'Declarations Applicable to be Made on Every Wholesale Package',
    requirement: 'Every wholesale package must carry legible, definite, plain and conspicuous declarations of: 1) Manufacturer/importer/packer name and address, 2) Identity of commodity, 3) Either total number of retail packages or net quantity in standard units of weight, measure or number.',
    applicableDeclaration: 'Wholesale Carton / Master Shipper Declarations',
    category: 'Wholesale & Trade Compliance',
    prescribedParameters: 'Outer master cartons must declare commodity identity, manufacturer details, and count of retail packages or total net quantity.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Inspect master corrugated cartons (Outer Carton) during warehouse audits.'
  },
  {
    id: 'RULE-25',
    ruleNo: 'Rule 25',
    subRule: 'Rule 25',
    title: 'Restrictions on Sale of Export Packages in India',
    requirement: 'An export package must not be sold in India unless the manufacturer or packer has repacked or relabelled the commodity in accordance with Chapter II. An export package sold in India without such repacking/relabeling is treated as a non-compliant retail package.',
    applicableDeclaration: 'Export Packages Re-routed for Domestic Market',
    category: 'Trade & Import-Export',
    prescribedParameters: 'Export merchandise diverted to domestic retail must carry all Chapter II declarations (MRP in ₹, Net Qty in SI units, Consumer Care).',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Check surplus export consignments sold in local outlets; non-rupee pricing or foreign units constitute violations.'
  },
  {
    id: 'RULE-26',
    ruleNo: 'Rule 26',
    subRule: 'Clauses (a)–(e)',
    title: 'Exemption in Respect of Certain Packages (Small Packs, Fast Food & DPCO)',
    requirement: 'The Rules do not apply to: (a) packages containing 10 grams or 10 millilitres or less when sold by weight/measure (except tobacco and tobacco products); (b) fast-food items packed by restaurants/hotels; (c) scheduled/non-scheduled drug formulations covered under Drugs (Prices Control) Order; and (d) thread sold in coils to handloom weavers.',
    applicableDeclaration: 'Statutory Exemptions (<=10g/ml, Restaurant Food, DPCO Drugs)',
    category: 'Scope & Exemptions',
    prescribedParameters: 'Small sachets <= 10g or 10ml are exempt from standard net quantity declaration sizing (except tobacco). DPCO medicines follow NPPA pricing rules.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Statutory exemption threshold',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Verify net quantity before booking small sachets. Note: Tobacco products have NO small-pack exemption.'
  },
  {
    id: 'RULE-27',
    ruleNo: 'Rule 27',
    subRule: 'Sub-rules (1)–(4)',
    title: 'Registration of Manufacturers, Packers and Importers',
    requirement: 'Every individual, firm, Hindu undivided family, society, company or corporation that pre-packs or imports commodities for sale, distribution or delivery must apply to the Director or Controller for registration of its name and complete address, with prescribed fee and within prescribed period.',
    applicableDeclaration: 'Statutory Pre-packer / Importer Registration Certificate',
    category: 'Regulatory Registration',
    prescribedParameters: 'Mandatory registration certificate under Rule 27 with Director of Legal Metrology (Central) or State Controller.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(2) of Legal Metrology Act, 2009: Fine up to ₹25,000 for unregistered packing/importing.',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Check manufacturer\'s Rule 27 registration number in central registry.'
  },
  {
    id: 'RULE-28',
    ruleNo: 'Rule 28',
    subRule: 'Sub-rules (1)–(3)',
    title: 'Registration of Shorter Address Permissible',
    requirement: 'A manufacturer or packer may apply for registration of a shorter address in addition to the complete address. The Director/Controller may register it after inquiry if it is sufficient to identify the manufacturer or packer. Once registered, the shorter address may be stated on the label.',
    applicableDeclaration: 'Approved Shorter Registered Address',
    category: 'Regulatory Registration',
    prescribedParameters: 'Permits abbreviated corporate name/address on label ONLY after formal approval and registration under Rule 28.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'If manufacturer uses abbreviated address, require proof of Rule 28 approval certificate.'
  },
  {
    id: 'RULE-29',
    ruleNo: 'Rule 29',
    subRule: 'Sub-rules (1)–(2)',
    title: 'Maintenance of Register of Manufacturers and Packers',
    requirement: 'The Director or Controller must maintain a register containing the name and complete address of each manufacturer or packer whose registration application has been made under Rule 27. The register must be open to public inspection.',
    applicableDeclaration: 'Public Registry of Pre-packers & Importers',
    category: 'Regulatory Registration',
    prescribedParameters: 'Official government registry maintained by Central Director and State Controllers.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Administrative governance obligation',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Cross-reference field inspection records against official Rule 29 registry records.'
  },
  {
    id: 'RULE-30',
    ruleNo: 'Rule 30',
    subRule: 'Rule 30',
    title: 'Compilation of Lists of Manufacturers or Packers and Circulation to States',
    requirement: 'The Director/Controller must compile a State-wise list of manufacturers and packers registered under Rule 29 and circulate it to the Controller of the concerned State so that appropriate inspection and enforcement can be taken.',
    applicableDeclaration: 'Inter-State Enforcement Intelligence Sharing',
    category: 'Regulatory Registration',
    prescribedParameters: 'Quarterly state-wise directory sharing for market surveillance coordination.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Inter-state enforcement coordination mandate',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Use circulated state lists to verify out-of-state manufacturer legitimacy.'
  },
  {
    id: 'RULE-31',
    ruleNo: 'Rule 31',
    subRule: 'Sub-rules (1)–(2)',
    title: 'Advertisement Mentioning Retail Sale Price to Include Net Quantity',
    requirement: 'Any advertisement mentioning the retail sale price of a pre-packaged commodity must also contain a clear declaration of the net quantity or number of the commodity in the package. The font size of the net quantity in the advertisement must be prominent and legible.',
    applicableDeclaration: 'Commercial Price Advertisements (Print, Media, E-Commerce)',
    category: 'Advertising & E-Commerce Compliance',
    prescribedParameters: 'Any public advertisement (print, hoardings, TV, digital, e-commerce) quoting price must display net quantity alongside price in matching prominence.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Section 36(1) of Legal Metrology Act, 2009',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Inspect newspaper ads, billboards, and e-commerce listings quoting discounted prices without stating net quantity.'
  },
  {
    id: 'RULE-32',
    ruleNo: 'Rule 32',
    subRule: 'Rule 32',
    title: 'Fine for Contravention of Rules',
    requirement: 'Whoever contravenes any provision of these Rules for which no punishment is otherwise provided in the Act is liable to a fine which may extend to five thousand rupees.',
    applicableDeclaration: 'General Residual Penalty Clause',
    category: 'Penalties & Legal Prosecution',
    prescribedParameters: 'Residual penalty clause for technical or administrative non-compliances not covered under specific sections.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Fine up to ₹5,000 for general contraventions',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Applicable when specific penalty section is not designated in Legal Metrology Act, 2009.'
  },
  {
    id: 'RULE-32A',
    ruleNo: 'Rule 32A',
    subRule: 'Rule 32A',
    title: 'Compounding of Offences and Statutory Compounding Fee Schedule',
    requirement: 'The sum for compounding offences under the Act is specified in the statutory table: 1) Contravention of Section 29 (failure to verify equipment): ₹10,000; 2) Contravention of Section 36(1) (non-declaration / violation of packaged commodities rules): ₹25,000 (first offence), ₹50,000 (second offence); 3) Contravention of Section 36(2) (unregistered packer/importer): ₹25,000; 4) Selling products above maximum retail price: prescribed compounding sums by category.',
    applicableDeclaration: 'Statutory Compounding Table (Section 48)',
    category: 'Penalties & Legal Prosecution',
    prescribedParameters: 'Enables authorized officers to compound first-time offences without immediate court prosecution upon payment of prescribed compounding fee.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011 & Section 48 of Act',
    penalProvision: 'Compounding fee ₹25,000 (Section 36(1) first offence), ₹50,000 (second offence), ₹25,000 (Section 36(2)).',
    lastUpdated: '2023-01-01',
    officerGuidance: 'Issue statutory compounding notice under Rule 32A allowing manufacturer 15 days to compound or face court prosecution.'
  },
  {
    id: 'RULE-33',
    ruleNo: 'Rule 33',
    subRule: 'Sub-rules (1)–(2)',
    title: 'Power of Central Government to Relax Rules',
    requirement: 'The Central Government may, after ascertaining the genuineness of the case/application, permit a manufacturer or packer to pack for sale for a reasonable period by relaxing one or more provisions of the Rules, subject to specified corrective measures. It may also permit packing in non-standard sizes for up to one year.',
    applicableDeclaration: 'Central Government Statutory Relaxation Order',
    category: 'Preliminary & Governance',
    prescribedParameters: 'Applies only pursuant to formal gazetted notifications (e.g. GST rate transitions, supply chain emergencies).',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Statutory exemption power of Central Government',
    lastUpdated: '2023-01-01',
    officerGuidance: 'If manufacturer claims relaxation, require official Central Government Gazette order copy.'
  },
  {
    id: 'RULE-34',
    ruleNo: 'Rule 34',
    subRule: 'Sub-rules (1)–(5)',
    title: 'Repeal and Savings',
    requirement: 'The Standards of Weights and Measures (Packaged Commodities) Rules, 1977 are repealed. The repeal does not affect previous operations, acts/omissions, accrued rights and obligations, penalties/forfeitures/punishments, or investigations and legal proceedings relating to the repealed Rules.',
    applicableDeclaration: 'Repeal of 1977 Rules & Transitional Provisions',
    category: 'Preliminary & Governance',
    prescribedParameters: 'All legacy proceedings initiated under 1977 rules continue to have legal standing.',
    source: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    penalProvision: 'Transitional savings clause',
    lastUpdated: '2011-04-01',
    officerGuidance: 'Enforcement actions must cite the 2011 Rules as amended.'
  }
];

export const STATUTORY_GAZETTE_CITATIONS: Record<string, {
  sourcePdf: string;
  sourcePdfPage: number;
  amendmentCitation: string;
  effectiveDate: string;
}> = {
  'RULE-1': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 1,
    amendmentCitation: 'G.S.R. 202(E) / 2023.01.27 amendment in PCR_1732871665---25.pdf (p. 2)',
    effectiveDate: '1st April, 2011'
  },
  'RULE-2': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 1,
    amendmentCitation: 'G.S.R. 779(E) Legal Metrology Definitions & E-commerce',
    effectiveDate: '1st January, 2023'
  },
  'RULE-3': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 4,
    amendmentCitation: 'G.S.R. 202(E) Chapter II Scope (Exemption >25kg/25L, Bags >50kg)',
    effectiveDate: '1st April, 2011'
  },
  'RULE-4': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 4,
    amendmentCitation: 'G.S.R. 202(E) Regulation for pre-packing & sale',
    effectiveDate: '1st April, 2011'
  },
  'RULE-5': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 5,
    amendmentCitation: 'G.S.R. 577(E) Rationalized Second Schedule Commodities',
    effectiveDate: '14th July, 2022'
  },
  'RULE-6-1-A': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 5,
    amendmentCitation: 'G.S.R. 779(E) Read with Rule 10 Complete Address & PIN code',
    effectiveDate: '1st December, 2022'
  },
  'RULE-6-1-B': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 5,
    amendmentCitation: 'G.S.R. 202(E) Generic or Common Name on PDP',
    effectiveDate: '1st April, 2011'
  },
  'RULE-6-1-C': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 6,
    amendmentCitation: 'G.S.R. 202(E) Metric SI Net Quantity Symbols (Rules 11-13)',
    effectiveDate: '1st April, 2011'
  },
  'RULE-6-1-D': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 6,
    amendmentCitation: 'G.S.R. 779(E) Month and Year of Manufacture / Packing',
    effectiveDate: '1st December, 2022'
  },
  'RULE-6-1-DA': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 6,
    amendmentCitation: 'G.S.R. 385(E) Best Before / Expiry for Perishables',
    effectiveDate: '14th May, 2015'
  },
  'RULE-6-1-E': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 6,
    amendmentCitation: 'G.S.R. 779(E) Maximum Retail Price (MRP) incl. of all taxes',
    effectiveDate: '1st January, 2022'
  },
  'RULE-6-1-EA': {
    sourcePdf: 'The Legal Metrology (Packaged Commodities) (Amendment) Rules, 2021_1732871439--2.pdf',
    sourcePdfPage: 2,
    amendmentCitation: 'G.S.R. 779(E) Unit Sale Price (USP) per g/ml/piece',
    effectiveDate: '1st December, 2022'
  },
  'RULE-6-1-F': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 7,
    amendmentCitation: 'G.S.R. 202(E) Consumer Care Contact Details',
    effectiveDate: '1st April, 2011'
  },
  'RULE-6-1-G': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 7,
    amendmentCitation: 'G.S.R. 202(E) Batch / Lot / Dimensions Declaration',
    effectiveDate: '1st April, 2011'
  },
  'RULE-6-10': {
    sourcePdf: '8(10)_0_1732861286--10.pdf',
    sourcePdfPage: 1,
    amendmentCitation: 'G.S.R. 629(E) E-Commerce Mandatory Declarations',
    effectiveDate: '23rd June, 2017'
  },
  'RULE-6-11': {
    sourcePdf: 'The Legal Metrology (Packaged Commodities) (Amendment) Rules, 2021_1732871439--2.pdf',
    sourcePdfPage: 2,
    amendmentCitation: 'G.S.R. 779(E) Unit Sale Price Rounded to Nearest Two Decimal Places',
    effectiveDate: '1st December, 2022'
  },
  'RULE-7': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 8,
    amendmentCitation: 'G.S.R. 202(E) Wholesale Package Declarations',
    effectiveDate: '1st April, 2011'
  },
  'RULE-8': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 9,
    amendmentCitation: 'G.S.R. 202(E) General Provisions Relating to Declarations',
    effectiveDate: '1st April, 2011'
  },
  'RULE-9': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 9,
    amendmentCitation: 'G.S.R. 202(E) Principal Display Panel Size & Typography',
    effectiveDate: '1st April, 2011'
  },
  'RULE-10': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 10,
    amendmentCitation: 'G.S.R. 779(E) Name and Complete Address with 6-digit Postal PIN code',
    effectiveDate: '1st January, 2022'
  },
  'RULE-11': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 11,
    amendmentCitation: 'G.S.R. 202(E) Net Quantity Declaration General Requirements',
    effectiveDate: '1st April, 2011'
  },
  'RULE-12': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 12,
    amendmentCitation: 'G.S.R. 202(E) Units of Weight, Measure or Number',
    effectiveDate: '1st April, 2011'
  },
  'RULE-13': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 13,
    amendmentCitation: 'G.S.R. 202(E) Table 1 Minimum Numeral Height Specifications',
    effectiveDate: '1st April, 2011'
  },
  'RULE-14': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 14,
    amendmentCitation: 'G.S.R. 202(E) Combination Packages Declarations',
    effectiveDate: '1st April, 2011'
  },
  'RULE-15': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 15,
    amendmentCitation: 'G.S.R. 202(E) Group Packages Declarations',
    effectiveDate: '1st April, 2011'
  },
  'RULE-16': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 15,
    amendmentCitation: 'G.S.R. 629(E) E-commerce Marketplace Display',
    effectiveDate: '23rd June, 2017'
  },
  'RULE-18': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 16,
    amendmentCitation: 'G.S.R. 202(E) Prohibition of Overcharging above MRP',
    effectiveDate: '1st April, 2011'
  },
  'RULE-24': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 18,
    amendmentCitation: 'G.S.R. 202(E) Wholesale Packages Exemption Criteria',
    effectiveDate: '1st April, 2011'
  },
  'RULE-26': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 19,
    amendmentCitation: 'G.S.R. 202(E) Small Package Exemption (<=10g or 10ml)',
    effectiveDate: '1st April, 2011'
  },
  'RULE-26-E': {
    sourcePdf: '2022 3rd amendment in PCR Garments_1733228786--22.pdf',
    sourcePdfPage: 2,
    amendmentCitation: 'G.S.R. 648(E) Exemption for Loose Garments / Metric Sizing in cm or m',
    effectiveDate: '1st January, 2023'
  },
  'RULE-27': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 20,
    amendmentCitation: 'G.S.R. 202(E) Registration of Manufacturers and Importers',
    effectiveDate: '1st April, 2011'
  },
  'RULE-32': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 22,
    amendmentCitation: 'G.S.R. 202(E) General Residual Penalty Clause',
    effectiveDate: '1st April, 2011'
  },
  'RULE-32A': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 23,
    amendmentCitation: 'G.S.R. 779(E) Compounding Table under Section 48 / Section 36(1)',
    effectiveDate: '1st January, 2022'
  },
  'RULE-33': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 24,
    amendmentCitation: 'G.S.R. 202(E) Power of Central Government to Relax Rules',
    effectiveDate: '1st April, 2011'
  },
  'RULE-34': {
    sourcePdf: '8_1732871406--1.pdf',
    sourcePdfPage: 25,
    amendmentCitation: 'G.S.R. 202(E) Repeal and Savings (Repeal of 1977 Rules)',
    effectiveDate: '1st April, 2011'
  }
};

// Automatically enrich LEGAL_RULES with authoritative Knowledge Base citations
LEGAL_RULES.forEach(r => {
  const cite = STATUTORY_GAZETTE_CITATIONS[r.id];
  if (cite) {
    r.sourcePdf = cite.sourcePdf;
    r.sourcePdfPage = cite.sourcePdfPage;
    r.amendmentCitation = cite.amendmentCitation;
    r.effectiveDate = cite.effectiveDate;
  } else {
    r.sourcePdf = '8_1732871406--1.pdf';
    r.sourcePdfPage = 1;
  }
});
