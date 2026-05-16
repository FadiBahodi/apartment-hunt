#!/usr/bin/env python3
"""
Build drive_matrix.json — zone-aware drive-time multipliers + premium index.
Baseline: osrm_routes.json (off-peak OSRM duration_min).
Applies zone-specific multipliers grounded in GTA traffic research (INsauga,
r/mississauga, r/toronto, DriveBC/INRIX, 2025-2026 construction impacts).
"""
import json
import re
import os
import math

ROOT = '/Users/rawproductivity/apartment-hunt'
DATA = f'{ROOT}/data'

CVH = (43.5594410, -79.7037121)


# ------------------------------------------------------------------
# Load all apartments (data.js + JSONL) with zone + rent info
# ------------------------------------------------------------------
def load_apartments():
    apts = {}  # id -> {id, lat, lng, zone, rent_low, rent_high, ...}

    # ---- data.js (regex; flat fields) ----
    with open(f'{ROOT}/data.js') as f:
        text = f.read()
    # Split on top-level object boundaries — find each apartment object
    # Each object starts with `{\s*id: "..."` and ends with `}`. Use a non-greedy match
    # bounded by the next `{ id:` or the closing `];`.
    obj_pat = re.compile(
        r'\{\s*id:\s*"(?P<id>[^"]+)"(?P<body>.*?)(?=\n\s*\{\s*id:|\n\s*\]\s*;)',
        re.DOTALL
    )
    for m in obj_pat.finditer(text):
        oid = m.group('id')
        body = m.group('body')
        def grab(key, default=None, numeric=True):
            mm = re.search(rf'\b{key}:\s*([\-\d.]+|null|"[^"]*")', body)
            if not mm:
                return default
            v = mm.group(1)
            if v == 'null':
                return None
            if v.startswith('"'):
                return v[1:-1]
            if numeric:
                try:
                    return float(v) if '.' in v else int(v)
                except ValueError:
                    return default
            return v
        zone_m = re.search(r'zone:\s*"([^"]+)"', body)
        apts[oid] = {
            'id': oid,
            'lat': grab('lat'),
            'lng': grab('lng'),
            'zone': zone_m.group(1) if zone_m else None,
            'rent_1bed_low': grab('rent_1bed_low'),
            'rent_1bed_high': grab('rent_1bed_high'),
            'source': 'data.js',
        }

    # ---- JSONL files ----
    for fn in ['more_listings.jsonl', 'wave2_listings.jsonl']:
        path = f'{DATA}/{fn}'
        if not os.path.exists(path):
            continue
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if d['id'] in apts:
                    continue
                apts[d['id']] = {
                    'id': d['id'],
                    'lat': d.get('lat'),
                    'lng': d.get('lng'),
                    'zone': d.get('zone'),
                    'rent_1bed_low': d.get('rent_1bed_low'),
                    'rent_1bed_high': d.get('rent_1bed_high'),
                    'source': fn,
                }
    return apts


# ------------------------------------------------------------------
# Zone classification + multipliers
# ------------------------------------------------------------------
# Multipliers grounded in:
# - INsauga 2025 reports on QEW Credit River bridge replacement (2024-2027)
# - r/mississauga discussions on Hurontario LRT construction impact (Eglinton/Burnhamthorpe)
# - r/toronto on 427/QEW interchange bottleneck (Etobicoke inbound AM)
# - INRIX 2024 GTA congestion report (Mississauga ranks #4 worst in N. America for time lost)
# - DriveBC equivalent (511on.ca) for active Mississauga Rd reconstruction (Streetsville)
# - Reverse-commute studies: GTA "contraflow" out of CVH at 7-8am ~1.1-1.2x vs off-peak
#   (Eglinton W flows AWAY from 403/QEW pull)

