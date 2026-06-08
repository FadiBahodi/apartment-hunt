#!/usr/bin/env python3
"""Wave L — fetch Google Maps traffic RANGES (optimistic + best + pessimistic)
for top 50 finalist buildings × 3 time slots × 2 directions.

This solves the "your single number is misleading" problem. We'll display
"Mon 7am: 25-49 min" instead of "Mon 7am: 41 min".

Time slots:
  - mon_7am  AM shift start, home → CVH
  - mon_3pm  Day shift end, CVH → home (the painful direction)
  - sat_10am Weekend leisure, home → CVH

Models: optimistic, best_guess, pessimistic

Budget: ~50 buildings × 3 times × 3 models × 1-2 dirs = 600-900 calls = $6-9
Run with: CONFIRM=1 python3 data/fetch_google_range.py
"""
import os, sys, json, time, urllib.request, calendar
from datetime import datetime, timedelta

API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
if not API_KEY:
    print("ERROR: GOOGLE_MAPS_API_KEY missing", file=sys.stderr); sys.exit(1)

CVH = (43.5594, -79.7037)

def next_weekday(wd, hour):
    today = datetime.now()
    days = (wd - today.weekday()) % 7
    if days == 0 and today.hour >= hour: days = 7
    target = today + timedelta(days=days)
    return int(target.replace(hour=hour, minute=0, second=0, microsecond=0).timestamp())

MON_7AM = next_weekday(calendar.MONDAY, 7)
MON_3PM = next_weekday(calendar.MONDAY, 15)
SAT_10AM = next_weekday(calendar.SATURDAY, 10)

MODELS = ['optimistic', 'best_guess', 'pessimistic']

def fetch(olat, olng, dlat, dlng, dep, model):
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={olat},{olng}&destinations={dlat},{dlng}&departure_time={dep}&traffic_model={model}&mode=driving&key={API_KEY}'
    try:
        d = json.load(urllib.request.urlopen(url, timeout=20))
        el = d['rows'][0]['elements'][0]
        if el.get('status') != 'OK': return None
        return round(el.get('duration_in_traffic', el['duration'])['value']/60.0, 1)
    except Exception as e:
        return None

# Load existing
RANGE_PATH = 'data/google_ranges.json'
ranges = json.load(open(RANGE_PATH)) if os.path.exists(RANGE_PATH) else {'updated': None, 'routes': {}}

# Top 50: finalists + verified + Wave G best + Zone H best
TOP_IDS = [
    # Finalists (15)
    'eau_du_soleil','vita_on_the_lake','lago_waterfront','park_lawn_285','shoreline_towers',
    'markwood_4365','arc_erin_mills','collegeway_2285','collegeway_2375','reid_drive',
    'lakewood_ii_1285','lakeshore_2335','lakeshore_2495','lakeshore_206e','bloordale_4340',
]

# Add wave 4 + wave 5 top scores (load + sort by axis_cvh_min ascending as proxy)
import re
def load_listings(fn):
    out = []
    if not os.path.exists(fn): return out
    for line in open(fn):
        line = line.strip()
        if not line: continue
        try:
            d = json.loads(line)
            out.append(d)
        except: pass
    return out

for fn in ['data/wave4_zones.jsonl', 'data/wave5_high_park.jsonl']:
    for d in load_listings(fn):
        if d.get('id') and d['id'] not in TOP_IDS:
            TOP_IDS.append(d['id'])
TOP_IDS = TOP_IDS[:60]  # cap

# Need lat/lng for each
ALL_COORDS = {}
text = open('data.js').read()
for m in re.finditer(r'\{\s*id:\s*"([^"]+)"[^}]*?lat:\s*([\-\d.]+),\s*lng:\s*([\-\d.]+)', text, re.DOTALL):
    ALL_COORDS[m.group(1)] = (float(m.group(2)), float(m.group(3)))
for fn in ['data/more_listings.jsonl','data/wave2_listings.jsonl','data/wave3_listings.jsonl','data/wave4_zones.jsonl','data/wave5_high_park.jsonl']:
    for d in load_listings(fn):
        if d.get('lat') and d.get('lng'):
            ALL_COORDS[d['id']] = (d['lat'], d['lng'])

targets = [(bid, ALL_COORDS[bid]) for bid in TOP_IDS if bid in ALL_COORDS]
print(f'Top targets: {len(targets)}')

count = 0
for i, (bid, (lat, lng)) in enumerate(targets):
    if bid not in ranges['routes']:
        ranges['routes'][bid] = {}

    # Mon 7am (home → CVH)
    if 'mon_7am' not in ranges['routes'][bid]:
        result = {}
        for m in MODELS:
            v = fetch(lat, lng, CVH[0], CVH[1], MON_7AM, m)
            if v is not None: result[m] = v
            time.sleep(0.05)
        if result: ranges['routes'][bid]['mon_7am'] = result; count += len(result)

    # Mon 3pm (CVH → home — REVERSE direction, end-of-shift)
    if 'mon_3pm_home' not in ranges['routes'][bid]:
        result = {}
        for m in MODELS:
            v = fetch(CVH[0], CVH[1], lat, lng, MON_3PM, m)
            if v is not None: result[m] = v
            time.sleep(0.05)
        if result: ranges['routes'][bid]['mon_3pm_home'] = result; count += len(result)

    # Sat 10am (weekend leisure, home → CVH for context)
    if 'sat_10am' not in ranges['routes'][bid]:
        result = {}
        for m in MODELS:
            v = fetch(lat, lng, CVH[0], CVH[1], SAT_10AM, m)
            if v is not None: result[m] = v
            time.sleep(0.05)
        if result: ranges['routes'][bid]['sat_10am'] = result; count += len(result)

    if (i+1) % 10 == 0:
        ranges['updated'] = datetime.now().isoformat()
        json.dump(ranges, open(RANGE_PATH, 'w'), indent=2)
        print(f'  [{i+1}/{len(targets)}] +{count} routes so far')

ranges['updated'] = datetime.now().isoformat()
json.dump(ranges, open(RANGE_PATH, 'w'), indent=2)
print(f'\nDone. +{count} routes (~${count*0.01:.2f})')
