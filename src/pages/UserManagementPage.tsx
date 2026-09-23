import React, { useState } from 'react';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { RoleBadge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { MOCK_USERS } from '../data/mockUsers';
import { User, OfficerRole, Jurisdiction } from '../types';
import { JurisdictionSelector } from '../components/jurisdiction/JurisdictionSelector';
import {
  Users,
  UserPlus,
  Shield,
  CheckCircle2,
  Lock,
  Mail,
  Phone,
  Edit2,
  RotateCcw
} from 'lucide-react';

export const UserManagementPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>(MOCK_USERS);
  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);
  const [auditedOfficer, setAuditedOfficer] = useState<User | null>(null);

  // New Officer Form
  const [newName, setNewName] = useState('');
  const [newBadge, setNewBadge] = useState('');
  const [newRole, setNewRole] = useState<OfficerRole>('OFFICER');
  const [newDept, setNewDept] = useState('Legal Metrology Field Enforcement Unit');
  const [newEmail, setNewEmail] = useState('');
  const [newJurisdiction, setNewJurisdiction] = useState<Jurisdiction>({
    country: 'India',
    state: 'Maharashtra',
    city: 'Dhule',
    pinCode: '424001'
  });

  const handleAddOfficer = (e: React.FormEvent) => {
    e.preventDefault();
    const zoneStr = `${newJurisdiction.state}${newJurisdiction.city ? ', ' + newJurisdiction.city : ''}${newJurisdiction.pinCode ? ' (' + newJurisdiction.pinCode + ')' : ''}`;
    const newUser: User = {
      id: `USR-LM-${Date.now().toString().slice(-4)}`,
      name: newName,
      badgeNumber: newBadge,
      role: newRole,
      department: newDept,
      jurisdictionZone: zoneStr,
      email: newEmail,
      phone: '+91 98000 00000',
      status: 'Active',
      lastActive: 'Just registered'
    };
    setUsers(prev => [newUser, ...prev]);
    setIsAddModalOpen(false);
    setNewName('');
    setNewBadge('');
    setNewEmail('');
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Officer & User Management</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Role-Based Access Control (RBAC) and credentialing for authorized enforcement officers
          </p>
        </div>
        <Button
          variant="primary"
          size="sm"
          leftIcon={<UserPlus className="w-4 h-4" />}
          onClick={() => setIsAddModalOpen(true)}
        >
          Provision New Officer
        </Button>
      </div>

      {/* Officers Table */}
      <Card>
        <CardHeader
          title={`Enrolled Officers (${users.length})`}
          subtitle="Active directory of credentialed inspectors, controllers, and auditors"
        />
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-800 border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Officer Particulars</th>
                <th className="py-3 px-4">Assigned Role</th>
                <th className="py-3 px-4">Department / Division</th>
                <th className="py-3 px-4">Jurisdiction Zone</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Last Active</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2.5">
                      <div className="w-8 h-8 rounded-full bg-[#F5F3FF] text-[#6D28D9] border border-[#DDD6FE] flex items-center justify-center font-bold text-xs shrink-0">
                        {u.name.charAt(0)}
                      </div>
                      <div>
                        <span className="font-bold text-slate-900 block">{u.name}</span>
                        <span className="text-[10px] text-slate-500 font-mono block">
                          Badge: {u.badgeNumber} • {u.email}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <RoleBadge role={u.role} />
                  </td>
                  <td className="py-3 px-4 text-slate-700 max-w-[170px] truncate">
                    {u.department}
                  </td>
                  <td className="py-3 px-4 text-slate-600">
                    {u.jurisdictionZone}
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center text-xs font-semibold text-emerald-700">
                      <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5"></span>
                      {u.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-500 font-mono text-[11px]">
                    {u.lastActive}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => setAuditedOfficer(u)}
                      className="text-xs text-[#6D28D9] hover:underline font-semibold cursor-pointer"
                    >
                      Audit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Role Permissions Matrix Explanation */}
      <Card>
        <CardHeader
          title="Role Permissions Matrix"
          subtitle="Defined capabilities per statutory Legal Metrology rank"
        />
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border border-slate-200 border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200 font-bold text-slate-700">
              <tr>
                <th className="p-3 border-r border-slate-200">Enforcement Capability</th>
                <th className="p-3 border-r border-slate-200 text-center">ADMIN (Controller)</th>
                <th className="p-3 border-r border-slate-200 text-center">SENIOR OFFICER (Asst. Controller)</th>
                <th className="p-3 border-r border-slate-200 text-center">OFFICER (Field Inspector)</th>
                <th className="p-3 text-center">VIEWER (Legal Auditor)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              <tr>
                <td className="p-3 font-medium border-r border-slate-200">Scan & Initiate Market Inspections</td>
                <td className="p-3 text-center border-r border-slate-200 text-emerald-700 font-bold">✓ Full</td>
                <td className="p-3 text-center border-r border-slate-200 text-emerald-700 font-bold">✓ Full</td>
                <td className="p-3 text-center border-r border-slate-200 text-emerald-700 font-bold">✓ Full</td>
                <td className="p-3 text-center text-slate-400">Read-Only</td>
              </tr>
              <tr>
                <td className="p-3 font-medium border-r border-slate-200">Edit Extracted Values / Calibrate</td>
                <td className="p-3 text-center border-r border-slate-200 text-emerald-700 font-bold">✓ Full</td>
                <td className="p-3 text-center border-r border-slate-200 text-emerald-700 font-bold">✓ Full</td>
                <td className="p-3 text-center border-r border-slate-200 text-emerald-700 font-bold">✓ Full</td>
                <td className="p-3 text-center text-slate-400">Disabled</td>
              </tr>
              <tr>
                <td className="p-3 font-medium border-r border-slate-200">Issue Compounding Notices / Section 36 Orders</td>
                <td className="p-3 text-center border-r border-slate-200 text-emerald-700 font-bold">✓ Full</td>
                <td className="p-3 text-center border-r border-slate-200 text-emerald-700 font-bold">✓ Full</td>
                <td className="p-3 text-center border-r border-slate-200 text-amber-700 font-bold">Recommend Only</td>
                <td className="p-3 text-center text-slate-400">Disabled</td>
              </tr>
              <tr>
                <td className="p-3 font-medium border-r border-slate-200">Modify Rule Parameters & Schedules</td>
                <td className="p-3 text-center border-r border-slate-200 text-emerald-700 font-bold">✓ Full</td>
                <td className="p-3 text-center border-r border-slate-200 text-slate-400">Restricted</td>
                <td className="p-3 text-center border-r border-slate-200 text-slate-400">Disabled</td>
                <td className="p-3 text-center text-slate-400">Disabled</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      {/* Add Officer Modal */}
      {isAddModalOpen && (
        <Modal
          isOpen={true}
          onClose={() => setIsAddModalOpen(false)}
          title="Provision New Legal Metrology Officer"
          subtitle="Enrol official credentials on the National Enforcement Portal"
          maxWidth="lg"
          footer={
            <>
              <Button variant="outline" size="sm" onClick={() => setIsAddModalOpen(false)}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" onClick={handleAddOfficer}>
                Provision Officer Credentials
              </Button>
            </>
          }
        >
          <form className="space-y-3 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Full Legal Name</label>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g. Suresh Chand Meena"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-900 focus:border-[#7C3AED] focus:outline-none"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Official Badge Number</label>
                <input
                  type="text"
                  value={newBadge}
                  onChange={(e) => setNewBadge(e.target.value)}
                  placeholder="LM-DEL-2026-0994"
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs font-mono text-slate-900 focus:border-[#7C3AED] focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Officer Rank / Role</label>
                <select
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value as OfficerRole)}
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-900 focus:border-[#7C3AED] focus:outline-none"
                >
                  <option value="OFFICER">OFFICER (Field Inspector)</option>
                  <option value="SENIOR_OFFICER">SENIOR OFFICER (Asst. Controller)</option>
                  <option value="ADMIN">ADMIN (Zonal Controller)</option>
                  <option value="VIEWER">VIEWER (Legal Auditor)</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Government Email (NIC / State Domain)</label>
              <input
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="s.meena@legalmetrology.gov.in"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-900 focus:ring-1 focus:ring-[#7C3AED] focus:outline-none"
                required
              />
            </div>
            <div className="pt-2 border-t border-slate-200">
              <JurisdictionSelector
                value={newJurisdiction}
                onChange={setNewJurisdiction}
                layout="grid"
                title="Assigned Territorial Jurisdiction"
                subtitle="Official State, District, and PIN Code station"
              />
            </div>
          </form>
        </Modal>
      )}

      {/* Officer Credential Audit Dossier Modal */}
      {auditedOfficer && (
        <Modal
          isOpen={true}
          onClose={() => setAuditedOfficer(null)}
          title="Officer Credential Audit Dossier"
          subtitle="Statutory verification under National Legal Metrology Directory"
          maxWidth="md"
          footer={
            <Button variant="primary" size="sm" onClick={() => setAuditedOfficer(null)}>
              Close Dossier
            </Button>
          }
        >
          <div className="space-y-4 text-xs text-slate-700">
            <div className="flex items-center space-x-3 p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <div className="w-10 h-10 rounded-full bg-[#F5F3FF] text-[#6D28D9] border border-[#DDD6FE] flex items-center justify-center font-bold text-sm">
                {auditedOfficer.name.charAt(0)}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-slate-900 text-sm">{auditedOfficer.name}</h4>
                  <RoleBadge role={auditedOfficer.role} />
                </div>
                <p className="text-[11px] text-slate-500 font-mono mt-0.5">
                  Badge: {auditedOfficer.badgeNumber} • ID: {auditedOfficer.id}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 border border-slate-200 rounded-lg p-3 bg-white">
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-semibold block">Department</span>
                <span className="font-medium text-slate-800 text-[11px]">{auditedOfficer.department}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-semibold block">Jurisdiction Zone</span>
                <span className="font-medium text-slate-800 text-[11px]">{auditedOfficer.jurisdictionZone}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-semibold block">Enforcement Status</span>
                <span className="font-semibold text-emerald-700 text-[11px] flex items-center mt-0.5">
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" /> Active & Enrolled
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-semibold block">Last Active</span>
                <span className="font-mono text-slate-600 text-[11px]">{auditedOfficer.lastActive}</span>
              </div>
            </div>

            <div className="p-3 bg-emerald-50/60 border border-emerald-200 rounded-lg space-y-1.5 text-[11px]">
              <div className="flex items-center space-x-1.5 font-bold text-emerald-900">
                <Shield className="w-4 h-4 text-emerald-600" />
                <span>Statutory Authority & Cryptographic Verification</span>
              </div>
              <p className="text-emerald-800 leading-relaxed">
                Credentials validated against the National Controllerate Directory. Authorized to conduct packaging audits, record panchnamas, and issue legal compound notices under Section 15 & 48 of the Legal Metrology Act, 2009.
              </p>
              <div className="pt-1 font-mono text-[10px] text-emerald-700">
                Hash: SHA256:{auditedOfficer.id.replace(/-/g, '').padEnd(32, 'a7e9')}... • Status: VALID
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
