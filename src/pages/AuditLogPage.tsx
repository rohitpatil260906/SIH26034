import React, { useState, useMemo } from 'react';
import { useInspection } from '../context/InspectionContext';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import {
  ShieldCheck,
  Search,
  Filter,
  Download,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Clock,
  Terminal
} from 'lucide-react';

export const AuditLogPage: React.FC = () => {
  const { auditLogs } = useInspection();

  const [searchTerm, setSearchTerm] = useState('');
  const [moduleFilter, setModuleFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const modules = useMemo(() => {
    return Array.from(new Set(auditLogs.map(l => l.module)));
  }, [auditLogs]);

  const filteredLogs = useMemo(() => {
    return auditLogs.filter(log => {
      const matchesSearch =
        searchTerm === '' ||
        log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.recordId.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.details.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesModule = moduleFilter === 'ALL' || log.module === moduleFilter;
      const matchesStatus = statusFilter === 'ALL' || log.status === statusFilter;

      return matchesSearch && matchesModule && matchesStatus;
    });
  }, [auditLogs, searchTerm, moduleFilter, statusFilter]);

  const handleExportAuditCSV = () => {
    const headers = "Log ID,Timestamp,Officer,Role,Action,Module,Record ID,Status,Details,IP Address\n";
    const rows = filteredLogs.map(l =>
      `"${l.id}","${l.timestamp}","${l.user}","${l.role}","${l.action}","${l.module}","${l.recordId}","${l.status}","${l.details.replace(/"/g, '""')}","${l.ipAddress}"`
    ).join("\n");
    const blob = new Blob([headers + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `LMCS_Audit_Trail_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">System Audit Log & Chain of Custody</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Cryptographically timestamped audit trail tracking every inspection event, manual override, and enforcement order
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          leftIcon={<Download className="w-4 h-4" />}
          onClick={handleExportAuditCSV}
        >
          Export Official Audit Trail (CSV)
        </Button>
      </div>

      {/* Filter Card */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="relative md:col-span-2">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search audit actions, officer names, record IDs, or details..."
                className="w-full bg-slate-50 border border-slate-300 rounded pl-9 pr-3 py-1.5 text-xs text-slate-900 focus:bg-white focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              />
            </div>
            <div>
              <select
                value={moduleFilter}
                onChange={(e) => setModuleFilter(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:outline-none"
              >
                <option value="ALL">All Modules</option>
                {modules.map(m => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
            <div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:outline-none"
              >
                <option value="ALL">All Event Severities</option>
                <option value="Success">Success (Routine Event)</option>
                <option value="Warning">Warning (Infraction Logged)</option>
                <option value="Override">Override (Manual Value Calibrated)</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Audit Log Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-800 border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-3">Timestamp (IST)</th>
                <th className="py-3 px-3">Enforcement Officer</th>
                <th className="py-3 px-3">Action Executed</th>
                <th className="py-3 px-3">Module</th>
                <th className="py-3 px-3">Docket / Record</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3">Operational Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-3 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                    {log.timestamp}
                  </td>
                  <td className="py-3 px-3 whitespace-nowrap">
                    <span className="font-semibold text-slate-900 block">{log.user}</span>
                    <span className="text-[10px] text-slate-400 font-mono block">{log.role}</span>
                  </td>
                  <td className="py-3 px-3 font-medium text-slate-900">
                    {log.action}
                  </td>
                  <td className="py-3 px-3">
                    <span className="inline-block px-1.5 py-0.5 rounded text-[10px] bg-slate-100 text-slate-700 font-mono border border-slate-200">
                      {log.module}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono text-[11px] font-semibold text-slate-800 whitespace-nowrap">
                    {log.recordId}
                  </td>
                  <td className="py-3 px-3">
                    {log.status === 'Success' && (
                      <span className="inline-flex items-center text-[10px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        SUCCESS
                      </span>
                    )}
                    {log.status === 'Warning' && (
                      <span className="inline-flex items-center text-[10px] font-semibold text-red-800 bg-red-50 px-2 py-0.5 rounded border border-red-200">
                        INFRACTION
                      </span>
                    )}
                    {log.status === 'Override' && (
                      <span className="inline-flex items-center text-[10px] font-semibold text-blue-800 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                        MANUAL OVERRIDE
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-slate-600 max-w-sm">
                    <p className="text-[11px] leading-relaxed line-clamp-2">
                      {log.details}
                    </p>
                    <span className="text-[9px] font-mono text-slate-400 block mt-0.5">
                      Node: {log.ipAddress}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
