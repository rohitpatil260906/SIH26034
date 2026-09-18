import { User } from '../types';

export const MOCK_USERS: User[] = [
  {
    id: 'USR-LM-01',
    name: 'Rajesh Kumar Sharma',
    badgeNumber: 'LM-DEL-2018-0442',
    role: 'OFFICER',
    department: 'Legal Metrology Enforcement Wing, Central Division',
    jurisdictionZone: 'Delhi NCR - Central & New Delhi District',
    email: 'r.sharma@legalmetrology.gov.in',
    phone: '+91 98110 44219',
    status: 'Active',
    lastActive: '10 mins ago'
  },
  {
    id: 'USR-LM-02',
    name: 'Dr. Priya V. Nambiar',
    badgeNumber: 'LM-DEL-2014-0108',
    role: 'SENIOR_OFFICER',
    department: 'Standards & Quality Surveillance Directorate',
    jurisdictionZone: 'Delhi NCR - Northern & Western Zone',
    email: 'p.nambiar@legalmetrology.gov.in',
    phone: '+91 98450 11208',
    status: 'Active',
    lastActive: '25 mins ago'
  },
  {
    id: 'USR-LM-03',
    name: 'Virendra Singh Rawat',
    badgeNumber: 'LM-HQ-2010-0012',
    role: 'ADMIN',
    department: 'Controllerate of Legal Metrology, HQ New Delhi',
    jurisdictionZone: 'National Coordination & Zonal Administration',
    email: 'v.rawat.controller@legalmetrology.gov.in',
    phone: '+91 99100 88210',
    status: 'Active',
    lastActive: 'Just now'
  },
  {
    id: 'USR-LM-04',
    name: 'Ananya Deshmukh',
    badgeNumber: 'LM-AUD-2022-0981',
    role: 'VIEWER',
    department: 'Consumer Grievances & Legal Audit Cell',
    jurisdictionZone: 'Appellate & Tribunal Audit Review',
    email: 'a.deshmukh@legalmetrology.gov.in',
    phone: '+91 94220 77112',
    status: 'Active',
    lastActive: '2 hours ago'
  }
];
