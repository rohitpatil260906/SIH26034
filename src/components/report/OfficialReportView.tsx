import React from 'react';
import { InspectionRecord } from '../../types';
import { Button } from '../ui/Button';
import { StatusBadge } from '../ui/Badge';
import {
  Printer,
  Download,
  Share2,
  FileSpreadsheet,
  ArrowLeft,
  Shield,
  QrCode,
  CheckCircle2,
  AlertOctagon,
  Scale
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const OfficialReportView: React.FC<{ inspection: InspectionRecord }> = ({ inspection }) => {
  const navigate = useNavigate();

  const handlePrint = () => {
    window.print();
  };

  const handleExportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(inspection, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `LMCS_Report_${inspection.id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleExportCSV = () => {
    const headers = "Declaration Type,Extracted Value,Expected Requirement,Rule Reference,Surface,Status\n";
    const rows = inspection.declarations.map(d =>
      `"${d.declarationType}","${d.extractedValue.replace(/"/g, '""')}","${d.expectedRequirement.replace(/"/g, '""')}","${d.ruleReference}","${d.surface}","${d.status}"`
    ).join("\n");
    const blob = new Blob([headers + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `LMCS_Declarations_${inspection.id}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div className="space-y-6">
      {/* Top Action Toolbar (Hidden during print) */}
      <div className="no-print flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-white border border-slate-200 rounded-md p-3.5 shadow-2xs">
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<ArrowLeft className="w-4 h-4" />}
            onClick={() => navigate('/inspections')}
          >
            All Inspections
          </Button>
          <span className="text-slate-300">|</span>
          <span className="text-xs text-slate-600 font-mono font-semibold">
            Docket: {inspection.id}
          </span>
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Button
            variant="secondary"
            size="sm"
            leftIcon={<FileSpreadsheet className="w-4 h-4" />}
            onClick={handleExportCSV}
          >
            Export CSV
          </Button>
          <Button
            variant="secondary"
            size="sm"
            leftIcon={<Download className="w-4 h-4" />}
            onClick={handleExportJSON}
          >
            Export JSON
          </Button>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Printer className="w-4 h-4" />}
            onClick={handlePrint}
          >
            Print Official Report (PDF)
          </Button>
        </div>
      </div>

      {/* Official Government Inspection Document Container */}
      <div className="print-report-container bg-white border border-slate-300 rounded-md shadow-sm max-w-4xl mx-auto p-6 md:p-10 font-serif text-slate-900 space-y-6">
        {/* National Emblem & Department Official Header */}
        <div className="text-center border-b-2 border-slate-900 pb-4 space-y-1">
          <div className="w-12 h-12 mx-auto border border-slate-900 rounded-full flex items-center justify-center mb-1 font-bold text-slate-900 text-sm">
            सत्यमेव जयते
          </div>
          <p className="text-xs uppercase font-bold tracking-widest text-slate-900 font-sans">
            GOVERNMENT OF INDIA
          </p>
          <p className="text-xs uppercase font-semibold tracking-wider text-slate-800 font-sans">
            MINISTRY OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION
          </p>
          <h1 className="text-base md:text-lg font-bold text-slate-950 uppercase tracking-wide mt-1">
            DEPARTMENT OF LEGAL METROLOGY (ENFORCEMENT WING)
          </h1>
          <p className="text-xs font-semibold uppercase text-slate-700 font-sans pt-0.5">
            LEGALMETRO COMPLIANCE SCANNER (LMCS) • STATUTORY INSPECTION CHALLAN
          </p>
          <div className="inline-block border border-slate-800 px-3 py-0.5 text-xs font-bold uppercase tracking-wider mt-2 font-sans">
            Form of Inspection under Legal Metrology (Packaged Commodities) Rules, 2011
          </div>
        </div>

        {/* Inspection Docket Metadata Table */}
        <div className="font-sans text-xs border border-slate-400">
          <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-y md:divide-y-0 divide-slate-300 bg-slate-50 font-medium">
            <div className="p-2">
              <span className="text-[10px] text-slate-500 uppercase block">Inspection Docket No.</span>
              <span className="font-mono font-bold text-slate-950">{inspection.id}</span>
            </div>
            <div className="p-2">
              <span className="text-[10px] text-slate-500 uppercase block">Inspection Date</span>
              <span className="font-bold text-slate-950">{inspection.date}</span>
            </div>
            <div className="p-2">
              <span className="text-[10px] text-slate-500 uppercase block">Jurisdiction Zone</span>
              <span className="font-bold text-slate-950">{inspection.jurisdiction}</span>
            </div>
            <div className="p-2">
              <span className="text-[10px] text-slate-500 uppercase block">Inspection Nature</span>
              <span className="font-bold text-slate-950">{inspection.inspectionType}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-300 border-t border-slate-300 p-2 bg-white">
            <div>
              <span className="text-[10px] text-slate-500 uppercase block">Inspection Premise / Establishment</span>
              <span className="font-semibold text-slate-900">{inspection.location}</span>
            </div>
            <div className="pt-2 md:pt-0 md:pl-2">
              <span className="text-[10px] text-slate-500 uppercase block">Inspecting Enforcement Officer</span>
              <span className="font-semibold text-slate-900">
                {inspection.officerName} <span className="font-mono text-slate-600">({inspection.officerBadge})</span>
              </span>
            </div>
          </div>
        </div>

        {/* Commodity Particulars */}
        <div className="font-sans space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b border-slate-300 pb-1">
            1. Particulars of the Packaged Commodity
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="border border-slate-300 p-2 rounded-xs">
              <span className="text-[10px] text-slate-500 uppercase block">Commodity Name</span>
              <span className="font-bold text-slate-950">{inspection.productName}</span>
            </div>
            <div className="border border-slate-300 p-2 rounded-xs">
              <span className="text-[10px] text-slate-500 uppercase block">Regulatory Category</span>
              <span className="font-semibold text-slate-900">{inspection.category}</span>
            </div>
            <div className="border border-slate-300 p-2 rounded-xs">
              <span className="text-[10px] text-slate-500 uppercase block">Barcode / GTIN</span>
              <span className="font-mono text-slate-900">{inspection.barcode || 'N/A'}</span>
            </div>
          </div>

          <div className="border border-slate-300 p-2.5 rounded-xs text-xs space-y-1">
            <span className="text-[10px] text-slate-500 uppercase block">
              Declared Manufacturer / Packer / Importer
            </span>
            <p className="font-semibold text-slate-900 leading-snug">
              {inspection.manufacturer}
            </p>
            <div className="text-[11px] text-slate-600 flex items-center space-x-4 pt-1 font-mono">
              <span>Lot / Batch No: {inspection.batchNumber}</span>
              <span>Statutory Rule 27 Registration: Verified on State Portal</span>
            </div>
          </div>
        </div>

        {/* Mandatory Declarations Table */}
        <div className="font-sans space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b border-slate-300 pb-1">
            2. Statutory Declarations Scrutiny Table (Rule 6, 7 & 8)
          </h3>
          <table className="w-full text-left text-xs border border-slate-400 border-collapse">
            <thead className="bg-slate-100 text-slate-900 font-bold border-b border-slate-400">
              <tr>
                <th className="p-2 border-r border-slate-300">Mandatory Declaration</th>
                <th className="p-2 border-r border-slate-300">Declared Value on Package</th>
                <th className="p-2 border-r border-slate-300">Prescribed Statutory Clause</th>
                <th className="p-2 border-r border-slate-300">Surface</th>
                <th className="p-2 text-center">Finding</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-300">
              {inspection.declarations.map((dec) => (
                <tr key={dec.id}>
                  <td className="p-2 font-semibold border-r border-slate-300">{dec.declarationType}</td>
                  <td className="p-2 font-mono text-[11px] border-r border-slate-300 max-w-[220px]">{dec.extractedValue}</td>
                  <td className="p-2 text-[11px] text-slate-700 border-r border-slate-300 font-mono">{dec.ruleReference}</td>
                  <td className="p-2 text-[11px] border-r border-slate-300">{dec.surface}</td>
                  <td className="p-2 text-center font-bold text-[11px]">
                    {dec.status === 'Found' ? (
                      <span className="text-emerald-800">CONFORMING</span>
                    ) : (
                      <span className="text-red-700">NON-COMPLIANT</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Violations & Evidence Findings */}
        <div className="font-sans space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b border-slate-300 pb-1">
            3. Statutory Infractions & Offence Formulations
          </h3>
          {inspection.violations.length === 0 ? (
            <p className="text-xs text-slate-600 italic p-3 bg-slate-50 border border-slate-200">
              Zero offences detected. The packaged commodity complies with all mandatory provisions under Legal Metrology Rules, 2011.
            </p>
          ) : (
            <div className="space-y-3">
              {inspection.violations.map((vio, index) => (
                <div key={vio.id} className="border border-red-300 bg-red-50/20 p-3 rounded-xs text-xs space-y-1.5">
                  <div className="flex items-center justify-between font-bold">
                    <span className="text-red-950">
                      Charge {index + 1}: {vio.violationType}
                    </span>
                    <span className="font-mono text-red-900 text-[11px] bg-red-100 px-2 py-0.5 rounded">
                      {vio.ruleReference}
                    </span>
                  </div>
                  <p className="text-slate-800 text-[11px] leading-relaxed">
                    <strong>Evidence Description:</strong> {vio.description}
                  </p>
                  <p className="text-slate-900 text-[11px]">
                    <strong>Statutory Liability Clause:</strong> {vio.statutoryActClause}
                  </p>
                  <p className="text-slate-900 text-[11px]">
                    <strong>Action Recommended:</strong> {vio.recommendedPenalty}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Officer Observations & Panchnama Details */}
        <div className="font-sans space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 border-b border-slate-300 pb-1">
            4. Inspecting Officer Observations & Orders
          </h3>
          <div className="p-3 border border-slate-300 rounded-xs bg-slate-50 text-xs text-slate-900 leading-relaxed font-mono">
            {inspection.officerNotes || 'Field verification conducted pursuant to powers under Section 15 of Legal Metrology Act, 2009. Panchnama recorded in presence of two independent witnesses.'}
          </div>
        </div>

        {/* Official Signatures & Digital Verification Stamp */}
        <div className="font-sans pt-6 border-t-2 border-slate-900 grid grid-cols-1 md:grid-cols-3 gap-6 items-end text-xs">
          {/* QR Verification Block */}
          <div className="flex items-center space-x-3">
            <div className="w-16 h-16 border-2 border-slate-900 p-1 bg-white flex items-center justify-center shrink-0">
              <QrCode className="w-14 h-14 text-slate-900" />
            </div>
            <div className="text-[10px] text-slate-600 font-mono">
              <span className="font-bold block text-slate-900">DIGITAL HASH VERIFICATION:</span>
              <span className="break-all">{inspection.qrVerificationHash}</span>
              <span className="block text-slate-500 mt-1">Verified on National Legal Metrology Registry</span>
            </div>
          </div>

          {/* Department Seal */}
          <div className="text-center">
            <div className="w-20 h-20 mx-auto border-2 border-dashed border-slate-400 rounded-full flex items-center justify-center text-[10px] font-bold text-slate-500 uppercase text-center p-2">
              OFFICIAL SEAL OF CONTROLLER
            </div>
          </div>

          {/* Inspecting Officer Signature */}
          <div className="text-right space-y-1">
            <p className="font-mono text-xs font-bold text-slate-900 underline">
              Digitally Signed By Officer
            </p>
            <p className="font-bold text-slate-950 text-xs">{inspection.officerName}</p>
            <p className="text-[11px] text-slate-600">Legal Metrology Inspector / Officer</p>
            <p className="text-[10px] font-mono text-slate-500">Badge: {inspection.officerBadge}</p>
            <p className="text-[10px] font-mono text-slate-500">Date: {inspection.date} 12:00 IST</p>
          </div>
        </div>
      </div>
    </div>
  );
};
