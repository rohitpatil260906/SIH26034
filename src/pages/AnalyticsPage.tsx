import React, { useState, useMemo } from 'react';
import { useInspection } from '../context/InspectionContext';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import {
  BarChart3,
  Calendar,
  Filter,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Building,
  ClipboardList
} from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const { inspections } = useInspection();
  const [timeRange, setTimeRange] = useState('All Recorded Dockets');

  const totalInspections = inspections.length;
  const compliantCount = inspections.filter(i => i.status === 'Compliant').length;
  const nonCompliantCount = inspections.filter(i => i.status === 'Non-Compliant').length;
  const totalViolations = inspections.reduce((acc, i) => acc + (i.violations?.length || 0), 0);
  const portDetentions = inspections.filter(
    i => i.inspectionType === 'Port of Entry Inward' && i.status === 'Non-Compliant'
  ).length;

  const complianceRate = totalInspections > 0
    ? ((compliantCount / totalInspections) * 100).toFixed(1)
    : '0.0';

  const compoundingTotal = totalViolations * 25000;

  // Monthly timeline aggregation
  const monthlyInspectionsData = useMemo(() => {
    if (inspections.length === 0) return [];
    const map: Record<string, { total: number; compliant: number; violations: number }> = {};
    inspections.forEach(i => {
      const month = i.date ? i.date.substring(0, 7) : 'Current';
      if (!map[month]) map[month] = { total: 0, compliant: 0, violations: 0 };
      map[month].total += 1;
      if (i.status === 'Compliant') map[month].compliant += 1;
      if (i.status === 'Non-Compliant') map[month].violations += (i.violations?.length || 1);
    });
    return Object.entries(map).map(([month, data]) => ({
      month,
      ...data
    }));
  }, [inspections]);

  // Infraction distribution by rule
  const commonViolationTypes = useMemo(() => {
    const counts: Record<string, number> = {};
    inspections.flatMap(i => i.violations || []).forEach(v => {
      const label = v.ruleReference ? `${v.ruleReference} — ${v.violationType}` : v.violationType;
      counts[label] = (counts[label] || 0) + 1;
    });
    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([type, count]) => ({
        type,
        count,
        share: total > 0 ? `${((count / total) * 100).toFixed(1)}%` : '0%'
      }));
  }, [inspections]);

  // Violations by category
  const violationsByCategoryData = useMemo(() => {
    const counts: Record<string, number> = {};
    inspections.forEach(i => {
      const cat = i.category || 'General';
      const vios = i.violations?.length || (i.status === 'Non-Compliant' ? 1 : 0);
      counts[cat] = (counts[cat] || 0) + vios;
    });
    return Object.entries(counts).map(([category, violations]) => ({
      category,
      violations,
      compoundingFines: `₹ ${(violations * 25000).toLocaleString('en-IN')}`
    }));
  }, [inspections]);

  // Zonal aggregation
  const zonalCaseload = useMemo(() => {
    const map: Record<string, { inspections: number; compliant: number }> = {};
    inspections.forEach(i => {
      const zone = i.jurisdiction || 'Default Zone';
      if (!map[zone]) map[zone] = { inspections: 0, compliant: 0 };
      map[zone].inspections += 1;
      if (i.status === 'Compliant') map[zone].compliant += 1;
    });
    return Object.entries(map).map(([zone, data]) => ({
      zone,
      inspections: data.inspections,
      complianceRate: data.inspections > 0
        ? `${((data.compliant / data.inspections) * 100).toFixed(1)}%`
        : '0.0%'
    }));
  }, [inspections]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Enforcement & Compliance Analytics</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Operational intelligence for Legal Metrology controllers, zone supervisors, and enforcement officers
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded">
            Total Dockets Analyzed: <strong>{totalInspections}</strong>
          </span>
        </div>
      </div>

      {/* Top 3 Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
            National Average Compliance
          </span>
          <span className="text-2xl font-bold text-emerald-700 font-mono mt-1 block">
            {complianceRate}%
          </span>
          <span className="text-[11px] text-slate-500 mt-1 block">
            {compliantCount} of {totalInspections} audited packages compliant
          </span>
        </Card>

        <Card className="p-4">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
            Estimated Compounding Potential
          </span>
          <span className="text-2xl font-bold text-slate-900 font-mono mt-1 block">
            ₹ {compoundingTotal.toLocaleString('en-IN')}
          </span>
          <span className="text-[11px] text-slate-500 mt-1 block">
            Based on {totalViolations} flagged statutory infractions
          </span>
        </Card>

        <Card className="p-4">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
            Port Consignments Detained
          </span>
          <span className="text-2xl font-bold text-red-700 font-mono mt-1 block">
            {portDetentions} Batches
          </span>
          <span className="text-[11px] text-slate-500 mt-1 block">
            Detained under Customs / Inward Cargo audits
          </span>
        </Card>
      </div>

      {/* Main Charts: 2 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Monthly Inspections Chart (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <Card>
            <CardHeader
              title="Inspection Caseload & Compliance Timeline"
              subtitle="Conforming vs non-conforming packaging samples by period"
            />
            <CardContent className="p-4">
              {monthlyInspectionsData.length === 0 ? (
                <div className="h-56 flex flex-col items-center justify-center text-slate-400 text-xs space-y-1">
                  <ClipboardList className="w-8 h-8 opacity-40 mb-1" />
                  <span>No inspection data recorded for this timeline.</span>
                  <span className="text-[10px] text-slate-400">Conduct inspections to generate historical throughput charts.</span>
                </div>
              ) : (
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={monthlyInspectionsData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} />
                      <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                      <Tooltip
                        contentStyle={{ fontSize: '11px', borderRadius: '4px', borderColor: '#cbd5e1' }}
                      />
                      <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                      <Bar dataKey="compliant" name="Compliant Packages" fill="#15803d" radius={[2, 2, 0, 0]} />
                      <Bar dataKey="violations" name="Violations Flagged" fill="#b91c1c" radius={[2, 2, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Common Violation Types Breakdown */}
          <Card>
            <CardHeader
              title="Prevalent Legal Metrology Infraction Clauses"
              subtitle="Distribution of statutory charges filed under Section 36"
            />
            <div className="divide-y divide-slate-200 text-xs">
              {commonViolationTypes.length === 0 ? (
                <div className="p-6 text-center text-slate-400">
                  No statutory infractions recorded yet.
                </div>
              ) : (
                commonViolationTypes.map((v, i) => (
                  <div key={i} className="p-3 flex items-center justify-between hover:bg-slate-50">
                    <div className="max-w-md">
                      <span className="font-semibold text-slate-900 block">{v.type}</span>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="font-mono font-bold text-red-700">{v.count} Cases</span>
                      <span className="block text-[10px] text-slate-400 font-mono">({v.share})</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>

        {/* Violations by Category & Zonal Table (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <Card>
            <CardHeader
              title="Violations by Commodity Sector"
              subtitle="Audit results across product classifications"
            />
            <div className="p-4 space-y-3 text-xs">
              {violationsByCategoryData.length === 0 ? (
                <div className="py-6 text-center text-slate-400">
                  No commodity categories audited yet.
                </div>
              ) : (
                violationsByCategoryData.map((item, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-800">{item.category}</span>
                      <span className="font-mono text-red-700 font-bold">{item.violations} Violations</span>
                    </div>
                    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-[#0f2942]"
                        style={{ width: `${Math.min(100, Math.max(8, item.violations * 20))}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono block">
                      Estimated Compounding: {item.compoundingFines}
                    </span>
                  </div>
                ))
              )}
            </div>
          </Card>

          {/* Zonal Performance Table */}
          <Card>
            <CardHeader
              title="Enforcement Activity by Zonal Jurisdiction"
              subtitle="Field officer activity across state divisions"
            />
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-800 border-collapse">
                <thead className="bg-slate-50 border-b border-slate-200 text-[10px] font-bold text-slate-600 uppercase">
                  <tr>
                    <th className="py-2 px-3">Jurisdiction</th>
                    <th className="py-2 px-3 text-center">Audits</th>
                    <th className="py-2 px-3 text-right">Compliance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {zonalCaseload.length === 0 ? (
                    <tr>
                      <td colSpan={3} className="py-4 text-center text-slate-400">
                        No zonal inspections logged yet.
                      </td>
                    </tr>
                  ) : (
                    zonalCaseload.map((z, idx) => (
                      <tr key={idx} className="hover:bg-slate-50">
                        <td className="py-2 px-3 font-medium text-slate-900 truncate max-w-[130px]">
                          {z.zone}
                        </td>
                        <td className="py-2 px-3 text-center font-mono">{z.inspections}</td>
                        <td className="py-2 px-3 text-right font-mono font-bold text-emerald-800">{z.complianceRate}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
