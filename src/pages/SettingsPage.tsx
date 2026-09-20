import React, { useState } from 'react';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import {
  Sliders,
  Save,
  RotateCcw,
  CheckCircle2,
  Building2,
  Printer,
  Bell,
  Shield,
  WifiOff
} from 'lucide-react';
import { useInspection } from '../context/InspectionContext';
import { JurisdictionSelector } from '../components/jurisdiction/JurisdictionSelector';
import { Jurisdiction } from '../types';

export const SettingsPage: React.FC = () => {
  const { activeJurisdiction, setActiveJurisdiction } = useInspection();
  const [terminalJurisdiction, setTerminalJurisdiction] = useState<Jurisdiction>(activeJurisdiction);
  const [fontTolerance, setFontTolerance] = useState('0.15 mm');
  const [autoFlagViolations, setAutoFlagViolations] = useState(true);
  const [offlineCacheEnabled, setOfflineCacheEnabled] = useState(true);
  const [printerFormat, setPrinterFormat] = useState('A4 Portrait (Official Form)');
  const [isSaved, setIsSaved] = useState(false);

  const handleSaveSettings = (e: React.FormEvent) => {
    e.preventDefault();
    setActiveJurisdiction(terminalJurisdiction);
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2500);
  };

  const handleResetData = () => {
    if (window.confirm('Reset all demo inspections, audit logs, and products to initial state?')) {
      localStorage.clear();
      window.location.reload();
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E5E2DD] pb-4">
        <div>
          <h1 className="text-2xl font-bold text-[#1F2328] tracking-tight">System & Enforcement Settings</h1>
          <p className="text-xs text-[#5F6368] mt-0.5">
            Configure jurisdictional defaults, statutory tolerances, printer templates, and local cache
          </p>
        </div>
        {isSaved && (
          <div className="flex items-center space-x-1.5 text-xs text-[#16A34A] bg-[#F0FDF4] border border-[#BBF7D0] px-3 py-1.5 rounded-lg animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 text-[#16A34A]" />
            <span>Settings saved successfully</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSaveSettings} className="space-y-6">
        {/* Jurisdictional Defaults */}
        <Card>
          <CardHeader
            title="Jurisdiction & Field Station Defaults"
            subtitle="Default enforcement station mapped to current inspection terminal"
          />
          <CardContent className="space-y-4 text-xs">
            <JurisdictionSelector
              value={terminalJurisdiction}
              onChange={setTerminalJurisdiction}
              layout="grid"
              showTitle={false}
            />

            <div className="pt-3 border-t border-[#F0EDE8]">
              <label className="block font-semibold text-[#1F2328] mb-1">
                Terminal Machine Node ID
              </label>
              <input
                type="text"
                readOnly
                value="LMCS-TERMINAL-MH-04"
                className="w-full sm:w-1/2 bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs text-[#5F6368] font-mono"
              />
            </div>
          </CardContent>
        </Card>

        {/* Rule Tolerances & Optical Parameters */}
        <Card>
          <CardHeader
            title="Statutory Rule Tolerances & Verification Sensitivity"
            subtitle="Optical measurement tolerances for font height and maximum permissible errors"
          />
          <CardContent className="space-y-4 text-xs">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold text-[#1F2328] mb-1">
                  PDP Numeral Height Tolerance (Rule 7 & 8)
                </label>
                <select
                  value={fontTolerance}
                  onChange={(e) => setFontTolerance(e.target.value)}
                  className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED] cursor-pointer"
                >
                  <option value="0.10 mm">Strict: ± 0.10 mm</option>
                  <option value="0.15 mm">Standard Departmental: ± 0.15 mm (Recommended)</option>
                  <option value="0.25 mm">Lenient: ± 0.25 mm</option>
                </select>
                <span className="text-[11px] text-[#8A8F98] mt-1 block">
                  Permitted variance when calibrating curved pouch or bottle labels
                </span>
              </div>

              <div>
                <label className="block font-semibold text-[#1F2328] mb-1">
                  Automated Non-Compliance Tagging
                </label>
                <label className="flex items-center space-x-2 mt-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoFlagViolations}
                    onChange={(e) => setAutoFlagViolations(e.target.checked)}
                    className="rounded text-[#7C3AED] focus:ring-[#7C3AED] border-[#E5E2DD] cursor-pointer"
                  />
                  <span className="text-[#5F6368]">
                    Immediately flag omitted statutory phrases ("inclusive of all taxes") as High Severity
                  </span>
                </label>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Printer & Official Report Template */}
        <Card>
          <CardHeader
            title="Official Report & Print Formatting"
            subtitle="Parameters for generating Legal Metrology Challan documents"
          />
          <CardContent className="space-y-4 text-xs">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold text-[#1F2328] mb-1">
                  Standard Print Paper Format
                </label>
                <select
                  value={printerFormat}
                  onChange={(e) => setPrinterFormat(e.target.value)}
                  className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED] cursor-pointer"
                >
                  <option value="A4 Portrait (Official Form)">A4 Portrait (Official Legal Metrology Form)</option>
                  <option value="Legal Size (Court Docket)">Legal Size (Court Evidence Docket)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-[#1F2328] mb-1">
                  Cryptographic Verification Seal
                </label>
                <input
                  type="text"
                  readOnly
                  value="Enabled (SHA-256 Hash + Verification QR)"
                  className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs text-[#5F6368] font-mono"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Offline Cache & Field Storage */}
        <Card>
          <CardHeader
            title="Offline Field Operation Mode"
            subtitle="Local storage settings for inspections in rural markets or low-connectivity zones"
          />
          <CardContent className="space-y-3 text-xs">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={offlineCacheEnabled}
                onChange={(e) => setOfflineCacheEnabled(e.target.checked)}
                className="rounded text-[#7C3AED] focus:ring-[#7C3AED] border-[#E5E2DD] cursor-pointer"
              />
              <span className="font-semibold text-[#1F2328]">
                Enable local encrypted storage of inspections when offline
              </span>
            </label>
            <p className="text-[#5F6368] text-[11px] leading-relaxed">
              When working in field inspections without active connectivity, images and inspection dockets are securely cached on the browser local storage and queued for synchronization.
            </p>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleResetData}
            leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
          >
            Reset Prototype Demonstration Data
          </Button>

          <Button
            type="submit"
            variant="primary"
            size="md"
            leftIcon={<Save className="w-4 h-4 text-white" />}
          >
            Save Regulatory Settings
          </Button>
        </div>
      </form>
    </div>
  );
};
