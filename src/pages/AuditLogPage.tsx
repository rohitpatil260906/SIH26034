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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E5E2DD] pb-4">
        <div>
          <h1 className="text-2xl font-bold text-[#1F2328] tracking-tight">System Audit Log & Chain of Custody</h1>
          <p className="text-xs text-[#5F6368] mt-0.5">
            Cryptographically timestamped audit trail tracking every inspection event, manual override, and enforcement order
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          leftIcon={<Download className="w-4 h-4 text-[#5F6368]" />}
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
              <Search className="w-4 h-4 text-[#8A8F98] absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search audit actions, officer names, record IDs, or details..."
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg pl-9 pr-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED]"
              />
            </div>
            <div>
              <select
                value={moduleFilter}
                onChange={(e) => setModuleFilter(e.target.value)}
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED] cursor-pointer"
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
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED] cursor-pointer"
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
          <table className="w-full text-left text-xs text-[#1F2328] border-collapse">
            <thead className="bg-[#FAF9F7] border-b border-[#E5E2DD] text-[11px] font-bold text-[#5F6368] uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Timestamp & ID</th>
                <th className="py-3 px-4">Officer / Principal</th>
                <th className="py-3 px-4">Action Performed</th>
                <th className="py-3 px-4">Module</th>
                <th className="py-3 px-4">Record ID</th>
                <th className="py-3 px-4">Audit Details</th>
                <th className="py-3 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F0EDE8] bg-white font-mono text-[11px]">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-[#FAF9F7] transition-colors">
                  <td className="py-3 px-4 whitespace-nowrap text-[#5F6368]">
                    <span className="block text-[#1F2328] font-bold">{log.timestamp}</span>
                    <span className="text-[10px] text-[#8A8F98]">{log.id}</span>
                  </td>
                  <td className="py-3 px-4 font-sans font-medium text-[#1F2328] whitespace-nowrap">
                    <span>{log.user}</span>
                    <span className="block text-[10px] font-mono text-[#8A8F98]">{log.role}</span>
                  </td>
                  <td className="py-3 px-4 font-sans font-semibold text-[#1F2328] whitespace-nowrap">
                    {log.action}
                  </td>
                  <td className="py-3 px-4 font-sans text-[#5F6368]">
                    <span className="inline-block px-2 py-0.5 rounded-md text-[10px] bg-[#FAF9F7] text-[#5F6368] border border-[#E5E2DD]">
                      {log.module}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-bold text-[#6D28D9]">
                    {log.recordId}
                  </td>
                  <td className="py-3 px-4 font-sans text-[#5F6368] max-w-sm">
                    {log.details}
                  </td>
                  <td className="py-3 px-4 text-center">
                    {log.status === 'Success' && (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#F0FDF4] text-[#16A34A] border border-[#BBF7D0]">
                        <CheckCircle2 className="w-3 h-3 mr-0.5" />
                        SUCCESS
                      </span>
                    )}
                    {log.status === 'Warning' && (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#FEF2F2] text-[#DC2626] border border-[#FECACA]">
                        <AlertTriangle className="w-3 h-3 mr-0.5" />
                        VIOLATION
                      </span>
                    )}
                    {log.status === 'Override' && (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#FFFBEB] text-[#D97706] border border-[#FDE68A]">
                        OVERRIDE
                      </span>
                    )}
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
