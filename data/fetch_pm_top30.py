#!/usr/bin/env python3
"""Focused PM-direction Google fetch for top-30 finalists only.

Budget: 30 buildings × 2 times (Mon 2pm + Fri 5pm CVH→home) = 60 routes ≈ $0.60.
This adds the painful end-of-shift commute number per finalist.
"""
import json, os, sys, time, urllib.request, urllib.parse
from datetime import datetime, timedelta
import calendar

API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
if not API_KEY:
    print("ERROR: GOOGLE_MAPS_API_KEY not set", file=sys.stderr); sys.exit(1)

CVH = (43.5594, -79.7037)

def next_weekday(wd, hour):
    today = datetime.now()
    days = (wd - today.weekday()) % 7
    if days == 0 and today.hour >= hour: days = 7
    target = today + timedelta(days=days)
    return int(target.replace(hour=hour, minute=0, second=0, microsecond=0).timestamp())

TIMES_PM = {
    'pm_2pm': next_weekday(calendar.MONDAY, 14),
    'pm_5pm': next_weekday(calendar.FRIDAY, 17),
}

def fetch(olat, olng, dlat, dlng, dep):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={olat},{olng}&destinations={dlat},{dlng}&departure_time={dep}&traffic_model=best_guess&mode=driving&key={API_KEY}"
    try:
        d = json.load(urllib.request.urlopen(url, timeout=15))
        el = d['rows'][0]['elements'][0]
        if el.get('status') != 'OK': return None, el.get('status')
        dur = el.get('duration_in_traffic', el['duration'])['value']/60.0
        dist = el['distance']['value']/1000.0
        return {'duration_min': round(dur,1), 'distance_km': round(dist,2)}, 'OK'
    except Exception as e:
        return None, str(e)

# Build top-30 list: 15 finalists + 15 next-best Verified by Fit (a rough proxy)
finalists = list(json.load(open('data/finalist_deep.json')).keys())
print(f'Finalists: {len(finalists)}')

# Collect all buildings with their lat/lng
import re
all_apts = {}
text = open('data.js').read()
for m in re.finditer(r'\{\s*id:\s*"([^"]+)"[^}]*?lat:\s*([\-\d.]+),\s*lng:\s*([\-\d.]+)', text, re.DOTALL):
    all_apts[m.group(1)] = (float(m.group(2)), float(m.group(3)))
for fn in ['data/more_listings.jsonl', 'data/wave2_listings.jsonl', 'data/wave3_listings.jsonl']:
    for line in open(fn):
        line = line.strip()
        if not line: continue
        try:
            d = json.loads(line)
            if d.get('lat') and d.get('lng') and d['id'] not in all_apts:
                all_apts[d['id']] = (d['lat'], d['lng'])
        except: pass

# Top-30 = all 15 finalists + 15 buildings closest to CVH (Strategy B picks worth checking)
def hav(lat1, lng1, lat2=CVH[0], lng2=CVH[1]):
    from math import radians, cos, sin, asin, sqrt
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    a = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lng2-lng1)/2)**2
    return 6371 * 2 * asin(sqrt(a))

extra_candidates = [(bid, hav(*pos)) for bid, pos in all_apts.items() if bid not in finalists]
extra_candidates.sort(key=lambda x: x[1])
top_extra = [b for b, _ in extra_candidates[:15]]

top30 = list(set(finalists + top_extra))
print(f'Top-30 set: {len(top30)} buildings')

# Load existing google_routes
out_path = 'data/google_routes.json'
out = json.load(open(out_path))

count = 0
for bid in top30:
    if bid not in all_apts: continue
    lat, lng = all_apts[bid]
    if bid not in out['routes']: out['routes'][bid] = {}
    if 'cvh' not in out['routes'][bid]: out['routes'][bid]['cvh'] = {}
    for tkey, dep in TIMES_PM.items():
        if tkey in out['routes'][bid]['cvh']: continue  # cached
        # PM direction: CVH → building
        r, status = fetch(CVH[0], CVH[1], lat, lng, dep)
        if r is None:
            print(f'  {bid} {tkey}: {status}', file=sys.stderr)
            continue
        out['routes'][bid]['cvh'][tkey] = r
        count += 1
        time.sleep(0.05)
    if count and count % 10 == 0:
        json.dump(out, open(out_path,'w'), indent=2)
        print(f'  saved (so far +{count} routes)')

out['meta']['updated'] = datetime.now().isoformat()
json.dump(out, open(out_path,'w'), indent=2)
print(f'\nDone. +{count} new PM routes (≈${count*0.01:.2f})')
