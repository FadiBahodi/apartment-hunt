#!/usr/bin/env python3
"""Build run_routes.json — 5K / 10K / 20K running suggestions per building.

Strategy:
- Load OSM trails + parks geometry (10 trails, 13 parks)
- For each building lat/lng, compute haversine distance to nearest point of each trail
  and to centroid of each park
- 5K = nearest single trail/park out-and-back (2.5K each way)
- 10K = nearest 1-2 trails strung together
- 20K = best long-distance trail (Waterfront / Martin Goodman / Etobicoke Creek etc.)
  stringing 2+ trails when geographically possible

For Brampton/Oakville/Milton zones where dataset has no trail nearby (>3km), we still
produce routes but flagged "drive-to required" and reference the well-known local trail
(Esker Lake, Sixteen Mile Creek, Mill Pond, etc.).
"""
import json
import math
from collections import defaultdict
from pathlib import Path

DATA = Path('/Users/rawproductivity/apartment-hunt/data')

# ---------- Geometry helpers ----------

def haversine(lat1, lon1, lat2, lon2):
    """Distance in km between two lat/lng points."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def flatten_multilinestring(geom):
    """Return flat list of (lat, lng) points for a MultiLineString or LineString."""
    pts = []
    if geom['type'] == 'MultiLineString':
        for seg in geom['coordinates']:
            for x, y in seg:  # GeoJSON is [lng, lat]
                pts.append((y, x))
    elif geom['type'] == 'LineString':
        for x, y in geom['coordinates']:
            pts.append((y, x))
    return pts


def polygon_centroid(geom):
    """Approximate centroid of a Polygon (first ring)."""
    if geom['type'] != 'Polygon':
        return None
    ring = geom['coordinates'][0]
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return (sum(ys) / len(ys), sum(xs) / len(xs))


def nearest_point_on_trail(lat, lng, trail_pts):
    """Find nearest point in a list and return (distance_km, (plat, plng))."""
    best = (float('inf'), None)
    for plat, plng in trail_pts:
        d = haversine(lat, lng, plat, plng)
        if d < best[0]:
            best = (d, (plat, plng))
    return best


# ---------- Load data ----------

with open(DATA / 'osm_geo.json') as f:
    osm = json.load(f)

trails = []
for t in osm['trails']:
    pts = flatten_multilinestring(t['geometry'])
    trails.append({
        'name': t['name'],
        'length_km': t.get('length_km'),
        'surface': t.get('surface', 'paved'),
        'winter': t.get('winter_maintained', False),
        'note': t.get('note', ''),
        'pts': pts,
    })

parks = []
for p in osm['parks']:
    c = polygon_centroid(p['geometry'])
    parks.append({
        'name': p['name'],
        'acres': p.get('area_acres'),
        'note': p.get('note', ''),
        'centroid': c,
    })


# ---------- Hand-curated supplements for zones outside OSM dataset ----------

# Real local trails the OSM dataset doesn't cover, keyed by zone substring.
# These are used when nothing in the dataset is within reach.
EXTERNAL_TRAILS = {
    'Brampton/Bramalea':    {'trail': 'Esker Lake Trail',          'park': 'Chinguacousy Park',          'long': 'Etobicoke Creek Trail (south end)'},
    'Brampton/Downtown':    {'trail': 'Etobicoke Creek Trail',     'park': 'Gage Park',                  'long': 'Etobicoke Creek Trail end-to-end'},
    'Brampton/Central':     {'trail': 'Etobicoke Creek Trail',     'park': 'Chinguacousy Park',          'long': 'Etobicoke Creek Trail'},
    'Brampton/Queen Mary':  {'trail': 'Etobicoke Creek Trail',     'park': 'Chinguacousy Park',          'long': 'Etobicoke Creek Trail'},
    'Brampton/Fletchers':   {'trail': 'Fletchers Creek Trail',     'park': 'Loafers Lake Park',          'long': 'Etobicoke Creek + Fletchers Creek'},
    'Brampton/Heart Lake':  {'trail': 'Heart Lake Conservation Area', 'park': 'Heart Lake CA',           'long': 'Heart Lake CA loops + Etobicoke Creek'},
    'Brampton/Sandalwood':  {'trail': 'Fletchers Creek Trail',     'park': 'Chinguacousy Park',          'long': 'Fletchers Creek Trail'},
    'Brampton/Springdale':  {'trail': 'Esker Lake Trail',          'park': 'Professors Lake',            'long': 'Professors Lake loop + Esker Lake'},
    'Brampton/Kennedy':     {'trail': 'Etobicoke Creek Trail',     'park': 'Chinguacousy Park',          'long': 'Etobicoke Creek Trail'},
    'Oakville/Kerr':        {'trail': 'Sixteen Mile Creek Trail',  'park': 'Coronation Park',            'long': 'Waterfront Trail (Oakville segment)'},
    'Oakville/Bronte':      {'trail': 'Bronte Creek Trail',        'park': 'Bronte Heritage Waterfront Park', 'long': 'Bronte Creek PP + Waterfront Trail'},
    'Oakville/Old':         {'trail': 'Sixteen Mile Creek Trail',  'park': 'Lakeside Park',              'long': 'Waterfront Trail (Oakville)'},
    'Oakville/Glen Abbey':  {'trail': 'Fourteen Mile Creek Trail', 'park': 'Glen Abbey Community Park',  'long': 'Fourteen Mile + Sixteen Mile Creek'},
    'Oakville/College':     {'trail': 'Sixteen Mile Creek Trail',  'park': 'Postridge Park',             'long': 'Sixteen Mile Creek end-to-end'},
    'Oakville/Coronation':  {'trail': 'Waterfront Trail',          'park': 'Coronation Park',            'long': 'Waterfront Trail Oakville→Burlington'},
    'Oakville/River Oaks':  {'trail': 'Sixteen Mile Creek Trail',  'park': 'River Oaks Park',            'long': 'Sixteen Mile Creek Trail full'},
    'Oakville/Iroquois':    {'trail': 'Joshua Creek Trail',        'park': 'Iroquois Ridge Park',        'long': 'Joshua Creek + Sixteen Mile Creek'},
    'Oakville/Trafalgar':   {'trail': 'Sixteen Mile Creek Trail',  'park': 'Postridge Park',             'long': 'Sixteen Mile Creek Trail'},
    'Oakville/West Oak':    {'trail': 'Fourteen Mile Creek Trail', 'park': 'West Oak Trails Community Park', 'long': 'Fourteen Mile + Bronte Creek'},
    'Oakville Trafalgar':   {'trail': 'Sixteen Mile Creek Trail',  'park': 'Lakeside Park',              'long': 'Waterfront Trail Oakville'},
    'Milton':               {'trail': 'Mill Pond Trail',           'park': 'Rotary Park',                'long': 'Bruce Trail (Kelso/Crawford Lake)'},
}


def external_for_zone(zone):
    for key, val in EXTERNAL_TRAILS.items():
        if key.lower() in zone.lower():
            return val
    return None


# ---------- Per-building distance table ----------

def trail_distances(lat, lng):
    """Return list of (distance_km, nearest_point, trail) sorted nearest first."""
    out = []
    for t in trails:
        d, pt = nearest_point_on_trail(lat, lng, t['pts'])
        out.append((d, pt, t))
    out.sort(key=lambda x: x[0])
    return out


def park_distances(lat, lng):
    out = []
    for p in parks:
        if not p['centroid']:
            continue
        d = haversine(lat, lng, p['centroid'][0], p['centroid'][1])
        out.append((d, p))
    out.sort(key=lambda x: x[0])
    return out


# ---------- Route synthesis ----------

def warmup_min(distance_km):
    """Approx jog warmup minutes to a trailhead at ~6:00/km pace."""
    return max(1, int(round(distance_km * 6)))


def lighting_note(trail):
    name = trail['name'].lower()
    if 'waterfront' in name or 'martin goodman' in name:
        return 'lit at major park nodes (Marie Curtis, Humber Bay); dark between'
    if 'humber river' in name or 'mimico' in name:
        return 'partial — lit near roads, dark in valley sections'
    if 'cooksville' in name or 'burnhamthorpe' in name:
        return 'partial street-lit; trail itself unlit'
    if 'glen erin' in name or 'sawmill' in name or 'culham' in name:
        return 'unlit ravine — headlamp required before dawn / after dusk'
    if 'etobicoke creek' in name:
        return 'unlit valley — use headlamp early/late shifts'
    return 'unlit trail sections — bring headlamp for pre-6am or post-8pm runs'


def winter_note(trail):
    if trail['winter']:
        return f"{trail['name']} is winter-maintained (plowed/salted)"
    return f"{trail['name']} NOT winter-maintained — switch to road or Burnhamthorpe Trail Dec-Mar"


def dog_note(trail, parks_near):
    onleash = [p['name'] for d, p in parks_near[:3] if 'leash' in (p.get('note') or '').lower()]
    base = 'leash required on trail'
    if onleash:
        base += f'; off-leash zones nearby ({", ".join(onleash[:2])})'
    return base


def scenery_note(trail):
    name = trail['name'].lower()
    if 'waterfront' in name or 'martin goodman' in name:
        return 'Lake Ontario shoreline + marina + skyline views'
    if 'humber bay' in name or 'mimico' in name:
        return 'creek valley + lakefront wetlands'
    if 'cooksville' in name:
        return 'urban creek corridor through Mississauga'
    if 'sawmill' in name:
        return 'UTM campus woods + ravine'
    if 'culham' in name:
        return 'Credit River valley, boardwalk, Erindale Park'
    if 'glen erin' in name:
        return 'Erin Mills suburban ravine'
    if 'etobicoke creek' in name:
        return 'Etobicoke Creek valley, marshland near Marie Curtis'
    if 'burnhamthorpe' in name:
        return 'straight east-west paved path, neighbourhood views'
    if 'humber river' in name:
        return 'Humber River valley, mature forest, Old Mill bridge'
    return 'mixed urban + natural'


def strava_segment(trail):
    name = trail['name'].lower()
    if 'martin goodman' in name or 'waterfront' in name:
        return 'Lakeshore West (popular)'
    if 'humber bay' in name:
        return 'Humber Bay Loop'
    if 'sawmill' in name:
        return 'Sawmill Valley'
    if 'culham' in name:
        return 'Credit River Culham'
    if 'etobicoke creek' in name:
        return 'Etobicoke Creek Trail South'
    if 'burnhamthorpe' in name:
        return 'Burnhamthorpe Trail'
    if 'cooksville' in name:
        return 'Cooksville Creek'
    if 'mimico' in name:
        return 'Mimico Creek Trail'
    if 'humber river' in name:
        return 'Humber River South'
    if 'glen erin' in name:
        return 'Glen Erin Trail'
    return None


def build_5k(lat, lng, td, pd, zone):
    if td and td[0][0] <= 1.5:
        d_to, pt, tr = td[0]
        return {
            'name': f"{tr['name']} out-and-back",
            'distance_km': round(5 + d_to * 2, 1),
            'surface': tr['surface'],
            'lighting': lighting_note(tr),
            'winter_ok': bool(tr['winter']),
            'road_crossings': 1 if d_to < 0.4 else 2,
            'dog_friendly': dog_note(tr, pd),
            'scenery': scenery_note(tr),
            'starts_at_trail': f"{tr['name']} access point {int(d_to * 1000)}m from door",
            'approx_warmup_to_trailhead_min': warmup_min(d_to),
            'strava_segment_estimated': strava_segment(tr),
        }
    # Drive-to or doorstep loop fallback
    ext = external_for_zone(zone)
    if ext:
        return {
            'name': f"{ext['trail']} out-and-back (drive-to)",
            'distance_km': 5.0,
            'surface': 'paved (most likely)',
            'lighting': 'unlit trail — headlamp for early/late',
            'winter_ok': False,
            'road_crossings': 1,
            'dog_friendly': 'leash on trail',
            'scenery': 'local ravine/creek corridor',
            'starts_at_trail': f"{ext['trail']} — drive-to required; no doorstep trail within OSM dataset",
            'approx_warmup_to_trailhead_min': 0,
            'strava_segment_estimated': None,
            'note': f"No trail within 1.5km of door — drive 5-10 min to {ext['trail']}",
        }
    # Pure road loop
    return {
        'name': 'Residential road 2.5K out-and-back',
        'distance_km': 5.0,
        'surface': 'sidewalk',
        'lighting': 'street-lit (residential)',
        'winter_ok': True,
        'road_crossings': 4,
        'dog_friendly': 'leash on sidewalk',
        'scenery': 'residential streets',
        'starts_at_trail': 'no trail within 1.5km — road run from door',
        'approx_warmup_to_trailhead_min': 0,
        'strava_segment_estimated': None,
    }


def build_10k(lat, lng, td, pd, zone):
    near = [x for x in td if x[0] <= 2.5]
    if len(near) >= 2:
        a, b = near[0], near[1]
        return {
            'name': f"{a[2]['name']} + {b[2]['name']} link",
            'distance_km': round(10 + (a[0] + b[0]) * 1.5, 1),
            'surface': f"{a[2]['surface']} / {b[2]['surface']}",
            'lighting': lighting_note(a[2]),
            'winter_ok': bool(a[2]['winter'] and b[2]['winter']),
            'road_crossings': 3,
            'dog_friendly': dog_note(a[2], pd),
            'scenery': f"{scenery_note(a[2])} + {scenery_note(b[2])}",
            'starts_at_trail': f"{a[2]['name']} {int(a[0]*1000)}m from door → connect to {b[2]['name']}",
            'approx_warmup_to_trailhead_min': warmup_min(a[0]),
            'strava_segment_estimated': strava_segment(a[2]) or strava_segment(b[2]),
        }
    if near:
        d_to, pt, tr = near[0]
        return {
            'name': f"{tr['name']} 5K out-and-back",
            'distance_km': round(10 + d_to * 2, 1),
            'surface': tr['surface'],
            'lighting': lighting_note(tr),
            'winter_ok': bool(tr['winter']),
            'road_crossings': 2,
            'dog_friendly': dog_note(tr, pd),
            'scenery': scenery_note(tr),
            'starts_at_trail': f"{tr['name']} {int(d_to*1000)}m from door",
            'approx_warmup_to_trailhead_min': warmup_min(d_to),
            'strava_segment_estimated': strava_segment(tr),
        }
    ext = external_for_zone(zone)
    if ext:
        return {
            'name': f"{ext['trail']} 10K (drive-to)",
            'distance_km': 10.0,
            'surface': 'paved',
            'lighting': 'unlit trail — headlamp required early/late',
            'winter_ok': False,
            'road_crossings': 2,
            'dog_friendly': 'leash on trail',
            'scenery': 'creek/ravine corridor',
            'starts_at_trail': f"{ext['trail']} — drive 5-10 min from door",
            'approx_warmup_to_trailhead_min': 0,
            'strava_segment_estimated': None,
            'note': 'No trail within 2.5km of door — drive-to required',
        }
    return {
        'name': 'Neighbourhood 5K loop x2',
        'distance_km': 10.0,
        'surface': 'sidewalk + minor road',
        'lighting': 'street-lit',
        'winter_ok': True,
        'road_crossings': 8,
        'dog_friendly': 'leash on sidewalk',
        'scenery': 'residential / arterial',
        'starts_at_trail': 'no trail within 2.5km — road loops only',
        'approx_warmup_to_trailhead_min': 0,
        'strava_segment_estimated': None,
    }


def build_20k(lat, lng, td, pd, zone):
    """Long run — string 2+ trails OR use a single big trail (Waterfront/Martin Goodman/Etobicoke Creek)."""
    near = [x for x in td if x[0] <= 4.0]
    # Long trails suitable for 20K solo (length >= 10km)
    big_solo = [x for x in near if x[2]['length_km'] and x[2]['length_km'] >= 10]
    if big_solo:
        d_to, pt, tr = big_solo[0]
        # If there's also a connecting trail within 5km, chain them
        chain = None
        for d2, pt2, tr2 in near:
            if tr2['name'] != tr['name'] and tr2['length_km'] and tr2['length_km'] >= 5:
                chain = tr2
                break
        if chain:
            return {
                'name': f"{tr['name']} → {chain['name']} long run",
                'distance_km': round(20 + d_to * 2, 1),
                'surface': f"{tr['surface']} + {chain['surface']}",
                'lighting': lighting_note(tr),
                'winter_ok': bool(tr['winter'] and chain['winter']),
                'road_crossings': 5,
                'dog_friendly': dog_note(tr, pd),
                'scenery': f"{scenery_note(tr)} → {scenery_note(chain)}",
                'starts_at_trail': f"{tr['name']} {int(d_to*1000)}m from door; chain to {chain['name']} mid-run",
                'approx_warmup_to_trailhead_min': warmup_min(d_to),
                'strava_segment_estimated': strava_segment(tr),
                'fueling_note': 'carry 1 gel + 500ml water; refill at park taps May-Oct',
                'door_to_door_achievable': True,
            }
        return {
            'name': f"{tr['name']} 10K out-and-back",
            'distance_km': round(20 + d_to * 2, 1),
            'surface': tr['surface'],
            'lighting': lighting_note(tr),
            'winter_ok': bool(tr['winter']),
            'road_crossings': 4,
            'dog_friendly': dog_note(tr, pd),
            'scenery': scenery_note(tr),
            'starts_at_trail': f"{tr['name']} {int(d_to*1000)}m from door — run full length out, back",
            'approx_warmup_to_trailhead_min': warmup_min(d_to),
            'strava_segment_estimated': strava_segment(tr),
            'fueling_note': 'carry 1 gel + 500ml water; refill at park taps May-Oct',
            'door_to_door_achievable': True,
        }
    # Try chaining 2 shorter trails
    if len(near) >= 2:
        a, b = near[0], near[1]
        total = (a[2]['length_km'] or 5) + (b[2]['length_km'] or 5)
        if total >= 10:
            return {
                'name': f"{a[2]['name']} + {b[2]['name']} long-run link",
                'distance_km': round(20 + (a[0] + b[0]) * 1.5, 1),
                'surface': f"{a[2]['surface']} / {b[2]['surface']}",
                'lighting': lighting_note(a[2]),
                'winter_ok': bool(a[2]['winter'] and b[2]['winter']),
                'road_crossings': 6,
                'dog_friendly': dog_note(a[2], pd),
                'scenery': f"{scenery_note(a[2])} + {scenery_note(b[2])}",
                'starts_at_trail': f"{a[2]['name']} {int(a[0]*1000)}m from door; back through {b[2]['name']}",
                'approx_warmup_to_trailhead_min': warmup_min(a[0]),
                'strava_segment_estimated': strava_segment(a[2]) or strava_segment(b[2]),
                'fueling_note': 'carry 1 gel + 500ml water; refill at park taps',
                'door_to_door_achievable': True,
            }
    # Drive-to long run
    ext = external_for_zone(zone)
    if ext:
        return {
            'name': f"{ext['long']} (drive-to)",
            'distance_km': 20.0,
            'surface': 'paved + crushed',
            'lighting': 'unlit',
            'winter_ok': False,
            'road_crossings': 3,
            'dog_friendly': 'leash on trail',
            'scenery': 'local creek/conservation area',
            'starts_at_trail': f"{ext['long']} — drive 10-20 min from door; no door-to-door 20K achievable",
            'approx_warmup_to_trailhead_min': 0,
            'strava_segment_estimated': None,
            'fueling_note': 'carry full water bottle + 2 gels — limited refill in conservation areas',
            'door_to_door_achievable': False,
            'note': 'For a doorstep 20K consider driving to Mississauga Waterfront or Martin Goodman Trail instead',
        }
    # Fallback — road long run
    return {
        'name': 'Mixed road long run from door',
        'distance_km': 20.0,
        'surface': 'sidewalk + minor road',
        'lighting': 'street-lit',
        'winter_ok': True,
        'road_crossings': 15,
        'dog_friendly': 'leash on sidewalk',
        'scenery': 'suburban arterials',
        'starts_at_trail': 'no major trail within 4km — road-only long run; consider driving to Waterfront Trail',
        'approx_warmup_to_trailhead_min': 0,
        'strava_segment_estimated': None,
        'fueling_note': 'plan a water cache or convenience-store loop',
        'door_to_door_achievable': False,
    }


def winter_alt(td, zone):
    """Pick the nearest winter-maintained trail (or fallback)."""
    for d, pt, tr in td:
        if tr['winter']:
            label = f"{tr['name']} (winter-cleared)"
            if d <= 1.5:
                return f"{label} — {int(d*1000)}m from door"
            return f"{label} — {round(d,1)}km drive or warmup"
    if 'oakville' in zone.lower():
        return 'Sixteen Mile Creek paved sections (partially cleared) — verify in person Dec-Mar'
    if 'brampton' in zone.lower():
        return 'Etobicoke Creek south sections + sidewalk loops'
    if 'milton' in zone.lower():
        return 'Indoor track at Milton Sports Centre + sidewalk loops'
    return 'Burnhamthorpe Trail (winter-cleared) + Mississauga Valley sidewalks'


def best_for_note(td, zone):
    if td and td[0][0] <= 0.6:
        tr = td[0][2]
        return f"doorstep access to {tr['name']} — ideal pre-shift easy aerobic"
    if td and td[0][0] <= 1.5:
        tr = td[0][2]
        return f"short warmup to {tr['name']} — works for tempo + long runs"
    if td and td[0][0] <= 3.0:
        return 'best as weekend long-run base — weekday runs are road-heavy'
    return 'road-only from door — keep trail runs as weekend drive-to sessions'


# ---------- Main ----------

def main():
    listings = []
    for fn in ['wave2_listings.jsonl', 'more_listings.jsonl']:
        with open(DATA / fn) as f:
            for line in f:
                listings.append(json.loads(line))

    out = {}
    door_20k_count = 0

    for l in listings:
        lat, lng = l['lat'], l['lng']
        zone = l.get('zone', '')
        td = trail_distances(lat, lng)
        pd = park_distances(lat, lng)

        k5 = build_5k(lat, lng, td, pd, zone)
        k10 = build_10k(lat, lng, td, pd, zone)
        k20 = build_20k(lat, lng, td, pd, zone)

        if k20.get('door_to_door_achievable'):
            door_20k_count += 1

        nearest = td[0]
        out[l['id']] = {
            'building': l.get('name'),
            'zone': zone,
            'nearest_trail': {
                'name': nearest[2]['name'],
                'distance_km': round(nearest[0], 2),
            },
            '5k': k5,
            '10k': k10,
            '20k_long_run': k20,
            'winter_alternative': winter_alt(td, zone),
            'best_for': best_for_note(td, zone),
        }

    with open(DATA / 'run_routes.json', 'w') as f:
        json.dump(out, f, indent=2)

    print(f'Wrote {len(out)} buildings to run_routes.json')
    print(f'Door-to-door 20K achievable: {door_20k_count}/{len(out)} ({100*door_20k_count/len(out):.1f}%)')

    # Zone breakdown of 20K achievability
    by_zone = defaultdict(lambda: [0, 0])
    for l in listings:
        rid = l['id']
        by_zone[l['zone']][1] += 1
        if out[rid]['20k_long_run'].get('door_to_door_achievable'):
            by_zone[l['zone']][0] += 1
    print('\nTop zones by door-to-door 20K share:')
    for z, (a, b) in sorted(by_zone.items(), key=lambda x: -x[1][0])[:15]:
        print(f'  {a}/{b}  {z}')


if __name__ == '__main__':
    main()
