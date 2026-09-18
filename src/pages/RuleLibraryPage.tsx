import React, { useState, useMemo } from 'react';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { LEGAL_RULES } from '../data/mockRules';
import { LegalRuleItem } from '../types';
import {
  BookOpen,
  Search,
  Filter,
  ExternalLink,
  Info,
  Scale,
  FileCheck,
  ShieldAlert,
  ChevronRight
} from 'lucide-react';

export const RuleLibraryPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [selectedRule, setSelectedRule] = useState<LegalRuleItem | null>(null);

  const categories = useMemo(() => {
    return Array.from(new Set(LEGAL_RULES.map(r => r.category)));
  }, []);

  const filteredRules = useMemo(() => {
    return LEGAL_RULES.filter(rule => {
      const matchesSearch =
        searchTerm === '' ||
        rule.ruleNo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rule.subRule.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rule.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rule.requirement.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rule.applicableDeclaration.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesCategory = categoryFilter === 'ALL' || rule.category === categoryFilter;
      return matchesSearch && matchesCategory;
    });
  }, [searchTerm, categoryFilter]);

  return (
    <div className="space-y-6">
      {/* Mandatory Statutory Notice Banner */}
      <div className="bg-amber-50 border-2 border-amber-300 rounded-md p-4 flex items-start space-x-3 text-xs text-amber-950">
        <Info className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
        <div>
          <h4 className="font-bold uppercase tracking-wider text-[11px] text-amber-900">
            Official Regulatory Notice
          </h4>
          <p className="mt-0.5 leading-relaxed font-sans">
            “Rule references shown in this prototype are for demonstration and must be verified against the current applicable Legal Metrology requirements before enforcement use.”
            Statutory statutory notices must reference Gazette notifications and amendments as notified by the Ministry of Consumer Affairs, Food & Public Distribution.
          </p>
        </div>
      </div>

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Legal Metrology (Packaged Commodities) Rules, 2011 — Compendium
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Authoritative statutory rule repository, numeral height schedules, and enforcement officer field directives
          </p>
        </div>
        <div className="text-xs font-mono text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded">
          Active Statutory Clauses: <strong>{LEGAL_RULES.length}</strong>
        </div>
      </div>

      {/* Filter Toolbar */}
      <Card>
        <CardContent className="p-4 space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="relative md:col-span-2">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by Rule No. (e.g. Rule 6), Title, Keyword, or Declaration..."
                className="w-full bg-slate-50 border border-slate-300 rounded pl-9 pr-3 py-1.5 text-xs text-slate-900 focus:bg-white focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              />
            </div>
            <div>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:outline-none"
              >
                <option value="ALL">All Rule Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Rules Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-800 border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Rule No. & Clause</th>
                <th className="py-3 px-4">Subject & Title</th>
                <th className="py-3 px-4">Statutory Requirement</th>
                <th className="py-3 px-4">Mandatory Declaration</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {filteredRules.map((rule) => (
                <tr key={rule.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-4 font-mono font-bold text-slate-900 whitespace-nowrap">
                    <div>
                      <span>{rule.ruleNo}</span>
                      <span className="text-[10px] text-slate-500 block font-normal">{rule.subRule}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 font-semibold text-slate-900 max-w-[180px]">
                    {rule.title}
                  </td>
                  <td className="py-3 px-4 text-slate-600 max-w-sm">
                    <p className="line-clamp-2 text-[11px] leading-relaxed">
                      {rule.requirement}
                    </p>
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-block bg-slate-100 text-slate-800 px-2 py-0.5 rounded text-[11px] font-medium border border-slate-200">
                      {rule.applicableDeclaration}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-500 text-[11px]">
                    {rule.category}
                  </td>
                  <td className="py-3 px-4 text-right whitespace-nowrap">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedRule(rule)}
                    >
                      View Clause Details
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Rule Detail Modal */}
      {selectedRule && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedRule(null)}
          title={`${selectedRule.ruleNo} — ${selectedRule.title}`}
          subtitle={`${selectedRule.subRule} • ${selectedRule.category}`}
          maxWidth="2xl"
          footer={
            <Button variant="primary" size="sm" onClick={() => setSelectedRule(null)}>
              Close Rule Details
            </Button>
          }
        >
          <div className="space-y-4 text-xs">
            {/* Full Statutory Text */}
            <div className="p-3 bg-slate-50 border border-slate-200 rounded space-y-1">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Statutory Rule Language:
              </span>
              <p className="text-slate-900 text-xs leading-relaxed">
                {selectedRule.requirement}
              </p>
            </div>

            {/* Prescribed Parameters */}
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Prescribed Implementation Standards:
              </span>
              <p className="text-slate-800 mt-1 leading-relaxed">
                {selectedRule.prescribedParameters}
              </p>
            </div>

            {/* Font Height Table if applicable */}
            {selectedRule.fontTable && (
              <div className="space-y-1.5 pt-1">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                  Mandatory Numeral & Letter Height Schedule Table (Rule 7 & 8):
                </span>
                <table className="w-full text-left text-xs border border-slate-300 border-collapse">
                  <thead className="bg-slate-100 text-slate-900 font-bold border-b border-slate-300 text-[11px]">
                    <tr>
                      <th className="p-2 border-r border-slate-200">Area of Principal Display Panel (A)</th>
                      <th className="p-2 border-r border-slate-200">Standard Packages</th>
                      <th className="p-2">Blow Moulded / Perforated</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white">
                    {selectedRule.fontTable.map((row, idx) => (
                      <tr key={idx}>
                        <td className="p-2 border-r border-slate-200 font-medium">{row.area}</td>
                        <td className="p-2 border-r border-slate-200 font-mono text-emerald-800 font-bold">{row.minHeightNormal}</td>
                        <td className="p-2 font-mono text-slate-700">{row.minHeightBlowMoulded}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Officer Enforcement Guidance */}
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded text-emerald-950 space-y-1">
              <span className="font-bold flex items-center">
                <FileCheck className="w-4 h-4 mr-1 text-emerald-700" />
                Enforcement Officer Inspection Directive:
              </span>
              <p className="text-[11px] leading-relaxed">
                {selectedRule.officerGuidance}
              </p>
            </div>

            {/* Penal Provision */}
            <div className="p-3 bg-red-50 border border-red-200 rounded text-red-950 space-y-1">
              <span className="font-bold flex items-center">
                <Scale className="w-4 h-4 mr-1 text-red-700" />
                Penal Liability upon Default:
              </span>
              <p className="text-[11px] font-mono leading-relaxed text-red-900">
                {selectedRule.penalProvision}
              </p>
            </div>

            <div className="text-[10px] text-slate-400 font-mono pt-1">
              Source Reference: {selectedRule.source} • Last Updated: {selectedRule.lastUpdated}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
