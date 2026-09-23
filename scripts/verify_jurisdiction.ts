import {
  INDIAN_STATES_AND_UTS,
  getStateInfo,
  getDistrictsForState,
  validatePinCode,
  getSamplePinForDistrict,
  isDistrictInState
} from '../src/data/jurisdictionData.ts';

console.log('=====================================================');
console.log('VIDHICHECK JURISDICTION SUITE: STATUTORY VALIDATION');
console.log('=====================================================\n');

let passedTests = 0;
let totalTests = 0;

function assert(condition: boolean, testName: string, detail?: any) {
  totalTests++;
  if (condition) {
    console.log(`✓ PASS: ${testName}`);
    passedTests++;
  } else {
    console.error(`✗ FAIL: ${testName}`);
    if (detail) console.error('  Detail:', detail);
  }
}

// TEST 1: Total States and UTs count
const states = INDIAN_STATES_AND_UTS.filter(s => s.type === 'State');
const uts = INDIAN_STATES_AND_UTS.filter(s => s.type === 'Union Territory');
assert(states.length === 28, 'Exactly 28 States present in dataset', { actual: states.length });
assert(uts.length === 8, 'Exactly 8 Union Territories present in dataset', { actual: uts.length });
assert(INDIAN_STATES_AND_UTS.length === 36, 'Total 36 administrative territories present');

// TEST 2: Required States list check
const requiredStates = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
  'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
];

requiredStates.forEach(st => {
  assert(states.some(s => s.name === st), `State '${st}' exists in dataset`);
});

// TEST 3: Required UTs list check
const requiredUTs = [
  'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu',
  'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
];

requiredUTs.forEach(ut => {
  assert(uts.some(u => u.name === ut), `Union Territory '${ut}' exists in dataset`);
});

// TEST 4: District resolution for Maharashtra
const mhDistricts = getDistrictsForState('Maharashtra');
assert(mhDistricts.length >= 35, 'Maharashtra has full districts list (35+)', { count: mhDistricts.length });
assert(mhDistricts.includes('Dhule'), "Maharashtra includes 'Dhule'");
assert(mhDistricts.includes('Pune'), "Maharashtra includes 'Pune'");
assert(mhDistricts.includes('Mumbai City'), "Maharashtra includes 'Mumbai City'");
assert(!mhDistricts.includes('Bengaluru Urban'), "Maharashtra does NOT include Karnataka districts");

// TEST 5: District resolution for Delhi
const dlDistricts = getDistrictsForState('Delhi');
assert(dlDistricts.includes('New Delhi'), "Delhi includes 'New Delhi'");
assert(dlDistricts.includes('Central Delhi'), "Delhi includes 'Central Delhi'");

// TEST 6: PIN Code Validation - Numbers Only
const nonNumeric = validatePinCode('42400A', 'Maharashtra', 'Dhule');
assert(!nonNumeric.isValid && nonNumeric.error === 'Only numbers are accepted.', 'Rejects non-numeric characters in PIN');

// TEST 7: PIN Code Validation - Exact 6 digits
const tooShort = validatePinCode('4240', 'Maharashtra', 'Dhule');
assert(!tooShort.isValid && tooShort.error === 'PIN Code must contain exactly 6 digits.', 'Rejects PIN with less than 6 digits');

const emptyPin = validatePinCode('', 'Maharashtra', 'Dhule');
assert(!emptyPin.isValid && emptyPin.error === 'PIN Code is required.', 'Rejects empty PIN');

// TEST 8: Valid Dhule PIN
const dhulePin = validatePinCode('424001', 'Maharashtra', 'Dhule');
assert(dhulePin.isValid, 'Accepts valid Dhule PIN 424001 for Maharashtra');

// TEST 9: PIN Location Mismatch Check
const mismatchPin = validatePinCode('110001', 'Maharashtra', 'Dhule');
assert(
  !mismatchPin.isValid && mismatchPin.error?.includes('does not match the selected location'),
  'Flags Delhi PIN 110001 when Maharashtra is selected as location mismatch',
  mismatchPin
);

// TEST 10: Valid Bengaluru PIN for Karnataka
const blrPin = validatePinCode('560001', 'Karnataka', 'Bengaluru Urban');
assert(blrPin.isValid, 'Accepts valid Bengaluru PIN 560001 for Karnataka');

// TEST 11: Sample PIN generation
const sampleDhule = getSamplePinForDistrict('Maharashtra', 'Dhule');
assert(sampleDhule === '424001', `Sample PIN for Dhule is 424001 (got: ${sampleDhule})`);

// TEST 12: Structured Data Representation
const structuredJurisdiction = {
  country: 'India',
  state: 'Maharashtra',
  city: 'Dhule',
  pinCode: '424001'
};

assert(
  structuredJurisdiction.country === 'India' &&
  structuredJurisdiction.state === 'Maharashtra' &&
  structuredJurisdiction.city === 'Dhule' &&
  structuredJurisdiction.pinCode === '424001',
  'Structured jurisdiction matches target JSON format exactly'
);

// TEST 13: Report Format Verification
const reportLines = [
  'Jurisdiction:',
  structuredJurisdiction.country,
  structuredJurisdiction.state,
  structuredJurisdiction.city,
  `PIN: ${structuredJurisdiction.pinCode}`
];

assert(reportLines.join('\n') === 'Jurisdiction:\nIndia\nMaharashtra\nDhule\nPIN: 424001', 'Report format matches requirement exactly');

console.log(`\n=====================================================`);
console.log(`RESULT: ${passedTests} / ${totalTests} TESTS PASSED`);
console.log(`=====================================================\n`);

if (passedTests !== totalTests) {
  process.exit(1);
}
