/**
 * Official Indian Administrative Jurisdiction Dataset
 * Covers all 28 States and 8 Union Territories with comprehensive district mappings,
 * postal circle prefixes, and statutory validation helpers.
 */

export interface StateInfo {
  name: string;
  type: 'State' | 'Union Territory';
  code: string;
  pinPrefixes: string[]; // 2-digit postal circle prefixes
  districts: string[];
  districtPinOverrides?: Record<string, string[]>; // Optional district-level 3-digit prefixes
  defaultPinByDistrict?: Record<string, string>;
}

export const INDIAN_STATES_AND_UTS: StateInfo[] = [
  {
    name: 'Andaman and Nicobar Islands',
    type: 'Union Territory',
    code: 'AN',
    pinPrefixes: ['74'],
    districts: ['Nicobar', 'North and Middle Andaman', 'South Andaman'],
    defaultPinByDistrict: {
      'South Andaman': '744101',
      'North and Middle Andaman': '744205',
      'Nicobar': '744301'
    }
  },
  {
    name: 'Andhra Pradesh',
    type: 'State',
    code: 'AP',
    pinPrefixes: ['51', '52', '53'],
    districts: [
      'Alluri Sitharama Raju',
      'Anakapalli',
      'Ananthapuramu',
      'Annamayya',
      'Bapatla',
      'Chittoor',
      'Dr. B.R. Ambedkar Konaseema',
      'East Godavari',
      'Eluru',
      'Guntur',
      'Kakinada',
      'Krishna',
      'Kurnool',
      'Nandyal',
      'NTR',
      'Palnadu',
      'Parvathipuram Manyam',
      'Prakasam',
      'Sri Potti Sriramulu Nellore',
      'Sri Sathya Sai',
      'Srikakulam',
      'Tirupati',
      'Visakhapatnam',
      'Vizianagaram',
      'West Godavari',
      'YSR Kadapa'
    ],
    defaultPinByDistrict: {
      'Visakhapatnam': '530001',
      'Vijayawada': '520001',
      'Guntur': '522001',
      'Tirupati': '517501',
      'Kurnool': '518001',
      'NTR': '520002'
    }
  },
  {
    name: 'Arunachal Pradesh',
    type: 'State',
    code: 'AR',
    pinPrefixes: ['79'],
    districts: [
      'Anjaw',
      'Changlang',
      'Dibang Valley',
      'East Kameng',
      'East Siang',
      'Itanagar Capital Complex',
      'Kamle',
      'Kra Daadi',
      'Kurung Kumey',
      'Lepa Rada',
      'Lohit',
      'Longding',
      'Lower Dibang Valley',
      'Lower Siang',
      'Lower Subansiri',
      'Namsai',
      'Pakke Kessang',
      'Papum Pare',
      'Shi Yomi',
      'Siang',
      'Tawang',
      'Tirap',
      'Upper Siang',
      'Upper Subansiri',
      'West Kameng',
      'West Siang'
    ],
    defaultPinByDistrict: {
      'Papum Pare': '791111',
      'Itanagar Capital Complex': '791111',
      'Tawang': '790104',
      'East Siang': '791102'
    }
  },
  {
    name: 'Assam',
    type: 'State',
    code: 'AS',
    pinPrefixes: ['78'],
    districts: [
      'Baksa',
      'Barpeta',
      'Biswanath',
      'Bongaigaon',
      'Cachar',
      'Charaideo',
      'Chirang',
      'Darrang',
      'Dhemaji',
      'Dhubri',
      'Dibrugarh',
      'Dima Hasao',
      'Goalpara',
      'Golaghat',
      'Hailakandi',
      'Hojai',
      'Jorhat',
      'Kamrup',
      'Kamrup Metropolitan',
      'Karbi Anglong',
      'Karimganj',
      'Kokrajhar',
      'Lakhimpur',
      'Majuli',
      'Morigaon',
      'Nagaon',
      'Nalbari',
      'Sivasagar',
      'Sonitpur',
      'South Salmara-Mankachar',
      'Tamulpur',
      'Tinsukia',
      'Udalguri',
      'West Karbi Anglong',
      'Bajali'
    ],
    defaultPinByDistrict: {
      'Kamrup Metropolitan': '781001',
      'Dibrugarh': '786001',
      'Silchar': '788001',
      'Jorhat': '785001'
    }
  },
  {
    name: 'Bihar',
    type: 'State',
    code: 'BR',
    pinPrefixes: ['80', '81', '82', '84', '85'],
    districts: [
      'Araria',
      'Arwal',
      'Aurangabad',
      'Banka',
      'Begusarai',
      'Bhagalpur',
      'Bhojpur',
      'Buxar',
      'Darbhanga',
      'East Champaran',
      'Gaya',
      'Gopalganj',
      'Jamui',
      'Jehanabad',
      'Kaimur',
      'Katihar',
      'Khagaria',
      'Kishanganj',
      'Lakhisarai',
      'Madhepura',
      'Madhubani',
      'Munger',
      'Muzaffarpur',
      'Nalanda',
      'Nawada',
      'Patna',
      'Purnia',
      'Rohtas',
      'Saharsa',
      'Samastipur',
      'Saran',
      'Sheikhpura',
      'Sheohar',
      'Sitamarhi',
      'Siwan',
      'Supaul',
      'Vaishali',
      'West Champaran'
    ],
    defaultPinByDistrict: {
      'Patna': '800001',
      'Gaya': '823001',
      'Muzaffarpur': '842001',
      'Bhagalpur': '812001'
    }
  },
  {
    name: 'Chandigarh',
    type: 'Union Territory',
    code: 'CH',
    pinPrefixes: ['16'],
    districts: ['Chandigarh'],
    defaultPinByDistrict: {
      'Chandigarh': '160017'
    }
  },
  {
    name: 'Chhattisgarh',
    type: 'State',
    code: 'CG',
    pinPrefixes: ['49'],
    districts: [
      'Balod',
      'Baloda Bazar',
      'Balrampur',
      'Bastar',
      'Bemetara',
      'Bijapur',
      'Bilaspur',
      'Dantewada',
      'Dhamtari',
      'Durg',
      'Gariaband',
      'Gaurela-Pendra-Marwahi',
      'Janjgir-Champa',
      'Jashpur',
      'Kabirdham',
      'Kanker',
      'Khairagarh-Chhuikhadan-Gandai',
      'Kondagaon',
      'Korba',
      'Koriya',
      'Mahasamund',
      'Manendragarh-Chirmiri-Bharatpur',
      'Mohla-Manpur-Ambagarh Chowki',
      'Mungeli',
      'Narayanpur',
      'Raigarh',
      'Raipur',
      'Rajnandgaon',
      'Sakti',
      'Sarangarh-Bilaigarh',
      'Sukma',
      'Surajpur',
      'Surguja'
    ],
    defaultPinByDistrict: {
      'Raipur': '492001',
      'Bilaspur': '495001',
      'Durg': '491001',
      'Bhilai': '490006'
    }
  },
  {
    name: 'Dadra and Nagar Haveli and Daman and Diu',
    type: 'Union Territory',
    code: 'DN',
    pinPrefixes: ['39'],
    districts: ['Dadra and Nagar Haveli', 'Daman', 'Diu'],
    defaultPinByDistrict: {
      'Daman': '396210',
      'Diu': '362520',
      'Dadra and Nagar Haveli': '396230'
    }
  },
  {
    name: 'Delhi',
    type: 'Union Territory',
    code: 'DL',
    pinPrefixes: ['11'],
    districts: [
      'Central Delhi',
      'East Delhi',
      'New Delhi',
      'North Delhi',
      'North East Delhi',
      'North West Delhi',
      'Shahdara',
      'South Delhi',
      'South East Delhi',
      'South West Delhi',
      'West Delhi'
    ],
    defaultPinByDistrict: {
      'New Delhi': '110001',
      'Central Delhi': '110002',
      'South Delhi': '110016',
      'North Delhi': '110007',
      'East Delhi': '110092',
      'West Delhi': '110015'
    }
  },
  {
    name: 'Goa',
    type: 'State',
    code: 'GA',
    pinPrefixes: ['40'],
    districts: ['North Goa', 'South Goa'],
    defaultPinByDistrict: {
      'North Goa': '403001',
      'South Goa': '403601'
    }
  },
  {
    name: 'Gujarat',
    type: 'State',
    code: 'GJ',
    pinPrefixes: ['36', '37', '38', '39'],
    districts: [
      'Ahmedabad',
      'Amreli',
      'Anand',
      'Aravalli',
      'Banaskantha',
      'Bharuch',
      'Bhavnagar',
      'Botad',
      'Chhota Udaipur',
      'Dahod',
      'Dang',
      'Devbhoomi Dwarka',
      'Gandhinagar',
      'Gir Somnath',
      'Jamnagar',
      'Junagadh',
      'Kheda',
      'Kutch',
      'Mahisagar',
      'Mehsana',
      'Morbi',
      'Narmada',
      'Navsari',
      'Panchmahal',
      'Patan',
      'Porbandar',
      'Rajkot',
      'Sabarkantha',
      'Surat',
      'Surendranagar',
      'Tapi',
      'Vadodara',
      'Valsad'
    ],
    defaultPinByDistrict: {
      'Ahmedabad': '380001',
      'Surat': '395001',
      'Vadodara': '390001',
      'Rajkot': '360001',
      'Gandhinagar': '382010'
    }
  },
  {
    name: 'Haryana',
    type: 'State',
    code: 'HR',
    pinPrefixes: ['12', '13'],
    districts: [
      'Ambala',
      'Bhiwani',
      'Charkhi Dadri',
      'Faridabad',
      'Fatehabad',
      'Gurugram',
      'Hisar',
      'Jhajjar',
      'Jind',
      'Kaithal',
      'Karnal',
      'Kurukshetra',
      'Mahendragarh',
      'Nuh',
      'Palwal',
      'Panchkula',
      'Panipat',
      'Rewari',
      'Rohtak',
      'Sirsa',
      'Sonipat',
      'Yamunanagar'
    ],
    defaultPinByDistrict: {
      'Gurugram': '122001',
      'Faridabad': '121001',
      'Panchkula': '134109',
      'Panipat': '132103',
      'Ambala': '133001'
    }
  },
  {
    name: 'Himachal Pradesh',
    type: 'State',
    code: 'HP',
    pinPrefixes: ['17'],
    districts: [
      'Bilaspur',
      'Chamba',
      'Hamirpur',
      'Kangra',
      'Kinnaur',
      'Kullu',
      'Lahaul and Spiti',
      'Mandi',
      'Shimla',
      'Sirmaur',
      'Solan',
      'Una'
    ],
    defaultPinByDistrict: {
      'Shimla': '171001',
      'Dharamshala': '176215',
      'Kullu': '175101',
      'Solan': '173212'
    }
  },
  {
    name: 'Jammu and Kashmir',
    type: 'Union Territory',
    code: 'JK',
    pinPrefixes: ['18', '19'],
    districts: [
      'Anantnag',
      'Bandipora',
      'Baramulla',
      'Budgam',
      'Doda',
      'Ganderbal',
      'Jammu',
      'Kathua',
      'Kishtwar',
      'Kulgam',
      'Kupwara',
      'Poonch',
      'Pulwama',
      'Rajouri',
      'Ramban',
      'Reasi',
      'Samba',
      'Shopian',
      'Srinagar',
      'Udhampur'
    ],
    defaultPinByDistrict: {
      'Srinagar': '190001',
      'Jammu': '180001',
      'Anantnag': '192101',
      'Baramulla': '193101'
    }
  },
  {
    name: 'Jharkhand',
    type: 'State',
    code: 'JH',
    pinPrefixes: ['81', '82', '83'],
    districts: [
      'Bokaro',
      'Chatra',
      'Deoghar',
      'Dhanbad',
      'Dumka',
      'East Singhbhum',
      'Garhwa',
      'Giridih',
      'Godda',
      'Gumla',
      'Hazaribagh',
      'Jamtara',
      'Khunti',
      'Koderma',
      'Latehar',
      'Lohardaga',
      'Pakur',
      'Palamu',
      'Ramgarh',
      'Ranchi',
      'Sahebganj',
      'Seraikela Kharsawan',
      'Simdega',
      'West Singhbhum'
    ],
    defaultPinByDistrict: {
      'Ranchi': '834001',
      'East Singhbhum': '831001',
      'Dhanbad': '826001',
      'Bokaro': '827001'
    }
  },
  {
    name: 'Karnataka',
    type: 'State',
    code: 'KA',
    pinPrefixes: ['56', '57', '58', '59'],
    districts: [
      'Bagalkot',
      'Ballari',
      'Belagavi',
      'Bengaluru Rural',
      'Bengaluru Urban',
      'Bidar',
      'Chamarajanagar',
      'Chikkaballapur',
      'Chikkamagaluru',
      'Chitradurga',
      'Dakshina Kannada',
      'Davanagere',
      'Dharwad',
      'Gadag',
      'Hassan',
      'Haveri',
      'Kalaburagi',
      'Kodagu',
      'Kolar',
      'Koppal',
      'Mandya',
      'Mysuru',
      'Raichur',
      'Ramanagara',
      'Shivamogga',
      'Tumakuru',
      'Udupi',
      'Uttara Kannada',
      'Vijayanagara',
      'Vijayapura',
      'Yadgir'
    ],
    defaultPinByDistrict: {
      'Bengaluru Urban': '560001',
      'Bengaluru Rural': '562123',
      'Mysuru': '570001',
      'Dakshina Kannada': '575001',
      'Dharwad': '580001',
      'Belagavi': '590001'
    }
  },
  {
    name: 'Kerala',
    type: 'State',
    code: 'KL',
    pinPrefixes: ['67', '68', '69'],
    districts: [
      'Alappuzha',
      'Ernakulam',
      'Idukki',
      'Kannur',
      'Kasaragod',
      'Kollam',
      'Kottayam',
      'Kozhikode',
      'Malappuram',
      'Palakkad',
      'Pathanamthitta',
      'Thiruvananthapuram',
      'Thrissur',
      'Wayanad'
    ],
    defaultPinByDistrict: {
      'Thiruvananthapuram': '695001',
      'Ernakulam': '682001',
      'Kozhikode': '673001',
      'Thrissur': '680001'
    }
  },
  {
    name: 'Ladakh',
    type: 'Union Territory',
    code: 'LA',
    pinPrefixes: ['19'],
    districts: ['Kargil', 'Leh'],
    defaultPinByDistrict: {
      'Leh': '194101',
      'Kargil': '194103'
    }
  },
  {
    name: 'Lakshadweep',
    type: 'Union Territory',
    code: 'LD',
    pinPrefixes: ['68'],
    districts: ['Lakshadweep'],
    defaultPinByDistrict: {
      'Lakshadweep': '682555'
    }
  },
  {
    name: 'Madhya Pradesh',
    type: 'State',
    code: 'MP',
    pinPrefixes: ['45', '46', '47', '48'],
    districts: [
      'Agar Malwa',
      'Alirajpur',
      'Anuppur',
      'Ashoknagar',
      'Balaghat',
      'Barwani',
      'Betul',
      'Bhind',
      'Bhopal',
      'Burhanpur',
      'Chhatarpur',
      'Chhindwara',
      'Damoh',
      'Datia',
      'Dewas',
      'Dhar',
      'Dindori',
      'Guna',
      'Gwalior',
      'Harda',
      'Hoshangabad (Narmadapuram)',
      'Indore',
      'Jabalpur',
      'Jhabua',
      'Katni',
      'Khandwa',
      'Khargone',
      'Maihar',
      'Mandla',
      'Mandsaur',
      'Mauganj',
      'Morena',
      'Narsinghpur',
      'Neemuch',
      'Niwari',
      'Pandhurna',
      'Panna',
      'Raisen',
      'Rajgarh',
      'Ratlam',
      'Rewa',
      'Sagar',
      'Satna',
      'Sehore',
      'Seoni',
      'Shahdol',
      'Shajapur',
      'Sheopur',
      'Shivpuri',
      'Sidhi',
      'Singrauli',
      'Tikamgarh',
      'Ujjain',
      'Umaria',
      'Vidisha'
    ],
    defaultPinByDistrict: {
      'Bhopal': '462001',
      'Indore': '452001',
      'Jabalpur': '482001',
      'Gwalior': '474001',
      'Ujjain': '456001'
    }
  },
  {
    name: 'Maharashtra',
    type: 'State',
    code: 'MH',
    pinPrefixes: ['40', '41', '42', '43', '44'],
    districts: [
      'Ahmednagar (Ahilyanagar)',
      'Akola',
      'Amravati',
      'Chhatrapati Sambhajinagar',
      'Beed',
      'Bhandara',
      'Buldhana',
      'Chandrapur',
      'Dhule',
      'Gadchiroli',
      'Gondia',
      'Hingoli',
      'Jalgaon',
      'Jalna',
      'Kolhapur',
      'Latur',
      'Mumbai City',
      'Mumbai Suburban',
      'Nagpur',
      'Nanded',
      'Nandurbar',
      'Nashik',
      'Dharashiv (Osmanabad)',
      'Palghar',
      'Parbhani',
      'Pune',
      'Raigad',
      'Ratnagiri',
      'Sangli',
      'Satara',
      'Sindhudurg',
      'Solapur',
      'Thane',
      'Wardha',
      'Washim',
      'Yavatmal'
    ],
    districtPinOverrides: {
      'Dhule': ['424'],
      'Pune': ['411', '412'],
      'Mumbai City': ['400'],
      'Mumbai Suburban': ['400'],
      'Nashik': ['422', '423'],
      'Nagpur': ['440', '441'],
      'Thane': ['400', '401', '421'],
      'Jalgaon': ['425'],
      'Chhatrapati Sambhajinagar': ['431']
    },
    defaultPinByDistrict: {
      'Dhule': '424001',
      'Mumbai City': '400001',
      'Mumbai Suburban': '400051',
      'Pune': '411001',
      'Nagpur': '440001',
      'Nashik': '422001',
      'Thane': '400601',
      'Chhatrapati Sambhajinagar': '431001',
      'Kolhapur': '416001',
      'Solapur': '413001'
    }
  },
  {
    name: 'Manipur',
    type: 'State',
    code: 'MN',
    pinPrefixes: ['79'],
    districts: [
      'Bishnupur',
      'Chandel',
      'Churachandpur',
      'Imphal East',
      'Imphal West',
      'Jiribam',
      'Kakching',
      'Kamjong',
      'Kangpokpi',
      'Noney',
      'Pherzawl',
      'Senapati',
      'Tamenglong',
      'Tengnoupal',
      'Thoubal',
      'Ukhrul'
    ],
    defaultPinByDistrict: {
      'Imphal West': '795001',
      'Imphal East': '795005',
      'Churachandpur': '795128'
    }
  },
  {
    name: 'Meghalaya',
    type: 'State',
    code: 'ML',
    pinPrefixes: ['79'],
    districts: [
      'Eastern West Khasi Hills',
      'East Garo Hills',
      'East Jaintia Hills',
      'East Khasi Hills',
      'North Garo Hills',
      'Ri Bhoi',
      'South Garo Hills',
      'South West Garo Hills',
      'South West Khasi Hills',
      'West Garo Hills',
      'West Jaintia Hills',
      'West Khasi Hills'
    ],
    defaultPinByDistrict: {
      'East Khasi Hills': '793001',
      'West Garo Hills': '794001'
    }
  },
  {
    name: 'Mizoram',
    type: 'State',
    code: 'MZ',
    pinPrefixes: ['79'],
    districts: [
      'Aizawl',
      'Champhai',
      'Hnahthial',
      'Khawzawl',
      'Kolasib',
      'Lawngtlai',
      'Lunglei',
      'Mamit',
      'Saitual',
      'Serchhip',
      'Siaha'
    ],
    defaultPinByDistrict: {
      'Aizawl': '796001',
      'Lunglei': '796701'
    }
  },
  {
    name: 'Nagaland',
    type: 'State',
    code: 'NL',
    pinPrefixes: ['79'],
    districts: [
      'Chumoukedima',
      'Dimapur',
      'Kiphire',
      'Kohima',
      'Longleng',
      'Mokokchung',
      'Mon',
      'Niuland',
      'Noklak',
      'Peren',
      'Phek',
      'Shamator',
      'Tseminyu',
      'Tuensang',
      'Wokha',
      'Zunheboto'
    ],
    defaultPinByDistrict: {
      'Kohima': '797001',
      'Dimapur': '797112',
      'Mokokchung': '798601'
    }
  },
  {
    name: 'Odisha',
    type: 'State',
    code: 'OD',
    pinPrefixes: ['75', '76', '77'],
    districts: [
      'Angul',
      'Balangir',
      'Balasore',
      'Bargarh',
      'Bhadrak',
      'Boudh',
      'Cuttack',
      'Deogarh',
      'Dhenkanal',
      'Gajapati',
      'Ganjam',
      'Jagatsinghpur',
      'Jajpur',
      'Jharsuguda',
      'Kalahandi',
      'Kandhamal',
      'Kendrapara',
      'Kendujhar',
      'Khordha',
      'Koraput',
      'Malkangiri',
      'Mayurbhanj',
      'Nabarangpur',
      'Nayagarh',
      'Nuapada',
      'Puri',
      'Rayagada',
      'Sambalpur',
      'Subarnapur',
      'Sundargarh'
    ],
    defaultPinByDistrict: {
      'Khordha': '751001',
      'Cuttack': '753001',
      'Rourkela': '769001',
      'Puri': '752001',
      'Sambalpur': '768001'
    }
  },
  {
    name: 'Puducherry',
    type: 'Union Territory',
    code: 'PY',
    pinPrefixes: ['60'],
    districts: ['Karaikal', 'Mahe', 'Puducherry', 'Yanam'],
    defaultPinByDistrict: {
      'Puducherry': '605001',
      'Karaikal': '609602',
      'Mahe': '673310',
      'Yanam': '533464'
    }
  },
  {
    name: 'Punjab',
    type: 'State',
    code: 'PB',
    pinPrefixes: ['14', '15'],
    districts: [
      'Amritsar',
      'Barnala',
      'Bathinda',
      'Faridkot',
      'Fatehgarh Sahib',
      'Fazilka',
      'Ferozepur',
      'Gurdaspur',
      'Hoshiarpur',
      'Jalandhar',
      'Kapurthala',
      'Ludhiana',
      'Malerkotla',
      'Mansa',
      'Moga',
      'Muktsar',
      'Pathankot',
      'Patiala',
      'Rupnagar',
      'Sahibzada Ajit Singh Nagar (Mohali)',
      'Sangrur',
      'Shahid Bhagat Singh Nagar',
      'Tarn Taran'
    ],
    defaultPinByDistrict: {
      'Ludhiana': '141001',
      'Amritsar': '143001',
      'Jalandhar': '144001',
      'Patiala': '147001',
      'Sahibzada Ajit Singh Nagar (Mohali)': '160055'
    }
  },
  {
    name: 'Rajasthan',
    type: 'State',
    code: 'RJ',
    pinPrefixes: ['30', '31', '32', '33', '34'],
    districts: [
      'Ajmer',
      'Alwar',
      'Anupgarh',
      'Balotra',
      'Banswara',
      'Baran',
      'Barmer',
      'Beawar',
      'Bharatpur',
      'Bhilwara',
      'Bikaner',
      'Bundi',
      'Chittorgarh',
      'Churu',
      'Dausa',
      'Deeg',
      'Dholpur',
      'Didwana-Kuchaman',
      'Dudu',
      'Dungarpur',
      'Ganganagar',
      'Gangapur City',
      'Hanumangarh',
      'Hindaun',
      'Jaipur',
      'Jaipur Rural',
      'Jaisalmer',
      'Jalore',
      'Jhalawar',
      'Jhunjhunu',
      'Jodhpur',
      'Jodhpur Rural',
      'Karauli',
      'Kekri',
      'Khairthal-Tijara',
      'Kota',
      'Kotputli-Behror',
      'Nagaur',
      'Neem Ka Thana',
      'Pali',
      'Phalodi',
      'Pratapgarh',
      'Rajsamand',
      'Salumbar',
      'Sanchore',
      'Sawai Madhopur',
      'Shahpura',
      'Sikar',
      'Sirohi',
      'Tonk',
      'Udaipur'
    ],
    defaultPinByDistrict: {
      'Jaipur': '302001',
      'Jodhpur': '342001',
      'Kota': '324001',
      'Udaipur': '313001',
      'Ajmer': '305001',
      'Bikaner': '334001'
    }
  },
  {
    name: 'Sikkim',
    type: 'State',
    code: 'SK',
    pinPrefixes: ['73'],
    districts: ['Gangtok', 'Gyalshing', 'Mangan', 'Namchi', 'Pakyong', 'Soreng'],
    defaultPinByDistrict: {
      'Gangtok': '737101',
      'Namchi': '737126',
      'Gyalshing': '737111',
      'Mangan': '737116'
    }
  },
  {
    name: 'Tamil Nadu',
    type: 'State',
    code: 'TN',
    pinPrefixes: ['60', '61', '62', '63', '64'],
    districts: [
      'Ariyalur',
      'Chengalpattu',
      'Chennai',
      'Coimbatore',
      'Cuddalore',
      'Dharmapuri',
      'Dindigul',
      'Erode',
      'Kallakurichi',
      'Kanchipuram',
      'Kanyakumari',
      'Karur',
      'Krishnagiri',
      'Madurai',
      'Mayiladuthurai',
      'Nagapattinam',
      'Namakkal',
      'Nilgiris',
      'Perambalur',
      'Pudukkottai',
      'Ramanathapuram',
      'Ranipet',
      'Salem',
      'Sivaganga',
      'Tenkasi',
      'Thanjavur',
      'Theni',
      'Thoothukudi',
      'Tiruchirappalli',
      'Tirunelveli',
      'Tirupathur',
      'Tiruppur',
      'Tiruvallur',
      'Tiruvannamalai',
      'Tiruvarur',
      'Vellore',
      'Viluppuram',
      'Virudhunagar'
    ],
    defaultPinByDistrict: {
      'Chennai': '600001',
      'Coimbatore': '641001',
      'Madurai': '625001',
      'Tiruchirappalli': '620001',
      'Salem': '636001',
      'Tiruppur': '641601'
    }
  },
  {
    name: 'Telangana',
    type: 'State',
    code: 'TG',
    pinPrefixes: ['50'],
    districts: [
      'Adilabad',
      'Bhadradri Kothagudem',
      'Hanumakonda',
      'Hyderabad',
      'Jagtial',
      'Jangaon',
      'Jayashankar Bhupalpally',
      'Jogulamba Gadwal',
      'Kamareddy',
      'Karimnagar',
      'Khammam',
      'Kumuram Bheem Asifabad',
      'Mahabubabad',
      'Mahabubnagar',
      'Mancherial',
      'Medak',
      'Medchal-Malkajgiri',
      'Mulugu',
      'Nagarkurnool',
      'Nalgonda',
      'Narayanpet',
      'Nirmal',
      'Nizamabad',
      'Peddapalli',
      'Rajanna Sircilla',
      'Ranga Reddy',
      'Sangareddy',
      'Siddipet',
      'Suryapet',
      'Vikarabad',
      'Wanaparthy',
      'Warangal',
      'Yadadri Bhuvanagiri'
    ],
    defaultPinByDistrict: {
      'Hyderabad': '500001',
      'Secunderabad': '500003',
      'Warangal': '506001',
      'Karimnagar': '505001',
      'Nizamabad': '503001'
    }
  },
  {
    name: 'Tripura',
    type: 'State',
    code: 'TR',
    pinPrefixes: ['79'],
    districts: [
      'Dhalai',
      'Gomati',
      'Khowai',
      'North Tripura',
      'Sepahijala',
      'South Tripura',
      'Unakoti',
      'West Tripura'
    ],
    defaultPinByDistrict: {
      'West Tripura': '799001',
      'Dhalai': '799278',
      'North Tripura': '799250'
    }
  },
  {
    name: 'Uttar Pradesh',
    type: 'State',
    code: 'UP',
    pinPrefixes: ['20', '21', '22', '23', '24', '25', '26', '27', '28'],
    districts: [
      'Agra',
      'Aligarh',
      'Ambedkar Nagar',
      'Amethi',
      'Amroha',
      'Auraiya',
      'Ayodhya',
      'Azamgarh',
      'Baghpat',
      'Bahraich',
      'Ballia',
      'Balrampur',
      'Banda',
      'Barabanki',
      'Bareilly',
      'Basti',
      'Bhadohi',
      'Bijnor',
      'Budaun',
      'Bulandshahr',
      'Chandauli',
      'Chitrakoot',
      'Deoria',
      'Etah',
      'Etawah',
      'Farrukhabad',
      'Fatehpur',
      'Firozabad',
      'Gautam Buddha Nagar (Noida)',
      'Ghaziabad',
      'Ghazipur',
      'Gonda',
      'Gorakhpur',
      'Hamirpur',
      'Hapur',
      'Hardoi',
      'Hathras',
      'Jalaun',
      'Jaunpur',
      'Jhansi',
      'Kannauj',
      'Kanpur Dehat',
      'Kanpur Nagar',
      'Kasganj',
      'Kaushambi',
      'Kheri',
      'Kushinagar',
      'Lalitpur',
      'Lucknow',
      'Maharajganj',
      'Mahoba',
      'Mainpuri',
      'Mathura',
      'Mau',
      'Meerut',
      'Mirzapur',
      'Moradabad',
      'Muzaffarnagar',
      'Pilibhit',
      'Pratapgarh',
      'Prayagraj (Allahabad)',
      'Raebareli',
      'Rampur',
      'Saharanpur',
      'Sambhal',
      'Sant Kabir Nagar',
      'Shahjahanpur',
      'Shamli',
      'Shravasti',
      'Siddharthnagar',
      'Sitapur',
      'Sonbhadra',
      'Sultanpur',
      'Unnao',
      'Varanasi'
    ],
    defaultPinByDistrict: {
      'Lucknow': '226001',
      'Kanpur Nagar': '208001',
      'Varanasi': '221001',
      'Prayagraj (Allahabad)': '211001',
      'Agra': '282001',
      'Gautam Buddha Nagar (Noida)': '201301',
      'Ghaziabad': '201001',
      'Meerut': '250001'
    }
  },
  {
    name: 'Uttarakhand',
    type: 'State',
    code: 'UK',
    pinPrefixes: ['24', '26'],
    districts: [
      'Almora',
      'Bageshwar',
      'Chamoli',
      'Champawat',
      'Dehradun',
      'Haridwar',
      'Nainital',
      'Pauri Garhwal',
      'Pithoragarh',
      'Rudraprayag',
      'Tehri Garhwal',
      'Udham Singh Nagar',
      'Uttarkashi'
    ],
    defaultPinByDistrict: {
      'Dehradun': '248001',
      'Haridwar': '249401',
      'Nainital': '263001',
      'Udham Singh Nagar': '263153'
    }
  },
  {
    name: 'West Bengal',
    type: 'State',
    code: 'WB',
    pinPrefixes: ['70', '71', '72', '73', '74'],
    districts: [
      'Alipurduar',
      'Bankura',
      'Birbhum',
      'Cooch Behar',
      'Dakshin Dinajpur',
      'Darjeeling',
      'Hooghly',
      'Howrah',
      'Jalpaiguri',
      'Jhargram',
      'Kalimpong',
      'Kolkata',
      'Malda',
      'Murshidabad',
      'Nadia',
      'North 24 Parganas',
      'Paschim Bardhaman',
      'Paschim Medinipur',
      'Purba Bardhaman',
      'Purba Medinipur',
      'Purulia',
      'South 24 Parganas',
      'Uttar Dinajpur'
    ],
    defaultPinByDistrict: {
      'Kolkata': '700001',
      'Howrah': '711101',
      'Darjeeling': '734101',
      'North 24 Parganas': '700124',
      'South 24 Parganas': '700144'
    }
  }
];

