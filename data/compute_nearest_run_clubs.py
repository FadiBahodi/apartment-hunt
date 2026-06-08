#!/usr/bin/env python3
"""Compute the nearest 3 run clubs per building (by haversine distance).
Writes data/nearest_run_clubs.json: {building_id: [{club, dist_km, ...}]}
"""
import json, re, math, os

def hav(la1, lo1, la2, lo2):
    R = 6371
    la1, lo1, la2, lo2 = map(math.radians, [la1, lo1, la2, lo2])
    a = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return R * 2 * math.asin(math.sqrt(a))

# Geocode meet_location -> (lat,lng) via OSM Nominatim ? Or use area as proxy.
# Faster: use a manual map of common Toronto meet areas → coords
AREA_COORDS = {
    'Parkdale': (43.6395, -79.4395), 'West Toronto': (43.6500, -79.4500),
    'Liberty Village': (43.6385, -79.4180), 'King West': (43.6437, -79.4030),
    'High Park': (43.6465, -79.4640), 'Junction': (43.6620, -79.4540),
    'Roncesvalles': (43.6480, -79.4470), 'Bloor West': (43.6500, -79.4900),
    'Humber Bay': (43.6230, -79.4810), 'Mimico': (43.6080, -79.4970),
    'Long Branch': (43.5905, -79.5325), 'Etobicoke': (43.6450, -79.5500),
    'Stonegate': (43.6320, -79.4970), 'Mississauga': (43.5890, -79.6440),
    'Port Credit': (43.5560, -79.5870), 'Streetsville': (43.5840, -79.7170),
    'Erin Mills': (43.5610, -79.7160), 'Cooksville': (43.5810, -79.6390),
    'Lakeshore': (43.5950, -79.5400), 'Toronto': (43.6532, -79.3832),
    'Downtown': (43.6532, -79.3832),
}

def club_coords(club):
    """Best-effort guess of club's meet area lat/lng."""
    area = (club.get('area') or '').lower()
    for k, c in AREA_COORDS.items():
        if k.lower() in area: return c
    # Fallback: search meet_locations for known area names
    for loc in club.get('meet_locations', []):
        for k, c in AREA_COORDS.items():
            if k.lower() in loc.lower(): return c
    return None

rc = json.load(open('data/run_clubs.json'))
clubs = rc['clubs']
# Decorate each club with approximate lat/lng
for c in clubs:
    coords = club_coords(c)
    if coords:
        c['_lat'], c['_lng'] = coords

# Load all buildings
import re
all_b = {}
text = open('data.js').read()
for m in re.finditer(r'\{\s*id:\s*"([^"]+)"[^}]*?lat:\s*([\-\d.]+),\s*lng:\s*([\-\d.]+)', text, re.DOTALL):
    all_b[m.group(1)] = (float(m.group(2)), float(m.group(3)))
for fn in ['data/more_listings.jsonl','data/wave2_listings.jsonl','data/wave3_listings.jsonl','data/wave4_zones.jsonl','data/wave5_high_park.jsonl','data/wave6_king_west.jsonl','data/wave7_junction_depth.jsonl']:
    if not os.path.exists(fn): continue
    for line in open(fn):
        line = line.strip()
        if not line: continue
        try:
            d = json.loads(line)
            if d.get('lat') and d.get('lng'): all_b[d['id']] = (d['lat'], d['lng'])
        except: pass
print(f'Buildings: {len(all_b)}')

out = {}
for bid, (lat, lng) in all_b.items():
    ranked = []
    for c in clubs:
        if '_lat' not in c: continue
        d = hav(lat, lng, c['_lat'], c['_lng'])
        ranked.append((d, c))
    ranked.sort(key=lambda x: x[0])
    out[bid] = [
        {
            'name': c['name'],
            'dist_km': round(d, 1),
            'area': c.get('area',''),
            'meet_days': c.get('meet_days',''),
            'demographics': c.get('demographics_age_skew',''),
            'social_signal': c.get('social_signal','')[:120] if c.get('social_signal') else '',
        }
        for d, c in ranked[:3]
    ]

with open('data/nearest_run_clubs.json','w') as f: json.dump(out, f, indent=2)
print(f'Wrote nearest_run_clubs for {len(out)} buildings')
