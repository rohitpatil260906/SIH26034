import React, { useState, useMemo } from 'react';
import { useInspection } from '../context/InspectionContext';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { StatusBadge } from '../components/ui/Badge';
import {
  Search,
  Filter,
  Calendar,
  User,
  MapPin,
  Eye,
  FileText,
  RotateCcw,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { InspectionStatus } from '../types';

export const InspectionHistoryPage: React.FC = () => {
  const { inspections } = useInspection();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Search and filter states
  const initialSearch = searchParams.get('search') || '';
  const [searchTerm, setSearchTerm] = useState(initialSearch);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [officerFilter, setOfficerFilter] = useState<string>('ALL');

  // Pagination
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 8;

  // Filter logic
  const filteredInspections = useMemo(() => {
    return inspections.filter(insp => {
      const matchesSearch =
        searchTerm === '' ||
        insp.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        insp.productName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        insp.brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
        insp.manufacturer.toLowerCase().includes(searchTerm.toLowerCase()) ||
        insp.barcode.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStatus = statusFilter === 'ALL' || insp.status === statusFilter;
      const matchesCategory = categoryFilter === 'ALL' || insp.category === categoryFilter;
      const matchesOfficer = officerFilter === 'ALL' || insp.officerName.includes(officerFilter);

      return matchesSearch && matchesStatus && matchesCategory && matchesOfficer;
    });
  }, [inspections, searchTerm, statusFilter, categoryFilter, officerFilter]);

  const totalPages = Math.ceil(filteredInspections.length / itemsPerPage) || 1;
  const paginatedInspections = filteredInspections.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const resetFilters = () => {
    setSearchTerm('');
    setStatusFilter('ALL');
    setCategoryFilter('ALL');
    setOfficerFilter('ALL');
    setCurrentPage(1);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Inspections Registry</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Comprehensive archive of statutory inspections conducted under Legal Metrology Rules, 2011
          </p>
        </div>
        <div className="text-xs font-mono text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded">
          Total Recorded: <strong>{inspections.length}</strong> dockets
        </div>
      </div>

      {/* Filter Controls Card */}
      <Card>
        <CardContent className="p-4 space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            {/* Search */}
            <div className="relative md:col-span-2">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                placeholder="Search by Docket ID, Product Name, Brand, or Manufacturer..."
                className="w-full bg-slate-50 border border-slate-300 rounded pl-9 pr-3 py-1.5 text-xs text-slate-900 focus:bg-white focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              />
            </div>

            {/* Status Filter */}
            <div>
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:outline-none"
              >
                <option value="ALL">All Compliance Statuses</option>
                <option value="Compliant">Compliant</option>
                <option value="Non-Compliant">Non-Compliant</option>
                <option value="Under Review">Under Review</option>
              </select>
            </div>

            {/* Category Filter */}
            <div>
              <select
                value={categoryFilter}
                onChange={(e) => {
                  setCategoryFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:outline-none"
              >
                <option value="ALL">All Product Categories</option>
                <option value="Edible Oils & Fats">Edible Oils & Fats</option>
                <option value="Food & Grains">Food & Grains</option>
                <option value="Food & Beverages">Food & Beverages</option>
                <option value="Food & Spices">Food & Spices</option>
                <option value="Personal Care & Cosmetics">Personal Care & Cosmetics</option>
                <option value="Household Chemicals">Household Chemicals</option>
                <option value="Consumer Electronics">Consumer Electronics</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-between pt-1 text-xs text-slate-500">
            <span>
              Showing {filteredInspections.length} result(s)
            </span>
            <button
              onClick={resetFilters}
              className="text-xs text-[#0f2942] hover:underline flex items-center space-x-1"
            >
              <RotateCcw className="w-3 h-3 mr-1" />
              Reset All Filters
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Main Table Card */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-800 border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-3">Docket ID</th>
                <th className="py-3 px-3">Date</th>
                <th className="py-3 px-3">Product Name</th>
                <th className="py-3 px-3">Inspecting Officer</th>
                <th className="py-3 px-3">Location / Premise</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3 text-center">Violations</th>
                <th className="py-3 px-3 text-right">Official Report</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {paginatedInspections.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center p-8 text-slate-500 text-xs">
                    No inspection records found matching the specified filters.
                  </td>
                </tr>
              ) : (
                paginatedInspections.map((insp) => (
                  <tr key={insp.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-3 font-mono font-bold text-slate-900">
                      {insp.id}
                    </td>
                    <td className="py-3 px-3 text-slate-600 font-mono">
                      {insp.date}
                    </td>
                    <td className="py-3 px-3">
                      <div>
                        <span className="font-semibold text-slate-900 block max-w-[200px] truncate">
                          {insp.productName}
                        </span>
                        <span className="text-[10px] text-slate-400 block max-w-[180px] truncate">
                          {insp.manufacturer}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-slate-700">
                      {insp.officerName}
                    </td>
                    <td className="py-3 px-3 text-slate-600 max-w-[180px] truncate">
                      {insp.location}
                    </td>
                    <td className="py-3 px-3">
                      <StatusBadge status={insp.status} />
                    </td>
                    <td className="py-3 px-3 text-center font-mono font-bold">
                      {insp.violations.length > 0 ? (
                        <span className="text-red-700 bg-red-50 px-2 py-0.5 rounded border border-red-200">
                          {insp.violations.length}
                        </span>
                      ) : (
                        <span className="text-emerald-700">0</span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        leftIcon={<FileText className="w-3.5 h-3.5 text-[#0f2942]" />}
                        onClick={() => navigate(`/reports/${insp.id}`)}
                      >
                        Report
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="p-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-600">
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
};
