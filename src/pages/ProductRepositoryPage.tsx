import React, { useState, useMemo } from 'react';
import { useInspection } from '../context/InspectionContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { StatusBadge } from '../components/ui/Badge';
import {
  Package,
  Search,
  Filter,
  Eye,
  Plus,
  ArrowRight,
  ExternalLink,
  RotateCcw,
  Camera
} from 'lucide-react';
import { InspectionStatus } from '../types';

export const ProductRepositoryPage: React.FC = () => {
  const { inspections, startNewInspection, updateInspectionDetails } = useInspection();
  const navigate = useNavigate();

  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Derive unique product catalogue from inspections
  const products = useMemo(() => {
    const map = new Map<string, {
      id: string;
      name: string;
      barcode: string;
      brand: string;
      category: string;
      manufacturer: string;
      standardQuantity: string;
      lastInspectionDate: string;
      complianceStatus: InspectionStatus;
      totalViolations: number;
      lastInspectionId?: string;
    }>();

    inspections.forEach(insp => {
      const key = insp.barcode || insp.productName;
      const existing = map.get(key);

      if (!existing) {
        map.set(key, {
          id: insp.id,
          name: insp.productName,
          barcode: insp.barcode,
          brand: insp.brand,
          category: insp.category,
          manufacturer: insp.manufacturer,
          standardQuantity: (insp as any).standardQuantity || insp.structuredData?.net_quantity || '',
          lastInspectionDate: insp.date,
          complianceStatus: insp.status,
          totalViolations: insp.violations.length,
          lastInspectionId: insp.id
        });
      } else {
        existing.totalViolations += insp.violations.length;
      }
    });

    return Array.from(map.values());
  }, [inspections]);

  const filteredProducts = useMemo(() => {
    return products.filter(p => {
      const matchesSearch =
        searchTerm === '' ||
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.manufacturer.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.barcode.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesCategory = categoryFilter === 'ALL' || p.category === categoryFilter;
      const matchesStatus = statusFilter === 'ALL' || p.complianceStatus === statusFilter;

      return matchesSearch && matchesCategory && matchesStatus;
    });
  }, [products, searchTerm, categoryFilter, statusFilter]);

  const handleStartNew = () => {
    startNewInspection();
    navigate('/new-inspection?step=2');
  };

  const handleInspectAgain = (productName: string, barcode: string, brand: string, category: string, manufacturer: string) => {
    startNewInspection(undefined, 2);
    updateInspectionDetails({
      productName,
      barcode,
      brand,
      category,
      manufacturer
    });
    navigate('/new-inspection?step=2&camera=open');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E5E2DD] pb-4">
        <div>
          <h1 className="text-2xl font-bold text-[#1F2328] tracking-tight">Product Repository</h1>
          <p className="text-xs text-[#5F6368] mt-0.5">
            Central catalog of packaged commodities audited for Legal Metrology compliance
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="primary"
            size="sm"
            onClick={handleStartNew}
            className="flex items-center space-x-1.5"
          >
            <Camera className="w-4 h-4 text-white" />
            <span>Scan New Commodity</span>
          </Button>
          <div className="text-xs font-mono text-[#5F6368] bg-white border border-[#E5E2DD] px-3 py-1.5 rounded-lg shadow-2xs">
            Registered: <strong className="text-[#1F2328]">{products.length}</strong>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <Card>
        <CardContent className="p-4 space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="relative md:col-span-2">
              <Search className="w-4 h-4 text-[#8A8F98] absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by Product Name, Brand, Manufacturer, or GTIN..."
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg pl-9 pr-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED]"
              />
            </div>

            <div>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED] cursor-pointer"
              >
                <option value="ALL">All Categories</option>
                <option value="Edible Oils & Fats">Edible Oils & Fats</option>
                <option value="Food & Grains">Food & Grains</option>
                <option value="Food & Beverages">Food & Beverages</option>
                <option value="Food & Spices">Food & Spices</option>
                <option value="Personal Care & Cosmetics">Personal Care & Cosmetics</option>
                <option value="Household Chemicals">Household Chemicals</option>
                <option value="Consumer Electronics">Consumer Electronics</option>
              </select>
            </div>

            <div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full bg-[#FAF9F7] border border-[#E5E2DD] rounded-lg px-3 py-1.5 text-xs text-[#1F2328] focus:bg-white focus:outline-none focus:border-[#7C3AED] cursor-pointer"
              >
                <option value="ALL">All Compliance Ratings</option>
                <option value="Compliant">Compliant</option>
                <option value="Non-Compliant">Non-Compliant</option>
                <option value="Under Review">Under Review</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Products Table */}
      <Card>
        {filteredProducts.length === 0 ? (
          <div className="py-12 px-4 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-[#FAF9F7] border border-[#E5E2DD] flex items-center justify-center mx-auto text-[#8A8F98]">
              <Package className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-[#1F2328]">
              {products.length === 0 ? 'No Commodities Registered Yet' : 'No Matching Commodities Found'}
            </h3>
            <p className="text-xs text-[#5F6368] max-w-md mx-auto">
              {products.length === 0
                ? 'Commodities audited under Legal Metrology compliance inspections will automatically be registered in this central repository.'
                : 'Try adjusting your search terms or filters to find the registered commodity.'}
            </p>
            {products.length === 0 && (
              <Button variant="primary" size="sm" onClick={handleStartNew} className="mt-2">
                Initiate First Inspection
              </Button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-[#1F2328] border-collapse">
              <thead className="bg-[#FAF9F7] border-b border-[#E5E2DD] text-[11px] font-bold text-[#5F6368] uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Product Particulars</th>
                  <th className="py-3 px-4">Manufacturer / Packer</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Standard Qty</th>
                  <th className="py-3 px-4">Last Inspected</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-center">Violations</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F0EDE8] bg-white">
                {filteredProducts.map((prod) => (
                  <tr key={prod.id} className="hover:bg-[#FAF9F7] transition-colors">
                    <td className="py-3 px-4">
                      <div>
                        <span className="font-semibold text-[#1F2328] block max-w-[220px]">
                          {prod.name}
                        </span>
                        <span className="text-[10px] text-[#8A8F98] font-mono block">
                          GTIN: {prod.barcode || 'N/A'}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-[#5F6368] max-w-[180px] truncate">
                      {prod.manufacturer || 'Unspecified'}
                    </td>
                    <td className="py-3 px-4 text-[#5F6368]">
                      {prod.category}
                    </td>
                    <td className="py-3 px-4 font-mono text-[#5F6368]">
                      {prod.standardQuantity || '—'}
                    </td>
                    <td className="py-3 px-4 text-[#5F6368] font-mono">
                      {prod.lastInspectionDate}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={prod.complianceStatus} />
                    </td>
                    <td className="py-3 px-4 text-center font-mono font-bold">
                      {prod.totalViolations > 0 ? (
                        <span className="text-[#DC2626] bg-[#FEF2F2] px-2 py-0.5 rounded-md border border-[#FECACA]">
                          {prod.totalViolations}
                        </span>
                      ) : (
                        <span className="text-[#16A34A]">0</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end space-x-1.5">
                        {prod.lastInspectionId && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => navigate(`/reports/${prod.lastInspectionId}`)}
                            title="View Last Report"
                          >
                            View
                          </Button>
                        )}
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleInspectAgain(prod.name, prod.barcode, prod.brand, prod.category, prod.manufacturer)}
                          title="Initiate Re-audit"
                        >
                          Re-inspect
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
