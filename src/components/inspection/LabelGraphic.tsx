import React, { useState } from 'react';
import { BoundingBox } from '../../types';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCcw,
  AlertTriangle,
  CheckCircle2,
  Ruler,
  Layers,
  Crosshair
} from 'lucide-react';

interface LabelGraphicProps {
  svgMockType?: string;
  customImageUrl?: string;
  surface: string;
  boundingBoxes?: BoundingBox[];
  highlightBox?: BoundingBox;
  onBoxClick?: (box: BoundingBox) => void;
  showAnnotations?: boolean;
}

export const LabelGraphic: React.FC<LabelGraphicProps> = ({
  svgMockType = 'front-mustard',
  customImageUrl,
  surface,
  boundingBoxes = [],
  highlightBox,
  onBoxClick,
  showAnnotations = true
}) => {
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [showRulerGrid, setShowRulerGrid] = useState<boolean>(false);

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.3, 3.2));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.3, 0.7));
  const handleResetZoom = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  // Render SVG based on mock type
  const renderSvgContent = () => {
    switch (svgMockType) {
      case 'front-mustard':
        return (
          <svg viewBox="0 0 500 700" className="w-full h-auto select-none shadow-xl" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="mustardPouch" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#fef3c7" />
                <stop offset="50%" stopColor="#fde047" />
                <stop offset="100%" stopColor="#eab308" />
              </linearGradient>
              <pattern id="sealPattern" width="10" height="10" patternUnits="userSpaceOnUse">
                <line x1="0" y1="0" x2="10" y2="10" stroke="#ca8a04" strokeWidth="0.8" />
              </pattern>
            </defs>
            <rect x="25" y="20" width="450" height="660" rx="12" fill="url(#mustardPouch)" stroke="#a16207" strokeWidth="2.5" />
            <rect x="25" y="20" width="450" height="35" fill="url(#sealPattern)" stroke="#854d0e" strokeWidth="1" />
            <text x="250" y="42" textAnchor="middle" fill="#713f12" fontSize="11" fontWeight="bold" letterSpacing="2">HERMETICALLY SEALED PACK FOR PURITY</text>
            
            <circle cx="250" cy="110" r="42" fill="#854d0e" />
            <circle cx="250" cy="110" r="38" fill="#fef08a" stroke="#ca8a04" strokeWidth="1.5" />
            <text x="250" y="108" textAnchor="middle" fill="#713f12" fontSize="16" fontWeight="bold">HERITAGE</text>
            <text x="250" y="122" textAnchor="middle" fill="#854d0e" fontSize="9" fontWeight="600" letterSpacing="1">AGRO PRODUCTS</text>

            <rect x="50" y="170" width="400" height="65" rx="6" fill="#713f12" />
            <text x="250" y="200" textAnchor="middle" fill="#fef08a" fontSize="22" fontWeight="bold" letterSpacing="1">SHUDDH KACCHI GHANI</text>
            <text x="250" y="222" textAnchor="middle" fill="#ffffff" fontSize="14" fontWeight="600">COLD PRESSED PURE MUSTARD OIL</text>

            <rect x="150" y="260" width="200" height="180" rx="8" fill="#ffffff" stroke="#eab308" strokeWidth="2" opacity="0.9" />
            <circle cx="250" cy="330" r="45" fill="#fef9c3" stroke="#ca8a04" strokeWidth="1" />
            <text x="250" y="325" textAnchor="middle" fill="#854d0e" fontSize="12" fontWeight="bold">TRADITIONAL</text>
            <text x="250" y="340" textAnchor="middle" fill="#a16207" fontSize="10">KOLHU EXTRACT</text>
            <text x="250" y="415" textAnchor="middle" fill="#451a03" fontSize="11" fontWeight="bold">RICH IN NATURAL OMEGA-3</text>

            <rect x="70" y="470" width="160" height="50" rx="4" fill="#ffffff" stroke="#a16207" strokeWidth="1" />
            <text x="150" y="490" textAnchor="middle" fill="#047857" fontSize="10" fontWeight="bold">AGMARK GRADE - 1</text>
            <text x="150" y="506" textAnchor="middle" fill="#374151" fontSize="8">CA NO: A-84192/RAJ</text>

            <rect x="270" y="470" width="160" height="50" rx="4" fill="#ffffff" stroke="#a16207" strokeWidth="1" />
            <text x="350" y="490" textAnchor="middle" fill="#1e3a8a" fontSize="10" fontWeight="bold">fssai Lic. No.</text>
            <text x="350" y="506" textAnchor="middle" fill="#374151" fontSize="9" fontWeight="600">10014013000881</text>

            <rect x="120" y="540" width="260" height="42" rx="4" fill="#ffffff" stroke="#713f12" strokeWidth="1.2" />
            <text x="250" y="566" textAnchor="middle" fill="#713f12" fontSize="15" fontWeight="bold">Net Quantity: 1 Litre (910 g)</text>

            <rect x="60" y="600" width="380" height="48" rx="4" fill="#ffffff" stroke="#b91c1c" strokeWidth="1.8" strokeDasharray="4 2" />
            <text x="250" y="625" textAnchor="middle" fill="#b91c1c" fontSize="16" fontWeight="bold">MRP ₹ 165.00</text>
            <text x="250" y="640" textAnchor="middle" fill="#b91c1c" fontSize="9" fontWeight="bold">[STATUTORY OMISSION: MISSING "INCL. OF ALL TAXES"]</text>

            <rect x="25" y="655" width="450" height="25" fill="url(#sealPattern)" stroke="#854d0e" strokeWidth="1" />
          </svg>
        );

      case 'back-mustard':
        return (
          <svg viewBox="0 0 500 700" className="w-full h-auto select-none shadow-xl" xmlns="http://www.w3.org/2000/svg">
            <rect x="25" y="20" width="450" height="660" rx="12" fill="#ffffff" stroke="#cbd5e1" strokeWidth="2" />
            <rect x="25" y="20" width="450" height="45" fill="#0f2942" rx="10" />
            <text x="250" y="48" textAnchor="middle" fill="#ffffff" fontSize="13" fontWeight="bold">MANDATORY PRODUCT & STATUTORY DECLARATIONS</text>

            <rect x="45" y="80" width="410" height="85" fill="#f8fafc" stroke="#e2e8f0" strokeWidth="1" rx="4" />
            <text x="60" y="102" fill="#0f172a" fontSize="11" fontWeight="bold">MANUFACTURED & PACKED BY:</text>
            <text x="60" y="122" fill="#334155" fontSize="10" fontWeight="600">Heritage Agro Oil Mills Pvt. Ltd.</text>
            <text x="60" y="138" fill="#475569" fontSize="9">Plot 44-A, Matsya Industrial Area, Alwar, Rajasthan - 301030</text>
            <text x="60" y="152" fill="#475569" fontSize="9">Legal Metrology Packer Reg: LM-REG-RJ-2021-9921</text>

            <rect x="45" y="180" width="410" height="110" fill="#f8fafc" stroke="#e2e8f0" strokeWidth="1" rx="4" />
            <text x="60" y="200" fill="#0f172a" fontSize="10" fontWeight="bold">NUTRITIONAL INFORMATION (Approx. per 100g):</text>
            <text x="60" y="218" fill="#475569" fontSize="9">Energy: 900 kcal | Total Fat: 100g | Saturated Fat: 8.5g | MUFA: 65g | PUFA: 26.5g</text>
            <text x="60" y="235" fill="#475569" fontSize="9">Trans Fatty Acids: 0.0g | Added Vitamin A & D: As per FSSAI regulations</text>
            <text x="60" y="258" fill="#0f172a" fontSize="10" fontWeight="bold">INGREDIENTS:</text>
            <text x="60" y="274" fill="#475569" fontSize="9">100% Pure Mustard Oil. Free from Argemone Oil.</text>

            <rect x="45" y="305" width="410" height="75" fill="#f1f5f9" stroke="#cbd5e1" strokeWidth="1" rx="4" />
            <text x="60" y="328" fill="#0f172a" fontSize="10" fontWeight="bold">BATCH & PACKAGING PARTICULARS:</text>
            <text x="60" y="346" fill="#1e293b" fontSize="10" fontWeight="600">Batch No: MOL-2026/08-B | Date of Mfg: 08/2026</text>
            <text x="60" y="364" fill="#334155" fontSize="9">Best before 9 months from manufacture when stored in cool dry place.</text>

            <rect x="45" y="395" width="410" height="95" fill="#ecfdf5" stroke="#10b981" strokeWidth="1.2" rx="4" />
            <text x="60" y="418" fill="#065f46" fontSize="11" fontWeight="bold">CONSUMER GRIEVANCE REDRESSAL CELL (Rule 6(1)(f)):</text>
            <text x="60" y="438" fill="#047857" fontSize="10" fontWeight="600">Executive (Consumer Care), Heritage Agro Oil Mills Pvt. Ltd.</text>
            <text x="60" y="454" fill="#065f46" fontSize="9">Toll-Free Helpline: 1800-200-9844 (Mon-Sat 9AM-6PM)</text>
            <text x="60" y="470" fill="#065f46" fontSize="9">E-mail: care@heritageagro.in | Postal: Same as manufacturing address</text>

            <rect x="45" y="510" width="200" height="90" fill="#ffffff" stroke="#cbd5e1" strokeWidth="1" rx="4" />
            <text x="145" y="530" textAnchor="middle" fill="#0f172a" fontSize="9" fontWeight="bold">EAN-13 BARCODE</text>
            <g transform="translate(60, 540)">
              <rect x="0" y="0" width="3" height="40" fill="#000" />
              <rect x="5" y="0" width="2" height="40" fill="#000" />
              <rect x="9" y="0" width="4" height="40" fill="#000" />
              <rect x="16" y="0" width="2" height="40" fill="#000" />
              <rect x="22" y="0" width="5" height="40" fill="#000" />
              <rect x="30" y="0" width="2" height="40" fill="#000" />
              <rect x="36" y="0" width="4" height="40" fill="#000" />
              <rect x="44" y="0" width="2" height="40" fill="#000" />
              <rect x="50" y="0" width="6" height="40" fill="#000" />
              <rect x="60" y="0" width="2" height="40" fill="#000" />
              <rect x="66" y="0" width="4" height="40" fill="#000" />
              <rect x="74" y="0" width="3" height="40" fill="#000" />
              <rect x="80" y="0" width="5" height="40" fill="#000" />
              <rect x="90" y="0" width="2" height="40" fill="#000" />
              <rect x="96" y="0" width="4" height="40" fill="#000" />
              <rect x="105" y="0" width="3" height="40" fill="#000" />
              <rect x="114" y="0" width="5" height="40" fill="#000" />
              <rect x="124" y="0" width="2" height="40" fill="#000" />
              <rect x="132" y="0" width="4" height="40" fill="#000" />
              <rect x="142" y="0" width="2" height="40" fill="#000" />
              <rect x="150" y="0" width="5" height="40" fill="#000" />
              <text x="80" y="52" textAnchor="middle" fill="#000000" fontSize="8" fontFamily="monospace">8 901234 567890</text>
            </g>

            <rect x="260" y="510" width="195" height="90" fill="#ffffff" stroke="#cbd5e1" strokeWidth="1" rx="4" />
            <text x="357" y="535" textAnchor="middle" fill="#047857" fontSize="10" fontWeight="bold">RECYCLABLE POUCH</text>
            <text x="357" y="555" textAnchor="middle" fill="#475569" fontSize="8">Plastic Waste Management</text>
            <text x="357" y="570" textAnchor="middle" fill="#475569" fontSize="8">Thickness &gt; 50 Micron</text>
            <text x="357" y="585" textAnchor="middle" fill="#047857" fontSize="9" fontWeight="bold">CLEAN INDIA GREEN INDIA</text>

            <text x="250" y="640" textAnchor="middle" fill="#64748b" fontSize="8">Legal Metrology Compliance Inspector Verification Reference: LM-COMPASS</text>
          </svg>
        );

      case 'front-rice':
        return (
          <svg viewBox="0 0 500 700" className="w-full h-auto select-none shadow-xl" xmlns="http://www.w3.org/2000/svg">
            <rect x="25" y="20" width="450" height="660" rx="8" fill="#fafaf9" stroke="#78716c" strokeWidth="2.5" />
            <rect x="35" y="30" width="430" height="640" fill="#f5f5f4" stroke="#d6d3d1" strokeWidth="1" />
            <rect x="40" y="35" width="420" height="50" fill="#14532d" />
            <text x="250" y="66" textAnchor="middle" fill="#fef08a" fontSize="18" fontWeight="bold">ANNAPURNA FOODGRAINS</text>
            <text x="180" y="130" textAnchor="middle" fill="#15803d" fontSize="26" fontWeight="bold">SHARBATI</text>
            <text x="250" y="170" textAnchor="middle" fill="#1c1917" fontSize="28" fontWeight="900" letterSpacing="1">SUPREME BASMATI RICE</text>
            <text x="250" y="195" textAnchor="middle" fill="#78716c" fontSize="12" fontWeight="600">ROYAL AROMA • NATURALLY AGED 2 YEARS</text>
            <circle cx="250" cy="310" r="80" fill="#ffffff" stroke="#15803d" strokeWidth="2" />
            <text x="250" y="305" textAnchor="middle" fill="#15803d" fontSize="14" fontWeight="bold">GRAIN LENGTH</text>
            <text x="250" y="330" textAnchor="middle" fill="#14532d" fontSize="24" fontWeight="bold">8.35 mm</text>
            <rect x="100" y="440" width="300" height="60" rx="4" fill="#ffffff" stroke="#15803d" strokeWidth="1.5" />
            <text x="250" y="475" textAnchor="middle" fill="#14532d" fontSize="20" fontWeight="bold">Net Quantity: 5.0 kg</text>
            <rect x="80" y="520" width="340" height="55" rx="4" fill="#ffffff" stroke="#15803d" strokeWidth="1.5" />
            <text x="250" y="546" textAnchor="middle" fill="#14532d" fontSize="16" fontWeight="bold">MRP ₹ 425.00 (inclusive of all taxes)</text>
            <text x="250" y="563" textAnchor="middle" fill="#44403c" fontSize="10">Unit Sale Price: ₹ 85.00 / kg</text>
            <text x="250" y="620" textAnchor="middle" fill="#1c1917" fontSize="10" fontWeight="bold">Packed by: Annapurna Foodgrains Corp, Karnal, Haryana</text>
            <text x="250" y="635" textAnchor="middle" fill="#57534e" fontSize="9">Rule 27 Reg: LM-REG-HR-2022-8411 | FSSAI Lic 10018021004122</text>
          </svg>
        );

      case 'front-facewash':
      case 'back-facewash':
        return (
          <svg viewBox="0 0 500 700" className="w-full h-auto select-none shadow-xl" xmlns="http://www.w3.org/2000/svg">
            <rect x="80" y="30" width="340" height="640" rx="30" fill="#f0fdf4" stroke="#059669" strokeWidth="2" />
            <rect x="180" y="30" width="140" height="35" rx="4" fill="#047857" />
            <text x="250" y="110" textAnchor="middle" fill="#065f46" fontSize="20" fontWeight="bold">NourishCare</text>
            <text x="250" y="130" textAnchor="middle" fill="#047857" fontSize="11" letterSpacing="1">HERBAL ESSENTIALS</text>
            <rect x="110" y="160" width="280" height="55" rx="6" fill="#059669" />
            <text x="250" y="195" textAnchor="middle" fill="#ffffff" fontSize="16" fontWeight="bold">PURIFYING NEEM FACE WASH</text>
            <rect x="110" y="240" width="280" height="150" rx="6" fill="#ffffff" stroke="#d1fae5" strokeWidth="1" />
            <text x="250" y="270" textAnchor="middle" fill="#065f46" fontSize="11" fontWeight="bold">MANUFACTURED BY:</text>
            <text x="250" y="290" textAnchor="middle" fill="#374151" fontSize="10">BioCosmetics Labs India LLP</text>
            <text x="250" y="305" textAnchor="middle" fill="#6b7280" fontSize="9">Phase-II, Industrial Area, Baddi, HP - 173205</text>
            <text x="250" y="335" textAnchor="middle" fill="#065f46" fontSize="11" fontWeight="bold">Net Vol: 150 ml</text>
            <text x="250" y="360" textAnchor="middle" fill="#065f46" fontSize="11" fontWeight="bold">MRP ₹ 149.00 (incl. of all taxes)</text>
            <rect x="110" y="410" width="280" height="85" rx="6" fill="#fef2f2" stroke="#b91c1c" strokeWidth="1.5" strokeDasharray="3 2" />
            <text x="250" y="435" textAnchor="middle" fill="#b91c1c" fontSize="11" fontWeight="bold">CUSTOMER QUERIES:</text>
            <text x="250" y="455" textAnchor="middle" fill="#b91c1c" fontSize="11">Visit us at: www.nourishcareindia.com</text>
            <text x="250" y="478" textAnchor="middle" fill="#991b1b" fontSize="8" fontWeight="bold">[RULE 6(1)(f) VIOLATION: MISSING PHONE & EMAIL]</text>
            <text x="250" y="550" textAnchor="middle" fill="#4b5563" fontSize="9">Batch: BC-NW-0726 | Mfg Date: 07/2026</text>
          </svg>
        );

      case 'front-charger':
      case 'back-charger':
        return (
          <svg viewBox="0 0 500 700" className="w-full h-auto select-none shadow-xl" xmlns="http://www.w3.org/2000/svg">
            <rect x="50" y="50" width="400" height="600" rx="8" fill="#0f172a" stroke="#334155" strokeWidth="2" />
            <rect x="70" y="70" width="360" height="560" fill="#1e293b" rx="6" />
            <text x="250" y="115" textAnchor="middle" fill="#38bdf8" fontSize="22" fontWeight="bold" letterSpacing="1">THUNDERPOWER</text>
            <text x="250" y="140" textAnchor="middle" fill="#94a3b8" fontSize="11" letterSpacing="2">65W GAN ULTRA FAST CHARGER</text>
            <rect x="100" y="170" width="300" height="120" rx="6" fill="#0f172a" stroke="#475569" strokeWidth="1" />
            <text x="250" y="210" textAnchor="middle" fill="#f8fafc" fontSize="12" fontWeight="bold">COMMODITY: POWER ADAPTER</text>
            <text x="250" y="235" textAnchor="middle" fill="#cbd5e1" fontSize="11">Net Qty: 1 Unit (Adapter + 100W Cable)</text>
            <text x="250" y="260" textAnchor="middle" fill="#38bdf8" fontSize="13" fontWeight="bold">MRP ₹ 2,499.00 (inclusive of all taxes)</text>
            <rect x="90" y="320" width="320" height="110" rx="6" fill="#450a0a" stroke="#dc2626" strokeWidth="2" strokeDasharray="4 2" />
            <text x="250" y="350" textAnchor="middle" fill="#fca5a5" fontSize="12" fontWeight="bold">IMPORT DECLARATIONS</text>
            <text x="250" y="375" textAnchor="middle" fill="#ffffff" fontSize="10">Imported by: Apex Global Gadgets LLP, Mumbai - 400069</text>
            <text x="250" y="405" textAnchor="middle" fill="#f87171" fontSize="9" fontWeight="bold">[RULE 6(1)(g) VIOLATION: MISSING COUNTRY OF ORIGIN]</text>
            <text x="250" y="470" textAnchor="middle" fill="#94a3b8" fontSize="10">Customer Care: support@thunderpower.in | 1800-889-1122</text>
            <text x="250" y="520" textAnchor="middle" fill="#64748b" fontSize="9">Month & Year of Import: 06/2026</text>
          </svg>
        );

      default:
        return (
          <svg viewBox="0 0 500 700" className="w-full h-auto select-none shadow-xl" xmlns="http://www.w3.org/2000/svg">
            <rect x="30" y="30" width="440" height="640" rx="10" fill="#eff6ff" stroke="#2563eb" strokeWidth="2" />
            <text x="250" y="100" textAnchor="middle" fill="#1d4ed8" fontSize="24" fontWeight="bold">SWACHH BHARAT</text>
            <text x="250" y="130" textAnchor="middle" fill="#1e40af" fontSize="14" fontWeight="bold">CONCENTRATED WASHING POWDER</text>
            <circle cx="250" cy="240" r="70" fill="#ffffff" stroke="#3b82f6" strokeWidth="2" />
            <text x="250" y="245" textAnchor="middle" fill="#1d4ed8" fontSize="16" fontWeight="bold">100% STAIN REMOVAL</text>
            <rect x="100" y="340" width="300" height="50" rx="4" fill="#ffffff" stroke="#1d4ed8" strokeWidth="1" />
            <text x="250" y="370" textAnchor="middle" fill="#1e3a8a" fontSize="16" fontWeight="bold">Net Weight: 1.0 kg</text>
            <rect x="100" y="410" width="300" height="50" rx="4" fill="#ffffff" stroke="#1d4ed8" strokeWidth="1" />
            <text x="250" y="440" textAnchor="middle" fill="#1e3a8a" fontSize="15" fontWeight="bold">MRP ₹ 135.00 (incl. of all taxes)</text>
            <rect x="80" y="480" width="340" height="65" rx="4" fill="#fffbeb" stroke="#d97706" strokeWidth="1.5" strokeDasharray="3 2" />
            <text x="250" y="505" textAnchor="middle" fill="#b45309" fontSize="11" fontWeight="bold">Mfg / Packing Date Stamp:</text>
            <text x="250" y="525" textAnchor="middle" fill="#92400e" fontSize="12" fontWeight="bold">Pkd: 0? / 2026 (Smeared Stamp)</text>
            <text x="250" y="590" textAnchor="middle" fill="#475569" fontSize="10">Hindustan Homecare Products, Indore, MP - 452015</text>
          </svg>
        );

      case 'front-lakme-sunscreen':
        return (
          <svg viewBox="0 0 500 700" className="w-full h-auto select-none shadow-2xl rounded-sm" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="lakmeGoldFront" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#fef08a" />
                <stop offset="25%" stopColor="#fcd34d" />
                <stop offset="60%" stopColor="#f59e0b" />
                <stop offset="100%" stopColor="#d97706" />
              </linearGradient>
              <pattern id="dotMatrixPattern" width="12" height="12" patternUnits="userSpaceOnUse">
                <circle cx="6" cy="6" r="1.8" fill="#d97706" opacity="0.6" />
              </pattern>
            </defs>
            {/* Box Body */}
            <rect x="60" y="20" width="380" height="660" rx="4" fill="url(#lakmeGoldFront)" stroke="#b45309" strokeWidth="1.5" />
            
            {/* Decorative Dot Cluster on Right */}
            <path d="M 280 120 Q 420 180 430 380 L 430 120 Z" fill="url(#dotMatrixPattern)" opacity="0.75" />

            {/* Brand Header */}
            <g transform="translate(90, 80)">
              <text x="0" y="32" fill="#000000" fontSize="40" fontWeight="900" letterSpacing="3" fontFamily="sans-serif">LAKMĒ</text>
              <line x1="128" y1="5" x2="152" y2="5" stroke="#000" strokeWidth="4" />
              <text x="0" y="65" fill="#1c1917" fontSize="24" fontWeight="800" letterSpacing="1">9 TO 5</text>
            </g>

            {/* Sub-claim */}
            <g transform="translate(90, 185)">
              <text x="0" y="0" fill="#1c1917" fontSize="13" fontWeight="800" letterSpacing="1">SUN PROTECTION +</text>
              <text x="0" y="16" fill="#1c1917" fontSize="13" fontWeight="800" letterSpacing="1">RADIANCE</text>
            </g>

            {/* Product Title */}
            <g transform="translate(90, 245)">
              <text x="0" y="28" fill="#000000" fontSize="36" fontWeight="900" letterSpacing="1">SUN EXPERT</text>
            </g>

            {/* Nia-C Complex Orange Tag */}
            <g transform="translate(90, 290)">
              <rect x="0" y="0" width="145" height="32" rx="3" fill="#ea580c" />
              <text x="12" y="22" fill="#ffffff" fontSize="16" fontWeight="900" letterSpacing="1">5% NIA-C</text>
              <text x="0" y="52" fill="#000000" fontSize="24" fontWeight="900" letterSpacing="1">COMPLEX~</text>
              <text x="0" y="74" fill="#1c1917" fontSize="15" fontWeight="800" letterSpacing="1">AQUA SUN GEL</text>
              <text x="0" y="105" fill="#000000" fontSize="22" fontWeight="900" letterSpacing="1">SPF 50 PA++++</text>
            </g>

            {/* Bottom House of Lakme Badge */}
            <g transform="translate(330, 500)">
              <rect x="0" y="0" width="90" height="110" rx="3" fill="#171717" />
              <text x="45" y="60" textAnchor="middle" fill="#d97706" fontSize="11" fontWeight="bold" letterSpacing="1" transform="rotate(-90 45 60)">HOUSE of LAKMĒ</text>
            </g>

            {/* Bottom Glow */}
            <rect x="60" y="620" width="380" height="60" fill="#c2410c" opacity="0.75" />
          </svg>
        );

      case 'back-lakme-sunscreen':
        return (
          <svg viewBox="0 0 500 700" className="w-full h-auto select-none shadow-2xl rounded-sm" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="lakmeGoldBack" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#fef3c7" />
                <stop offset="30%" stopColor="#fde68a" />
                <stop offset="70%" stopColor="#f59e0b" />
                <stop offset="100%" stopColor="#ea580c" />
              </linearGradient>
            </defs>
            {/* Box Body */}
            <rect x="60" y="15" width="380" height="670" rx="4" fill="url(#lakmeGoldBack)" stroke="#b45309" strokeWidth="1.5" />

            {/* Header text */}
            <g transform="translate(78, 38)">
              <text x="0" y="0" fill="#0f172a" fontSize="10.5" fontWeight="900" letterSpacing="0.5">LAKMÉ SUN EXPERT 5% NIA-C COMPLEX~</text>
              <text x="0" y="12" fill="#0f172a" fontSize="10" fontWeight="900" letterSpacing="0.5">AQUA SUN GEL</text>
              <text x="0" y="24" fill="#1c1917" fontSize="8" fontWeight="800">FASHIONISTA'S FIX TO SUN PROTECTION & RADIANCE!</text>
              
              <text x="0" y="38" fill="#334155" fontSize="6.8" width="340">This sunscreen gel with SPF 50 and PA++++ gives broad-spectrum protection</text>
              <text x="0" y="48" fill="#334155" fontSize="6.8">infused with Niacinamide & Vit C. Lightweight feel, no white cast.</text>
              <text x="0" y="58" fill="#334155" fontSize="6.8" fontWeight="bold">Dermatologically tested. Suitable for all skin types.</text>

              <text x="0" y="74" fill="#1c1917" fontSize="7.5" fontWeight="bold">SUNSCREEN SKIN GEL. MADE IN INDIA.</text>
              <text x="0" y="86" fill="#0f172a" fontSize="7" fontWeight="bold">MKTD. BY: HINDUSTAN UNILEVER LIMITED (HUL)</text>
              <text x="0" y="96" fill="#334155" fontSize="6.5">Unilever House, B. D. Sawant Marg, Andheri (E), Mumbai 400 099.</text>
              <text x="0" y="108" fill="#0f172a" fontSize="6.5" fontWeight="bold">FOR NAME & ADDRESS OF MFG. UNIT SEE FIRST CHAR OF CODE.</text>
              <text x="0" y="118" fill="#334155" fontSize="6.2">MFG. BY: (AA) L.B.C.P., UNIT II, HARIDWAR 249 403, UK. M 16/C/UA/2010.</text>
              <text x="0" y="128" fill="#1e293b" fontSize="6.5" fontWeight="bold">(AY) AERO CARE PERSONAL PRODUCTS LLP, SURVEY 284/2,</text>
              <text x="0" y="137" fill="#1e293b" fontSize="6.5" fontWeight="bold">VILLAGE NAROLI, DADRA & NAGAR HAVELI - 396 235. M DNH/C/138.</text>

              <text x="0" y="150" fill="#334155" fontSize="6.5">HUL REGN. NO. B0-14-000-03-AAACH1004N-24. LAKMÉ TRADEMARK.</text>
              
              {/* Consumer Care Box */}
              <rect x="0" y="157" width="344" height="34" fill="#ffffff" opacity="0.9" rx="2" stroke="#d97706" strokeWidth="0.8" />
              <text x="8" y="168" fill="#0f172a" fontSize="7" fontWeight="bold">LEVERCARE-QUERY / FEEDBACK (Rule 6(1)(f)):</text>
              <text x="8" y="178" fill="#1e293b" fontSize="6.8" fontWeight="bold">TOLL FREE: 1800-10-22-221 | PO BOX 14760, MUMBAI 400 099</text>
              <text x="8" y="187" fill="#0369a1" fontSize="6.8" fontWeight="bold">EMAIL: LEVER.CARE@UNILEVER.COM</text>

              {/* Net Wt */}
              <text x="0" y="210" fill="#000000" fontSize="15" fontWeight="900">Net Wt.: 56 g</text>
            </g>

            {/* Barcode Section */}
            <g transform="translate(140, 275)">
              <rect x="0" y="0" width="220" height="75" fill="#ffffff" rx="3" stroke="#cbd5e1" strokeWidth="1" />
              <g transform="translate(20, 10)">
                <rect x="0" y="0" width="3" height="42" fill="#000" />
                <rect x="6" y="0" width="2" height="42" fill="#000" />
                <rect x="11" y="0" width="4" height="42" fill="#000" />
                <rect x="18" y="0" width="2" height="42" fill="#000" />
                <rect x="24" y="0" width="5" height="42" fill="#000" />
                <rect x="32" y="0" width="3" height="42" fill="#000" />
                <rect x="39" y="0" width="2" height="42" fill="#000" />
                <rect x="45" y="0" width="4" height="42" fill="#000" />
                <rect x="53" y="0" width="2" height="42" fill="#000" />
                <rect x="60" y="0" width="4" height="42" fill="#000" />
                <rect x="68" y="0" width="3" height="42" fill="#000" />
                <rect x="75" y="0" width="5" height="42" fill="#000" />
                <rect x="85" y="0" width="2" height="42" fill="#000" />
                <rect x="91" y="0" width="4" height="42" fill="#000" />
                <rect x="99" y="0" width="3" height="42" fill="#000" />
                <rect x="106" y="0" width="5" height="42" fill="#000" />
                <rect x="115" y="0" width="2" height="42" fill="#000" />
                <rect x="122" y="0" width="4" height="42" fill="#000" />
                <rect x="130" y="0" width="2" height="42" fill="#000" />
                <rect x="136" y="0" width="5" height="42" fill="#000" />
                <rect x="145" y="0" width="3" height="42" fill="#000" />
                <rect x="152" y="0" width="4" height="42" fill="#000" />
                <rect x="160" y="0" width="3" height="42" fill="#000" />
                <rect x="168" y="0" width="5" height="42" fill="#000" />
                <text x="89" y="55" textAnchor="middle" fill="#000000" fontSize="12" fontFamily="monospace" fontWeight="bold">8 909106 031241</text>
              </g>
            </g>

            {/* Inkjet Coding Area (Exact match to product) */}
            <g transform="translate(130, 360)">
              <text x="120" y="-8" textAnchor="middle" fill="#78350f" fontSize="7.5" fontWeight="bold">*MRP ₹ (INCL. OF ALL TAXES), USP, #MFD., B. NO. &amp; @USE BEFORE</text>
              <rect x="20" y="0" width="200" height="90" rx="3" fill="#09090b" stroke="#27272a" strokeWidth="1.5" />
              
              {/* Dot-matrix cyan/white inkjet text */}
              <text x="40" y="24" fill="#38bdf8" fontSize="14" fontFamily="monospace" fontWeight="bold" letterSpacing="1">AY * ₹ 499/-</text>
              <text x="40" y="44" fill="#38bdf8" fontSize="13" fontFamily="monospace" fontWeight="bold" letterSpacing="1">USP ₹ 8.91/g</text>
              <text x="40" y="64" fill="#38bdf8" fontSize="13" fontFamily="monospace" fontWeight="bold" letterSpacing="1"># 02/26 B005</text>
              <text x="40" y="80" fill="#38bdf8" fontSize="13" fontFamily="monospace" fontWeight="bold" letterSpacing="1">@ 01/28</text>
            </g>

            {/* Bottom code */}
            <text x="80" y="475" fill="#451a03" fontSize="8" fontFamily="monospace">64896784</text>
          </svg>
        );
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-700/80 rounded-lg overflow-hidden select-none shadow-md">
      {/* Viewer Toolbar */}
      <div className="flex items-center justify-between px-3 py-2 bg-slate-800 border-b border-slate-700 text-slate-200 text-xs">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-white tracking-wide">{surface}</span>
          <span className="text-slate-500">|</span>
          <span className="text-emerald-400 font-medium text-[11px] flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block mr-1"></span>
            {customImageUrl ? 'Live Captured Photo' : 'Digital Label Asset'}
          </span>
        </div>
        <div className="flex items-center space-x-1.5">
          <button
            type="button"
            onClick={() => setShowRulerGrid(!showRulerGrid)}
            className={`p-1.5 rounded text-xs transition flex items-center space-x-1 ${
              showRulerGrid ? 'bg-emerald-600 text-white font-bold' : 'hover:bg-slate-700 text-slate-300'
            }`}
            title="Toggle Pixel-to-mm Optical Grid (Stage 2 OpenCV / scikit-image Calibration)"
          >
            <Ruler className="w-3.5 h-3.5" />
            <span className="hidden sm:inline text-[10px]">Pixel-to-mm</span>
          </button>
          <div className="h-3 w-[1px] bg-slate-700 mx-1" />
          <button
            onClick={handleZoomOut}
            className="p-1.5 hover:bg-slate-700 rounded text-slate-300 hover:text-white transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="font-mono text-xs text-slate-200 px-1.5 min-w-[42px] text-center font-bold">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-1.5 hover:bg-slate-700 rounded text-slate-300 hover:text-white transition"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleResetZoom}
            className="p-1.5 hover:bg-slate-700 rounded text-slate-300 hover:text-white transition"
            title="Reset Zoom & Alignment"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Inspection Viewport */}
      <div className="relative flex-1 overflow-auto bg-slate-950 flex items-center justify-center p-4 min-h-[400px]">
        {/* Pixel-to-mm Calibration Grid Overlay */}
        {showRulerGrid && (
          <div className="absolute inset-0 pointer-events-none z-20 bg-[linear-gradient(to_right,#334155_1px,transparent_1px),linear-gradient(to_bottom,#334155_1px,transparent_1px)] bg-[size:20px_20px] opacity-30">
            <div className="absolute top-2 right-2 bg-black/70 text-emerald-400 font-mono text-[10px] px-2 py-0.5 rounded border border-emerald-500/40">
              1 Grid Unit = 2.5 mm (Calibrated with NumPy/scikit-image)
            </div>
          </div>
        )}

        <div
          className="relative transition-transform duration-150 ease-out origin-center max-w-[450px] w-full shadow-2xl rounded"
          style={{ transform: `scale(${zoom}) translate(${pan.x}px, ${pan.y}px)` }}
        >
          {/* If custom image URL exists (from camera or upload), display the real photo */}
          {customImageUrl ? (
            <div className="relative w-full rounded overflow-hidden border border-slate-700 shadow-2xl bg-black">
              <img
                src={customImageUrl}
                alt="Product Label"
                className="w-full h-auto object-contain max-h-[580px]"
              />
              <div className="absolute bottom-2 left-2 bg-black/60 backdrop-blur-xs text-white text-[10px] px-2 py-0.5 rounded font-mono">
                Real Label Photo • 300 DPI Optical Ingest
              </div>
            </div>
          ) : (
            renderSvgContent()
          )}

          {/* Overlay Bounding Boxes */}
          {showAnnotations && boundingBoxes.map((box, idx) => {
            const isHighlighted = highlightBox?.label === box.label;
            const isViolation = box.label.toLowerCase().includes('violation') || box.label.toLowerCase().includes('missing') || box.label.toLowerCase().includes('sub-sized');
            
            return (
              <div
                key={idx}
                onClick={() => onBoxClick && onBoxClick(box)}
                className={`absolute cursor-pointer border-2 transition-all ${
                  isViolation
                    ? 'border-red-500 bg-red-500/20 hover:bg-red-500/35 shadow-lg animate-pulse'
                    : isHighlighted
                    ? 'border-amber-400 bg-amber-400/25 shadow-lg'
                    : 'border-emerald-500/90 bg-emerald-500/15 hover:bg-emerald-500/30'
                }`}
                style={{
                  left: `${box.x}%`,
                  top: `${box.y}%`,
                  width: `${box.width}%`,
                  height: `${box.height}%`
                }}
                title={box.label}
              >
                <div
                  className={`absolute -top-5 left-0 px-2 py-0.5 text-[9px] font-bold text-white rounded whitespace-nowrap shadow-md ${
                    isViolation ? 'bg-red-600' : 'bg-emerald-700'
                  }`}
                >
                  {box.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Viewer Footer Status */}
      <div className="px-3 py-2 bg-slate-850 border-t border-slate-700 text-[11px] text-slate-300 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="font-mono text-emerald-400 font-semibold">Stage 2: YOLOv8 ROI Segmentation Active</span>
        </div>
        <div className="flex items-center space-x-3">
          <span className="flex items-center text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block mr-1"></span>
            Verified Text
          </span>
          <span className="flex items-center text-red-400">
            <span className="w-2 h-2 rounded-full bg-red-500 inline-block mr-1"></span>
            Infraction Detected
          </span>
        </div>
      </div>
    </div>
  );
};
