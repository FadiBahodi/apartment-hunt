// Fit Score algorithm — tailored to Fadi's golden path
// 0-100 score based on weighted axes that matter for HIM
//
// Axes (weights sum to 100):
//   35 — CVH commute (peak min)        // job reliability
//   25 — Running (winter trail access) // 100km/wk identity
//   18 — Cost vs budget (effective rent)
//   10 — Toronto access (Union min)    // social access
//    7 — Building rating quality (good > caution > avoid)
//    5 — Sqft vs price (value/space)

window.computeFitScore = function(a, costs, osrm) {
  let score = 0;
  const breakdown = [];

  // 1. CVH commute (30 pts max)
  // Prefer real OSRM off-peak minutes when available, scale +30% for "peak" estimation
  const osrmRoute = (osrm || window.OSRM || {})[a.id];
  let timeUsed, source;
  if (osrmRoute) {
    timeUsed = Math.round(osrmRoute.duration_min * 1.4); // off-peak → peak estimate
    source = `${osrmRoute.duration_min}m OSRM off-peak (~${timeUsed}m peak)`;
  } else {
    timeUsed = a.drive_to_cvh_min_peak || 99;
    source = `${timeUsed}m peak (est)`;
  }
  let cvhPts = 0;
  if (timeUsed <= 8) cvhPts = 35;
  else if (timeUsed <= 12) cvhPts = 29;
  else if (timeUsed <= 17) cvhPts = 21;
  else if (timeUsed <= 25) cvhPts = 12;
  else if (timeUsed <= 35) cvhPts = 5;
  score += cvhPts;
  breakdown.push({k: 'CVH commute', v: cvhPts, max: 35, note: source});

  // 2. Running (25 pts) — proximity + winter access
  let runPts = 10; // baseline
  const zone = (a.zone || '').toLowerCase();
  const running = (a.running || '').toLowerCase();
  if (running.includes('martin goodman') || running.includes('humber bay')) runPts = 25;
  else if (running.includes('sawmill') || running.includes('culham') || running.includes('riverwood')) runPts = 22;
  else if (running.includes('lakefront') || running.includes('rattray') || running.includes('jack darling')) runPts = 20;
  else if (running.includes('etobicoke creek') || running.includes('centennial')) runPts = 17;
  else if (running.includes('burnhamthorpe') || running.includes('applewood')) runPts = 18; // winter cleared
  else if (running.includes('cooksville')) runPts = 12;
  score += runPts;
  breakdown.push({k: 'Running', v: runPts, max: 25, note: 'Trail proximity + winter access'});

  // 3. Cost vs budget (18 pts)
  const rent = a.rent_1bed_low || a.rent_2bed || 9999;
  const c = costs && costs[a.id];
  const effectiveRent = c?.net_effective_1bed || rent;
  const totalEst = c?.estimated_monthly_total_1bed || (rent + 100);
  let costPts = 0;
  if (totalEst <= 1900) costPts = 18;
  else if (totalEst <= 2100) costPts = 15;
  else if (totalEst <= 2300) costPts = 12;
  else if (totalEst <= 2500) costPts = 8;
  else if (totalEst <= 2700) costPts = 4;
  else costPts = 1;
  score += costPts;
  breakdown.push({k: 'Cost', v: costPts, max: 18, note: `~$${totalEst}/mo all-in`});

  // 4. Toronto access (10 pts)
  const u = a.drive_to_union_min_offpeak || 99;
  let torPts = 0;
  if (u <= 16) torPts = 10;
  else if (u <= 22) torPts = 8;
  else if (u <= 28) torPts = 5;
  else if (u <= 35) torPts = 2;
  score += torPts;
  breakdown.push({k: 'Toronto access', v: torPts, max: 10, note: `${u}min Union`});

  // 5. Building rating (7 pts)
  let bldgPts = 3;
  const r = (a.rating || '').toUpperCase();
  if (r.startsWith('GOOD')) bldgPts = 7;
  else if (r.startsWith('FINE') || r.startsWith('POTENTIAL') || r.startsWith('STRETCH')) bldgPts = 4;
  else if (r.startsWith('CAUTION')) bldgPts = 1;
  else if (r.startsWith('AVOID')) bldgPts = 0;
  score += bldgPts;
  breakdown.push({k: 'Building rep', v: bldgPts, max: 7, note: a.rating || 'unknown'});

  // 6. Value (5 pts) — sqft per dollar
  const sqft = a.sqft_high || a.sqft_low || 600;
  const sqftPerDollar = sqft / Math.max(rent, 1);
  let valPts = 0;
  if (sqftPerDollar > 0.40) valPts = 5;
  else if (sqftPerDollar > 0.32) valPts = 4;
  else if (sqftPerDollar > 0.27) valPts = 3;
  else if (sqftPerDollar > 0.22) valPts = 2;
  else valPts = 1;
  score += valPts;
  breakdown.push({k: 'Value (sqft/$)', v: valPts, max: 5, note: `${sqft}sf @ $${rent}`});

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

  return [
    { tier: "CVH OPERATIONAL EXCELLENCE", why: "Shortest AM-peak commute with verified pet + good rating + real OSRM routing.", picks: cvhFirst },
    { tier: "TORONTO LIFE", why: "Close to Union via GO + waterfront/streetcar zones for the old-Harbourfront feel.", picks: torontoLife },
    { tier: "BEST VALUE", why: "Cheapest effective rent for the unit + meaningful promo + below-zone-market premium index.", picks: bestValue },
    { tier: "RUNNER-FIRST", why: "Closest building to top-tier trail (winter-cleared bonus) with manageable CVH commute.", picks: runnerFirst },
    { tier: "AMENITY RICH", why: "Concierge + pool + gym + co-work / theatre — modern building feel.", picks: amenityRich },
    { tier: "SAFEST BET", why: "Highest external rating (Google + RentSafeTO) with verified pet and no documented red flags.", picks: safestBet }
  ];
};