// Helper to look up state by name (case-insensitive)
export function getStateInfo(stateName: string): StateInfo | undefined {
  if (!stateName) return undefined;
  const clean = stateName.trim().toLowerCase();
  return INDIAN_STATES_AND_UTS.find(s => s.name.toLowerCase() === clean);
}

// Helper to retrieve all districts for a given state
export function getDistrictsForState(stateName: string): string[] {
  const state = getStateInfo(stateName);
  return state ? [...state.districts].sort() : [];
}

// Helper to check if a state name is valid
export function isValidState(stateName: string): boolean {
  return !!getStateInfo(stateName);
}

// Helper to check if a district belongs to a state
export function isDistrictInState(stateName: string, districtName: string): boolean {
  const districts = getDistrictsForState(stateName);
  const target = districtName.trim().toLowerCase();
  return districts.some(d => d.toLowerCase() === target);
}

// Get sample or default PIN for a district
export function getSamplePinForDistrict(stateName: string, districtName: string): string {
  const state = getStateInfo(stateName);
  if (!state) return '';
  if (state.defaultPinByDistrict && state.defaultPinByDistrict[districtName]) {
    return state.defaultPinByDistrict[districtName];
  }
  // Try case-insensitive lookup
  if (state.defaultPinByDistrict) {
    const key = Object.keys(state.defaultPinByDistrict).find(
      k => k.toLowerCase() === districtName.toLowerCase()
    );
    if (key) return state.defaultPinByDistrict[key];
  }
  // Fallback to first postal prefix + "001"
  if (state.pinPrefixes.length > 0) {
    return `${state.pinPrefixes[0]}0001`;
  }
  return '';
}

