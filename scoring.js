// Fit Score algorithm — tailored to Fadi's golden path
// 0-100 score based on weighted axes that matter for HIM
//
// Context: 27yo, YOUNGEST attending at CVH (peers won't come from work),
// 100km/wk runner, single (just out of LTR), downtown-curious post-NYC,
// type: white/Asian/Jewish women, open to US relocation partners.
//
// Axes (weights sum to 100):
//   30 — CVH commute (peak min)        // job — but reverse-commute friendly
//   22 — Singles-scene zone density    // YOU WON'T FIND PEERS AT CVH (youngest attending) — env matters
//   20 — Running (winter trail access) // 100km/wk identity
//   13 — Cost vs budget                 // important but #4
//    8 — Toronto access (Union/King W) // dating + social — but Singles-scene captures most
//    4 — Building rating quality
//    3 — Sqft vs price

window.computeFitScore = function(a, costs, osrm) {
  let score = 0;
  const breakdown = [];

  // 1. CVH commute (30 pts max)
  // ER attending shifts deliberately avoid 8am rush (start 7/11am/3pm/7pm/11pm).
  // Use OSRM off-peak directly with a smaller (×1.15) multiplier for realistic lived experience.
  const osrmRoute = (osrm || window.OSRM || {})[a.id];
  let timeUsed, source;
  if (osrmRoute) {
    timeUsed = Math.round(osrmRoute.duration_min * 1.15);
    source = `${osrmRoute.duration_min}m OSRM off-peak (~${timeUsed}m lived)`;
  } else {
    timeUsed = a.drive_to_cvh_min_peak || 99;
    source = `${timeUsed}m peak (est)`;
  }
  let cvhPts = 0;
  if (timeUsed <= 10) cvhPts = 30;       // walking/very close
  else if (timeUsed <= 18) cvhPts = 26;  // tier-1 commute (Markwood lives here)
  else if (timeUsed <= 25) cvhPts = 20;  // acceptable (Humber Bay lives here)
  else if (timeUsed <= 32) cvhPts = 12;  // long
  else if (timeUsed <= 45) cvhPts = 5;
  score += cvhPts;
  breakdown.push({k: 'CVH commute', v: cvhPts, max: 30, note: source});

  // 2. Singles-scene zone density (22 pts) — YOU WON'T FIND PEERS AT CVH (youngest attending)
  let singlesPts = 6; // baseline (no data)
  const ds = (window.DATING_SCENE && window.DATING_SCENE.zones) || {};
  const dsKey = Object.keys(ds).find(k => k.toLowerCase() === (a.zone||'').toLowerCase()) || Object.keys(ds).find(k => (a.zone||'').toLowerCase().includes(k.split('/')[0].trim().toLowerCase()));
  const datingScore = dsKey ? ds[dsKey].single_density_score : null;
  if (datingScore !== null && datingScore !== undefined) {
    // Map 0-100 dating score → 0-22 pts
    singlesPts = Math.round(datingScore * 0.22);
  }
  score += singlesPts;
  breakdown.push({k: 'Singles scene', v: singlesPts, max: 22, note: dsKey ? `${dsKey} = ${datingScore}/100` : 'no zone data'});

  // 3. Running (20 pts) — proximity + winter access
  let runPts = 8; // baseline
  const zone = (a.zone || '').toLowerCase();
  const running = (a.running || '').toLowerCase();
  if (running.includes('martin goodman') || running.includes('humber bay')) runPts = 20;
  else if (running.includes('sawmill') || running.includes('culham') || running.includes('riverwood')) runPts = 18;
  else if (running.includes('lakefront') || running.includes('rattray') || running.includes('jack darling')) runPts = 16;
  else if (running.includes('etobicoke creek') || running.includes('centennial')) runPts = 14;
  else if (running.includes('burnhamthorpe') || running.includes('applewood')) runPts = 15;
  else if (running.includes('cooksville')) runPts = 10;
  score += runPts;
  breakdown.push({k: 'Running', v: runPts, max: 20, note: 'Trail proximity + winter access'});

  // 4. Cost (13 pts)
  const rent = a.rent_1bed_low || a.rent_2bed || 9999;
  const c = costs && costs[a.id];
  const effectiveRent = c?.net_effective_1bed || rent;
  const totalEst = c?.estimated_monthly_total_1bed || (rent + 100);
  let costPts = 0;
  if (totalEst <= 1900) costPts = 13;
  else if (totalEst <= 2100) costPts = 11;
  else if (totalEst <= 2300) costPts = 8;
  else if (totalEst <= 2500) costPts = 5;
  else if (totalEst <= 2700) costPts = 3;
  else costPts = 1;
  score += costPts;
  breakdown.push({k: 'Cost', v: costPts, max: 13, note: `~$${totalEst}/mo all-in`});

  // 5. Toronto access (8 pts) — King West / Union (real OSRM via destinations.json)
  const dest = ((window.DESTINATIONS && window.DESTINATIONS.routes) || {})[a.id];
  const kwMin = dest?.king_west?.duration_min;
  const u = kwMin || a.drive_to_union_min_offpeak || 99;
  let torPts = 0;
  if (u <= 15) torPts = 8;
  else if (u <= 22) torPts = 6;
  else if (u <= 30) torPts = 4;
  else if (u <= 40) torPts = 2;
  score += torPts;
  breakdown.push({k: 'Toronto access', v: torPts, max: 8, note: kwMin?`${kwMin.toFixed(0)}m to King West (OSRM)`:`${u}m Union (est)`});

  // 6. Building rating (4 pts) — PUNISH unverified condos (declaration pending), AVOIDs, CAUTIONs
  let bldgPts = 2;
  const r = (a.rating || '').toUpperCase();
  const isUnverifiedCondo = /pending\s+condo\s+declaration|pending\s+declaration|condo.*unverified/i.test(a.rating || '');
  if (isUnverifiedCondo) bldgPts = -8; // we can't recommend a unit when we don't know if pets allowed, fees, rent vs sale
  else if (r.startsWith('GOOD')) bldgPts = 4;
  else if (r.startsWith('FINE') || r.startsWith('POTENTIAL') || r.startsWith('STRETCH')) bldgPts = 2;
  else if (r.startsWith('CAUTION')) bldgPts = -10;
  else if (r.startsWith('AVOID')) bldgPts = -25;
  score += bldgPts;
  breakdown.push({k: 'Building rep', v: bldgPts, max: 4, note: a.rating || 'unknown'});

  // 7. Value (3 pts)
  const sqft = a.sqft_high || a.sqft_low || 600;
  const sqftPerDollar = sqft / Math.max(rent, 1);
  let valPts = 0;
  if (sqftPerDollar > 0.40) valPts = 3;
  else if (sqftPerDollar > 0.32) valPts = 2;
  else valPts = 1;
  score += valPts;
  breakdown.push({k: 'Value (sqft/$)', v: valPts, max: 3, note: `${sqft}sf @ $${rent}`});

  return {score: Math.round(score), breakdown};
};

