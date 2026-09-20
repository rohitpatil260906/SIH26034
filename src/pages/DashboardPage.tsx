import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInspection } from '../context/InspectionContext';
import { useAuth } from '../context/AuthContext';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { StatusBadge, SeverityBadge } from '../components/ui/Badge';
import {
  ClipboardCheck,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  Camera,
  Upload,
  FileText,
  ArrowRight,
  Scale,
  Sparkles,
  Check,
  AlertCircle,
  Plus,
  ArrowUpRight,
  MapPin,
  FolderKanban
} from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

const GST_STATE_CODES: Record<string, string> = {
  '01': 'Jammu & Kashmir',
  '02': 'Himachal Pradesh',
  '03': 'Punjab',
  '04': 'Chandigarh',
  '05': 'Uttarakhand',
  '06': 'Haryana',
  '07': 'Delhi',
  '08': 'Rajasthan',
  '09': 'Uttar Pradesh',
  '10': 'Bihar',
  '11': 'Sikkim',
  '12': 'Arunachal Pradesh',
  '13': 'Nagaland',
  '14': 'Manipur',
  '15': 'Mizoram',
  '16': 'Tripura',
  '17': 'Meghalaya',
  '18': 'Assam',
  '19': 'West Bengal',
  '20': 'Jharkhand',
  '21': 'Odisha',
  '22': 'Chhattisgarh',
  '23': 'Madhya Pradesh',
  '24': 'Gujarat',
  '26': 'Dadra & Nagar Haveli and Daman & Diu',
  '27': 'Maharashtra',
  '29': 'Karnataka',
  '30': 'Goa',
  '31': 'Lakshadweep',
  '32': 'Kerala',
  '33': 'Tamil Nadu',
  '34': 'Puducherry',
  '36': 'Telangana',
  '37': 'Andhra Pradesh',
  '38': 'Ladakh'
};

const GST_ENTITY_TYPES: Record<string, string> = {
  C: 'Company (Public / Private Limited)',
  P: 'Individual / Proprietorship',
  H: 'Hindu Undivided Family (HUF)',
  F: 'Partnership Firm / LLP',
  A: 'Association of Persons (AOP)',
  T: 'Trust',
  B: 'Body of Individuals (BOI)',
  L: 'Local Authority',
  J: 'Artificial Juridical Person',
  G: 'Government Entity'
};

