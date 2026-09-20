import React, { useState, useMemo } from 'react';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import {
  BookOpen,
  Search,
  Filter,
  FileCheck,
  Scale,
  ExternalLink,
  ChevronRight,
  Info,
  Shield
} from 'lucide-react';
import { LEGAL_RULES } from '../data/mockRules';
import { LegalRuleItem } from '../types';

export const RuleLibraryPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [selectedRule, setSelectedRule] = useState<LegalRuleItem | null>(null);
  const [focusedRuleId, setFocusedRuleId] = useState<string | null>(null);

  const categories = useMemo(() => {
    return Array.from(new Set(LEGAL_RULES.map((r: LegalRuleItem) => r.category)));
  }, []);

  const filteredRules = useMemo(() => {
    return LEGAL_RULES.filter((r: LegalRuleItem) => {
      const matchesSearch =
        searchTerm === '' ||
        r.ruleNo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.applicableDeclaration.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.requirement.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesCat = categoryFilter === 'ALL' || r.category === categoryFilter;
      return matchesSearch && matchesCat;
    });
  }, [searchTerm, categoryFilter]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E5E2DD] pb-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-[#1F2328] tracking-tight">
            Legal Metrology Rules Repository
          </h1>
          <p className="text-xs text-[#5F6368] mt-0.5">
            Legal Metrology (Packaged Commodities) Rules, 2011 codified statutory rule base.
          </p>
        </div>
        <div className="text-xs font-mono text-[#5F6368] bg-white border border-[#E5E2DD] px-3 py-1.5 rounded-lg shadow-2xs">
          Active Clauses: <strong className="text-[#1F2328]">{LEGAL_RULES.length}</strong>
        </div>
      </div>

      {/* Filter Toolbar */}
      <Card>
        <CardContent className="p-4 space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="relative md:col-span-2">
              <Search className="w-4 h-4 text-[#8A8F98] absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by Rule No. (e.g. Rule 6), Title, Keyword, or Declaration..."
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg pl-9 pr-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED]"
              />
            </div>
            <div>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED] cursor-pointer"
              >
                <option value="ALL">All Rule Categories</option>
                {categories.map((cat: string) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Clean Modern Rule Cards Grid (Click-to-Focus / Zoom) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredRules.map((rule: LegalRuleItem) => {
          const isFocused = focusedRuleId === rule.id;
          return (
            <div
              key={rule.id}
              className={`bg-white border rounded-xl p-5 shadow-2xs flex flex-col justify-between group cursor-pointer select-none transition-all duration-250 ease-out ${
                isFocused
                  ? 'scale-[1.03] shadow-md border-[#7C3AED] ring-2 ring-[#7C3AED]/30 z-10'
                  : 'border-[#E5E2DD] hover:border-[#D8D4CE]'
              }`}
              onClick={() => {
                if (focusedRuleId === rule.id) {
                  setSelectedRule(rule);
                } else {
                  setFocusedRuleId(rule.id);
                }
              }}
              title="Click once to focus, click again to view full rule details"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-[#6D28D9] bg-[#F5F3FF] px-2.5 py-0.5 rounded-md border border-[#DDD6FE]">
                    {rule.ruleNo}
                  </span>
                  <span className="text-[11px] text-[#8A8F98] bg-[#FAF9F7] px-2 py-0.5 rounded-md border border-[#E5E2DD]">
                    {rule.category}
                  </span>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-[#1F2328] group-hover:text-[#6D28D9] transition-colors line-clamp-1">
                    {rule.title}
                  </h3>
                  <p className="text-[11px] text-[#8A8F98] mt-0.5 font-mono">
                    {rule.subRule}
                  </p>
                </div>

                <div className="p-2.5 bg-[#FAF9F7] border border-[#E5E2DD]/80 rounded-lg text-xs space-y-1">
                  <span className="text-[10px] font-semibold text-[#8A8F98] uppercase tracking-wider block">
                    Applicable Condition
                  </span>
                  <span className="font-medium text-[#1F2328] text-[11.5px] block truncate">
                    {rule.applicableDeclaration}
                  </span>
                </div>

                <p className="text-xs text-[#5F6368] line-clamp-2 leading-relaxed">
                  {rule.requirement}
                </p>
              </div>

              <div className="pt-3.5 mt-3 border-t border-[#F0EDE8] flex items-center justify-between text-xs">
                <span className="text-[11px] text-[#8A8F98]">
                  Updated: {rule.lastUpdated}
                </span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedRule(rule);
                  }}
                  className="text-xs font-semibold text-[#6D28D9] group-hover:underline flex items-center space-x-1 cursor-pointer"
                >
                  <span>View Logic</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

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
            <div className="p-3.5 bg-[#FAF9F7] border border-[#E5E2DD] rounded-xl space-y-1">
              <span className="text-[10px] font-bold text-[#8A8F98] uppercase tracking-wider block">
                Statutory Rule Language:
              </span>
              <p className="text-[#1F2328] text-xs leading-relaxed">
                {selectedRule.requirement}
              </p>
            </div>

            {/* Prescribed Parameters */}
            <div>
              <span className="text-[10px] font-bold text-[#8A8F98] uppercase tracking-wider block">
                Prescribed Implementation Standards:
              </span>
              <p className="text-[#1F2328] mt-1 leading-relaxed">
                {selectedRule.prescribedParameters}
              </p>
            </div>

            {/* Officer Enforcement Guidance */}
            <div className="p-3.5 bg-[#F0FDF4] border border-[#BBF7D0] rounded-xl text-[#16A34A] space-y-1">
              <span className="font-bold flex items-center">
                <FileCheck className="w-4 h-4 mr-1 text-[#16A34A]" />
                Enforcement Officer Inspection Directive:
              </span>
              <p className="text-[11px] leading-relaxed text-[#1F2328]">
                {selectedRule.officerGuidance}
              </p>
            </div>

            {/* Penal Provision */}
            <div className="p-3.5 bg-[#FEF2F2] border border-[#FECACA] rounded-xl text-[#DC2626] space-y-1">
              <span className="font-bold flex items-center">
                <Scale className="w-4 h-4 mr-1 text-[#DC2626]" />
                Penal Liability upon Default:
              </span>
              <p className="text-[11px] font-mono leading-relaxed text-[#DC2626]">
                {selectedRule.penalProvision}
              </p>
            </div>

            <div className="text-[10px] text-[#8A8F98] font-mono pt-1">
              Source Reference: {selectedRule.source} • Last Updated: {selectedRule.lastUpdated}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
