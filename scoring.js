// Fit Score algorithm — tailored to Fadi's golden path
// 0-100 score based on weighted axes that matter for HIM
//
// Axes (weights sum to 100):
//   30 — CVH commute (peak min)        // job reliability
//   20 — Running (winter trail access) // 100km/wk identity
//   15 — Pet quality (verified, large)  // dog
//   15 — Cost vs budget (effective rent)
//    8 — Toronto access (Union min)    // social/Nomi
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
  if (timeUsed <= 8) cvhPts = 30;
  else if (timeUsed <= 12) cvhPts = 25;
  else if (timeUsed <= 17) cvhPts = 18;
  else if (timeUsed <= 25) cvhPts = 10;
  else if (timeUsed <= 35) cvhPts = 4;
  score += cvhPts;
  breakdown.push({k: 'CVH commute', v: cvhPts, max: 30, note: source});

  // 2. Running (20 pts) — proximity + winter access
  // Heuristic: zone-based for now; can be improved when zones.json arrives
  let runPts = 8; // baseline
  const zone = (a.zone || '').toLowerCase();
  const running = (a.running || '').toLowerCase();
  if (running.includes('martin goodman') || running.includes('humber bay')) runPts = 20;
  else if (running.includes('sawmill') || running.includes('culham') || running.includes('riverwood')) runPts = 17;
  else if (running.includes('lakefront') || running.includes('rattray') || running.includes('jack darling')) runPts = 16;
  else if (running.includes('etobicoke creek') || running.includes('centennial')) runPts = 13;
  else if (running.includes('burnhamthorpe') || running.includes('applewood')) runPts = 14; // winter cleared
  else if (running.includes('cooksville')) runPts = 9;
  score += runPts;
  breakdown.push({k: 'Running', v: runPts, max: 20, note: 'Trail proximity + winter access'});

  // 3. Pet (15 pts)
  let petPts = 0;
  if (a.pet_status === 'verified-large-pets') petPts = 15;
  else if (a.pet_status === 'verified') petPts = 13;
  else if (a.pet_status === 'verify-specifics') petPts = 8;
  else if (a.pet_status === 'verify-condo-rules') petPts = 6;
  else if (a.pet_status === 'conflicting') petPts = 3;
  score += petPts;
  breakdown.push({k: 'Pet policy', v: petPts, max: 15, note: a.pet_status || 'unknown'});

  // 4. Cost vs budget (15 pts) — sweet spot $1,800-$2,200
  const rent = a.rent_1bed_low || a.rent_2bed || 9999;
  const c = costs && costs[a.id];
  const effectiveRent = c?.net_effective_1bed || rent;
  const totalEst = c?.estimated_monthly_total_1bed || (rent + 100); // assume +100 utilities
  let costPts = 0;
  if (totalEst <= 1900) costPts = 15;
  else if (totalEst <= 2100) costPts = 13;
  else if (totalEst <= 2300) costPts = 10;
  else if (totalEst <= 2500) costPts = 7;
  else if (totalEst <= 2700) costPts = 4;
  else costPts = 1;
  score += costPts;
  breakdown.push({k: 'Cost', v: costPts, max: 15, note: `~$${totalEst}/mo all-in`});

  // 5. Toronto access (8 pts)
  const u = a.drive_to_union_min_offpeak || 99;
  let torPts = 0;
  if (u <= 16) torPts = 8;
  else if (u <= 22) torPts = 6;
  else if (u <= 28) torPts = 4;
  else if (u <= 35) torPts = 2;
  score += torPts;
  breakdown.push({k: 'Toronto access', v: torPts, max: 8, note: `${u}min Union`});

  // 6. Building rating (7 pts)
  let bldgPts = 3;
  const r = (a.rating || '').toUpperCase();
  if (r.startsWith('GOOD')) bldgPts = 7;
  else if (r.startsWith('FINE') || r.startsWith('POTENTIAL') || r.startsWith('STRETCH')) bldgPts = 4;
  else if (r.startsWith('CAUTION')) bldgPts = 1;
  else if (r.startsWith('AVOID')) bldgPts = 0;
  score += bldgPts;
  breakdown.push({k: 'Building rep', v: bldgPts, max: 7, note: a.rating || 'unknown'});

  // 7. Value (5 pts) — sqft per dollar
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