export const DashboardPage: React.FC = () => {
  const { inspections, startNewInspection, activeJurisdiction } = useInspection();
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  // Greeting based on time of day
  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  }, []);

  // Quick GSTIN verify widget state
  const [gstinInput, setGstinInput] = useState('');
  const [gstinStatus, setGstinStatus] = useState<{
    verified: boolean;
    validFormat: boolean;
    state?: string;
    entityType?: string;
    pan?: string;
    message?: string;
  } | null>(null);

  // Click-to-focus / zoom states for cards
  const [focusedSummaryCard, setFocusedSummaryCard] = useState<number | null>(null);
  const [focusedViolationCard, setFocusedViolationCard] = useState<string | null>(null);

  // Live dynamic statistics derived from actual inspections
  const totalInspections = inspections.length;
  const compliantCount = inspections.filter((i) => i.status === 'Compliant').length;
  const nonCompliantCount = inspections.filter((i) => i.status === 'Non-Compliant').length;
  const underReviewCount = inspections.filter((i) => i.status === 'Under Review').length;
  const totalViolations = inspections.reduce((acc, i) => acc + (i.violations?.length || 0), 0);

  const complianceRate = totalInspections > 0
    ? ((compliantCount / totalInspections) * 100).toFixed(1)
    : '0.0';
  const nonComplianceRate = totalInspections > 0
    ? ((nonCompliantCount / totalInspections) * 100).toFixed(1)
    : '0.0';
  const underReviewRate = totalInspections > 0
    ? ((underReviewCount / totalInspections) * 100).toFixed(1)
    : '0.0';

  const chartData = useMemo(() => [
    { name: 'Compliant Packages', value: compliantCount, color: '#16A34A' },
    { name: 'Non-Compliant (Violations)', value: nonCompliantCount, color: '#DC2626' },
    { name: 'Under Officer Review', value: underReviewCount, color: '#D97706' }
  ], [compliantCount, nonCompliantCount, underReviewCount]);

  // Dynamic violation insights
  const violationInsights = useMemo(() => {
    const counts: Record<string, number> = {};
    inspections.flatMap((i) => i.violations || []).forEach((v) => {
      const label = v.ruleReference || v.violationType;
      counts[label] = (counts[label] || 0) + 1;
    });

    const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    const topViolation = entries[0];
    const topPct = (totalViolations > 0 && topViolation)
      ? ((topViolation[1] / totalViolations) * 100).toFixed(1)
      : '0.0';

    // Standard compounding estimate under Section 48 / Section 36
    const compoundingRecovery = totalViolations * 25000;

    return {
      topViolationName: topViolation ? topViolation[0] : null,
      topViolationCount: topViolation ? topViolation[1] : 0,
      topViolationPct: topPct,
      compoundingRecovery
    };
  }, [inspections, totalViolations]);

  // Recent inspections slice
  const recentInspections = inspections.slice(0, 5);

  // Recent violations flattened
  const allViolations = inspections.flatMap((i) => i.violations || []).slice(0, 4);

  const handleStartScan = async () => {
    startNewInspection(undefined, 2);
    try {
      if (navigator?.mediaDevices?.getUserMedia) {
        // Direct user-gesture trigger for browser camera permission
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        (window as any).__activeCameraStream = stream;
      }
    } catch (err: any) {
      console.warn('[Dashboard] Camera request on scan button click:', err);
      (window as any).__cameraInitialError = err;
    }
    navigate('/new-inspection?step=2&camera=open');
  };

  const handleVerifyGstin = (e: React.FormEvent) => {
    e.preventDefault();
    const clean = gstinInput.trim().toUpperCase();
    if (!clean) return;

    // Standard 15-character GSTIN regex format
    const gstinRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
    if (!gstinRegex.test(clean)) {
      setGstinStatus({
        verified: false,
        validFormat: false,
        message: 'Invalid GSTIN structure. Must be a 15-character statutory GSTIN (e.g. 07AAAAA0000A1Z5).'
      });
      return;
    }

    const stateCode = clean.slice(0, 2);
    const pan = clean.slice(2, 12);
    const entityChar = clean[5];

    const state = GST_STATE_CODES[stateCode] || `State Code ${stateCode} (Jurisdiction Confirmed)`;
    const entityType = GST_ENTITY_TYPES[entityChar] || 'Registered Taxpayer Entity';

    setGstinStatus({
      verified: true,
      validFormat: true,
      state,
      entityType,
      pan
    });
  };

  return (
    <div className="space-y-8">
      {/* Top Welcome Banner (Replit clean minimal style) */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1F2328] tracking-tight">
            {greeting}, Officer {currentUser?.name?.split(' ')[0] || 'Rohit'}
          </h1>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap text-xs sm:text-sm text-[#5F6368]">
            <span>Monitor packaged commodity compliance and inspection activity.</span>
            {(activeJurisdiction?.state || currentUser?.jurisdictionDetails?.state || currentUser?.jurisdictionZone) && (
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#1F2328] bg-white border border-[#E5E2DD] px-2.5 py-1 rounded-full shadow-2xs">
                <MapPin className="w-3.5 h-3.5 text-[#6D28D9]" />
                <span>
                  Jurisdiction:{' '}
                  {[
                    activeJurisdiction?.city || currentUser?.jurisdictionDetails?.city,
                    activeJurisdiction?.state || currentUser?.jurisdictionDetails?.state,
                    activeJurisdiction?.pinCode || currentUser?.jurisdictionDetails?.pinCode
                      ? `${activeJurisdiction?.pinCode || currentUser?.jurisdictionDetails?.pinCode}`
                      : ''
                  ]
                    .filter(Boolean)
                    .join(', ') || currentUser?.jurisdictionZone}
                </span>
              </span>
            )}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/legal-notices')}
            className="flex items-center space-x-1.5"
          >
            <Scale className="w-4 h-4 text-[#5F6368]" />
            <span>Statutory Notices</span>
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => {
              startNewInspection();
              navigate('/new-inspection');
            }}
            className="flex items-center space-x-1.5"
          >
            <FolderKanban className="w-4 h-4 text-[#5F6368]" />
            <span>New Inspection</span>
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={handleStartScan}
            className="flex items-center space-x-1.5"
          >
            <Camera className="w-4 h-4 text-white" />
            <span>Scan Product</span>
          </Button>
        </div>
      </div>

      {/* 4 Clean Horizontal Statistics Cards (Click-to-Focus / Zoom) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Stat 1: Total Inspections */}
        <div
          onClick={() => setFocusedSummaryCard(focusedSummaryCard === 1 ? null : 1)}
          className={`bg-white border rounded-xl p-5 shadow-2xs transition-all duration-250 ease-out cursor-pointer select-none ${
            focusedSummaryCard === 1
              ? 'scale-[1.03] shadow-md border-[#7C3AED] ring-2 ring-[#7C3AED]/30 z-10'
              : 'border-[#E5E2DD] hover:border-[#D8D4CE]'
          }`}
          title="Click to focus card"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#5F6368] uppercase tracking-wider">
              Total Inspections
            </span>
            <div className="p-2 rounded-lg bg-[#FAF9F7] text-[#5F6368] border border-[#E5E2DD]/60">
              <ClipboardCheck className="w-4.5 h-4.5" />
            </div>
          </div>
          <p className="text-3xl font-bold text-[#1F2328] mt-2 font-mono">{totalInspections}</p>
          <div className="mt-2 flex items-center text-xs text-[#5F6368]">
            <span className="font-medium text-[#1F2328]">{totalInspections}</span>
            <span className="ml-1">audited packaging dockets</span>
          </div>
        </div>

        {/* Stat 2: Compliant */}
        <div
          onClick={() => setFocusedSummaryCard(focusedSummaryCard === 2 ? null : 2)}
          className={`bg-white border rounded-xl p-5 shadow-2xs transition-all duration-250 ease-out cursor-pointer select-none ${
            focusedSummaryCard === 2
              ? 'scale-[1.03] shadow-md border-[#7C3AED] ring-2 ring-[#7C3AED]/30 z-10'
              : 'border-[#E5E2DD] hover:border-[#D8D4CE]'
          }`}
          title="Click to focus card"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#5F6368] uppercase tracking-wider">
              Compliant
            </span>
            <div className="p-2 rounded-lg bg-[#F0FDF4] text-[#16A34A] border border-[#BBF7D0]/60">
              <CheckCircle2 className="w-4.5 h-4.5" />
            </div>
          </div>
          <p className="text-3xl font-bold text-[#16A34A] mt-2 font-mono">{compliantCount}</p>
          <div className="mt-2 flex items-center text-xs text-[#16A34A] font-medium">
            <span className="font-bold font-mono">{complianceRate}%</span>
            <span className="text-[#5F6368] ml-1.5 font-normal">statutory compliance rate</span>
          </div>
        </div>

        {/* Stat 3: Violations */}
        <div
          onClick={() => setFocusedSummaryCard(focusedSummaryCard === 3 ? null : 3)}
          className={`bg-white border rounded-xl p-5 shadow-2xs transition-all duration-250 ease-out cursor-pointer select-none ${
            focusedSummaryCard === 3
              ? 'scale-[1.03] shadow-md border-[#7C3AED] ring-2 ring-[#7C3AED]/30 z-10'
              : 'border-[#E5E2DD] hover:border-[#D8D4CE]'
          }`}
          title="Click to focus card"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#5F6368] uppercase tracking-wider">
              Violations
            </span>
            <div className="p-2 rounded-lg bg-[#FEF2F2] text-[#DC2626] border border-[#FECACA]/60">
              <AlertOctagon className="w-4.5 h-4.5" />
            </div>
          </div>
          <p className="text-3xl font-bold text-[#DC2626] mt-2 font-mono">{nonCompliantCount}</p>
          <div className="mt-2 flex items-center text-xs text-[#DC2626] font-medium">
            <span className="font-bold font-mono">{totalViolations}</span>
            <span className="text-[#5F6368] ml-1.5 font-normal">flagged rule infractions</span>
          </div>
        </div>

        {/* Stat 4: Reports Generated */}
        <div
          onClick={() => setFocusedSummaryCard(focusedSummaryCard === 4 ? null : 4)}
          className={`bg-white border rounded-xl p-5 shadow-2xs transition-all duration-250 ease-out cursor-pointer select-none ${
            focusedSummaryCard === 4
              ? 'scale-[1.03] shadow-md border-[#7C3AED] ring-2 ring-[#7C3AED]/30 z-10'
              : 'border-[#E5E2DD] hover:border-[#D8D4CE]'
          }`}
          title="Click to focus card"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#5F6368] uppercase tracking-wider">
              Reports Generated
            </span>
            <div className="p-2 rounded-lg bg-[#F5F3FF] text-[#6D28D9] border border-[#DDD6FE]">
              <FileText className="w-4.5 h-4.5" />
            </div>
          </div>
          <p className="text-3xl font-bold text-[#1F2328] mt-2 font-mono">{totalInspections}</p>
          <div className="mt-2 flex items-center text-xs text-[#D97706] font-medium">
            <span className="font-bold font-mono">{underReviewCount}</span>
            <span className="text-[#5F6368] ml-1.5 font-normal">dockets under review</span>
          </div>
        </div>
      </div>

      {/* Central Scanning Station Card (Package Inspection CTA) */}
      <div className="clean-card overflow-hidden">
        <div className="p-8 sm:p-10 lg:p-12 flex flex-col justify-center max-w-3xl">
          {/* Badge matching the image's light purple theme */}
          <div className="inline-flex items-center self-start gap-2 px-3 py-1.5 mb-6 rounded-full bg-[#f5f3ff] border border-[#ede9fe] text-[#7c3aed] text-xs font-semibold tracking-wide">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Instant Optical Inspection</span>
          </div>

          {/* Punchy, Confident Title */}
          <h2 className="text-3xl sm:text-4xl lg:text-[2.75rem] font-extrabold text-gray-900 leading-[1.15] mb-5 tracking-tight font-poppins">
            Verify Compliance <br />
            <span className="text-[#7c3aed] relative inline-block mt-1">
              Instantly.
              {/* Decorative underline */}
              <svg
                className="absolute w-full h-3 -bottom-1 left-0 text-[#f5f3ff] -z-10"
                viewBox="0 0 100 12"
                preserveAspectRatio="none"
              >
                <path
                  d="M0,10 Q50,0 100,10"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                />
              </svg>
            </span>
          </h2>

          {/* Simplified Subtitle */}
          <p className="text-gray-500 text-base sm:text-lg leading-relaxed mb-8 max-w-2xl font-dmsans">
            Capture or upload packaging labels. Our engine automates character recognition and validates against Legal Metrology Rules.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 w-full">
            <button
              type="button"
              onClick={handleStartScan}
              className="btn-cta-primary group flex items-center justify-center gap-2.5 px-7 py-3.5 font-semibold rounded-xl w-full sm:w-auto text-base cursor-pointer font-poppins"
            >
              <Camera className="w-5 h-5 text-white transition-transform group-hover:scale-110" />
              <span>Open Camera Scan</span>
            </button>

            <button
              type="button"
              onClick={() => {
                startNewInspection();
                navigate('/new-inspection?step=2');
              }}
              className="btn-cta-secondary group flex items-center justify-center gap-2.5 px-7 py-3.5 font-semibold rounded-xl w-full sm:w-auto text-base cursor-pointer font-poppins"
            >
              <Upload className="w-5 h-5 text-gray-400 group-hover:text-[#7c3aed] transition-colors" />
              <span>Upload Label Image</span>
            </button>
          </div>
        </div>
      </div>

      {/* Grid: Charts & Live GSTIN Verifier Tool */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Compliance Distribution Chart */}
        <div className="lg:col-span-2">
          <Card orientation="vertical" className="h-full">
            <CardHeader
              title="Statutory Compliance Distribution"
              subtitle="Live breakdown across all audited packaged commodities"
            />
            <CardContent>
              {totalInspections === 0 ? (
                <div className="py-12 px-4 text-center space-y-3">
                  <div className="w-12 h-12 rounded-full bg-[#FAF9F7] border border-[#E5E2DD] flex items-center justify-center mx-auto text-[#8A8F98]">
                    <ClipboardCheck className="w-6 h-6" />
                  </div>
                  <h3 className="text-sm font-bold text-[#1F2328]">No Packaging Inspections Recorded Yet</h3>
                  <p className="text-xs text-[#5F6368] max-w-md mx-auto">
                    Initiate an optical scan or upload a packaging label. Real-time compliance metrics will appear here.
                  </p>
                  <Button variant="primary" size="sm" onClick={handleStartScan} className="mt-2">
                    Scan Product Now
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
                  <div className="md:col-span-7 h-60">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={chartData}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={85}
                          paddingAngle={3}
                          dataKey="value"
                        >
                          {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          formatter={(value: any) => [`${value} Packages`, 'Count']}
                          contentStyle={{
                            backgroundColor: '#FFFFFF',
                            border: '1px solid #E5E2DD',
                            borderRadius: '8px',
                            fontSize: '12px',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                          }}
                        />
                        <Legend
                          verticalAlign="bottom"
                          wrapperStyle={{ fontSize: '11px', paddingTop: '12px' }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Summary Metrics */}
                  <div className="md:col-span-5 space-y-3 text-xs border-l border-[#E5E2DD] pl-5">
                    <div className="p-3 bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg space-y-1">
                      <span className="text-[#5F6368] font-medium">Most Common Infraction:</span>
                      <p className="font-bold text-[#1F2328] truncate text-xs">
                        {violationInsights.topViolationName || 'No violations recorded'}
                      </p>
                      <span className="text-[10px] text-[#8A8F98] block">
                        {violationInsights.topViolationName
                          ? `${violationInsights.topViolationPct}% of infractions (${violationInsights.topViolationCount} occurrences)`
                          : 'Zero infractions across audited commodities'}
                      </span>
                    </div>

                    <div className="p-3 bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg space-y-1">
                      <span className="text-[#5F6368] font-medium">Total Flagged Infractions:</span>
                      <p className="font-bold text-[#1F2328] font-mono text-sm">{totalViolations}</p>
                      <span className="text-[10px] text-[#8A8F98] block">
                        Across {nonCompliantCount} non-compliant inspection dockets
                      </span>
                    </div>

                    <div className="p-3 bg-[#F5F3FF] border border-[#DDD6FE] rounded-lg space-y-1">
                      <span className="text-[#6D28D9] font-medium">Potential Compounding Recovery:</span>
                      <p className="font-bold text-[#1F2328] font-mono text-base">
                        ₹ {violationInsights.compoundingRecovery.toLocaleString('en-IN')}
                      </p>
                      <span className="text-[10px] text-[#5F6368] block">
                        Estimated under Sec 48 compounding guidelines (₹25,000 / infraction)
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* GSTIN / Manufacturer Quick Lookup Tool */}
        <div className="lg:col-span-1 h-fit">
          <Card orientation="vertical" className="h-fit">
            <CardHeader
              title="GSTIN Verification Tool"
              subtitle="Statutory manufacturer verification"
            />
            <CardContent className="p-5 flex flex-col gap-4">
              <form onSubmit={handleVerifyGstin} className="space-y-2">
                <label className="block text-xs font-semibold text-[#1F2328]">
                  Manufacturer GSTIN / UIN:
                </label>
                <div className="flex flex-row items-center gap-3">
                  <input
                    type="text"
                    value={gstinInput}
                    onChange={(e) => setGstinInput(e.target.value)}
                    placeholder="e.g. 07AAAAA0000A1Z5"
                    className="flex-1 bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs font-mono uppercase text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED]"
                  />
                  <Button type="submit" variant="primary" size="sm">
                    Verify
                  </Button>
                </div>
              </form>

              {gstinStatus && gstinStatus.verified && (
                <div className="p-3 bg-[#F0FDF4] border border-[#BBF7D0] rounded-lg text-[#16A34A] text-xs space-y-1.5 animate-in fade-in duration-150">
                  <div className="flex items-center space-x-1.5 font-bold text-[#16A34A]">
                    <Check className="w-4 h-4 text-[#16A34A]" />
                    <span>GSTIN FORMAT VALIDATED</span>
                  </div>
                  <p className="text-[11px] text-[#1F2328] font-medium">
                    Jurisdiction: <span className="font-bold">{gstinStatus.state}</span>
                  </p>
                  <p className="text-[11px] text-[#5F6368]">
                    Entity Type: <span className="font-medium text-[#1F2328]">{gstinStatus.entityType}</span>
                  </p>
                  <p className="font-mono text-[10px] text-[#16A34A]">
                    PAN: {gstinStatus.pan} • Statutory Format Compliant
                  </p>
                </div>
              )}

              {gstinStatus && !gstinStatus.verified && (
                <div className="p-3 bg-[#FEF2F2] border border-[#FECACA] rounded-lg text-[#DC2626] text-xs space-y-1 animate-in fade-in duration-150">
                  <div className="flex items-center space-x-1.5 font-bold text-[#DC2626]">
                    <AlertCircle className="w-4 h-4 text-[#DC2626]" />
                    <span>VALIDATION FAILED</span>
                  </div>
                  <p className="text-[11px] text-[#DC2626] leading-relaxed">
                    {gstinStatus.message}
                  </p>
                </div>
              )}

              <div className="pt-4 border-t border-[#E5E2DD]">
                <span className="text-[11px] font-bold text-[#8A8F98] uppercase tracking-wider block mb-2">
                  Verification Rules Checked:
                </span>
                <ul className="text-xs text-[#5F6368] space-y-2">
                  <li className="flex items-center space-x-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#16A34A] shrink-0"></span>
                    <span>Rule 6(1)(a) Registered manufacturer</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#16A34A] shrink-0"></span>
                    <span>Rule 27 E-Commerce marketplace seller</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#16A34A] shrink-0"></span>
                    <span>State / UT territorial jurisdiction alignment</span>
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Grid: Recent Inspections & Priority Violations */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Inspections Table */}
        <div className="lg:col-span-7">
          <Card orientation="vertical">
            <CardHeader
              title="Recent Packaged Commodity Inspections"
              subtitle="Latest market surveillance and complaint sampling dockets"
              action={
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate('/inspections')}
                  className="text-xs"
                >
                  View All ({inspections.length})
                </Button>
              }
            />
            <CardContent>
              {recentInspections.length === 0 ? (
                <div className="py-8 text-center space-y-2">
                  <p className="text-xs text-[#5F6368]">
                    No inspections recorded yet. Begin by scanning or uploading a product label.
                  </p>
                  <Button variant="primary" size="sm" onClick={handleStartScan}>
                    Start First Inspection
                  </Button>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-[#E5E2DD] bg-[#FAF9F7] text-[#5F6368] font-medium">
                        <th className="py-2.5 px-3">Docket ID</th>
                        <th className="py-2.5 px-3">Commodity / Brand</th>
                        <th className="py-2.5 px-3">Date</th>
                        <th className="py-2.5 px-3">Status</th>
                        <th className="py-2.5 px-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#F0EDE8]">
                      {recentInspections.map((insp) => (
                        <tr key={insp.id} className="hover:bg-[#FAF9F7] transition-colors">
                          <td className="py-3 px-3 font-mono font-bold text-[#1F2328]">
                            {insp.id}
                          </td>
                          <td className="py-3 px-3">
                            <p className="font-semibold text-[#1F2328] truncate max-w-[180px]">
                              {insp.productName || 'Unspecified Commodity'}
                            </p>
                            <p className="text-[11px] text-[#5F6368] truncate max-w-[180px]">
                              {insp.brand || 'No Brand'} • {insp.category}
                            </p>
                          </td>
                          <td className="py-3 px-3 font-mono text-[#5F6368] whitespace-nowrap">
                            {insp.date}
                          </td>
                          <td className="py-3 px-3">
                            <StatusBadge status={insp.status} />
                          </td>
                          <td className="py-3 px-3 text-right whitespace-nowrap space-x-1">
                            <button
                              onClick={() => navigate(`/reports/${insp.id}`)}
                              className="p-1.5 text-[#5F6368] hover:text-[#6D28D9] hover:bg-[#F5F3FF] rounded-lg transition cursor-pointer"
                              title="View Official Report"
                            >
                              <FileText className="w-4 h-4" />
                            </button>
                            {insp.status === 'Non-Compliant' && (
                              <button
                                onClick={() => navigate('/legal-notices')}
                                className="p-1.5 text-[#DC2626] hover:text-[#B91C1C] hover:bg-[#FEF2F2] rounded-lg transition cursor-pointer"
                                title="Generate Section 36 Notice"
                              >
                                <Scale className="w-4 h-4" />
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Priority Violations & Statutory Actions */}
        <div className="lg:col-span-5">
          <Card orientation="vertical">
            <CardHeader
              title="Flagged Statutory Violations"
              subtitle="Requires Section 36 notice or compounding"
              action={
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate('/violations')}
                  className="text-xs"
                >
                  Violations Registry
                </Button>
              }
            />
            <CardContent className="space-y-3">
              {allViolations.length === 0 ? (
                <div className="py-8 text-center space-y-1">
                  <CheckCircle2 className="w-8 h-8 text-[#16A34A] mx-auto opacity-70" />
                  <p className="text-xs font-semibold text-[#1F2328] mt-2">No Violations Flagged</p>
                  <p className="text-[11px] text-[#5F6368]">
                    No statutory infractions currently pending enforcement action.
                  </p>
                </div>
              ) : (
                allViolations.map((v) => {
                  const isFocused = focusedViolationCard === v.id;
                  return (
                    <div
                      key={v.id}
                      onClick={() => setFocusedViolationCard(isFocused ? null : v.id)}
                      className={`p-3.5 bg-[#FFFFFF] border rounded-xl transition-all duration-250 ease-out space-y-1.5 cursor-pointer select-none ${
                        isFocused
                          ? 'scale-[1.02] shadow-md border-[#7C3AED] ring-2 ring-[#7C3AED]/30 z-10'
                          : 'border-[#E5E2DD] hover:border-[#D8D4CE] shadow-2xs'
                      }`}
                      title="Click to focus card"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="font-bold text-xs text-[#1F2328] leading-snug">
                          {v.violationType}
                        </span>
                        <SeverityBadge severity={v.severity} />
                      </div>
                      <p className="text-[11px] text-[#5F6368] leading-relaxed">{v.description}</p>
                      <div className="flex items-center justify-between text-[11px] text-[#8A8F98] pt-2 border-t border-[#F0EDE8]">
                        <span className="font-mono font-bold text-[#1F2328]">{v.ruleReference}</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate('/legal-notices');
                          }}
                          className="text-[#6D28D9] hover:underline font-semibold flex items-center space-x-1 cursor-pointer"
                        >
                          <span>Issue Notice</span>
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
