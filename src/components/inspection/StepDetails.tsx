import React from 'react';
import { useInspection } from '../../context/InspectionContext';
import { useAuth } from '../../context/AuthContext';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { ArrowRight, Sparkles, Building2, User, Calendar, MapPin, Tag } from 'lucide-react';
import { InspectionType } from '../../types';

export const StepDetails: React.FC = () => {
  const { currentInspection, updateInspectionDetails, setActiveStep } = useInspection();
  const { currentUser } = useAuth();

  if (!currentInspection) return null;

  const handleContinue = (e: React.FormEvent) => {
    e.preventDefault();
    setActiveStep(2); // Proceed to Capture
  };

  return (
    <form onSubmit={handleContinue} className="space-y-6">
      <Card>
        <CardHeader
          title="Section 1: Statutory Inspection Docket Information"
          subtitle="Record mandatory inspection parameters in accordance with Rule 6 of Legal Metrology Rules, 2011"
        />
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Inspection ID */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Inspection Docket ID <span className="text-slate-400 font-normal">(Auto-generated)</span>
              </label>
              <input
                type="text"
                readOnly
                value={currentInspection.id}
                className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 font-mono font-medium focus:outline-none"
              />
            </div>

            {/* Inspection Date */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Inspection Date & Time
              </label>
              <input
                type="date"
                value={currentInspection.date}
                onChange={(e) => updateInspectionDetails({ date: e.target.value })}
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
                required
              />
            </div>

            {/* Inspection Type */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Inspection Classification / Type
              </label>
              <select
                value={currentInspection.inspectionType}
                onChange={(e) => updateInspectionDetails({ inspectionType: e.target.value as InspectionType })}
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              >
                <option value="Market Surveillance">Market Surveillance (Retail Depot / Supermarket)</option>
                <option value="Consumer Complaint">Consumer Complaint (Section 36 Investigation)</option>
                <option value="Port of Entry Inward">Port of Entry Inward (Customs Clearance Cargo)</option>
                <option value="Routine Audit">Routine Mandatory Packing Facility Audit</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            {/* Officer Name */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Authorized Enforcement Officer
              </label>
              <input
                type="text"
                value={currentInspection.officerName}
                onChange={(e) => updateInspectionDetails({ officerName: e.target.value })}
                className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
                required
              />
              <span className="text-[10px] text-slate-500 mt-0.5 block">
                Badge Number: {currentInspection.officerBadge}
              </span>
            </div>

            {/* Location */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Physical Inspection Location / Store / Warehouse
              </label>
              <input
                type="text"
                value={currentInspection.location}
                onChange={(e) => updateInspectionDetails({ location: e.target.value })}
                placeholder="e.g. Retail Store, Warehouse, or Port Terminal"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
                required
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader
          title="Section 2: Packaged Commodity & Manufacturer Particulars"
          subtitle="Declared commercial particulars as printed on the package outer carton or container (or leave blank to auto-extract via OCR in Step 2)"
        />
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Product Name */}
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Product Commercial Name
              </label>
              <input
                type="text"
                value={currentInspection.productName}
                onChange={(e) => updateInspectionDetails({ productName: e.target.value })}
                placeholder="e.g. Pure Ground Spices 200g (or auto-detected via OCR)"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              />
            </div>

            {/* Product Category */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Regulatory Category
              </label>
              <select
                value={currentInspection.category}
                onChange={(e) => updateInspectionDetails({ category: e.target.value })}
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              >
                <option value="Edible Oils & Fats">Edible Oils & Fats</option>
                <option value="Food & Grains">Food & Grains (Rice, Atta, Pulses)</option>
                <option value="Food & Beverages">Food & Beverages (Tea, Coffee, Juices)</option>
                <option value="Food & Spices">Food & Spices (Turmeric, Masalas)</option>
                <option value="Personal Care & Cosmetics">Personal Care & Cosmetics (Face Wash, Soaps)</option>
                <option value="Household Chemicals">Household Chemicals (Detergents, Cleaners)</option>
                <option value="Consumer Electronics">Consumer Electronics (Chargers, Accessories)</option>
                <option value="General Packaged Commodity">General Packaged Commodity</option>
                <option value="Textiles & Apparel">Textiles & Apparel</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Brand */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Brand Name
              </label>
              <input
                type="text"
                value={currentInspection.brand}
                onChange={(e) => updateInspectionDetails({ brand: e.target.value })}
                placeholder="e.g. Brand Name"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              />
            </div>

            {/* Barcode / GTIN */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                EAN-13 / Barcode / GTIN Number
              </label>
              <input
                type="text"
                value={currentInspection.barcode}
                onChange={(e) => updateInspectionDetails({ barcode: e.target.value })}
                placeholder="e.g. 8901234567890"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs font-mono text-slate-800 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              />
            </div>

            {/* Batch Number */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Lot / Batch Number
              </label>
              <input
                type="text"
                value={currentInspection.batchNumber}
                onChange={(e) => updateInspectionDetails({ batchNumber: e.target.value })}
                placeholder="e.g. BATCH-01/2026"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs font-mono text-slate-800 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              />
            </div>
          </div>

          {/* Manufacturer & Address */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Manufacturer / Packer / Importer Full Address (As Declared on Package)
            </label>
            <textarea
              rows={2}
              value={currentInspection.manufacturer}
              onChange={(e) => updateInspectionDetails({ manufacturer: e.target.value })}
              placeholder="e.g. Full Legal Entity Name, Industrial Estate, City, State - PIN Code"
              className="w-full bg-white border border-slate-300 rounded p-2 text-xs text-slate-800 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
            />
          </div>
        </CardContent>
      </Card>

      {/* Action Footer */}
      <div className="flex items-center justify-between pt-2">
        <div className="text-xs text-slate-500">
          You can enter known particulars now or proceed directly to photo capture for OCR extraction.
        </div>
        <Button
          type="submit"
          variant="primary"
          size="md"
          rightIcon={<ArrowRight className="w-4 h-4" />}
        >
          Continue to Product Capture
        </Button>
      </div>
    </form>
  );
};
