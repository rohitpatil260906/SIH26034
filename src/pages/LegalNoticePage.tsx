import React, { useState } from 'react';
import { useInspection } from '../context/InspectionContext';
import { useAuth } from '../context/AuthContext';
import {
  FileText,
  Printer,
  Download,
  Send,
  CheckCircle2,
  AlertTriangle,
  Building2,
  Calendar,
  Scale,
  Shield,
  QrCode,
  ArrowRight,
  Sparkles,
  ExternalLink,
  ChevronDown
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Badge, StatusBadge } from '../components/ui/Badge';
import { Card } from '../components/ui/Card';

export const LegalNoticePage: React.FC = () => {
  const { inspections, addAuditLog } = useInspection();
  const { currentUser } = useAuth();

  // Find non-compliant inspections
  const nonCompliantList = inspections.filter(
    (i) => i.status === 'Non-Compliant' || (i.violations && i.violations.length > 0)
  );

  const [selectedInspectionId, setSelectedInspectionId] = useState<string>(
    nonCompliantList[0]?.id || inspections[0]?.id || ''
  );

  const activeInspection = inspections.find((i) => i.id === selectedInspectionId) || inspections[0];

  // Notice Form State
  const [noticeType, setNoticeType] = useState<'SHOW_CAUSE' | 'COMPOUNDING' | 'PROSECUTION'>('SHOW_CAUSE');
  const [offenceCount, setOffenceCount] = useState<'FIRST' | 'SECOND' | 'SUBSEQUENT'>('FIRST');
  const [hearingDays, setHearingDays] = useState<number>(15);
  const [isDispatched, setIsDispatched] = useState<boolean>(false);
  const [dispatchDate, setDispatchDate] = useState<string>('');
  const [dispatchTrackingNo, setDispatchTrackingNo] = useState<string>('');

  const penaltyAmount =
    offenceCount === 'FIRST' ? '₹ 25,000' : offenceCount === 'SECOND' ? '₹ 50,000' : '₹ 1,00,000 (Non-Compoundable / Court Prosecution)';

  const noticeNumber = `LM/HQ/ENF/NOT/2026/${activeInspection?.id.split('-').pop() || '0842'}`;
  const noticeDate = new Date().toISOString().split('T')[0];

  // Hearing calculation
  const hearingDeadline = new Date();
  hearingDeadline.setDate(hearingDeadline.getDate() + hearingDays);
  const hearingDeadlineStr = hearingDeadline.toISOString().split('T')[0];

  const handlePrint = () => {
    window.print();
  };

  const handleDispatchNotice = () => {
    const tracking = `ED${Math.floor(100000000 + Math.random() * 900000000)}IN`;
    const now = new Date().toISOString().replace('T', ' ').substring(0, 16);
    setDispatchTrackingNo(tracking);
    setDispatchDate(now);
    setIsDispatched(true);

    addAuditLog(
      'LEGAL_NOTICE_DISPATCHED',
      'Enforcement & Legal Notices',
      noticeNumber,
      'Success',
      `Statutory ${noticeType.replace('_', ' ')} notice ${noticeNumber} dispatched to ${activeInspection.manufacturer}. Speed Post: ${tracking}`
    );
  };

  if (!activeInspection) {
    return (
      <div className="space-y-6">
        <div className="border-b border-slate-200 pb-4">
          <h1 className="text-xl md:text-2xl font-bold text-slate-900">
            Statutory Legal Notice Generator
          </h1>
          <p className="text-xs md:text-sm text-slate-600 mt-0.5">
            Issue formal Show Cause and Compounding Demand notices under Legal Metrology Act, 2009 and Packaged Commodities Rules, 2011.
          </p>
        </div>
        <Card className="p-12 text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400">
            <Scale className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-slate-800">No Non-Compliant Dockets Found</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Statutory notices under Section 36 are issued when an inspection reveals infractions. No non-conforming dockets have been recorded yet.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              STAGE 4 COMPLIANCE BRANCH
            </span>
            <span className="text-slate-300">•</span>
            <span className="text-xs text-red-700 font-semibold flex items-center">
              <Scale className="w-3.5 h-3.5 mr-1" />
              Section 36 / 48 Enforcement
            </span>
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900 mt-1">
            Statutory Legal Notice Generator
          </h1>
          <p className="text-xs md:text-sm text-slate-600 mt-0.5">
            Issue formal Show Cause and Compounding Demand notices under Legal Metrology Act, 2009 and Packaged Commodities Rules, 2011.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={handlePrint} className="flex items-center space-x-1.5">
            <Printer className="w-4 h-4 text-slate-600" />
            <span>Print Official Notice</span>
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleDispatchNotice}
            disabled={isDispatched}
            className="flex items-center space-x-1.5 bg-[#0f2942] hover:bg-[#163a5f]"
          >
            <Send className="w-4 h-4 text-amber-300" />
            <span>{isDispatched ? 'Notice Dispatched' : 'Dispatch via Speed Post & Email'}</span>
          </Button>
        </div>
      </div>

      {/* Dispatched Notification Banner */}
      {isDispatched && (
        <div className="bg-emerald-50 border border-emerald-300 text-emerald-900 rounded-lg p-3.5 flex items-start justify-between">
          <div className="flex items-start space-x-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold">Notice Successfully Dispatched to Manufacturer</p>
              <p className="text-xs text-emerald-800 mt-0.5">
                Notice Ref: <span className="font-mono font-bold">{noticeNumber}</span> • Speed Post Consignment Tracking No:{' '}
                <span className="font-mono font-bold">{dispatchTrackingNo}</span>
              </p>
              <p className="text-[11px] text-emerald-700 mt-1">
                Dispatched on {dispatchDate} via Postal Ingestion Node. Copy transmitted to registered corporate email.
              </p>
            </div>
          </div>
          <span className="text-[11px] bg-emerald-200 text-emerald-900 px-2 py-0.5 rounded font-mono font-semibold">
            DISPATCHED
          </span>
        </div>
      )}

      {/* Main Grid: Left Controls & Right Formal Document Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side: Parameters Form (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          <Card orientation="vertical">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center">
              <Building2 className="w-4 h-4 text-slate-500 mr-1.5" />
              1. Select Inspection Docket
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-600 font-medium mb-1">
                  Non-Compliant Case File:
                </label>
                <select
                  value={selectedInspectionId}
                  onChange={(e) => {
                    setSelectedInspectionId(e.target.value);
                    setIsDispatched(false);
                  }}
                  className="w-full bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 text-xs text-slate-900 font-medium focus:outline-none focus:ring-1 focus:ring-[#0f2942]"
                >
                  {inspections.map((insp) => (
                    <option key={insp.id} value={insp.id}>
                      {insp.id} — {insp.productName} ({insp.status})
                    </option>
                  ))}
                </select>
              </div>

              <div className="p-2.5 bg-slate-50 border border-slate-200 rounded text-[11px] space-y-1">
                <p>
                  <span className="text-slate-500">Manufacturer:</span>{' '}
                  <span className="font-semibold text-slate-900">{activeInspection.manufacturer}</span>
                </p>
                <p>
                  <span className="text-slate-500">Brand / Product:</span>{' '}
                  <span className="font-semibold text-slate-900">{activeInspection.productName}</span>
                </p>
                <p>
                  <span className="text-slate-500">Batch No:</span>{' '}
                  <span className="font-mono text-slate-800">{activeInspection.batchNumber}</span>
                </p>
                <p>
                  <span className="text-slate-500">Seizure / Sampling Location:</span>{' '}
                  <span className="text-slate-700">{activeInspection.location}</span>
                </p>
              </div>
            </div>
          </Card>

          {/* Statutory Options */}
          <Card orientation="vertical">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center">
              <Scale className="w-4 h-4 text-slate-500 mr-1.5" />
              2. Notice Classification & Penalty
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-600 font-medium mb-1">Statutory Notice Category:</label>
                <div className="space-y-1.5">
                  <label className="flex items-center space-x-2 p-2 border rounded-md cursor-pointer hover:bg-slate-50 transition border-slate-200">
                    <input
                      type="radio"
                      name="noticeType"
                      checked={noticeType === 'SHOW_CAUSE'}
                      onChange={() => setNoticeType('SHOW_CAUSE')}
                      className="text-[#0f2942] focus:ring-[#0f2942]"
                    />
                    <div>
                      <span className="font-semibold text-slate-900 block">Show Cause Notice</span>
                      <span className="text-[10px] text-slate-500">Rule 32 / Sec 36(1) — Mandatory 15 days reply</span>
                    </div>
                  </label>

                  <label className="flex items-center space-x-2 p-2 border rounded-md cursor-pointer hover:bg-slate-50 transition border-slate-200">
                    <input
                      type="radio"
                      name="noticeType"
                      checked={noticeType === 'COMPOUNDING'}
                      onChange={() => setNoticeType('COMPOUNDING')}
                      className="text-[#0f2942] focus:ring-[#0f2942]"
                    />
                    <div>
                      <span className="font-semibold text-slate-900 block">Compounding Demand Challan</span>
                      <span className="text-[10px] text-slate-500">Section 48 — Pre-litigation settlement fee</span>
                    </div>
                  </label>

                  <label className="flex items-center space-x-2 p-2 border rounded-md cursor-pointer hover:bg-slate-50 transition border-slate-200">
                    <input
                      type="radio"
                      name="noticeType"
                      checked={noticeType === 'PROSECUTION'}
                      onChange={() => setNoticeType('PROSECUTION')}
                      className="text-[#0f2942] focus:ring-[#0f2942]"
                    />
                    <div>
                      <span className="font-semibold text-slate-900 block">Prosecution Sanction</span>
                      <span className="text-[10px] text-slate-500">Filing complaint in Court of Metropolitan Magistrate</span>
                    </div>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Offence Severity / Prior History:</label>
                <select
                  value={offenceCount}
                  onChange={(e) => setOffenceCount(e.target.value as any)}
                  className="w-full bg-slate-50 border border-slate-300 rounded px-2.5 py-1.5 text-xs text-slate-900 focus:ring-1 focus:ring-[#0f2942]"
                >
                  <option value="FIRST">First Offence (Sec 36(1) — ₹25,000)</option>
                  <option value="SECOND">Second Offence (Sec 36(1) — ₹50,000)</option>
                  <option value="SUBSEQUENT">Subsequent Offence (Sec 36(1) — ₹1,00,000 / Jail)</option>
                </select>
              </div>

              <div className="p-3 bg-amber-50 border border-amber-200 rounded-md text-amber-900 space-y-1">
                <span className="text-[10px] uppercase font-bold tracking-wider text-amber-800">
                  Applicable Statutory Fee
                </span>
                <p className="text-base font-extrabold text-amber-950 font-mono">{penaltyAmount}</p>
                <p className="text-[10px] text-amber-800 leading-tight">
                  Levied under Section 48 compounding formula or Section 36 penalty provisions.
                </p>
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Reply Window (Days):</label>
                <div className="flex space-x-2">
                  {[7, 15, 30].map((days) => (
                    <button
                      key={days}
                      type="button"
                      onClick={() => setHearingDays(days)}
                      className={`flex-1 py-1 rounded text-xs font-semibold border transition ${
                        hearingDays === days
                          ? 'bg-[#0f2942] text-white border-[#0f2942]'
                          : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
                      }`}
                    >
                      {days} Days
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </Card>

          {/* Officer Details */}
          <Card orientation="vertical">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center">
              <Shield className="w-4 h-4 text-slate-500 mr-1.5" />
              Issuing Authority
            </h3>
            <div className="text-[11px] text-slate-600 space-y-1">
              <p>
                <span className="font-semibold text-slate-900">{currentUser?.name || activeInspection.officerName}</span>
              </p>
              <p>Inspector of Legal Metrology / Enforcement Authority</p>
              <p className="font-mono text-[10px] text-slate-500">
                Badge: {currentUser?.badgeNumber || activeInspection.officerBadge}
              </p>
              <p>{activeInspection.jurisdiction}</p>
            </div>
          </Card>
        </div>

        {/* Right Side: Formal Government Legal Notice Document (8 cols) */}
        <div className="lg:col-span-8">
          <div className="bg-white border-2 border-slate-300 shadow-md rounded-lg p-6 md:p-8 text-slate-900 font-serif leading-relaxed print:border-none print:shadow-none print:p-0">
            {/* National Emblem & Top Header */}
            <div className="text-center pb-4 border-b-2 border-slate-900 space-y-1">
              {/* Emblem graphic representation */}
              <div className="w-12 h-12 mx-auto rounded bg-slate-900 text-amber-300 flex items-center justify-center font-bold text-lg mb-2 shadow-xs">
                <Shield className="w-7 h-7 text-amber-300" />
              </div>
              <p className="text-[11px] uppercase tracking-widest font-sans font-bold text-slate-700">
                GOVERNMENT OF INDIA
              </p>
              <p className="text-xs font-sans font-bold text-slate-800">
                MINISTRY OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION
              </p>
              <p className="text-xs font-sans text-slate-600">
                DEPARTMENT OF CONSUMER AFFAIRS • LEGAL METROLOGY DIVISION
              </p>
              <p className="text-[11px] font-sans text-slate-500">
                OFFICE OF THE CONTROLLER OF LEGAL METROLOGY • {activeInspection.jurisdiction.toUpperCase()}
              </p>
            </div>

            {/* Document Reference Bar */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between text-xs font-sans font-medium py-3 border-b border-slate-200 gap-2">
              <div>
                <span className="text-slate-500">NOTICE REF NO: </span>
                <span className="font-mono font-bold text-slate-900">{noticeNumber}</span>
              </div>
              <div>
                <span className="text-slate-500">DATE OF ISSUE: </span>
                <span className="font-mono font-bold text-slate-900">{noticeDate}</span>
              </div>
            </div>

            {/* Statutory Title */}
            <div className="text-center my-5">
              <h2 className="text-base font-bold tracking-wide uppercase underline decoration-2 underline-offset-4 font-sans text-slate-950">
                {noticeType === 'SHOW_CAUSE' && 'STATUTORY SHOW CAUSE NOTICE'}
                {noticeType === 'COMPOUNDING' && 'NOTICE OF DEMAND FOR COMPOUNDING OF OFFENCE'}
                {noticeType === 'PROSECUTION' && 'FINAL PROSECUTION SANCTION & COURT SUMMONS'}
              </h2>
              <p className="text-[11px] font-sans text-slate-600 mt-1 italic">
                Issued under Section 36 and Section 48 of the Legal Metrology Act, 2009 read with Rule 32 of the Legal Metrology (Packaged Commodities) Rules, 2011.
              </p>
            </div>

            {/* Addressee */}
            <div className="space-y-1 text-xs font-sans text-slate-800 mb-5">
              <p className="font-bold">TO,</p>
              <p className="font-bold uppercase text-slate-950">{activeInspection.manufacturer}</p>
              <p className="text-slate-600">
                Registered Office / Manufacturing Facility Premises
              </p>
              <p className="text-slate-600">
                Registration / GSTIN:{' '}
                <span className="font-mono font-semibold text-slate-900">08AABCH1234F1Z8 (Verified)</span>
              </p>
            </div>

            {/* Subject & Reference */}
            <div className="bg-slate-50 border-l-4 border-[#0f2942] p-3 text-xs font-sans mb-5 space-y-1">
              <p>
                <span className="font-bold text-slate-900">SUB: </span>
                Contravention of Legal Metrology (Packaged Commodities) Rules, 2011 detected in commodity:{' '}
                <span className="font-bold">{activeInspection.productName}</span> (Batch No: {activeInspection.batchNumber}).
              </p>
              <p>
                <span className="font-bold text-slate-900">REF: </span>
                Market Surveillance Inspection Docket No.{' '}
                <span className="font-mono font-bold">{activeInspection.id}</span> dated {activeInspection.date}.
              </p>
            </div>

            {/* Body of the Notice */}
            <div className="space-y-3 text-xs leading-relaxed text-slate-800">
              <p>
                WHEREAS, an authorized inspection and sampling of packaged commodities was conducted by the undersigned Inspector of Legal Metrology on{' '}
                <span className="font-semibold">{activeInspection.date}</span> at premises located at{' '}
                <span className="font-semibold">{activeInspection.location}</span> under the powers conferred by Section 15 of the Legal Metrology Act, 2009.
              </p>

              <p>
                WHEREAS, upon optical inspection, computer vision scrutiny, and deterministic legal rule verification through the automated enforcement system (LM-COMPASS), the commodity manufactured/packed by you has been found in direct contravention of the statutory requirements as detailed hereunder:
              </p>

              {/* Table of Violations */}
              <div className="overflow-x-auto my-3">
                <table className="w-full text-left border-collapse border border-slate-300 text-[11px] font-sans">
                  <thead>
                    <tr className="bg-slate-100 text-slate-900 border-b border-slate-300">
                      <th className="p-2 border-r border-slate-300 font-bold">S.No</th>
                      <th className="p-2 border-r border-slate-300 font-bold">Nature of Violation</th>
                      <th className="p-2 border-r border-slate-300 font-bold">Statutory Rule Violated</th>
                      <th className="p-2 border-r border-slate-300 font-bold">Observed Label Defect</th>
                      <th className="p-2 font-bold">Evidence Ref</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activeInspection.violations && activeInspection.violations.length > 0 ? (
                      activeInspection.violations.map((v, idx) => (
                        <tr key={v.id} className="border-b border-slate-200">
                          <td className="p-2 border-r border-slate-200 font-mono text-center">{idx + 1}</td>
                          <td className="p-2 border-r border-slate-200 font-semibold">{v.violationType}</td>
                          <td className="p-2 border-r border-slate-200 font-mono font-bold text-slate-900">{v.ruleReference}</td>
                          <td className="p-2 border-r border-slate-200 text-slate-700">{v.description}</td>
                          <td className="p-2 font-mono text-[10px] text-slate-500">{v.evidenceImage || 'IMG-PDP-01'}</td>
                        </tr>
                      ))
                    ) : (
                      <tr className="border-b border-slate-200">
                        <td className="p-2 border-r border-slate-200 font-mono text-center">1</td>
                        <td className="p-2 border-r border-slate-200 font-semibold">Omission of Mandatory Tax Declaration on MRP</td>
                        <td className="p-2 border-r border-slate-200 font-mono font-bold text-slate-900">Rule 6(1)(e) read with Sec 36(1)</td>
                        <td className="p-2 border-r border-slate-200 text-slate-700">MRP ₹ 165.00 printed without "inclusive of all taxes".</td>
                        <td className="p-2 font-mono text-[10px] text-slate-500">IMG-PDP-01</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <p>
                NOW, THEREFORE, you are hereby called upon to <span className="font-bold underline">SHOW CAUSE</span> in writing within{' '}
                <span className="font-bold text-slate-950">{hearingDays} days</span> (on or before{' '}
                <span className="font-bold font-mono text-slate-950">{hearingDeadlineStr}</span>) as to why legal proceedings under{' '}
                <span className="font-bold">Section 36(1) of the Legal Metrology Act, 2009</span> should not be instituted against your company and its designated Directors.
              </p>

              {noticeType === 'COMPOUNDING' && (
                <div className="bg-amber-50 border border-amber-300 p-3 rounded font-sans text-xs text-amber-950 space-y-1">
                  <p className="font-bold uppercase tracking-wide text-amber-900">
                    Option for Compounding under Section 48
                  </p>
                  <p>
                    You are afforded an opportunity to compound the said offence by remitting a sum of{' '}
                    <span className="font-bold font-mono text-amber-950">{penaltyAmount}</span> into the designated Government Treasury Head through the electronic portal within 15 days, failing which an uncompounded criminal complaint shall be lodged before the competent jurisdictional Magistrate.
                  </p>
                </div>
              )}

              <p>
                Please note that if no reply is received within the stipulated period, it shall be presumed that you have no explanation to offer and necessary prosecution shall be launched ex-parte under the provisions of the law.
              </p>
            </div>

            {/* Signature & QR Footer */}
            <div className="mt-8 pt-6 border-t-2 border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-4 font-sans">
              <div className="flex items-center space-x-3">
                <div className="w-16 h-16 bg-slate-100 border border-slate-300 rounded flex items-center justify-center">
                  <QrCode className="w-12 h-12 text-slate-800" />
                </div>
                <div className="text-[10px] text-slate-500 space-y-0.5">
                  <p className="font-bold text-slate-800 uppercase">DIGITALLY VERIFIED NOTICE</p>
                  <p>Hash: 7f83b1657ff1fc53b92dc18148a1d65d</p>
                  <p>Verify at: https://legalmetrology.gov.in/verify</p>
                  <p className="font-mono text-emerald-700">Digital Signature: VALID (NIC CA 2026)</p>
                </div>
              </div>

              <div className="text-right text-xs space-y-1">
                <p className="font-serif italic text-slate-700 mb-4">[Digitally Signed by Enforcement Officer]</p>
                <p className="font-bold text-slate-950 uppercase">
                  ({currentUser?.name || activeInspection.officerName})
                </p>
                <p className="text-[11px] text-slate-600">
                  Inspector of Legal Metrology / Assistant Controller
                </p>
                <p className="text-[10px] font-mono text-slate-500">
                  Badge: {currentUser?.badgeNumber || activeInspection.officerBadge}
                </p>
                <p className="text-[10px] text-slate-500">{activeInspection.jurisdiction}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