# Each tuple: (am_mult, pm_mult, post_night_home_mult, late_night_mult,
#              primary_chokepoint, note)
ZONE_PROFILES = {
    'etobicoke_west_mall': (1.75, 1.60, 1.20, 0.85,
        '427/QEW interchange + QEW Credit River bridge construction',
        'East of 427: heavy inbound AM via QEW; bridge replacement adds 5-10 min variance'),
    'etobicoke_generic': (1.70, 1.55, 1.18, 0.85,
        '427/QEW interchange + QEW Credit River bridge construction',
        'Etobicoke origin: highway-dependent inbound; PM contraflow easier'),
    'mimico': (1.80, 1.65, 1.20, 0.85,
        'QEW Credit River bridge + 427 split',
        'Mimico/Stonegate inbound entirely highway-bound; bridge zone adds variance'),
    'stonegate': (1.80, 1.65, 1.20, 0.85,
        'QEW Credit River bridge + 427 split',
        'Heavy QEW dependence; construction zone in commute path'),
    'humber_bay': (1.85, 1.70, 1.22, 0.88,
        'QEW Credit River bridge + Park Lawn ramp queues',
        'Furthest east origin; Park Lawn QEW on-ramp queues add 5+ min AM'),
    'long_branch': (1.70, 1.55, 1.18, 0.85,
        'QEW Credit River bridge + Brown\'s Line merge',
        'Lakeshore + QEW corridor; manageable but bridge zone in path'),
    'lakeview': (1.55, 1.45, 1.15, 0.85,
        'QEW Credit River bridge (westbound)',
        'Lakeshore/QEW westbound; less merge stress than Etobicoke'),
    'markland_wood': (1.65, 1.50, 1.18, 0.85,
        '427/QEW interchange',
        'Etobicoke seam; 427 southbound to QEW westbound'),
    'applewood': (1.55, 1.45, 1.15, 0.85,
        'QEW Dixie/Cawthra interchange',
        'QEW westbound to Mavis or Erin Mills exit'),
    'cooksville': (1.50, 1.40, 1.12, 0.88,
        'Hurontario LRT construction + Dundas/Hurontario',
        'Hurontario corridor: LRT construction through 2026 adds lane closures'),
    'mississauga_valley': (1.55, 1.45, 1.15, 0.88,
        'Hurontario LRT construction + Burnhamthorpe queues',
        'Hurontario corridor + Square One spillover'),
    'square_one': (1.55, 1.45, 1.15, 0.88,
        'Hurontario LRT construction + Burnhamthorpe',
        'Square One/City Centre: LRT lane reductions + dense local network'),
    'port_credit': (1.45, 1.40, 1.15, 0.88,
        'Mississauga Rd / Lakeshore Mississauga Rd intersection',
        'Mississauga Rd N from Port Credit; manageable inbound'),
    'clarkson': (1.30, 1.28, 1.12, 0.85,
        'Southdown/QEW + Winston Churchill queues',
        'Clarkson/Lorne Park: short hop via Winston Churchill or QEW'),
    'central_erin_mills': (1.20, 1.20, 1.10, 0.88,
        'None (local arterial only)',
        'Erin Mills Pkwy/Eglinton — minimal highway dependence'),
    'sawmill_sheridan': (1.18, 1.18, 1.10, 0.88,
        'None (local arterial only)',
        'Sawmill/Sheridan: short Mississauga Rd/Collegeway hop'),
    'erin_mills_south': (1.20, 1.20, 1.10, 0.88,
        'None (local arterial only)',
        'Erin Mills south: Collegeway/Burnhamthorpe direct'),
    'churchill_meadows': (1.22, 1.20, 1.10, 0.88,
        'Eglinton/Erin Mills intersection',
        'Churchill Meadows: Eglinton W direct to CVH'),
    'streetsville': (1.20, 1.18, 1.12, 0.88,
        'Mississauga Road reconstruction (active 2025-2026)',
        'Streetsville: Mississauga Rd reconstruction adds 2-5 min variance'),
    'meadowvale': (1.22, 1.20, 1.10, 0.88,
        'None (local arterial only) — 401 if commuting east',
        'Meadowvale: Winston Churchill or Erin Mills Pkwy south'),
    'cooksville_mineola': (1.50, 1.40, 1.12, 0.88,
        'Hurontario LRT construction',
        'Cooksville/Mineola: Hurontario corridor lane closures'),
    'cooksville_hurontario': (1.55, 1.45, 1.15, 0.88,
        'Hurontario LRT construction',
        'Directly on Hurontario LRT alignment — heavy construction'),
    'oakville': (1.85, 1.65, 1.20, 0.85,
        'QEW Bronte / Ford Drive chokepoint',
        'Oakville: long QEW eastbound to Mississauga Rd exit; Bronte merge stress'),
    'oakville_kerr': (1.85, 1.65, 1.20, 0.85,
        'QEW Bronte chokepoint',
        'Kerr Village: QEW eastbound; significant distance'),
    'brampton': (1.90, 1.70, 1.20, 0.85,
        '410 + 401 collector congestion',
        'Brampton: 410 south to 401 collectors then 403 west; multi-highway risk'),
    'milton': (1.85, 1.65, 1.18, 0.85,
        '401 collectors + Mississauga Rd exit',
        'Milton: long 401 eastbound; collector lane congestion'),
    'default': (1.40, 1.35, 1.13, 0.88,
        'Unknown — verify',
        'Default GTA suburban multipliers applied'),
}


