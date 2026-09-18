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

export const SettingsPage: React.FC = () => {
  const [defaultZone, setDefaultZone] = useState('Delhi NCR - Central Zone');
  const [fontTolerance, setFontTolerance] = useState('0.15 mm');
  const [autoFlagViolations, setAutoFlagViolations] = useState(true);
  const [offlineCacheEnabled, setOfflineCacheEnabled] = useState(true);
  const [printerFormat, setPrinterFormat] = useState('A4 Portrait (Official Form)');
  const [isSaved, setIsSaved] = useState(false);

  const handleSaveSettings = (e: React.FormEvent) => {
    e.preventDefault();
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">System & Enforcement Settings</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Configure jurisdictional defaults, statutory tolerances, printer templates, and local cache
          </p>
        </div>
        {isSaved && (
          <div className="flex items-center space-x-1 text-xs text-emerald-800 bg-emerald-50 border border-emerald-300 px-3 py-1.5 rounded animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
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
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Primary Zonal Controllerate
                </label>
                <select
                  value={defaultZone}
                  onChange={(e) => setDefaultZone(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-[#0f2942]"
                >
                  <option value="Delhi NCR - Central Zone">Delhi NCR - Central Zone</option>
                  <option value="Maharashtra - Mumbai Zone I">Maharashtra - Mumbai Zone I</option>
                  <option value="Karnataka - Bengaluru South">Karnataka - Bengaluru South</option>
                  <option value="Tamil Nadu - Chennai North">Tamil Nadu - Chennai North</option>
                  <option value="West Bengal - Kolkata Central">West Bengal - Kolkata Central</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Terminal Machine Node ID
                </label>
                <input
                  type="text"
                  readOnly
                  value="LMCS-TERMINAL-DEL-04"
                  className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-700 font-mono"
                />
              </div>
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
                <label className="block font-semibold text-slate-700 mb-1">
                  PDP Numeral Height Tolerance (Rule 7 & 8)
                </label>
                <select
                  value={fontTolerance}
                  onChange={(e) => setFontTolerance(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-[#0f2942]"
                >
                  <option value="0.10 mm">Strict: ± 0.10 mm</option>
                  <option value="0.15 mm">Standard Departmental: ± 0.15 mm (Recommended)</option>
                  <option value="0.25 mm">Lenient: ± 0.25 mm</option>
                </select>
                <span className="text-[10px] text-slate-500 mt-1 block">
                  Permitted variance when calibrating curved pouch or bottle labels
                </span>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Automated Non-Compliance Tagging
                </label>
                <label className="flex items-center space-x-2 mt-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoFlagViolations}
                    onChange={(e) => setAutoFlagViolations(e.target.checked)}
                    className="rounded text-[#0f2942] focus:ring-[#0f2942] border-slate-300"
                  />
                  <span className="text-slate-700">
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
                <label className="block font-semibold text-slate-700 mb-1">
                  Standard Print Paper Format
                </label>
                <select
                  value={printerFormat}
                  onChange={(e) => setPrinterFormat(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-[#0f2942]"
                >
                  <option value="A4 Portrait (Official Form)">A4 Portrait (Official Legal Metrology Form)</option>
                  <option value="Legal Size (Court Docket)">Legal Size (Court Evidence Docket)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Cryptographic Verification Seal
                </label>
                <input
                  type="text"
                  readOnly
                  value="Enabled (SHA-256 Hash + Verification QR)"
                  className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-700 font-mono"
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
                className="rounded text-[#0f2942] focus:ring-[#0f2942] border-slate-300"
              />
              <span className="font-semibold text-slate-900">
                Enable local encrypted storage of inspections when offline
              </span>
            </label>
            <p className="text-slate-500 text-[11px] leading-relaxed">
              When working in field inspections without active NIC VPN connectivity, images and inspection dockets are securely cached on the browser local storage and queued for background synchronization.
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
            leftIcon={<Save className="w-4 h-4" />}
          >
            Save Regulatory Settings
          </Button>
        </div>
      </form>
    </div>
  );
};
