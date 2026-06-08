#!/usr/bin/env python3
"""Google Distance Matrix fetch for wave6 (King West) + wave7 (Junction depth) + wave8 (Square One).
~81 buildings × 3 routes = 243 calls = ~$2.43.
"""
import json, os, sys, time, urllib.request, calendar
from datetime import datetime, timedelta

API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
if not API_KEY:
    print("ERROR: GOOGLE_MAPS_API_KEY missing", file=sys.stderr); sys.exit(1)

CVH = (43.5594, -79.7037); KING_WEST = (43.6437, -79.4030)

def next_weekday(wd, hour):
    today = datetime.now()
    days = (wd - today.weekday()) % 7
    if days == 0 and today.hour >= hour: days = 7
    target = today + timedelta(days=days)
    return int(target.replace(hour=hour, minute=0, second=0, microsecond=0).timestamp())

MON_7AM = next_weekday(calendar.MONDAY, 7)
FRI_5PM = next_weekday(calendar.FRIDAY, 17)

def fetch(olat, olng, dlat, dlng, dep):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={olat},{olng}&destinations={dlat},{dlng}&departure_time={dep}&traffic_model=best_guess&mode=driving&key={API_KEY}"
    try:
        d = json.load(urllib.request.urlopen(url, timeout=20))
        el = d['rows'][0]['elements'][0]
        if el.get('status') != 'OK': return None
        dur = el.get('duration_in_traffic', el['duration'])['value']/60.0
        dist = el['distance']['value']/1000.0
        return {'duration_min': round(dur,1), 'distance_km': round(dist,2)}
    except: return None

g = json.load(open('data/google_routes.json'))
targets = []
for fn in ['data/wave6_king_west.jsonl', 'data/wave7_junction_depth.jsonl', 'data/wave8_square_one.jsonl']:
    if not os.path.exists(fn): continue
    for line in open(fn):
        line = line.strip()
        if not line: continue
        try:
            d = json.loads(line)
            if d.get('lat') and d.get('lng'): targets.append((d['id'], d['lat'], d['lng']))
        except: pass
print(f'Targets: {len(targets)}')

count = 0
for i, (bid, lat, lng) in enumerate(targets):
    if bid not in g['routes']: g['routes'][bid] = {}
    if 'cvh' not in g['routes'][bid]: g['routes'][bid]['cvh'] = {}
    if 'king_west' not in g['routes'][bid]: g['routes'][bid]['king_west'] = {}
    if 'mon_7am' not in g['routes'][bid]['cvh']:
        r = fetch(lat, lng, CVH[0], CVH[1], MON_7AM)
        if r: g['routes'][bid]['cvh']['mon_7am'] = r; count += 1
        time.sleep(0.05)
    if 'pm_5pm' not in g['routes'][bid]['cvh']:
        r = fetch(CVH[0], CVH[1], lat, lng, FRI_5PM)
        if r: g['routes'][bid]['cvh']['pm_5pm'] = r; count += 1
        time.sleep(0.05)
    if 'mon_7am' not in g['routes'][bid]['king_west']:
        r = fetch(lat, lng, KING_WEST[0], KING_WEST[1], MON_7AM)
        if r: g['routes'][bid]['king_west']['mon_7am'] = r; count += 1
        time.sleep(0.05)
    if (i+1) % 15 == 0:
        g['meta']['updated'] = datetime.now().isoformat()
        json.dump(g, open('data/google_routes.json', 'w'), indent=2)
        print(f'  [{i+1}/{len(targets)}] +{count} routes')
g['meta']['updated'] = datetime.now().isoformat()
json.dump(g, open('data/google_routes.json', 'w'), indent=2)
print(f'\nDone. +{count} routes (~${count*0.01:.2f})')
