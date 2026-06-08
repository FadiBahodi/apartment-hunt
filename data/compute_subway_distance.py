#!/usr/bin/env python3
"""Compute nearest subway/GO station + walking distance for all 700+ buildings.
Uses a hard-coded list of major GTA-west transit stations (no Overpass needed — faster + cached).
"""
import json, re, math, os

# All BD/YUS subway stations + GO Lakeshore West / Milton stations within 50km of CVH
STATIONS = [
    # BD (Line 2) — west to east
    ('Kipling',       43.6376, -79.5358, 'subway_bd'),
    ('Islington',     43.6451, -79.5239, 'subway_bd'),
    ('Royal York',    43.6480, -79.5099, 'subway_bd'),
    ('Old Mill',      43.6502, -79.4956, 'subway_bd'),
    ('Jane',          43.6493, -79.4849, 'subway_bd'),
    ('Runnymede',     43.6517, -79.4761, 'subway_bd'),
    ('High Park',     43.6539, -79.4670, 'subway_bd'),
    ('Keele',         43.6553, -79.4584, 'subway_bd'),
    ('Dundas West',   43.6660, -79.4516, 'subway_bd'),
    ('Lansdowne',     43.6601, -79.4419, 'subway_bd'),
    ('Dufferin',      43.6606, -79.4350, 'subway_bd'),
    ('Ossington',     43.6622, -79.4257, 'subway_bd'),
    ('Christie',      43.6647, -79.4180, 'subway_bd'),
    ('Bathurst',      43.6660, -79.4109, 'subway_bd'),
    # YUS (Line 1) selected southern
    ('St George',     43.6680, -79.3998, 'subway_yus'),
    ('Spadina',       43.6677, -79.4044, 'subway_yus'),
    ('Union',         43.6453, -79.3806, 'subway_yus'),
    # GO Lakeshore West (Mississauga + Etobicoke)
    ('Mimico GO',     43.6122, -79.4961, 'go_lakeshore'),
    ('Long Branch GO',43.5938, -79.5371, 'go_lakeshore'),
    ('Port Credit GO',43.5536, -79.5832, 'go_lakeshore'),
    ('Clarkson GO',   43.5093, -79.6242, 'go_lakeshore'),
    ('Oakville GO',   43.4444, -79.6794, 'go_lakeshore'),
    # GO Milton (Streetsville)
    ('Streetsville GO',43.5816,-79.7187, 'go_milton'),
    ('Cooksville GO', 43.5817, -79.6240, 'go_milton'),
    ('Erindale GO',   43.5573, -79.6601, 'go_milton'),
    ('Meadowvale GO', 43.5926, -79.7715, 'go_milton'),
    # Hurontario LRT (under construction, opens 2026)
    ('Mississauga City Centre (LRT)', 43.5938, -79.6440, 'lrt'),
    ('Cooksville (LRT)', 43.5837, -79.6240, 'lrt'),
    ('Port Credit Loop (LRT)', 43.5560, -79.5870, 'lrt'),
    # UP Express
    ('Bloor UP Express', 43.6660, -79.4516, 'up_express'),  # Dundas West station shared
    ('Weston UP Express', 43.7042, -79.5240, 'up_express'),
    ('Pearson UP Express', 43.6777, -79.6248, 'up_express'),
]

def hav(la1, lo1, la2, lo2):
    R = 6371
    la1, lo1, la2, lo2 = map(math.radians, [la1, lo1, la2, lo2])
    a = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return R * 2 * math.asin(math.sqrt(a))

all_b = {}
text = open('data.js').read()
for m in re.finditer(r'\{\s*id:\s*"([^"]+)"[^}]*?lat:\s*([\-\d.]+),\s*lng:\s*([\-\d.]+)', text, re.DOTALL):
    all_b[m.group(1)] = (float(m.group(2)), float(m.group(3)))
for fn in ['data/more_listings.jsonl','data/wave2_listings.jsonl','data/wave3_listings.jsonl','data/wave4_zones.jsonl','data/wave5_high_park.jsonl','data/wave6_king_west.jsonl','data/wave7_junction_depth.jsonl','data/wave8_square_one.jsonl']:
    if not os.path.exists(fn): continue
    for line in open(fn):
        line = line.strip()
        if not line: continue
        try:
            d = json.loads(line)
            if d.get('lat') and d.get('lng'): all_b[d['id']] = (d['lat'], d['lng'])
        except: pass
print(f'Buildings: {len(all_b)}')

# Approx walk speed 5km/h = 12 min/km, so walk_min = dist_km * 12
out = {}
for bid, (lat, lng) in all_b.items():
    ranked = []
    for name, slat, slng, kind in STATIONS:
        d_km = hav(lat, lng, slat, slng)
        ranked.append((d_km, name, kind))
    ranked.sort()
    # Top 3 nearest stations, regardless of kind
    out[bid] = {
        'top3': [
            {'station': name, 'kind': kind, 'dist_km': round(d, 2), 'walk_min': round(d * 12)}
            for d, name, kind in ranked[:3]
        ],
        # Best subway-walkable (BD/YUS) ≤1.5km
        'best_subway_walkable': next(
            ({'station': name, 'dist_km': round(d, 2), 'walk_min': round(d * 12)}
             for d, name, kind in ranked if kind.startswith('subway') and d <= 1.5),
            None
        ),
        'best_go_walkable': next(
            ({'station': name, 'dist_km': round(d, 2), 'walk_min': round(d * 12)}
             for d, name, kind in ranked if kind.startswith('go') and d <= 2.0),
            None
        ),
    }
with open('data/transit_distances.json','w') as f: json.dump(out, f, indent=2)
print(f'Wrote data/transit_distances.json for {len(out)} buildings')

# Stats
subway_walkable = sum(1 for v in out.values() if v['best_subway_walkable'])
go_walkable = sum(1 for v in out.values() if v['best_go_walkable'])
print(f'  Subway-walkable (≤1.5km): {subway_walkable}')
print(f'  GO-walkable (≤2km):       {go_walkable}')
