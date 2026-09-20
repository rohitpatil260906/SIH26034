import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { JurisdictionSelector } from './JurisdictionSelector';
import { Jurisdiction } from '../../types';
import { MapPin, Check, Save } from 'lucide-react';

interface JurisdictionModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentJurisdiction: Jurisdiction;
  onSave: (newJurisdiction: Jurisdiction) => void;
}

export const JurisdictionModal: React.FC<JurisdictionModalProps> = ({
  isOpen,
  onClose,
  currentJurisdiction,
  onSave
}) => {
  const [tempJurisdiction, setTempJurisdiction] = useState<Jurisdiction>(currentJurisdiction);
  const [isValid, setIsValid] = useState<boolean>(true);
  const [errorText, setErrorText] = useState<string | undefined>(undefined);

  // Synchronize when opening
  React.useEffect(() => {
    if (isOpen) {
      setTempJurisdiction(currentJurisdiction);
    }
  }, [isOpen, currentJurisdiction]);

  const handleSave = () => {
    if (!isValid) return;
    onSave(tempJurisdiction);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Set Operational Statutory Jurisdiction"
      maxWidth="lg"
      footer={
        <div className="flex items-center justify-between w-full">
          <div className="text-xs text-slate-500">
            {errorText && <span className="text-red-600 font-medium">{errorText}</span>}
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              disabled={!isValid}
              onClick={handleSave}
              leftIcon={<Save className="w-3.5 h-3.5" />}
            >
              Apply Jurisdiction
            </Button>
          </div>
        </div>
      }
    >
      <div className="space-y-4 py-2">
        <div className="bg-amber-50/80 border border-amber-200 rounded p-3 text-xs text-amber-950 flex items-start space-x-2.5">
          <MapPin className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold">Statutory Territorial Alignment</p>
            <p className="text-amber-800">
              Select the administrative State / Union Territory, City / District, and PIN Code where the enforcement officer is stationed.
              All subsequent inspection dockets, legal notices, and compliance reports will be mapped to this jurisdiction.
            </p>
          </div>
        </div>

        <JurisdictionSelector
          value={tempJurisdiction}
          onChange={setTempJurisdiction}
          onValidationChange={(valid, err) => {
            setIsValid(valid);
            setErrorText(err);
          }}
          layout="grid"
          showTitle={false}
        />
      </div>
    </Modal>
  );
};