export interface PinValidationResult {
  isValid: boolean;
  error?: string;
  warning?: string;
}

/**
 * Validates an Indian PIN code against format and statutory state/district alignment
 */
export function validatePinCode(
  pinCode: string,
  stateName?: string,
  districtName?: string
): PinValidationResult {
  const trimmed = (pinCode || '').trim();

  // Check if empty
  if (!trimmed) {
    return {
      isValid: false,
      error: 'PIN Code is required.'
    };
  }

  // Check numeric only
  if (!/^\d+$/.test(trimmed)) {
    return {
      isValid: false,
      error: 'Only numbers are accepted.'
    };
  }

  // Check length exactly 6 digits
  if (trimmed.length !== 6) {
    return {
      isValid: false,
      error: 'PIN Code must contain exactly 6 digits.'
    };
  }

  // Check valid first digit (Indian postal codes start with 1-8)
  const firstDigit = trimmed[0];
  if (firstDigit === '0' || firstDigit === '9') {
    return {
      isValid: false,
      error: 'Invalid Indian PIN code prefix.'
    };
  }

  // If a state is selected, verify state-level postal circle alignment
  if (stateName) {
    const state = getStateInfo(stateName);
    if (state) {
      const prefix2 = trimmed.slice(0, 2);
      const prefix3 = trimmed.slice(0, 3);
      
      const matchesStatePrefix = state.pinPrefixes.includes(prefix2);
      
      if (!matchesStatePrefix) {
        // Find which state this PIN belongs to for a helpful message
        const matchedState = INDIAN_STATES_AND_UTS.find(s => s.pinPrefixes.includes(prefix2));
        const belongsToText = matchedState ? ` (belongs to ${matchedState.name})` : '';
        return {
          isValid: false,
          error: `PIN Code does not match the selected location.${belongsToText}`
        };
      }

      // Check district-level prefix override if defined
      if (districtName && state.districtPinOverrides && state.districtPinOverrides[districtName]) {
        const allowedOverrides = state.districtPinOverrides[districtName];
        if (!allowedOverrides.includes(prefix3) && !allowedOverrides.includes(prefix2)) {
          // Soft warning rather than hard blocking because district boundaries can overlap postal circles
          return {
            isValid: true,
            warning: `Note: PIN ${trimmed} is usually outside primary postal sub-circle for ${districtName}.`
          };
        }
      }
    }
  }

  return { isValid: true };
}
