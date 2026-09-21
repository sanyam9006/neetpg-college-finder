const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

const createElem = () => ({
  style: {},
  classList: { add: ()=>{}, remove: ()=>{}, toggle: ()=>{} },
  addEventListener: ()=>{},
  value: '',
  textContent: '',
  innerHTML: ''
});

const elements = {
  cs: { value: 'UR', style: {} },
  ss: { value: '', style: {} },
  ts: { value: '', style: {} },
  sp: { value: '', style: {} },
  tierf: { value: '', style: {} },
  mi: { value: '600', style: {}, addEventListener: ()=>{} },
  ri: { value: '5000', style: {}, addEventListener: ()=>{} },
  res: { style: {}, scrollIntoView: () => {} },
  grd: { innerHTML: '' },
  pgn: { innerHTML: '' },
  predBanner: { style: {} },
  bannerRank: { textContent: '' },
  bannerScore: { textContent: '' },
  bannerRange: { textContent: '' },
  bannerPct: { textContent: '' },
  bannerCat: { textContent: '' },
  rl: { textContent: '' },
  cnt: { textContent: '' },
  'inicet-note': { style: {} },
  s1: { classList: { add: ()=>{}, remove: ()=>{} } },
  themeIcon: { textContent: '' },
  themeText: { textContent: '' },
  themeToggleBtn: { addEventListener: ()=>{} },
  authModal: { style: {}, addEventListener: ()=>{} },
  rankModal: { style: {}, addEventListener: ()=>{} },
  feedbackModal: { style: {}, addEventListener: ()=>{} },
  authHeaderWidget: { innerHTML: '' }
};

global.document = {
  getElementById: (id) => elements[id] || createElem(),
  querySelectorAll: () => [],
  documentElement: {
    setAttribute: (attr, val) => { elements.theme = val; },
    getAttribute: (attr) => elements.theme || 'light'
  }
};
global.window = { location: { protocol: 'http:' }, scrollTo: () => {} };
global.localStorage = {
  store: {
    neetpg_user: JSON.stringify({ name: 'Dr. Aspirant', email: 'aspirant@neet.com', batch: '2023' }),
    neetpg_theme: 'light'
  },
  getItem: (k) => global.localStorage.store[k] || null,
  setItem: (k, v) => { global.localStorage.store[k] = v; }
};
global.fetch = () => Promise.resolve({ ok: true, json: () => Promise.resolve({ status: 'healthy', models_loaded: [800], colleges_loaded: 351 }) });

const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) throw new Error('No script found');

const testRunner = `
currentUser = { name: 'Dr. Aspirant', email: 'aspirant@neet.com', batch: '2023' };

console.log('=== TEST 1: Theme System ===');
console.log('Default Theme:', document.documentElement.getAttribute('data-theme'));
toggleTheme();
console.log('Toggled Theme:', document.documentElement.getAttribute('data-theme'));
toggleTheme();
console.log('Toggled Back:', document.documentElement.getAttribute('data-theme'));

console.log('\\n=== TEST 2: Marks Search = 600 (UR, All Branches) ===');
activeMode = 'marks';
elements.mi.value = '600';
elements.sp.value = '';
runSearch();

console.log('Predicted Rank:', targetRank);
console.log('Banner Rank text:', elements.bannerRank.textContent);
console.log('Colleges returned count:', results.length);

const cardHtml = elements.grd.innerHTML;
console.log('Contains [object HTMLSelectElement]:', cardHtml.includes('[object HTMLSelectElement]'));
console.log('Contains "View Branch-Wise Cutoffs":', cardHtml.includes('View Branch-Wise Cutoffs'));
console.log('Contains "Branches Eligible":', cardHtml.includes('Branches Eligible'));

if (cardHtml.includes('[object HTMLSelectElement]')) {
  throw new Error('FAILED: Found [object HTMLSelectElement] in card output!');
}

console.log('\\n=== TEST 3: Specialty Search = MD Radio-diagnosis ===');
elements.sp.value = 'MD Radio-diagnosis';
runSearch();
const radioCardHtml = elements.grd.innerHTML;
console.log('Radio-diagnosis colleges eligible:', results.length);
console.log('Contains [object HTMLSelectElement]:', radioCardHtml.includes('[object HTMLSelectElement]'));
console.log('Contains "MD Radio-diagnosis":', radioCardHtml.includes('MD Radio-diagnosis'));

if (radioCardHtml.includes('[object HTMLSelectElement]')) {
  throw new Error('FAILED: Found [object HTMLSelectElement] in specialty search!');
}

console.log('\\n=== TEST 4: Branch-Wise Cutoffs for SMS Medical College Jaipur ===');
const sms = COLLEGES.find(c => c.n.includes('SMS Medical'));
if (sms) {
  const branches = getCollegeBranchDetails(sms, targetRank, 'UR');
  console.log('College:', sms.n, '| Base UR Cutoff (Gen Med):', sms.UR);
  console.log('Total branches:', branches.length);
  for (const b of branches.slice(0, 8)) {
    console.log('  - ' + b.name.padEnd(38) + ': Cutoff = ' + b.cutoff.toString().padStart(6) + ' | Margin = ' + (b.margin > 0 ? '+' : '') + b.margin.toString().padStart(6) + ' | Status = ' + b.probText);
  }
}

console.log('\\n=== ALL DOM & SIMULATION TESTS PASSED! ===');
`;

eval(scriptMatch[1] + '\n' + testRunner);