// Fit score color
window.fitScoreColor = function(score) {
  if (score >= 75) return '#4ade80';
  if (score >= 60) return '#a3e635';
  if (score >= 45) return '#fbbf24';
  if (score >= 30) return '#fb923c';
  return '#f87171';
};

// ============================================================
// AXIS PROFILE — five independent 0-100 axes + qualitative narrative.
// This replaces the single Fit Score on cards. Each axis is independently
// interpretable: you can be commute-good AND singles-bad at the same time,
// which is the actual Mississauga vs Toronto tradeoff.
// ============================================================
window.computeAxisProfile = function(a) {
  const osrm = (window.OSRM||{})[a.id];
  const dest = ((window.DESTINATIONS && window.DESTINATIONS.routes) || {})[a.id];
  const costs = (window.COSTS||{})[a.id];
  const visual = (window.VISUAL_NOTES||{})[a.id];
  const zones = (window.DATING_SCENE && window.DATING_SCENE.zones) || {};
  const zoneKey = Object.keys(zones).find(k => k.toLowerCase() === (a.zone||'').toLowerCase())
              || Object.keys(zones).find(k => (a.zone||'').toLowerCase().includes(k.split('/')[0].trim().toLowerCase()));
  const zone = zoneKey ? zones[zoneKey] : null;

  // ===== AXES (0-100 each, independent) =====

  // 1. CVH commute — piecewise: 5min=100, 15min=90, 20min=75, 25min=60, 30min=40, 35min=25, 45min=0
  const cvhMin = osrm ? osrm.duration_min : (a.drive_to_cvh_min_peak || 30);
  let cvh;
  if (cvhMin <= 5) cvh = 100;
  else if (cvhMin <= 15) cvh = 100 - (cvhMin - 5) * 1.0;       // 5→100, 15→90
  else if (cvhMin <= 25) cvh = 90 - (cvhMin - 15) * 3;          // 15→90, 25→60
  else if (cvhMin <= 35) cvh = 60 - (cvhMin - 25) * 3.5;        // 25→60, 35→25
  else if (cvhMin <= 45) cvh = Math.max(0, 25 - (cvhMin - 35) * 2.5);
  else cvh = 0;
  cvh = Math.round(cvh);

  // 2. Singles density — directly from zone dating score
  let singles = zone ? zone.single_density_score : 30; // baseline if unknown
  singles = Math.round(singles);

  // 3. Running — proximity + trail quality
  const r = (a.running || '').toLowerCase();
  let running;
  if (/martin goodman|humber bay shores park/.test(r)) running = 95;       // gold standard waterfront
  else if (/lakefront promenade|marie curtis|jack darling|rattray/.test(r)) running = 85;
  else if (/sawmill|culham|riverwood|burnhamthorpe/.test(r)) running = 80;
  else if (/etobicoke creek|centennial park/.test(r)) running = 75;
  else if (/applewood|cooksville creek/.test(r)) running = 60;
  else if (/sherway|west deane|cooksville/.test(r)) running = 50;
  else running = 35;

  // 4. Cost — lower = better; based on all-in monthly
  const rent = a.rent_1bed_low || a.rent_2bed || 9999;
  const allIn = costs?.estimated_monthly_total_1bed || (rent + 100);
  let cost;
  if (allIn <= 1700) cost = 100;
  else if (allIn <= 2000) cost = 100 - (allIn - 1700) / 300 * 15;   // 1700→100, 2000→85
  else if (allIn <= 2300) cost = 85 - (allIn - 2000) / 300 * 20;    // 2000→85, 2300→65
  else if (allIn <= 2700) cost = 65 - (allIn - 2300) / 400 * 30;    // 2300→65, 2700→35
  else if (allIn <= 3200) cost = 35 - (allIn - 2700) / 500 * 25;
  else cost = Math.max(0, 10 - (allIn - 3200) / 500 * 10);
  cost = Math.round(cost);

  // 5. Toronto access — King West drive time (real OSRM via destinations)
  const kwMin = dest?.king_west?.duration_min || a.drive_to_union_min_offpeak || 35;
  let toronto;
  if (kwMin <= 10) toronto = 100;
  else if (kwMin <= 15) toronto = 100 - (kwMin - 10) * 2;            // 10→100, 15→90
  else if (kwMin <= 25) toronto = 90 - (kwMin - 15) * 4;             // 15→90, 25→50
  else if (kwMin <= 35) toronto = 50 - (kwMin - 25) * 3;             // 25→50, 35→20
  else toronto = Math.max(0, 20 - (kwMin - 35) * 2);
  toronto = Math.round(toronto);

  // ===== QUALITATIVE =====
  const ratingUp = (a.rating || '').toUpperCase();
  const warningBadge = ratingUp.startsWith('AVOID') ? {label:'AVOID', color:'#dc2626'}
                     : ratingUp.startsWith('CAUTION') ? {label:'CAUTION', color:'#ea580c'}
                     : /pending\s+condo\s+declaration/i.test(a.rating||'') ? {label:'UNVERIFIED CONDO', color:'#ca8a04'}
                     : null;

  // Zone vibe — one-liner from dating_scene.json honest_vibe (truncated)
  let zoneVibe = zone?.honest_vibe || '';
  if (zoneVibe.length > 140) zoneVibe = zoneVibe.slice(0, 137).replace(/\s\S*$/, '') + '…';

  // Building-specific honest note (AI photo audit)
  const buildingNote = visual?.honest_note || '';

  return {
    axes: { cvh, singles, running, cost, toronto },
    raw: { cvh_min: Math.round(cvhMin), singles_score: zone?.single_density_score, rent, kw_min: Math.round(kwMin), all_in: allIn },
    qualitative: { zone_vibe: zoneVibe, building_note: buildingNote, warning: warningBadge, zone_label: zoneKey || a.zone },
    total: Math.round((cvh + singles + running + cost + toronto) / 5),
  };
};

