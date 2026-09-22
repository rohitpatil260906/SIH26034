import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInspection } from '../context/InspectionContext';
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
  Sparkles
} from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

export const DashboardPage: React.FC = () => {
  const { inspections, startNewInspection } = useInspection();
  const navigate = useNavigate();

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
    { name: 'Compliant Packages', value: compliantCount, color: '#15803d' },
    { name: 'Non-Compliant (Violations)', value: nonCompliantCount, color: '#b91c1c' },
    { name: 'Under Officer Review', value: underReviewCount, color: '#d97706' }
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

    return {
      topViolationName: topViolation ? topViolation[0] : null,
      topViolationCount: topViolation ? topViolation[1] : 0,
      topViolationPct: topPct
    };
  }, [inspections, totalViolations]);

  // Recent inspections slice
  const recentInspections = inspections.slice(0, 5);

  // Recent violations flattened
  const allViolations = inspections.flatMap((i) => i.violations || []).slice(0, 4);

  const handleStartScan = () => {
    startNewInspection(undefined, 2);
    navigate('/new-inspection?step=2&camera=open');
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Executive Overview */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-amber-900 bg-amber-100 border border-amber-300 px-2 py-0.5 rounded">
              LM-COMPASS • VIDHICHECK
            </span>
            <span className="text-slate-300">•</span>
            <span className="text-xs text-slate-500 font-medium">National Enforcement Portal</span>
          </div>
          <h1 className="text-xl md:text-2xl font-black text-slate-900 tracking-tight mt-1">
            Legal Metrology Enforcement Command Station
          </h1>
          <p className="text-xs md:text-sm text-slate-600 mt-0.5">
            Real-time compliance monitoring, optical label scanning, and statutory enforcement under Legal Metrology Rules, 2011.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/legal-notices')}
            className="flex items-center space-x-1.5"
          >
            <Scale className="w-4 h-4 text-indigo-700" />
            <span>Statutory Notices</span>
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={handleStartScan}
            className="flex items-center space-x-1.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold border border-amber-600 shadow-xs"
          >
            <Camera className="w-4 h-4 text-slate-950" />
            <span>Scan Product Now</span>
          </Button>
        </div>
      </div>

      {/* Hero Scanner & Ingestion Station Card */}
      <div className="bg-gradient-to-r from-[#0f2942] to-[#163a5f] rounded-xl p-5 md:p-6 text-white shadow-md border border-slate-800">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-amber-400/20 text-amber-300 border border-amber-400/30 text-xs font-mono">
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>Instant Optical Inspection • Multi-Surface Acquisition</span>
            </div>
            <h2 className="text-lg md:text-xl font-bold tracking-tight text-white">
              Ready to Inspect a Packaged Commodity?
            </h2>
            <p className="text-xs md:text-sm text-slate-200 leading-relaxed">
              Capture or upload packaging labels for automated optical character recognition, PDP area analysis, and deterministic rule validation under Legal Metrology (Packaged Commodities) Rules, 2011.
            </p>
          </div>

          {/* Direct CTA Buttons */}
          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <button
              onClick={handleStartScan}
              className="flex items-center space-x-2 px-4 py-2.5 bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold text-xs rounded-lg shadow-md transition transform active:scale-95 cursor-pointer"
            >
              <Camera className="w-4 h-4 text-slate-950" />
              <span>Open Camera & Capture</span>
            </button>

            <button
              onClick={() => {
                startNewInspection();
                navigate('/new-inspection?step=2');
              }}
              className="flex items-center space-x-2 px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white font-medium text-xs rounded-lg border border-white/20 transition cursor-pointer"
            >
              <Upload className="w-4 h-4 text-slate-300" />
              <span>Upload Label Image</span>
            </button>
          </div>
        </div>

        {/* 4-Stage Architecture Pipeline Status Strip */}
        <div className="mt-5 pt-4 border-t border-white/10 grid grid-cols-2 md:grid-cols-4 gap-3 text-[11px]">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-300">1. Optical Acquisition:</span>
            <span className="font-mono text-emerald-300 font-semibold">Ready</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-300">2. Tesseract OCR Engine:</span>
            <span className="font-mono text-emerald-300 font-semibold">Active</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-300">3. Rule 6/7/8 Validator:</span>
            <span className="font-mono text-emerald-300 font-semibold">LMPC 2011</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-300">4. Section 36 Notice:</span>
            <span className="font-mono text-emerald-300 font-semibold">Enabled</span>
          </div>
        </div>
      </div>

      {/* KPI Statistic Cards (Section 1) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Total Inspections */}
        <Card orientation="vertical" className="border-l-4 border-l-[#0f2942]">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Total Inspections
              </p>
              <p className="text-2xl font-bold text-slate-900 mt-1 font-mono">{totalInspections}</p>
            </div>
            <div className="p-2 rounded-md bg-slate-100 text-slate-700">
              <ClipboardCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-center text-xs text-slate-600 font-medium">
            <span>{totalInspections} total audited dockets</span>
          </div>
        </Card>

        {/* Card 2: Compliant Packages */}
        <Card orientation="vertical" className="border-l-4 border-l-emerald-600">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Compliant Packages
              </p>
              <p className="text-2xl font-bold text-emerald-700 mt-1 font-mono">{compliantCount}</p>
            </div>
            <div className="p-2 rounded-md bg-emerald-50 text-emerald-700">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-center text-xs text-emerald-800">
            <span className="font-semibold font-mono">{complianceRate}%</span>
            <span className="text-slate-500 ml-1.5">statutory compliance rate</span>
          </div>
        </Card>

        {/* Card 3: Non-Compliant / Violations */}
        <Card orientation="vertical" className="border-l-4 border-l-red-600">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Violations Flagged
              </p>
              <p className="text-2xl font-bold text-red-700 mt-1 font-mono">{nonCompliantCount}</p>
            </div>
            <div className="p-2 rounded-md bg-red-50 text-red-700">
              <AlertOctagon className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-center text-xs text-red-700">
            <span className="font-semibold font-mono">{nonComplianceRate}%</span>
            <span className="text-slate-500 ml-1.5">non-compliant dockets</span>
          </div>
        </Card>

        {/* Card 4: Under Officer Review */}
        <Card orientation="vertical" className="border-l-4 border-l-amber-600">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Pending Scrutiny
              </p>
              <p className="text-2xl font-bold text-amber-700 mt-1 font-mono">{underReviewCount}</p>
            </div>
            <div className="p-2 rounded-md bg-amber-50 text-amber-700">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-center text-xs text-amber-800">
            <span className="font-semibold font-mono">{underReviewRate}%</span>
            <span className="text-slate-500 ml-1.5">awaiting officer review</span>
          </div>
        </Card>
      </div>

      {/* Compliance Distribution Chart */}
      <div>
        <Card orientation="vertical" className="h-full">
          <CardHeader
            title="Statutory Compliance Distribution"
            subtitle="Live breakdown across all audited packaged commodities"
          />
          <CardContent>
            {totalInspections === 0 ? (
              <div className="py-12 px-4 text-center space-y-3">
                <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400">
                  <ClipboardCheck className="w-6 h-6" />
                </div>
                <h3 className="text-sm font-bold text-slate-800">No Packaging Inspections Recorded Yet</h3>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                  Initiate an optical scan or upload a packaging label. As dockets are created and verified, real-time compliance metrics will appear here.
                </p>
                <Button variant="primary" size="sm" onClick={handleStartScan} className="mt-2">
                  Scan Product Now
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
                <div className="md:col-span-7 h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={80}
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
                          backgroundColor: '#ffffff',
                          border: '1px solid #cbd5e1',
                          borderRadius: '4px',
                          fontSize: '12px'
                        }}
                      />
                      <Legend
                        verticalAlign="bottom"
                        wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Summary Metrics */}
                <div className="md:col-span-5 space-y-3 text-xs border-l border-slate-200 pl-4">
                  <div className="p-2.5 bg-slate-50 border border-slate-200 rounded space-y-1">
                    <span className="text-slate-500 font-medium">Most Common Infraction:</span>
                    <p className="font-bold text-slate-900 truncate">
                      {violationInsights.topViolationName || 'No violations recorded'}
                    </p>
                    <span className="text-[10px] text-slate-500 block">
                      {violationInsights.topViolationName
                        ? `${violationInsights.topViolationPct}% of all flagged violations (${violationInsights.topViolationCount} occurrences)`
                        : 'Zero infractions across audited commodities'}
                    </span>
                  </div>

                  <div className="p-2.5 bg-slate-50 border border-slate-200 rounded space-y-1">
                    <span className="text-slate-500 font-medium">Total Flagged Infractions:</span>
                    <p className="font-bold text-slate-900 font-mono">{totalViolations}</p>
                    <span className="text-[10px] text-slate-500 block">
                      Across {nonCompliantCount} non-compliant inspection dockets
                    </span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Grid: Recent Inspections & Priority Violations */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Inspections Table (7 cols) */}
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
                  <p className="text-xs text-slate-500">
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
                      <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-medium">
                        <th className="py-2.5 px-3">Docket ID</th>
                        <th className="py-2.5 px-3">Commodity / Brand</th>
                        <th className="py-2.5 px-3">Date</th>
                        <th className="py-2.5 px-3">Status</th>
                        <th className="py-2.5 px-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {recentInspections.map((insp) => (
                        <tr key={insp.id} className="hover:bg-slate-50/80 transition">
                          <td className="py-2.5 px-3 font-mono font-bold text-slate-900">
                            {insp.id}
                          </td>
                          <td className="py-2.5 px-3">
                            <p className="font-semibold text-slate-900 truncate max-w-[180px]">
                              {insp.productName || 'Unspecified Commodity'}
                            </p>
                            <p className="text-[10px] text-slate-500 truncate max-w-[180px]">
                              {insp.brand || 'No Brand'} • {insp.category}
                            </p>
                          </td>
                          <td className="py-2.5 px-3 font-mono text-slate-600 whitespace-nowrap">
                            {insp.date}
                          </td>
                          <td className="py-2.5 px-3">
                            <StatusBadge status={insp.status} />
                          </td>
                          <td className="py-2.5 px-3 text-right whitespace-nowrap space-x-1">
                            <button
                              onClick={() => navigate(`/reports/${insp.id}`)}
                              className="p-1 text-slate-500 hover:text-[#0f2942] hover:bg-slate-100 rounded cursor-pointer"
                              title="View Official Report"
                            >
                              <FileText className="w-3.5 h-3.5" />
                            </button>
                            {insp.status === 'Non-Compliant' && (
                              <button
                                onClick={() => navigate('/legal-notices')}
                                className="p-1 text-red-600 hover:text-red-800 hover:bg-red-50 rounded cursor-pointer"
                                title="Generate Section 36 Notice"
                              >
                                <Scale className="w-3.5 h-3.5" />
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

        {/* Priority Violations & Statutory Actions (5 cols) */}
        <div className="lg:col-span-5">
          <Card orientation="vertical">
            <CardHeader
              title="Flagged Statutory Violations"
              subtitle="Requires Section 36 statutory notice or compounding"
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
                  <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto opacity-70" />
                  <p className="text-xs font-semibold text-slate-700 mt-2">No Violations Flagged</p>
                  <p className="text-[11px] text-slate-500">
                    No statutory infractions currently pending enforcement action.
                  </p>
                </div>
              ) : (
                allViolations.map((v) => (
                  <div
                    key={v.id}
                    className="p-3 bg-slate-50 border border-slate-200 rounded-lg hover:border-slate-300 transition space-y-1.5"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <span className="font-bold text-xs text-slate-900 leading-snug">
                        {v.violationType}
                      </span>
                      <SeverityBadge severity={v.severity} />
                    </div>
                    <p className="text-[11px] text-slate-600 leading-relaxed">{v.description}</p>
                    <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-200">
                      <span className="font-mono font-bold text-slate-700">{v.ruleReference}</span>
                      <button
                        onClick={() => navigate('/legal-notices')}
                        className="text-indigo-700 hover:text-indigo-900 font-semibold flex items-center space-x-1 cursor-pointer"
                      >
                        <span>Issue Notice</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
