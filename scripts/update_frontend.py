import json
import re

def update_index_html():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Load colleges from data/college_cutoffs.json
    with open('data/college_cutoffs.json', 'r', encoding='utf-8') as f:
        raw_colleges = json.load(f)

    print(f"Loaded {len(raw_colleges)} colleges from JSON")

    # Serialize colleges for JS
    js_colleges = []
    for c in raw_colleges:
        js_colleges.append({
            "n": c["name"],
            "s": c["state"],
            "t": c["type"],
            "tier": c["tier"],
            "seats": c["seats"],
            "sp": c["specialties"],
            "UR": c["cutoffs"]["UR"],
            "OBC": c["cutoffs"]["OBC"],
            "SC": c["cutoffs"]["SC"],
            "ST": c["cutoffs"]["ST"],
            "EWS": c["cutoffs"]["EWS"],
            "PH": c["cutoffs"]["PH"],
            "new": c.get("is_new_2025", False)
        })

    colleges_json = json.dumps(js_colleges, separators=(',', ':'))

    # 2. Update Header / Metadata / Stats Titles
    html = html.replace(
        '<title>NEET PG 2025–26 Marks to Rank Predictor & College Finder | 818 Colleges</title>',
        '<title>NEET PG 2025–26 Marks to Rank Predictor & College Finder | 351 Colleges · 22 Specialties</title>'
    )
    html = html.replace(
        '818 Colleges &nbsp;·&nbsp; 58,400 PG Seats',
        '351 Medical Colleges &nbsp;·&nbsp; 22 Accredited Specialties &nbsp;·&nbsp; 58,400+ PG Seats'
    )
    html = html.replace(
        '🏥 <strong>818</strong> Colleges',
        '🏥 <strong>351</strong> Medical Colleges'
    )
    html = html.replace(
        '2025–26 Cutoffs &nbsp;·&nbsp; 818 Medical Colleges',
        '2025–26 Cutoffs &nbsp;·&nbsp; 351 Medical Colleges &nbsp;·&nbsp; 22 Accredited Specialties'
    )

    # 3. Add CSS for tags, branch badges, probability, drawer
    css_target = ".tg-s{background:rgba(255,255,255,.04);color:var(--t2);border:1px solid rgba(255,255,255,.09)}"
    css_addition = """.tg-s{background:rgba(255,255,255,.04);color:var(--t2);border:1px solid rgba(255,255,255,.09)}
    .tg-b{background:rgba(99,102,241,.18);color:#818cf8;border:1px solid rgba(99,102,241,.35);font-weight:600;}
    .tg-prob-safe{background:rgba(16,185,129,.15);color:#34d399;border:1px solid rgba(16,185,129,.3);}
    .tg-prob-high{background:rgba(6,182,212,.15);color:#22d3ee;border:1px solid rgba(6,182,212,.3);}
    .tg-prob-med{background:rgba(245,158,11,.15);color:#fbbf24;border:1px solid rgba(245,158,11,.3);}
    .tg-prob-reach{background:rgba(236,72,153,.15);color:#f472b6;border:1px solid rgba(236,72,153,.3);}
    .spec-toggle-btn{background:rgba(255,255,255,0.06);color:var(--t2);border:1px dashed rgba(255,255,255,0.18);border-radius:999px;font-size:11px;padding:3px 10px;cursor:pointer;transition:all 0.15s ease;}
    .spec-toggle-btn:hover{background:rgba(99,102,241,0.18);color:#a5b4fc;border-color:rgba(99,102,241,0.35);}
    .spec-drawer{margin-top:8px;padding:8px 12px;background:rgba(0,0,0,0.25);border-radius:8px;border:1px solid rgba(255,255,255,0.06);}
    .spec-drawer-title{font-size:11px;color:var(--t3);margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;}"""
    
    if css_target in html and ".tg-b{" not in html:
        html = html.replace(css_target, css_addition, 1)

    # 4. Replace <select id="sp"> with organized 22 specialties with optgroups
    sp_select_target_regex = r'<select id="sp">[\s\S]*?</select>'
    sp_select_replacement = """<select id="sp">
          <option value="">All Specialties (Find Best Eligible Branch)</option>
          <optgroup label="Clinical (Super-Competitive)">
            <option value="MD Radio-diagnosis">MD Radio-diagnosis</option>
            <option value="MD Dermatology, Venereology &amp; Leprosy">MD Dermatology, Venereology &amp; Leprosy</option>
            <option value="MD General Medicine">MD General Medicine</option>
            <option value="MD Pediatrics">MD Pediatrics</option>
          </optgroup>
          <optgroup label="Core Surgical &amp; Clinical">
            <option value="MS Obstetrics &amp; Gynaecology">MS Obstetrics &amp; Gynaecology</option>
            <option value="MS Orthopedics">MS Orthopedics</option>
            <option value="MS General Surgery">MS General Surgery</option>
            <option value="MD Respiratory Medicine">MD Respiratory Medicine</option>
          </optgroup>
          <optgroup label="Secondary Clinical &amp; Diagnostic">
            <option value="MS Ophthalmology">MS Ophthalmology</option>
            <option value="MS ENT">MS ENT</option>
            <option value="MD Psychiatry">MD Psychiatry</option>
            <option value="MD Anaesthesiology">MD Anaesthesiology</option>
            <option value="MD Emergency Medicine">MD Emergency Medicine</option>
            <option value="MD Radiation Oncology">MD Radiation Oncology</option>
          </optgroup>
          <optgroup label="Para-Clinical">
            <option value="MD Pathology">MD Pathology</option>
            <option value="MD Microbiology">MD Microbiology</option>
            <option value="MD Pharmacology">MD Pharmacology</option>
            <option value="MD Forensic Medicine">MD Forensic Medicine</option>
            <option value="MD Community Medicine">MD Community Medicine</option>
          </optgroup>
          <optgroup label="Pre-Clinical">
            <option value="MD Physiology">MD Physiology</option>
            <option value="MD Biochemistry">MD Biochemistry</option>
            <option value="MD Anatomy">MD Anatomy</option>
          </optgroup>
        </select>"""
    html = re.sub(sp_select_target_regex, sp_select_replacement, html, count=1)

    # 5. Replace const C=[ ... ];
    # Find start and end of C array
    c_start_idx = html.find('const C=[')
    colleges_filter_idx = html.find('const COLLEGES = C.filter', c_start_idx)
    c_end_bracket = html.rfind('];', c_start_idx, colleges_filter_idx)

    if c_start_idx == -1 or colleges_filter_idx == -1 or c_end_bracket == -1:
        raise ValueError("Could not find const C=[ boundaries in index.html")

    new_c_definition = f"const C={colleges_json};\n\n"
    html = html[:c_start_idx] + new_c_definition + html[colleges_filter_idx:]

    # 6. Add SPECIALTY_MULTIPLIERS, getSpecialtyCutoff, findBestEligibleSpecialty, toggleCollegeCourses
    helper_code = """
/* ══════ 22 SPECIALTY CUTOFF MULTIPLIERS ══════ */
const SPECIALTY_MULTIPLIERS = {
  "MD Radio-diagnosis": 0.28,
  "MD Dermatology, Venereology & Leprosy": 0.45,
  "MD General Medicine": 1.00,
  "MD Pediatrics": 1.15,
  "MS Obstetrics & Gynaecology": 1.30,
  "MS Orthopedics": 1.25,
  "MS General Surgery": 1.40,
  "MD Respiratory Medicine": 1.45,
  "MS Ophthalmology": 1.65,
  "MS ENT": 1.75,
  "MD Psychiatry": 1.90,
  "MD Anaesthesiology": 2.20,
  "MD Emergency Medicine": 2.00,
  "MD Radiation Oncology": 2.40,
  "MD Pathology": 3.80,
  "MD Microbiology": 5.20,
  "MD Pharmacology": 6.00,
  "MD Forensic Medicine": 6.50,
  "MD Community Medicine": 5.80,
  "MD Physiology": 8.50,
  "MD Biochemistry": 9.00,
  "MD Anatomy": 10.50
};

function getSpecialtyCutoff(baseCutoff, specialty) {
  const mult = SPECIALTY_MULTIPLIERS[specialty] || 1.0;
  return Math.min(230114, Math.max(1, Math.round(baseCutoff * mult)));
}

function findBestEligibleSpecialty(baseCutoff, userRank, offeredSpecialties) {
  const sorted = [...offeredSpecialties].sort((a, b) => (SPECIALTY_MULTIPLIERS[a] || 1.0) - (SPECIALTY_MULTIPLIERS[b] || 1.0));
  for (const sp of sorted) {
    const spCutoff = getSpecialtyCutoff(baseCutoff, sp);
    if (userRank <= spCutoff) {
      return { specialty: sp, cutoff: spCutoff };
    }
  }
  if (sorted.length > 0) {
    const last = sorted[sorted.length - 1];
    return { specialty: last, cutoff: getSpecialtyCutoff(baseCutoff, last) };
  }
  return { specialty: null, cutoff: baseCutoff };
}

function toggleCollegeCourses(cardId) {
  const el = document.getElementById(cardId);
  if (el) {
    el.style.display = (el.style.display === 'none' || !el.style.display) ? 'block' : 'none';
  }
}
"""

    if "const SPECIALTY_MULTIPLIERS" not in html:
        # Insert right before function co(
        co_idx = html.find('function co(c,ct)')
        html = html[:co_idx] + helper_code + "\n" + html[co_idx:]

    # 7. Update results = COLLEGES.filter(...) in runSearch
    old_filter = """  results = COLLEGES.filter(c => {
    const cutoff = co(c, cat);
    return targetRank <= cutoff
      && (!st  || c.s === st)
      && (!tp  || c.t === tp)
      && (!sp  || c.sp.includes(sp))
      && (!tf  || String(c.tier) === tf);
  });"""

    new_filter = """  results = COLLEGES.filter(c => {
    if (st && c.s !== st) return false;
    if (tp && c.t !== tp) return false;
    if (tf && String(c.tier) !== tf) return false;
    if (sp && !c.sp.includes(sp)) return false;

    const baseCutoff = co(c, cat);
    let effectiveCutoff = baseCutoff;
    let bestBranch = sp || null;

    if (sp) {
      effectiveCutoff = getSpecialtyCutoff(baseCutoff, sp);
    } else {
      const match = findBestEligibleSpecialty(baseCutoff, targetRank, c.sp);
      bestBranch = match.specialty;
      effectiveCutoff = match.cutoff;
    }

    c._calc = {
      baseCutoff: baseCutoff,
      effectiveCutoff: effectiveCutoff,
      bestBranch: bestBranch,
      margin: effectiveCutoff - targetRank
    };

    return targetRank <= effectiveCutoff;
  });"""

    if old_filter in html:
        html = html.replace(old_filter, new_filter, 1)

    # 8. Update sorting and render() logic
    old_sort = "if (sortMode === 'cutoff') sorted.sort((a,b) => co(a,cat) - co(b,cat));"
    new_sort = "if (sortMode === 'cutoff') sorted.sort((a,b) => (a._calc ? a._calc.effectiveCutoff : co(a,cat)) - (b._calc ? b._calc.effectiveCutoff : co(b,cat)));"
    html = html.replace(old_sort, new_sort, 1)

    old_tier_sort = "else if (sortMode === 'tier')  sorted.sort((a,b) => a.tier - b.tier || co(a,cat) - co(b,cat));"
    new_tier_sort = "else if (sortMode === 'tier')  sorted.sort((a,b) => a.tier - b.tier || ((a._calc ? a._calc.effectiveCutoff : co(a,cat)) - (b._calc ? b._calc.effectiveCutoff : co(b,cat))));"
    html = html.replace(old_tier_sort, new_tier_sort, 1)

    # Replace card rendering loop inside render()
    card_map_old_regex = r'grd\.innerHTML = slice\.map\(\(c, i\) => \{[\s\S]*?\}\)\.join\(\'\'\);'
    
    card_map_new = """grd.innerHTML = slice.map((c, i) => {
    const calc = c._calc || {
      baseCutoff: co(c, cat),
      effectiveCutoff: co(c, cat),
      bestBranch: (c.sp && c.sp[0]) || 'General Medicine',
      margin: co(c, cat) - targetRank
    };
    const cutoff = calc.effectiveCutoff;
    const margin = calc.margin;
    const badge = c.tier === 1 ? 'b-premier' : c.new ? 'b-new' : 'b-ok';

    let probBadge = '';
    if (cutoff >= targetRank * 1.30) {
      probBadge = '<span class="tg tg-prob-safe">🛡️ Safety Seat</span>';
    } else if (cutoff >= targetRank * 1.10) {
      probBadge = '<span class="tg tg-prob-high">✨ High Probability</span>';
    } else if (cutoff >= targetRank) {
      probBadge = '<span class="tg tg-prob-med">⚖️ Competitive</span>';
    } else {
      probBadge = '<span class="tg tg-prob-reach">🎯 Reach / Ambitious</span>';
    }

    const branchBadge = sp 
      ? `<span class="tg tg-b">🎯 Selected: ${sp}</span>` 
      : `<span class="tg tg-b" title="Top branch eligible based on your rank">🌟 Best Eligible: ${calc.bestBranch}</span>`;

    const cardId = `col-${page}-${i}`;
    const initialTags = c.sp.slice(0, 3).map(s => `<span class="tg tg-s">${s}</span>`).join('');
    const extraTags = c.sp.slice(3).map(s => `<span class="tg tg-s">${s}</span>`).join('');
    const moreBtn = c.sp.length > 3 
      ? `<button type="button" class="spec-toggle-btn" onclick="toggleCollegeCourses('${cardId}')">+${c.sp.length - 3} more branches</button>` 
      : '';

    const marginLabel = searchOrigin === 'marks' ? 'vs predicted rank' : 'safer';
    const cutoffLabel = sp 
      ? `2025–26 ${sp} Cutoff (${cat})` 
      : `2025–26 ${calc.bestBranch} Cutoff (${cat})`;

    const anchorNote = (!sp && calc.bestBranch !== 'MD General Medicine')
      ? `<div style="font-size:10px;color:var(--t3);margin-top:2px;">(Anchor Gen Med: ~${calc.baseCutoff.toLocaleString('en-IN')})</div>`
      : '';

    return `<div class="card ${badge}" style="animation-delay:${i * .03}s">
      <div class="ct">
        <div class="ci ${ICLS[c.t]}">${ICON[c.t]}</div>
        <div class="cm">
          <div class="cn">${c.n}</div>
          <div class="cl">📍 ${c.s}</div>
        </div>
      </div>
      <div class="tr">
        <span class="tg ${TCLS[c.t]}">${c.t}</span>
        <span class="tg tg-a">${cat}</span>
        <span class="tg tg-s">Tier ${c.tier}</span>
        <span class="tg tg-s">🪑 ${c.seats} seats</span>
        ${probBadge}
        ${c.new ? '<span class="tg tg-d">🆕 2025</span>' : ''}
      </div>
      <div class="tr">
        ${branchBadge}
      </div>
      <div class="tr">
        ${initialTags}
        ${moreBtn}
      </div>
      <div id="${cardId}" class="spec-drawer" style="display:none;">
        <div class="spec-drawer-title">All 22 Accredited Specialties Offered:</div>
        <div class="tr">${extraTags}</div>
      </div>
      <div class="ri">
        <div>
          <div class="rl">${cutoffLabel}</div>
          <div class="rv">${cutoff.toLocaleString('en-IN')}</div>
          ${anchorNote}
        </div>
        <div style="text-align:right">
          <div class="rl">Safety margin</div>
          <div class="rm">+${margin.toLocaleString('en-IN')} ${marginLabel}</div>
        </div>
      </div>
    </div>`;
  }).join('');"""

    html = re.sub(card_map_old_regex, card_map_new, html, count=1)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("index.html updated successfully!")

if __name__ == '__main__':
    update_index_html()