def classify_zone(zone_str, lat, lng):
    """Map free-form zone string to ZONE_PROFILES key. Fall back to geo heuristics."""
    if not zone_str:
        zone_str = ''
    z = zone_str.lower()

    # Direct keyword matches (order matters: most specific first)
    if 'humber bay' in z:
        return 'humber_bay'
    if 'mimico' in z:
        return 'mimico'
    if 'stonegate' in z:
        return 'stonegate'
    if 'long branch' in z or 'new toronto' in z:
        return 'long_branch'
    if 'lakeview' in z:
        return 'lakeview'
    if 'markland' in z:
        return 'markland_wood'
    if 'applewood' in z:
        return 'applewood'
    if 'west mall' in z or 'etobicoke west' in z:
        return 'etobicoke_west_mall'
    if 'etobicoke' in z:
        return 'etobicoke_generic'
    if 'oakville' in z and 'kerr' in z:
        return 'oakville_kerr'
    if 'oakville' in z:
        return 'oakville'
    if 'brampton' in z:
        return 'brampton'
    if 'milton' in z:
        return 'milton'
    if 'streetsville' in z:
        return 'streetsville'
    if 'meadowvale' in z and 'central erin mills' not in z:
        return 'meadowvale'
    if 'central erin mills' in z or 'central erin' in z:
        return 'central_erin_mills'
    if 'churchill meadow' in z:
        return 'churchill_meadows'
    if 'sawmill' in z or 'sheridan' in z:
        return 'sawmill_sheridan'
    if 'erin mills' in z:
        return 'erin_mills_south'
    if 'port credit' in z:
        return 'port_credit'
    if 'clarkson' in z or 'lorne park' in z:
        return 'clarkson'
    if 'square one' in z or 'city centre' in z or 'city center' in z:
        return 'square_one'
    if 'mississauga valley' in z:
        return 'mississauga_valley'
    if 'cooksville' in z and ('mineola' in z):
        return 'cooksville_mineola'
    if 'cooksville' in z and 'hurontario' in z:
        return 'cooksville_hurontario'
    if 'cooksville' in z or 'hurontario' in z:
        return 'cooksville'

    # Geo fallback
    if lat and lng:
        # Etobicoke: east of -79.55
        if lng > -79.55 and lat > 43.55:
            return 'etobicoke_generic'
        # Oakville: south of 43.50 and west of -79.65
        if lat < 43.50 and lng < -79.65:
            return 'oakville'
        # Brampton: north of 43.65
        if lat > 43.65:
            return 'brampton'
    return 'default'


# ------------------------------------------------------------------
# Zone -> zones.json key mapping (for avg_rent_1bed lookup)
# ------------------------------------------------------------------
ZONES_JSON_MAP = {
    'central_erin_mills': 'Central Erin Mills',
    'sawmill_sheridan': 'Sawmill Valley / Sheridan',
    'erin_mills_south': 'Central Erin Mills',  # closest match
    'streetsville': 'Streetsville',
    'meadowvale': 'Meadowvale',
    'churchill_meadows': 'Churchill Meadows',
    'cooksville': 'Cooksville',
    'cooksville_mineola': 'Cooksville',
    'cooksville_hurontario': 'Cooksville',
    'mississauga_valley': 'Mississauga Valley',
    'square_one': 'Square One / City Centre',
    'port_credit': 'Port Credit',
    'lakeview': 'Lakeview Mississauga',
    'clarkson': 'Clarkson / Lorne Park',
    'applewood': 'Applewood',
    'mimico': 'Mimico',
    'long_branch': 'Long Branch / New Toronto',
    'humber_bay': 'Humber Bay Shores',
    'stonegate': 'Stonegate',
    'markland_wood': 'Markland Wood',
    'etobicoke_west_mall': 'Etobicoke West Mall',
    'etobicoke_generic': 'Etobicoke West Mall',
}


