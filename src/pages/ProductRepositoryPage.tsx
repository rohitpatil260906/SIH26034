import React, { useState, useMemo } from 'react';
import { useInspection } from '../context/InspectionContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { StatusBadge } from '../components/ui/Badge';
import {
  Search,
  Package,
  PlusCircle,
  ExternalLink,
  Camera
} from 'lucide-react';

export const ProductRepositoryPage: React.FC = () => {
  const { products, startNewInspection, updateInspectionDetails } = useInspection();
  const navigate = useNavigate();

  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredProducts = useMemo(() => {
    return products.filter(p => {
      const matchesSearch =
        searchTerm === '' ||
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.manufacturer.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.barcode.includes(searchTerm);

      const matchesCategory = categoryFilter === 'ALL' || p.category === categoryFilter;
      const matchesStatus = statusFilter === 'ALL' || p.complianceStatus === statusFilter;

      return matchesSearch && matchesCategory && matchesStatus;
    });
  }, [products, searchTerm, categoryFilter, statusFilter]);

  const handleInspectAgain = (productName: string, barcode?: string, brand?: string, category?: string, manufacturer?: string) => {
    startNewInspection();
    updateInspectionDetails({
      productName,
      barcode: barcode || '',
      brand: brand || '',
      category: category || 'General Packaged Commodity',
      manufacturer: manufacturer || ''
    });
    navigate('/new-inspection?step=2');
  };

  const handleStartNew = () => {
    startNewInspection();
    navigate('/new-inspection?step=2&camera=open');
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Packaged Commodity Repository</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Central registry of audited packaged goods, manufacturer compliance history, and market surveillance records
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="primary"
            size="sm"
            onClick={handleStartNew}
            className="flex items-center space-x-1.5"
          >
            <Camera className="w-4 h-4" />
            <span>Scan New Commodity</span>
          </Button>
          <div className="text-xs font-mono text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded">
            Registered Products: <strong>{products.length}</strong>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <Card>
        <CardContent className="p-4 space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="relative md:col-span-2">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by Product Name, Brand, Manufacturer, or GTIN..."
                className="w-full bg-slate-50 border border-slate-300 rounded pl-9 pr-3 py-1.5 text-xs text-slate-900 focus:bg-white focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              />
            </div>

            <div>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:outline-none"
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
                className="w-full bg-slate-50 border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:outline-none"
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
            <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400">
              <Package className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-800">
              {products.length === 0 ? 'No Commodities Registered Yet' : 'No Matching Commodities Found'}
            </h3>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
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
            <table className="w-full text-left text-xs text-slate-800 border-collapse">
              <thead className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
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
              <tbody className="divide-y divide-slate-200 bg-white">
                {filteredProducts.map((prod) => (
                  <tr key={prod.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4">
                      <div>
                        <span className="font-semibold text-slate-900 block max-w-[220px]">
                          {prod.name}
                        </span>
                        <span className="text-[10px] text-slate-400 font-mono block">
                          GTIN: {prod.barcode || 'N/A'}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-700 max-w-[180px] truncate">
                      {prod.manufacturer || 'Unspecified'}
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      {prod.category}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-700">
                      {prod.standardQuantity || '—'}
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-mono">
                      {prod.lastInspectionDate}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={prod.complianceStatus} />
                    </td>
                    <td className="py-3 px-4 text-center font-mono font-bold">
                      {prod.totalViolations > 0 ? (
                        <span className="text-red-700 bg-red-50 px-2 py-0.5 rounded border border-red-200">
                          {prod.totalViolations}
                        </span>
                      ) : (
                        <span className="text-emerald-700">0</span>
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
