// Test dynamic classification & rule applicability logic

function classifyProduct(data) {
  const combined = `${data.product_name} ${data.commodity_name || ''} ${data.generic_name || ''}`.toLowerCase();
  const origin = (data.country_of_origin || '').toLowerCase();
  const isImported = (origin.length > 0 && origin !== 'india') || Boolean(data.importer_name);
  const isMultipack = Boolean(data.total_multipack_quantity);
  const net = (data.net_quantity || '').toLowerCase();
  const isLiquid = /\b(?:ml|l|litre)\b/i.test(net) || /oil|shampoo|lotion|liquid|water/i.test(combined);

  let productType = 'Other packaged commodity';
  let isPerishable = false;
  let isScheduledCommodity = false;

  if (/biscuit|bread|tea|coffee|atta|flour|rice|food|snack/i.test(combined)) {
    productType = 'Food';
    isPerishable = true;
    isScheduledCommodity = /biscuit|bread|tea|coffee|atta|flour|rice/i.test(combined);
  } else if (/sunscreen|lotion|cream|shampoo|cosmetic|lipstick/i.test(combined)) {
    productType = 'Cosmetic/toiletry';
    isPerishable = true;
  } else if (/shirt|trouser|garment|bedsheet|towel/i.test(combined)) {
    productType = 'Clothing/textile';
    isPerishable = false;
  }

  return { productType, isImported, isMultipack, isLiquid, isPerishable, isScheduledCommodity };
}

function isRuleApplicable(ruleId, classification, data) {
  if (ruleId === 'RULE-5') {
    if (!classification.isScheduledCommodity) {
      return { applicable: false, reason: 'Exempt: Non-scheduled commodity under Second Schedule' };
    }
    return { applicable: true };
  }
  if (ruleId === 'RULE-6-1-DA') {
    if (!classification.isPerishable && classification.productType !== 'Food' && classification.productType !== 'Cosmetic/toiletry') {
      return { applicable: false, reason: 'Exempt: Non-perishable commodity' };
    }
    return { applicable: true };
  }
  if (ruleId === 'RULE-6-1-EA' || ruleId === 'RULE-6-11') {
    const netVal = parseFloat(data.net_quantity) || 0;
    const isGramOrMl = /^(?:g|gm|ml)\b/i.test((data.net_quantity || '').replace(/^[\d.\s]+/, ''));
    if (!classification.isMultipack && isGramOrMl && netVal < 1000) {
      return { applicable: false, reason: 'Exempt: Net quantity <= 1kg / 1L' };
    }
    return { applicable: true };
  }
  if (ruleId === 'RULE-6-1-G') {
    if (classification.productType !== 'Clothing/textile') {
      return { applicable: false, reason: 'Exempt: Non-dimensional commodity' };
    }
    return { applicable: true };
  }
  if (ruleId === 'RULE-24') {
    return { applicable: false, reason: 'Exempt: Retail package, not wholesale shipper' };
  }
  return { applicable: true };
}

console.log('--- Testing Product 1: Lakme Sunscreen 56g ---');
const lakme = {
  product_name: 'Lakmé Sunscreen Lotion',
  commodity_name: 'Sunscreen Lotion',
  net_quantity: '56 g',
  country_of_origin: 'India'
};
const cLakme = classifyProduct(lakme);
console.log('Lakme Classification:', cLakme.productType, '| Perishable:', cLakme.isPerishable, '| Scheduled:', cLakme.isScheduledCommodity);

const r5Lakme = isRuleApplicable('RULE-5', cLakme, lakme);
console.log('Rule 5 (Second Schedule standard sizes): Applicable?', r5Lakme.applicable, '| Reason:', r5Lakme.reason);
if (r5Lakme.applicable !== false) throw new Error('Rule 5 should be NOT APPLICABLE for cosmetic sunscreen!');

const rUspLakme = isRuleApplicable('RULE-6-1-EA', cLakme, lakme);
console.log('Rule 6(1)(ea) (USP for <=1kg): Applicable?', rUspLakme.applicable, '| Reason:', rUspLakme.reason);
if (rUspLakme.applicable !== false) throw new Error('USP should be optional/exempt for 56g package!');

console.log('\n--- Testing Product 2: Cotton Bedsheet (Textile) ---');
const bedsheet = {
  product_name: 'Pure Cotton Bedsheet',
  commodity_name: 'Bedsheet',
  net_quantity: '1 N',
  country_of_origin: 'India'
};
const cBedsheet = classifyProduct(bedsheet);
console.log('Bedsheet Classification:', cBedsheet.productType, '| Perishable:', cBedsheet.isPerishable);

const rExpiryBedsheet = isRuleApplicable('RULE-6-1-DA', cBedsheet, bedsheet);
console.log('Rule 6(1)(da) (Best Before on bedsheet): Applicable?', rExpiryBedsheet.applicable, '| Reason:', rExpiryBedsheet.reason);
if (rExpiryBedsheet.applicable !== false) throw new Error('Best Before should be NOT APPLICABLE for cotton bedsheet!');

const rDimBedsheet = isRuleApplicable('RULE-6-1-G', cBedsheet, bedsheet);
console.log('Rule 6(1)(g) (Dimensions on bedsheet): Applicable?', rDimBedsheet.applicable);
if (rDimBedsheet.applicable !== true) throw new Error('Dimensions should be APPLICABLE for cotton bedsheet!');

console.log('\n--- Testing Product 3: Wheat Flour (Atta 5kg Scheduled Food) ---');
const atta = {
  product_name: 'Chakki Fresh Atta',
  commodity_name: 'Wheat Flour',
  net_quantity: '5 kg',
  country_of_origin: 'India'
};
const cAtta = classifyProduct(atta);
console.log('Atta Classification:', cAtta.productType, '| Scheduled:', cAtta.isScheduledCommodity);

const r5Atta = isRuleApplicable('RULE-5', cAtta, atta);
console.log('Rule 5 (Standard pack sizes for Atta): Applicable?', r5Atta.applicable);
if (r5Atta.applicable !== true) throw new Error('Rule 5 should be APPLICABLE for scheduled food (wheat flour)!');

console.log('\n ALL DYNAMIC RULE APPLICABILITY TESTS PASSED WITH 100% ACCURACY!');
