import React, { useState, useMemo } from 'react';
import { useInspection } from '../context/InspectionContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { SeverityBadge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { LabelGraphic } from '../components/inspection/LabelGraphic';
import {
  AlertOctagon,
  Search,
  Filter,
  Eye,
  Gavel,
  CheckCircle,
  MessageSquare,
  FileText
} from 'lucide-react';
import { InspectionViolation } from '../types';

export const ViolationsRegistryPage: React.FC = () => {
  const { inspections, updateViolationStatus } = useInspection();
  const navigate = useNavigate();

  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [selectedViolationForEvidence, setSelectedViolationForEvidence] = useState<InspectionViolation | null>(null);

  // Extract all violations with their associated inspection dockets
  const allViolations = useMemo(() => {
    return inspections.flatMap(insp =>
      insp.violations.map(v => ({
        ...v,
        inspectionId: insp.id,
        inspectionDate: insp.date,
        officer: insp.officerName
      }))
    );
  }, [inspections]);

  const filteredViolations = useMemo(() => {
    return allViolations.filter(v => {
      const matchesSearch =
        searchTerm === '' ||
        v.violationType.toLowerCase().includes(searchTerm.toLowerCase()) ||
        v.product.toLowerCase().includes(searchTerm.toLowerCase()) ||
        v.ruleReference.toLowerCase().includes(searchTerm.toLowerCase()) ||
        v.id.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesSeverity = severityFilter === 'ALL' || v.severity === severityFilter;
      return matchesSearch && matchesSeverity;
    });
  }, [allViolations, searchTerm, severityFilter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Violations & Enforcement Registry</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Active contraventions of Legal Metrology (Packaged Commodities) Rules, 2011 and Section 36 penalty tracking
          </p>
        </div>
        <div className="text-xs font-mono text-red-700 bg-red-50 border border-red-200 px-3 py-1.5 rounded">
          Active Infractions: <strong>{filteredViolations.length}</strong>
        </div>
      </div>

      {/* Filter Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="relative md:col-span-2">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by Violation Type, Rule Clause, Product, or Infraction ID..."
                className="w-full bg-slate-50 border border-slate-300 rounded pl-9 pr-3 py-1.5 text-xs text-slate-900 focus:bg-white focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              />
            </div>
            <div>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:outline-none"
              >
                <option value="ALL">All Severity Levels</option>
                <option value="High">High Severity (Section 36 Compounding)</option>
                <option value="Medium">Medium (Font Size / Smudge)</option>
                <option value="Low">Low (Rectification Warning)</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Violations Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-800 border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-3">Infraction ID</th>
                <th className="py-3 px-3">Violation Charge & Clause</th>
                <th className="py-3 px-3">Product Name</th>
                <th className="py-3 px-3">Surface</th>
                <th className="py-3 px-3">Severity</th>
                <th className="py-3 px-3">Officer Status</th>
                <th className="py-3 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {filteredViolations.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center p-8 text-slate-500 text-xs">
                    No violations found matching the criteria.
                  </td>
                </tr>
              ) : (
                filteredViolations.map((v) => (
                  <tr key={v.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-3 font-mono font-bold text-slate-900">
                      {v.id}
                    </td>
                    <td className="py-3 px-3 max-w-xs">
                      <div>
                        <span className="font-semibold text-slate-900 block">{v.violationType}</span>
                        <span className="text-[10px] font-mono text-red-700 block">{v.ruleReference}</span>
                        <p className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">{v.description}</p>
                      </div>
                    </td>
                    <td className="py-3 px-3 font-medium text-slate-800 max-w-[170px] truncate">
                      {v.product}
                    </td>
                    <td className="py-3 px-3">
                      <span className="inline-block px-1.5 py-0.5 rounded text-[10px] bg-slate-100 text-slate-700 border border-slate-200">
                        {v.surface}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <SeverityBadge severity={v.severity} />
                    </td>
                    <td className="py-3 px-3">
                      <span className="inline-block px-2 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
                        {v.officerStatus}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end space-x-1.5">
                        <Button
                          variant="outline"
                          size="sm"
                          leftIcon={<Eye className="w-3.5 h-3.5" />}
                          onClick={() => setSelectedViolationForEvidence(v)}
                        >
                          Evidence
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          leftIcon={<FileText className="w-3.5 h-3.5" />}
                          onClick={() => navigate(`/reports/${v.inspectionId}`)}
                        >
                          Report
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Evidence Inspection Modal */}
      {selectedViolationForEvidence && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedViolationForEvidence(null)}
          title={`Photographic Evidence: ${selectedViolationForEvidence.violationType}`}
          subtitle={`Infraction: ${selectedViolationForEvidence.id} • Rule: ${selectedViolationForEvidence.ruleReference}`}
          maxWidth="2xl"
          footer={
            <Button variant="primary" size="sm" onClick={() => setSelectedViolationForEvidence(null)}>
              Done Inspecting
            </Button>
          }
        >
          <div className="space-y-4">
            <div className="h-80 w-full">
              <LabelGraphic
                svgMockType="front-mustard"
                surface={selectedViolationForEvidence.surface}
                boundingBoxes={[selectedViolationForEvidence.evidenceBoundingBox]}
                highlightBox={selectedViolationForEvidence.evidenceBoundingBox}
              />
            </div>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded text-xs space-y-1">
              <p className="font-bold text-slate-900">Statutory Infraction Finding:</p>
              <p className="text-slate-700">{selectedViolationForEvidence.description}</p>
              <p className="font-mono text-red-800 pt-1">
                Prescribed Statutory Penalty: {selectedViolationForEvidence.recommendedPenalty}
              </p>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
