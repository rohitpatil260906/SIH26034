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
  FileText,
  Scale,
  ArrowRight,
  ExternalLink,
  RotateCcw
} from 'lucide-react';
import { InspectionViolation } from '../types';

export const ViolationsRegistryPage: React.FC = () => {
  const { inspections } = useInspection();
  const navigate = useNavigate();

  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [selectedViolationForEvidence, setSelectedViolationForEvidence] = useState<(InspectionViolation & { inspectionId: string }) | null>(null);

  // Flatten all violations across inspections
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
        v.ruleReference.toLowerCase().includes(searchTerm.toLowerCase()) ||
        v.product.toLowerCase().includes(searchTerm.toLowerCase()) ||
        v.id.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesSeverity = severityFilter === 'ALL' || v.severity === severityFilter;
      return matchesSearch && matchesSeverity;
    });
  }, [allViolations, searchTerm, severityFilter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E5E2DD] pb-4">
        <div>
          <h1 className="text-2xl font-bold text-[#1F2328] tracking-tight">Violations & Enforcement Registry</h1>
          <p className="text-xs text-[#5F6368] mt-0.5">
            Active contraventions of Legal Metrology (Packaged Commodities) Rules, 2011 and Section 36 penalty tracking
          </p>
        </div>
        <div className="text-xs font-mono text-[#DC2626] bg-[#FEF2F2] border border-[#FECACA] px-3 py-1.5 rounded-lg shadow-2xs">
          Active Infractions: <strong>{filteredViolations.length}</strong>
        </div>
      </div>

      {/* Filter Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="relative md:col-span-2">
              <Search className="w-4 h-4 text-[#8A8F98] absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by Violation Type, Rule Clause, Product, or Infraction ID..."
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg pl-9 pr-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED]"
              />
            </div>
            <div>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED] cursor-pointer"
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
          <table className="w-full text-left text-xs text-[#1F2328] border-collapse">
            <thead className="bg-[#FAF9F7] border-b border-[#E5E2DD] text-[11px] font-bold text-[#5F6368] uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Infraction ID</th>
                <th className="py-3 px-4">Violation Charge & Clause</th>
                <th className="py-3 px-4">Product Name</th>
                <th className="py-3 px-4">Surface</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Officer Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F0EDE8] bg-white">
              {filteredViolations.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center p-8 text-[#8A8F98] text-xs">
                    No violations found matching the criteria.
                  </td>
                </tr>
              ) : (
                filteredViolations.map((v) => (
                  <tr key={v.id} className="hover:bg-[#FAF9F7] transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-[#1F2328]">
                      {v.id}
                    </td>
                    <td className="py-3.5 px-4 max-w-xs">
                      <div>
                        <span className="font-semibold text-[#1F2328] block">{v.violationType}</span>
                        <span className="text-[10px] font-mono text-[#DC2626] block">{v.ruleReference}</span>
                        <p className="text-[11px] text-[#5F6368] line-clamp-1 mt-0.5">{v.description}</p>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-[#1F2328] max-w-[170px] truncate">
                      {v.product}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-block px-2 py-0.5 rounded-md text-[10px] bg-[#FAF9F7] text-[#5F6368] border border-[#E5E2DD]">
                        {v.surface}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <SeverityBadge severity={v.severity} />
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-block px-2 py-0.5 rounded-md text-xs font-semibold bg-[#FFFBEB] text-[#D97706] border border-[#FDE68A]">
                        {v.officerStatus}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-1.5">
                        <Button
                          variant="outline"
                          size="sm"
                          leftIcon={<Eye className="w-3.5 h-3.5 text-[#6D28D9]" />}
                          onClick={() => setSelectedViolationForEvidence(v)}
                        >
                          Evidence
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          leftIcon={<FileText className="w-3.5 h-3.5 text-[#5F6368]" />}
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
            <div className="h-80 w-full rounded-xl overflow-hidden border border-[#E5E2DD]">
              <LabelGraphic
                svgMockType="front-mustard"
                surface={selectedViolationForEvidence.surface}
                boundingBoxes={[selectedViolationForEvidence.evidenceBoundingBox]}
                highlightBox={selectedViolationForEvidence.evidenceBoundingBox}
              />
            </div>
            <div className="p-3.5 bg-[#FAF9F7] border border-[#E5E2DD] rounded-xl text-xs space-y-1.5">
              <p className="font-bold text-[#1F2328]">Statutory Infraction Finding:</p>
              <p className="text-[#5F6368]">{selectedViolationForEvidence.description}</p>
              <p className="font-mono text-[#DC2626] font-semibold pt-1">
                Prescribed Statutory Penalty: {selectedViolationForEvidence.recommendedPenalty}
              </p>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