def tier_from_am(am_min):
    if am_min <= 15:
        return 1
    if am_min <= 20:
        return 2
    if am_min <= 30:
        return 3
    if am_min <= 45:
        return 4
    return 5


def risk_score(baseline, am_mult, distance_km=None):
    """
    Variance × distance proxy. AM multiplier above 1.0 measures variance;
    multiply by trip length (baseline minutes as distance proxy) and normalize.
    """
    variance = (am_mult - 1.0)  # 0.18 .. 0.90
    length = baseline  # off-peak min as length proxy
    raw = variance * length * 6.5  # tuning constant
    return int(max(0, min(100, round(raw))))


def value_call(pi):
    if pi is None:
        return None
    if pi < 0.85:
        return 'below market'
    if pi < 1.05:
        return 'market'
    if pi < 1.20:
        return 'above market'
    return 'premium'


def main():
    apts = load_apartments()
    with open(f'{DATA}/osrm_routes.json') as f:
        osrm = json.load(f)
    with open(f'{DATA}/zones.json') as f:
        zones = json.load(f)

    out = {}
    for oid, a in apts.items():
        r = osrm.get(oid)
        if not r:
            continue
        baseline = round(r['duration_min'], 1)
        dist_km = r.get('distance_km')

        zkey = classify_zone(a.get('zone'), a.get('lat'), a.get('lng'))
        am_mult, pm_mult, post_mult, late_mult, choke, note = ZONE_PROFILES[zkey]

        am_min = round(baseline * am_mult)
        pm_min = round(baseline * pm_mult)
        post_min = round(baseline * post_mult)
        late_min = round(baseline * late_mult)
        off_min = round(baseline)

        zjson_key = ZONES_JSON_MAP.get(zkey)
        zone_avg = zones.get(zjson_key, {}).get('avg_rent_1bed') if zjson_key else None

        # Building rent: prefer midpoint of low/high; else low; else high
        rl = a.get('rent_1bed_low')
        rh = a.get('rent_1bed_high')
        building_rent = None
        if rl and rh:
            building_rent = (rl + rh) / 2
        elif rl:
            building_rent = rl
        elif rh:
            building_rent = rh

        pi = None
        if building_rent and zone_avg:
            pi = round(building_rent / zone_avg, 3)

        out[oid] = {
            'baseline_osrm_min': baseline,
            'distance_km': dist_km,
            'off_peak_min': off_min,
            'am_peak_min': am_min,
            'pm_peak_min': pm_min,
            'post_night_home_min': post_min,
            'late_night_min': late_min,
            'am_multiplier': am_mult,
            'pm_multiplier': pm_mult,
            'tier': tier_from_am(am_min),
            'commute_risk_score': risk_score(baseline, am_mult),
            'zone': a.get('zone'),
            'zone_key': zkey,
            'primary_chokepoint': choke,
            'notes': note,
            'zone_avg_1bed': zone_avg,
            'building_rent_mid': round(building_rent) if building_rent else None,
            'premium_index': pi,
            'value_call': value_call(pi),
        }

    out_path = f'{DATA}/drive_matrix.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, sort_keys=True)

    # ---- distributions ----
    tiers = {}
    values = {}
    for v in out.values():
        tiers[v['tier']] = tiers.get(v['tier'], 0) + 1
        vc = v['value_call'] or 'unknown'
        values[vc] = values.get(vc, 0) + 1

    print(f'Wrote {len(out)} entries -> {out_path}')
    print('\nTier distribution (by AM peak commute):')
    for t in sorted(tiers):
        label = {1: '<=15min', 2: '<=20min', 3: '<=30min', 4: '<=45min', 5: '>45min'}[t]
        print(f'  Tier {t} ({label}): {tiers[t]}')

    print('\nPremium distribution (vs zone avg 1-bed):')
    for k in ['below market', 'market', 'above market', 'premium', 'unknown']:
        if k in values:
            print(f'  {k}: {values[k]}')


if __name__ == '__main__':
    main()
