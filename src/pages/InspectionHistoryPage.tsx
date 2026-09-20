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
  ChevronRight,
  Download
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E5E2DD] pb-4">
        <div>
          <h1 className="text-2xl font-bold text-[#1F2328] tracking-tight">Inspections Registry</h1>
          <p className="text-xs text-[#5F6368] mt-0.5">
            Comprehensive archive of statutory inspections conducted under Legal Metrology Rules, 2011
          </p>
        </div>
        <div className="text-xs font-mono text-[#5F6368] bg-white border border-[#E5E2DD] px-3 py-1.5 rounded-lg shadow-2xs">
          Total Recorded: <strong className="text-[#1F2328]">{inspections.length}</strong> dockets
        </div>
      </div>

      {/* Filter Controls Card */}
      <Card>
        <CardContent className="p-4 space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            {/* Search */}
            <div className="relative md:col-span-2">
              <Search className="w-4 h-4 text-[#8A8F98] absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                placeholder="Search by Docket ID, Product Name, Brand, or Manufacturer..."
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg pl-9 pr-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED]"
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
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED] cursor-pointer"
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
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED] cursor-pointer"
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

          <div className="flex items-center justify-between pt-1 text-xs text-[#5F6368]">
            <span>
              Showing {filteredInspections.length} result(s)
            </span>
            <button
              onClick={resetFilters}
              className="text-xs text-[#6D28D9] hover:underline flex items-center space-x-1 cursor-pointer font-medium"
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
          <table className="w-full text-left text-xs text-[#1F2328] border-collapse">
            <thead className="bg-[#FAF9F7] border-b border-[#E5E2DD] text-[11px] font-bold text-[#5F6368] uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Docket ID</th>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Product Name</th>
                <th className="py-3 px-4">Inspecting Officer</th>
                <th className="py-3 px-4">Location / Premise</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-center">Violations</th>
                <th className="py-3 px-4 text-right">Official Report</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F0EDE8] bg-white">
              {paginatedInspections.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center p-8 text-[#8A8F98] text-xs">
                    No inspection records found matching the specified filters.
                  </td>
                </tr>
              ) : (
                paginatedInspections.map((insp) => (
                  <tr key={insp.id} className="hover:bg-[#FAF9F7] transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-[#1F2328]">
                      {insp.id}
                    </td>
                    <td className="py-3.5 px-4 text-[#5F6368] font-mono">
                      {insp.date}
                    </td>
                    <td className="py-3.5 px-4">
                      <div>
                        <span className="font-semibold text-[#1F2328] block max-w-[200px] truncate">
                          {insp.productName}
                        </span>
                        <span className="text-[11px] text-[#8A8F98] block max-w-[180px] truncate">
                          {insp.manufacturer}
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-[#5F6368]">
                      {insp.officerName}
                    </td>
                    <td className="py-3.5 px-4 text-[#5F6368] max-w-[180px] truncate">
                      {insp.location}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={insp.status} />
                    </td>
                    <td className="py-3.5 px-4 text-center font-mono font-bold">
                      {insp.violations.length > 0 ? (
                        <span className="text-[#DC2626] bg-[#FEF2F2] px-2 py-0.5 rounded-md border border-[#FECACA]">
                          {insp.violations.length}
                        </span>
                      ) : (
                        <span className="text-[#16A34A]">0</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Button
                        variant="secondary"
                        size="sm"
                        leftIcon={<FileText className="w-3.5 h-3.5 text-[#5F6368]" />}
                        onClick={() => navigate(`/reports/${insp.id}`)}
                      >
                        View Report
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="p-3.5 border-t border-[#E5E2DD] bg-[#FAF9F7] flex items-center justify-between text-xs text-[#5F6368] rounded-b-xl">
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <div className="flex items-center space-x-1.5">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded-lg border border-[#E5E2DD] bg-white hover:bg-[#FAF9F7] disabled:opacity-50 disabled:cursor-not-allowed transition cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded-lg border border-[#E5E2DD] bg-white hover:bg-[#FAF9F7] disabled:opacity-50 disabled:cursor-not-allowed transition cursor-pointer"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
};
