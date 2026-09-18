import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useInspection } from '../context/InspectionContext';
import { OfficialReportView } from '../components/report/OfficialReportView';
import { Button } from '../components/ui/Button';
import { ArrowLeft, AlertCircle } from 'lucide-react';

export const InspectionDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { getInspectionById } = useInspection();
  const navigate = useNavigate();

  const inspection = id ? getInspectionById(id) : undefined;

  if (!inspection) {
    return (
      <div className="p-12 text-center space-y-4 max-w-md mx-auto">
        <AlertCircle className="w-12 h-12 text-amber-600 mx-auto" />
        <h2 className="text-base font-bold text-slate-900">Inspection Docket Not Found</h2>
        <p className="text-xs text-slate-500">
          The requested inspection docket ID <span className="font-mono">{id}</span> does not exist or has been archived.
        </p>
        <Button
          variant="primary"
          size="sm"
          leftIcon={<ArrowLeft className="w-4 h-4" />}
          onClick={() => navigate('/inspections')}
        >
          Return to Registry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <OfficialReportView inspection={inspection} />
    </div>
  );
};
