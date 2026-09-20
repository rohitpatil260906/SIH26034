import { User } from '../types';

export const MOCK_USERS: User[] = [
  {
    id: 'USR-LM-01',
    name: 'Rohit Patil',
    badgeNumber: 'LM-MH-2022-0941',
    role: 'OFFICER',
    department: 'Legal Metrology Enforcement Wing, Western Division',
    jurisdictionZone: 'Maharashtra, Mumbai (400001)',
    email: 'rohit.patil@legalmetrology.gov.in',
    phone: '+91 98200 44219',
    status: 'Active',
    lastActive: 'Just now'
  },
  {
    id: 'USR-LM-02',
    name: 'Dr. Priya V. Nambiar',
    badgeNumber: 'LM-DEL-2014-0108',
    role: 'SENIOR_OFFICER',
    department: 'Standards & Quality Surveillance Directorate',
    jurisdictionZone: 'Maharashtra, Mumbai City (400001)',
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
    jurisdictionZone: 'Delhi, Central Delhi (110002)',
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
    jurisdictionZone: 'Maharashtra, Pune (411001)',
    email: 'a.deshmukh@legalmetrology.gov.in',
    phone: '+91 94220 77112',
    status: 'Active',
    lastActive: '2 hours ago'
  }
];