// Color for an axis bar (red→amber→green)
window.axisColor = function(v) {
  if (v >= 80) return '#22c55e';     // green
  if (v >= 65) return '#84cc16';     // lime
  if (v >= 50) return '#eab308';     // amber
  if (v >= 35) return '#f97316';     // orange
  return '#ef4444';                  // red
};

// Render the 5-bar profile inline (compact, for cards)
window.renderAxisProfile = function(profile, opts) {
  opts = opts || {};
  const compact = opts.compact !== false;
  const labelW = compact ? 52 : 80;
  const barW = compact ? 90 : 160;
  const barH = compact ? 5 : 8;
  const axes = [
    {k: 'CVH', v: profile.axes.cvh, suffix: profile.raw.cvh_min + 'm'},
    {k: 'Single', v: profile.axes.singles, suffix: profile.raw.singles_score != null ? profile.raw.singles_score : '?'},
    {k: 'Run', v: profile.axes.running, suffix: ''},
    {k: 'Cost', v: profile.axes.cost, suffix: '$' + (profile.raw.rent || '?').toLocaleString()},
    {k: 'Toronto', v: profile.axes.toronto, suffix: profile.raw.kw_min + 'm'},
  ];
  const rows = axes.map(ax => `
    <div style="display:grid;grid-template-columns:${labelW}px ${barW}px 32px;gap:6px;align-items:center;font-size:${compact?'10px':'12px'};line-height:1.2;color:var(--muted)">
      <span style="text-align:right">${ax.k}</span>
      <span style="background:var(--panel-2);border-radius:2px;height:${barH}px;display:block;overflow:hidden;position:relative">
        <span style="background:${window.axisColor(ax.v)};height:100%;width:${ax.v}%;display:block;border-radius:2px"></span>
      </span>
      <span style="font-variant-numeric:tabular-nums;color:var(--text);font-weight:500;text-align:right">${ax.suffix}</span>
    </div>`).join('');
  return `<div style="display:flex;flex-direction:column;gap:${compact?'2px':'4px'}">${rows}</div>`;
};

