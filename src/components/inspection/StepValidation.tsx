import React, { useState, useMemo } from 'react';
import { useInspection } from '../../context/InspectionContext';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Modal } from '../ui/Modal';
import { LEGAL_RULES } from '../../data/mockRules';
import { LegalRuleItem, ComplianceCheckItem, StructuredProductData } from '../../types';
import { evaluateLegalMetrologyRules, classifyProduct } from '../../services/ruleEngineService';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowRight,
  ArrowLeft,
  Scale,
  Search,
  BookOpen,
  Info,
  Layers,
  ListChecks,
  FileText,
  Gavel,
  Eye,
  ShieldCheck,
  Tag,
  Filter
} from 'lucide-react';

type AuditTab = 'rules-matrix' | 'declarations' | 'lines';

export const StepValidation: React.FC = () => {
  const { currentInspection, setActiveStep } = useInspection();

  const [activeTab, setActiveTab] = useState<AuditTab>('rules-matrix');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [inspectingCheck, setInspectingCheck] = useState<ComplianceCheckItem | null>(null);
  const [focusedCard, setFocusedCard] = useState<number | null>(null);

  if (!currentInspection) return null;

  const structuredData: StructuredProductData = currentInspection.structuredData || {
    product_name: currentInspection.productName,
    commodity_name: currentInspection.category || 'Packaged Commodity',
    manufacturer: { name: currentInspection.manufacturer, address: currentInspection.manufacturer },
    packer: { name: '', address: '' },
    importer: { name: '', address: '' },
    net_quantity: '56 g',
    mrp: '₹ 499 (incl. of all taxes)',
    unit_sale_price: '₹ 8.91/g',
    batch_number: currentInspection.batchNumber || 'BATCH-001',
    manufacturing_date: '02/2026',
    packing_date: '',
    import_date: '',
    expiry_or_best_before: '01/2028',
    consumer_care: { phone: '1800-10-22-221', email: 'care@brand.in', address: currentInspection.manufacturer },
    country_of_origin: 'India',
    other_declarations: []
  };

  const rawDecs = currentInspection.declarations || [];

  // Run dynamic classification and rule evaluation
  const evaluationResult = useMemo(() => {
    return evaluateLegalMetrologyRules(
      structuredData,
      rawDecs,
      currentInspection.category || 'General Packaged Commodity',
      structuredData.classification
    );
  }, [structuredData, rawDecs, currentInspection.category]);

  const classification = evaluationResult.classification;
  const checks = evaluationResult.checks;

  // Counts
  const passCount = checks.filter(c => c.status === 'PASS').length;
  const failCount = checks.filter(c => c.status === 'FAIL').length;
  const reviewCount = checks.filter(c => c.status === 'NEEDS REVIEW' || c.status === 'UNREADABLE').length;
  const notApplicableCount = checks.filter(c => c.status === 'NOT APPLICABLE').length;
  const applicableCount = checks.filter(c => c.isApplicable).length;

  const categories = useMemo(() => {
    return Array.from(new Set(LEGAL_RULES.map(r => r.category)));
  }, []);

  // Filtered checks
  const filteredChecks = useMemo(() => {
    return checks.filter(check => {
      const rule = LEGAL_RULES.find(r => r.id === check.ruleId);
      const matchesCategory = categoryFilter === 'ALL' || (rule && rule.category === categoryFilter);

      let matchesStatus = true;
      if (statusFilter === 'PASS') matchesStatus = check.status === 'PASS';
      if (statusFilter === 'FAIL') matchesStatus = check.status === 'FAIL';
      if (statusFilter === 'NEEDS_REVIEW') matchesStatus = check.status === 'NEEDS REVIEW' || check.status === 'UNREADABLE';
      if (statusFilter === 'NOT_APPLICABLE') matchesStatus = check.status === 'NOT APPLICABLE';

      const searchLower = searchTerm.toLowerCase();
      const matchesSearch =
        searchTerm === '' ||
        check.ruleNo.toLowerCase().includes(searchLower) ||
        check.subRule.toLowerCase().includes(searchLower) ||
        check.requirement.toLowerCase().includes(searchLower) ||
        check.detectedInfo.toLowerCase().includes(searchLower) ||
        (check.applicabilityReason && check.applicabilityReason.toLowerCase().includes(searchLower)) ||
        (rule && rule.title.toLowerCase().includes(searchLower));

      return matchesCategory && matchesStatus && matchesSearch;
    });
  }, [checks, categoryFilter, statusFilter, searchTerm]);

  return (
    <div className="space-y-6">
      {/* Statutory Enforcement & Classification Banner */}
      <div className="bg-[#0f2942] text-white rounded-lg p-4 shadow-md border border-slate-700 space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start space-x-3">
            <Scale className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-bold text-amber-300 tracking-wide uppercase text-[11px]">
                Dynamic Statutory Legal Metrology Rules Engine (Rules 1 to 34)
              </h4>
              <p className="mt-0.5 text-slate-200 text-xs leading-relaxed">
                Rules are evaluated dynamically based on product classification, net quantity threshold, standard pack size schedules, and origin. No blind or generic checklists are used.
              </p>
            </div>
          </div>
          <span className="text-xs font-mono font-bold bg-amber-400/20 text-amber-300 border border-amber-400/40 px-2.5 py-1 rounded shrink-0">
            {evaluationResult.complianceScore}% Statutory Score
          </span>
        </div>

        {/* Classification Tags */}
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-700/80 text-[11px]">
          <span className="text-slate-400 flex items-center space-x-1">
            <Tag className="w-3 h-3 text-amber-400" />
            <span>Product Class:</span>
          </span>
          <span className="bg-slate-800 text-amber-300 font-semibold px-2 py-0.5 rounded border border-slate-700 font-mono">
            {classification.productType}
          </span>
          <span className={`px-2 py-0.5 rounded font-mono ${classification.isImported ? 'bg-purple-900 text-purple-200' : 'bg-slate-800 text-slate-300'}`}>
            {classification.isImported ? 'Imported Package (Rule 27)' : 'Domestic Manufacture (India)'}
          </span>
          <span className={`px-2 py-0.5 rounded font-mono ${classification.isScheduledCommodity ? 'bg-amber-900 text-amber-200' : 'bg-slate-800 text-slate-400'}`}>
            {classification.isScheduledCommodity ? 'Second Schedule Commodity' : 'Non-Scheduled Commodity'}
          </span>
          <span className={`px-2 py-0.5 rounded font-mono ${classification.isPerishable ? 'bg-blue-900 text-blue-200' : 'bg-slate-800 text-slate-400'}`}>
            {classification.isPerishable ? 'Perishable / Expiry Mandated' : 'Non-Perishable'}
          </span>
          <span className="bg-slate-800 text-slate-400 px-2 py-0.5 rounded font-mono">
            PDP Area: {Math.round(classification.pdpAreaCm2 || 120)} cm²
          </span>
        </div>
      </div>

      {/* Compliance Assessment KPI Summary Cards (Click-to-Focus / Zoom) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3.5">
        {[
          {
            id: 0,
            label: 'Compliance Score',
            value: `${evaluationResult.complianceScore}%`,
            valueColor: evaluationResult.complianceScore >= 90 ? 'text-emerald-700' : evaluationResult.complianceScore >= 70 ? 'text-amber-600' : 'text-red-700',
            icon: Scale,
            iconColor: 'text-[#6D28D9]',
          },
          {
            id: 1,
            label: 'Applicable Rules',
            value: `${applicableCount}`,
            suffix: '/ 34',
            valueColor: 'text-slate-900',
            icon: BookOpen,
            iconColor: 'text-slate-400',
          },
          {
            id: 2,
            label: 'Compliant (PASS)',
            value: `${passCount}`,
            valueColor: 'text-emerald-700',
            icon: CheckCircle2,
            iconColor: 'text-emerald-600',
          },
          {
            id: 3,
            label: 'Statutory Infractions',
            value: `${failCount}`,
            valueColor: 'text-red-700',
            icon: XCircle,
            iconColor: 'text-red-600',
          },
          {
            id: 4,
            label: 'Exempt / Not Applicable',
            value: `${notApplicableCount}`,
            valueColor: 'text-slate-600',
            icon: ShieldCheck,
            iconColor: 'text-slate-400',
          },
        ].map((card) => {
          const isFocused = focusedCard === card.id;
          const Icon = card.icon;
          return (
            <div
              key={card.id}
              onClick={() => setFocusedCard(isFocused ? null : card.id)}
              className={`bg-white border rounded-md p-3.5 flex items-center justify-between cursor-pointer select-none transition-all duration-250 ease-out ${
                isFocused
                  ? 'scale-[1.04] shadow-md border-[#7C3AED] ring-2 ring-[#7C3AED]/30 z-10'
                  : 'border-slate-200 hover:border-slate-300 hover:shadow-2xs'
              }`}
              title="Click to focus card"
            >
              <div>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">{card.label}</span>
                <span className={`text-xl font-bold mt-0.5 block ${card.valueColor}`}>
                  {card.value} {card.suffix && <span className="text-xs text-slate-400 font-normal">{card.suffix}</span>}
                </span>
              </div>
              <Icon className={`w-6 h-6 ${card.iconColor}`} />
            </div>
          );
        })}
      </div>

      {/* Tab Switcher Header */}
      <div className="flex border-b border-slate-200 bg-white rounded-t-lg px-2 pt-2 space-x-2">
        <button
          type="button"
          onClick={() => setActiveTab('rules-matrix')}
          className={`flex items-center space-x-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition cursor-pointer ${
            activeTab === 'rules-matrix'
              ? 'border-[#7C3AED] text-[#6D28D9] bg-[#F5F3FF]'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          <ListChecks className="w-4 h-4 text-emerald-700" />
          <span>Statutory Rules Compliance Matrix (Rules 1–34)</span>
          <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-mono font-bold">
            {checks.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('declarations')}
          className={`flex items-center space-x-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition cursor-pointer ${
            activeTab === 'declarations'
              ? 'border-[#7C3AED] text-[#6D28D9] bg-[#F5F3FF]'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          <Layers className="w-4 h-4 text-amber-700" />
          <span>Extracted Declarations</span>
          <span className="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded font-mono font-bold">
            {rawDecs.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('lines')}
          className={`flex items-center space-x-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition cursor-pointer ${
            activeTab === 'lines'
              ? 'border-[#7C3AED] text-[#6D28D9] bg-[#F5F3FF]'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          <FileText className="w-4 h-4 text-blue-700" />
          <span>Line-by-Line Optical Text Traceability</span>
          <span className="text-[10px] bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded font-mono font-bold">
            {currentInspection.extractedLines?.length || 0}
          </span>
        </button>
      </div>

      {/* TAB 1: RULES MATRIX */}
      {activeTab === 'rules-matrix' && (
        <div className="space-y-4">
          {/* Filter Bar */}
          <Card>
            <CardContent className="p-3.5 space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
                <div className="relative md:col-span-6">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search rule (e.g., 'MRP', 'Net Quantity', 'PIN', 'Rule 6', 'Rule 32A')..."
                    className="w-full bg-slate-50 border border-slate-300 rounded pl-9 pr-3 py-1.5 text-xs text-slate-900 focus:bg-white focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
                  />
                </div>

                <div className="md:col-span-3">
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:outline-none"
                  >
                    <option value="ALL">All Statuses ({checks.length})</option>
                    <option value="PASS">Pass / Compliant ({passCount})</option>
                    <option value="FAIL">Statutory Infractions ({failCount})</option>
                    <option value="NEEDS_REVIEW">Needs Review / Unreadable ({reviewCount})</option>
                    <option value="NOT_APPLICABLE">Exempt / Not Applicable ({notApplicableCount})</option>
                  </select>
                </div>

                <div className="md:col-span-3">
                  <select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:outline-none"
                  >
                    <option value="ALL">All Categories</option>
                    {categories.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Rules Table */}
          <Card>
            <CardHeader
              title={`Statutory Evaluation Matrix • ${currentInspection.productName}`}
              subtitle="Statutory verification of Legal Metrology (Packaged Commodities) Rules, 2011"
              action={
                <span className="text-xs font-mono text-slate-600 bg-slate-100 px-2.5 py-1 rounded border border-slate-300">
                  {filteredChecks.length} of {checks.length} Rules Shown
                </span>
              }
            />

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-800 border-collapse">
                <thead className="bg-slate-100/80 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                  <tr>
                    <th className="py-2.5 px-4">Statutory Clause</th>
                    <th className="py-2.5 px-4">Requirement Under Law</th>
                    <th className="py-2.5 px-4">Packaging Finding & Compliance Note</th>
                    <th className="py-2.5 px-4">Status</th>
                    <th className="py-2.5 px-4 text-center">Audit Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {filteredChecks.map((check) => {
                    const rule = LEGAL_RULES.find(r => r.id === check.ruleId);
                    const isPass = check.status === 'PASS';
                    const isFail = check.status === 'FAIL';
                    const isReview = check.status === 'NEEDS REVIEW' || check.status === 'UNREADABLE';
                    const isNotApplicable = check.status === 'NOT APPLICABLE';

                    return (
                      <tr
                        key={check.ruleId}
                        className={`hover:bg-slate-50/80 transition ${
                          isFail ? 'bg-red-50/30' : isReview ? 'bg-amber-50/20' : ''
                        }`}
                      >
                        {/* Statutory Clause */}
                        <td className="py-3 px-4 max-w-[180px]">
                          <div className="space-y-0.5">
                            <span className="font-bold text-slate-900 block font-mono">
                              {check.ruleNo}
                            </span>
                            <span className="text-[10px] text-slate-600 block">
                              {check.subRule}
                            </span>
                            {rule && (
                              <span className="text-[10px] text-slate-400 block font-mono">
                                {rule.category}
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Requirement Under Law */}
                        <td className="py-3 px-4 max-w-xs text-slate-700 leading-normal">
                          {check.requirement}
                        </td>

                        {/* Packaging Finding & Applicability */}
                        <td className="py-3 px-4 max-w-sm">
                          <div className="space-y-1">
                            <span className={`block font-medium ${
                              isFail ? 'text-red-700 font-bold' : isReview ? 'text-amber-800' : 'text-slate-900'
                            }`}>
                              {check.detectedInfo}
                            </span>
                            {check.applicabilityReason && isNotApplicable && (
                              <span className="inline-block text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
                                {check.applicabilityReason}
                              </span>
                            )}
                            {check.evidenceSource && (
                              <span className="block text-[10px] text-emerald-700 font-mono">
                                Evidence: {check.evidenceSource}
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Status Badge */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          {isPass && (
                            <span className="inline-flex items-center text-[10px] font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                              <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" /> Compliant
                            </span>
                          )}
                          {isFail && (
                            <span className="inline-flex items-center text-[10px] font-bold text-red-800 bg-red-50 px-2 py-0.5 rounded border border-red-200">
                              <XCircle className="w-3 h-3 mr-1 text-red-600" /> Infraction
                            </span>
                          )}
                          {isReview && (
                            <span className="inline-flex items-center text-[10px] font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                              <AlertTriangle className="w-3 h-3 mr-1 text-amber-600" /> Review
                            </span>
                          )}
                          {isNotApplicable && (
                            <span className="inline-flex items-center text-[10px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                              Not Applicable
                            </span>
                          )}
                        </td>

                        {/* Action */}
                        <td className="py-3 px-4 text-center whitespace-nowrap">
                          <button
                            type="button"
                            onClick={() => setInspectingCheck(check)}
                            className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] font-semibold transition flex items-center justify-center space-x-1 mx-auto"
                            title="Inspect Statutory Clause Details"
                          >
                            <Eye className="w-3 h-3" />
                            <span>Inspect</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* TAB 2: DECLARATIONS */}
      {activeTab === 'declarations' && (
        <Card>
          <CardHeader
            title="Mandatory Declarations Audit"
            subtitle="Review of statutory label declarations extracted from packaging surfaces"
          />
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-800 border-collapse">
              <thead className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-4">Declaration Item</th>
                  <th className="py-2.5 px-4">Extracted Value</th>
                  <th className="py-2.5 px-4">Statutory Reference</th>
                  <th className="py-2.5 px-4">Surface</th>
                  <th className="py-2.5 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {rawDecs.map(dec => (
                  <tr key={dec.id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-4 font-semibold text-slate-900">{dec.declarationType}</td>
                    <td className="py-2.5 px-4 font-mono">{dec.extractedValue}</td>
                    <td className="py-2.5 px-4 font-mono text-slate-600">{dec.ruleReference}</td>
                    <td className="py-2.5 px-4 font-mono text-slate-600">{dec.surface}</td>
                    <td className="py-2.5 px-4">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        dec.status === 'Found' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {dec.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* TAB 3: EXTRACTED LINES */}
      {activeTab === 'lines' && (
        <Card>
          <CardHeader
            title="Line-by-Line Packaging Optical Scan"
            subtitle="Verbatim optical detection of every printed label line mapped to statutory classifications"
          />
          <CardContent className="p-0">
            <div className="max-h-96 overflow-y-auto divide-y divide-slate-100">
              {currentInspection.extractedLines?.map((line) => (
                <div key={line.lineNumber} className="py-2 px-4 flex items-center justify-between text-xs hover:bg-slate-50 transition">
                  <div className="flex items-center space-x-3 min-w-0 pr-4">
                    <span className="text-[10px] font-mono font-bold text-slate-400 shrink-0 w-8">
                      L{String(line.lineNumber).padStart(2, '0')}
                    </span>
                    <span className="font-mono text-slate-900 font-medium select-all truncate">
                      {line.text}
                    </span>
                  </div>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded font-mono ${
                    line.status === 'Compliant' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'
                  }`}>
                    {line.status}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Inspect Rule Modal */}
      {inspectingCheck && (
        <Modal
          isOpen={true}
          onClose={() => setInspectingCheck(null)}
          title={`${inspectingCheck.ruleNo}: ${inspectingCheck.subRule}`}
          subtitle="Statutory legal provision and packaging evidence audit"
          footer={
            <Button variant="outline" size="sm" onClick={() => setInspectingCheck(null)}>
              Close
            </Button>
          }
        >
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-slate-50 rounded border border-slate-200 space-y-1">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-bold">
                Statutory Requirement Under Legal Metrology Rules:
              </span>
              <p className="text-slate-800 leading-relaxed font-medium">
                {inspectingCheck.requirement}
              </p>
            </div>

            <div className="p-3 bg-white rounded border border-slate-200 space-y-1">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-bold">
                Packaging Audit Finding:
              </span>
              <p className="text-slate-900 font-mono text-xs leading-relaxed">
                {inspectingCheck.detectedInfo}
              </p>
            </div>

            {inspectingCheck.applicabilityReason && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded text-blue-900 space-y-1">
                <span className="text-[10px] uppercase font-bold text-blue-700 block">
                  Applicability / Exemption Justification:
                </span>
                <p className="text-xs leading-relaxed">
                  {inspectingCheck.applicabilityReason}
                </p>
              </div>
            )}

            <div className="p-3 bg-slate-900 text-slate-200 rounded border border-slate-800 space-y-1 text-[11px]">
              <div className="flex items-center space-x-1.5 text-amber-400 font-semibold">
                <Gavel className="w-3.5 h-3.5" />
                <span>Statutory Adjudication Provision & Penal Schedule:</span>
              </div>
              <p className="text-slate-300 leading-relaxed">
                Contraventions attract prosecution under Section 36(1) of the Legal Metrology Act, 2009.
                Rule 32A prescribes compounding fees up to ₹25,000 for the first offence and ₹50,000 for subsequent offences.
              </p>
            </div>
          </div>
        </Modal>
      )}

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-2">
        <Button
          type="button"
          variant="outline"
          size="md"
          leftIcon={<ArrowLeft className="w-4 h-4" />}
          onClick={() => setActiveStep(4)}
        >
          Back to Declarations
        </Button>

        <Button
          type="button"
          variant="primary"
          size="md"
          rightIcon={<ArrowRight className="w-4 h-4" />}
          onClick={() => setActiveStep(6)}
        >
          Continue to Violations & Actions
        </Button>
      </div>
    </div>
  );
};
