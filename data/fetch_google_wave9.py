#!/usr/bin/env python3
"""Google fetch for Wave 9 (Mario's 44 MLS units) — focused 3 time slots that matter for ER 12pm-6am shifts.

Time slots:
  - mon_7am  AM shift start (Home → CVH)
  - mon_6am_home  6am POST-night-shift (CVH → home — empty roads)
  - mon_3pm_home  3pm PM peak (CVH → home — the brutal one)

44 units × 3 = 132 calls ≈ $1.32
"""
import json, os, sys, time, urllib.request, calendar
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
MON_6AM = next_weekday(calendar.MONDAY, 6)
MON_3PM = next_weekday(calendar.MONDAY, 15)

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
for line in open('data/wave9_mls_mario.jsonl'):
    line = line.strip()
    if not line: continue
    d = json.loads(line)
    if d.get('lat') and d.get('lng'): targets.append((d['id'], d['lat'], d['lng']))
print(f'Targets: {len(targets)}')

count = 0
for i, (bid, lat, lng) in enumerate(targets):
    if bid not in g['routes']: g['routes'][bid] = {}
    if 'cvh' not in g['routes'][bid]: g['routes'][bid]['cvh'] = {}
    if 'mon_7am' not in g['routes'][bid]['cvh']:
        r = fetch(lat, lng, CVH[0], CVH[1], MON_7AM)
        if r: g['routes'][bid]['cvh']['mon_7am'] = r; count += 1
        time.sleep(0.05)
    if 'mon_6am_home' not in g['routes'][bid]['cvh']:
        r = fetch(CVH[0], CVH[1], lat, lng, MON_6AM)
        if r: g['routes'][bid]['cvh']['mon_6am_home'] = r; count += 1
        time.sleep(0.05)
    if 'pm_3pm' not in g['routes'][bid]['cvh']:
        r = fetch(CVH[0], CVH[1], lat, lng, MON_3PM)
        if r: g['routes'][bid]['cvh']['pm_3pm'] = r; count += 1
        time.sleep(0.05)
    if (i+1) % 15 == 0:
        g['meta']['updated'] = datetime.now().isoformat()
        json.dump(g, open('data/google_routes.json', 'w'), indent=2)
        print(f'  [{i+1}/{len(targets)}] +{count}')

g['meta']['updated'] = datetime.now().isoformat()
json.dump(g, open('data/google_routes.json', 'w'), indent=2)
print(f'Done. +{count} routes (~${count*0.01:.2f})')