// === ALGORITHMIC TOP PICKS — generated from live data, not hand-curated ===
window.computeTopPicks = function() {
  const all = (window.APARTMENTS || []).map(a => ({
    a,
    fit: window.computeFitScore(a, window.COSTS||{}, window.OSRM||{}).score,
    cost: (window.COSTS||{})[a.id],
    review: (window.REVIEWS||{})[a.id],
    drive: (window.DRIVE_MATRIX||{})[a.id],
    osrm: (window.OSRM||{})[a.id],
    parking: (window.PARKING||{})[a.id]
  }));

  function score(x, fn) { return all.filter(x => x.a.lat && x.a.lng).map(x => ({ x, s: fn(x) })).sort((a,b)=>b.s-a.s); }
  function pick(arr, n=4) { return arr.slice(0,n).map(({x})=>x.a.id); }

  // 1. CVH operational excellence — short commute, verified pet, good rating, real OSRM
  const cvhFirst = pick(score(all, x => {
    let s = 0;
    if (x.drive?.am_peak_min) s += Math.max(0, 50 - x.drive.am_peak_min * 2);
    else if (x.osrm?.duration_min) s += Math.max(0, 50 - x.osrm.duration_min * 2.5);
    if (x.a.pet_status === 'verified' || x.a.pet_status === 'verified-large-pets') s += 15;
    if (/^GOOD/i.test(x.a.rating||'')) s += 10;
    if (x.fit) s += x.fit * 0.4;
    return s;
  }));

  // 2. Toronto life — close to Union, near waterfront, good amenities, pets ok
  const torontoLife = pick(score(all, x => {
    let s = 0;
    if (x.a.drive_to_union_min_offpeak) s += Math.max(0, 40 - x.a.drive_to_union_min_offpeak);
    if (/Humber Bay|Mimico|Long Branch|New Toronto|Stonegate|Roncesvalles|Junction|High Park|Swansea|Kingsway/i.test(x.a.zone||'')) s += 20;
    if (x.a.pet_status === 'verified' || x.a.pet_status === 'verified-large-pets') s += 10;
    if (x.fit) s += x.fit * 0.2;
    return s;
  }));

  // 3. Best value — low effective rent vs zone average, pets verified, decent commute
  const bestValue = pick(score(all, x => {
    let s = 0;
    const rent = x.a.rent_1bed_low || x.a.rent_2bed || 9999;
    s += Math.max(0, 50 - (rent - 1500) / 30); // cheaper = higher
    if (x.drive?.premium_index && x.drive.premium_index < 0.95) s += 15;
    if (x.cost?.promo_savings_year) s += Math.min(15, x.cost.promo_savings_year / 300);
    if (x.a.pet_status === 'verified') s += 10;
    if (x.fit > 50) s += 10;
    return s;
  }));

  // 4. Runner-first — closest to high-quality + winter-cleared trails
  const runnerFirst = pick(score(all, x => {
    let s = 0;
    const r = (x.a.running||'').toLowerCase();
    if (/martin goodman|humber bay/.test(r)) s += 35;
    else if (/sawmill|culham|riverwood/.test(r)) s += 28;
    else if (/lakefront|rattray|jack darling|waterfront/.test(r)) s += 22;
    else if (/burnhamthorpe|applewood/.test(r)) s += 18; // winter-cleared
    if (x.osrm?.duration_min) s += Math.max(0, 25 - x.osrm.duration_min);
    s += x.fit * 0.3;
    return s;
  }));

  // 5. Amenity premium — concierge, gym, pool, party room
  const amenityRich = pick(score(all, x => {
    let s = 0;
    const amen = (x.a.pros||[]).concat([x.a.promo||'']).join(' ').toLowerCase();
    if (/concierge|24.7/i.test(amen)) s += 15;
    if (/pool/i.test(amen)) s += 10;
    if (/gym|fitness/i.test(amen)) s += 10;
    if (/pet spa|dog wash|theatre|co.work|rooftop/i.test(amen)) s += 8;
    if (x.parking?.concierge === '24/7') s += 10;
    if (x.parking?.dog_amenities) s += 8;
    s += x.fit * 0.3;
    return s;
  }));

  // 6. Safest bet — high rating + verified pet + reviews exist + no red flags
  const safestBet = pick(score(all, x => {
    let s = 0;
    if (x.review?.google_rating) s += x.review.google_rating * 10;
    if (x.review?.rentsafeto_score) s += x.review.rentsafeto_score * 0.3;
    if (x.a.pet_status === 'verified' || x.a.pet_status === 'verified-large-pets') s += 15;
    if (!x.a.red_flags) s += 5;
    if (/^GOOD/i.test(x.a.rating||'')) s += 10;
    if (x.fit) s += x.fit * 0.3;
    return s;
  }));

  // 7. Singles-scene optimized — high-dating-density zone × reasonable CVH commute
  const singlesScene = pick(score(all, x => {
    let s = 0;
    const z = (window.DATING_SCENE?.zones || {});
    // Try zone-string match
    const zoneKey = Object.keys(z).find(k => k.toLowerCase() === (x.a.zone||'').toLowerCase()) || Object.keys(z).find(k => (x.a.zone||'').toLowerCase().includes(k.split('/')[0].trim().toLowerCase()));
    const datingScore = zoneKey ? z[zoneKey].single_density_score : null;
    if (datingScore) s += datingScore * 0.7; // 0-70
    if (x.osrm?.duration_min) s += Math.max(0, 25 - x.osrm.duration_min); // commute bonus 0-25
    if (x.a.pet_status !== 'no') s += 0; // neutralized
    s += x.fit * 0.15;
    return s;
  }));

  return [
    { tier: "SINGLES-SCENE OPTIMIZED", why: "Highest zone single-density score × reasonable CVH commute. Where 25-35 single professionals actually cluster.", picks: singlesScene },
    { tier: "CVH OPERATIONAL EXCELLENCE", why: "Shortest AM-peak commute + good rating + real OSRM routing.", picks: cvhFirst },
    { tier: "TORONTO LIFE", why: "Close to Union via GO + waterfront/streetcar zones for the old-Harbourfront feel.", picks: torontoLife },
    { tier: "BEST VALUE", why: "Cheapest effective rent + meaningful promo + below-zone-market premium index.", picks: bestValue },
    { tier: "RUNNER-FIRST", why: "Closest building to top-tier trail (winter-cleared bonus) with manageable CVH commute.", picks: runnerFirst },
    { tier: "AMENITY RICH", why: "Concierge + pool + gym + co-work / theatre — modern building feel.", picks: amenityRich },
    { tier: "SAFEST BET", why: "Highest external rating (Google + RentSafeTO) with no documented red flags.", picks: safestBet }
  ];
};

