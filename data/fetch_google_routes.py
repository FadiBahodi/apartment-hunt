#!/usr/bin/env python3
"""Fetch Google Maps Distance Matrix drive times for all buildings × key destinations.

THE FIX for the 'OSRM says 23min, Google says 38min' problem.

Setup:
1. Get a Google Cloud API key with Distance Matrix API enabled
   https://console.cloud.google.com/apis/library/distance-matrix-backend.googleapis.com
2. Get the free $200 credit (covers ~20,000 routes)
3. export GOOGLE_MAPS_API_KEY=AIza...
4. python3 data/fetch_google_routes.py
5. Outputs data/google_routes.json — used by site automatically

Cost: ~$0.01 per route. 500 buildings × 7 destinations × 3 time-of-day = 10,500 routes ≈ $105.
For just CVH at Mon 7am: 500 × 1 = $5.

Three time-of-day variants per destination:
- mon_7am   — Monday 7am (the painful shift commute)
- sat_10am  — Saturday 10am (weekend leisure)
- offpeak   — Sunday 5am (sanity baseline)

Usage:
  python3 data/fetch_google_routes.py            # all destinations, all times
  python3 data/fetch_google_routes.py cvh_only   # just CVH commute, all times
  python3 data/fetch_google_routes.py mon_7am    # all destinations, just Mon 7am
"""
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import re
from datetime import datetime, timedelta
import calendar

API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
if not API_KEY:
    print("ERROR: set GOOGLE_MAPS_API_KEY environment variable", file=sys.stderr)
    print("  Get one at https://console.cloud.google.com/apis/library/distance-matrix-backend.googleapis.com", file=sys.stderr)
    sys.exit(1)

DESTINATIONS = {
    "cvh":                          {"name": "Credit Valley Hospital",      "lat": 43.5594, "lng": -79.7037},
    "king_west":                    {"name": "King West / Wellington",      "lat": 43.6437, "lng": -79.4030},
    "yorkville":                    {"name": "Yorkville / Bay-Bloor",       "lat": 43.6705, "lng": -79.3940},
    "harbourfront":                 {"name": "Harbourfront",                "lat": 43.6432, "lng": -79.4006},
    "yyz_pearson":                  {"name": "Pearson YYZ T1",              "lat": 43.6777, "lng": -79.6248},
    "trillium_mississauga_hospital":{"name": "Trillium MS Hospital",        "lat": 43.5891, "lng": -79.5950},
    "toronto_general":              {"name": "Toronto General",             "lat": 43.6589, "lng": -79.3892},
}

# Future-dated departure times so Google uses live + historical patterns
def next_weekday(weekday, hour):
    """Get next occurrence of weekday at hour. Monday=0."""
    today = datetime.now()
    days = (weekday - today.weekday()) % 7
    if days == 0 and today.hour >= hour:
        days = 7
    target = today + timedelta(days=days)
    return int(target.replace(hour=hour, minute=0, second=0, microsecond=0).timestamp())

def next_saturday(hour=10):
    return next_weekday(calendar.SATURDAY, hour)

def next_sunday_5am():
    return next_weekday(calendar.SUNDAY, 5)

TIME_VARIANTS = {
    "mon_7am":  lambda: next_weekday(calendar.MONDAY, 7),
    "sat_10am": lambda: next_saturday(10),
    "offpeak":  lambda: next_sunday_5am(),
}

def fetch_route(origin_lat, origin_lng, dest_lat, dest_lng, departure_time):
    """Returns (duration_in_traffic_min, distance_km) or None."""
    base = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{origin_lat},{origin_lng}",
        "destinations": f"{dest_lat},{dest_lng}",
        "departure_time": str(departure_time),
        "traffic_model": "best_guess",
        "mode": "driving",
        "key": API_KEY,
    }
    url = f"{base}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            d = json.loads(r.read().decode())
        if d.get("status") != "OK":
            return None, None, d.get("status")
        elem = d["rows"][0]["elements"][0]
        if elem.get("status") != "OK":
            return None, None, elem.get("status")
        dur = elem.get("duration_in_traffic", elem["duration"])["value"] / 60.0
        dist = elem["distance"]["value"] / 1000.0
        return round(dur, 1), round(dist, 2), "OK"
    except Exception as e:
        return None, None, str(e)

def load_apartments():
    apts = []
    text = open(os.path.join(os.path.dirname(__file__), '..', 'data.js')).read()
    for m in re.finditer(r'\{\s*id:\s*"([^"]+)"[^}]*?lat:\s*([\-\d.]+),\s*lng:\s*([\-\d.]+)', text, re.DOTALL):
        apts.append({"id": m.group(1), "lat": float(m.group(2)), "lng": float(m.group(3))})
    for fn in ['more_listings.jsonl', 'wave2_listings.jsonl', 'wave3_listings.jsonl']:
        path = os.path.join(os.path.dirname(__file__), fn)
        if not os.path.exists(path):
            continue
        for line in open(path):
            line = line.strip()
            if not line: continue
            try:
                d = json.loads(line)
                if d.get("lat") and d.get("lng"):
                    apts.append({"id": d["id"], "lat": d["lat"], "lng": d["lng"]})
            except: pass
    seen, dedup = set(), []
    for a in apts:
        if a["id"] not in seen:
            dedup.append(a); seen.add(a["id"])
    return dedup

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    apts = load_apartments()
    print(f"Loaded {len(apts)} apartments")

    out_path = os.path.join(os.path.dirname(__file__), 'google_routes.json')
    out = json.load(open(out_path)) if os.path.exists(out_path) else {"meta": {"updated": None}, "routes": {}}

    dests = list(DESTINATIONS.keys())
    times = list(TIME_VARIANTS.keys())
    if mode == 'cvh_only':
        dests = ['cvh']
    elif mode in TIME_VARIANTS:
        times = [mode]

    total = len(apts) * len(dests) * len(times)
    print(f"Plan: {total} routes ({len(apts)} apts × {len(dests)} dests × {len(times)} times)")
    est_cost = total * 0.01
    print(f"Estimated cost: ${est_cost:.2f} USD")
    proceed = os.environ.get('CONFIRM') == '1' or input("Proceed? (y/N) ").lower() == 'y'
    if not proceed:
        print("Aborted"); return

    count = 0
    for i, a in enumerate(apts):
        if a["id"] not in out["routes"]:
            out["routes"][a["id"]] = {}
        for dkey in dests:
            dest = DESTINATIONS[dkey]
            if dkey not in out["routes"][a["id"]]:
                out["routes"][a["id"]][dkey] = {}
            for tkey in times:
                if tkey in out["routes"][a["id"]][dkey]:
                    continue  # already cached
                departure = TIME_VARIANTS[tkey]()
                dur, dist, status = fetch_route(a["lat"], a["lng"], dest["lat"], dest["lng"], departure)
                if dur is not None:
                    out["routes"][a["id"]][dkey][tkey] = {"duration_min": dur, "distance_km": dist}
                    count += 1
                else:
                    print(f"  {a['id']} → {dkey} {tkey}: {status}", file=sys.stderr)
                time.sleep(0.05)  # Polite throttle (Google allows 50 qps)
        if (i+1) % 20 == 0:
            out["meta"]["updated"] = datetime.now().isoformat()
            json.dump(out, open(out_path, 'w'), indent=2)
            print(f"  [{i+1}/{len(apts)}] saved (routes added so far: {count})")

    out["meta"]["updated"] = datetime.now().isoformat()
    out["meta"]["destinations"] = DESTINATIONS
    out["meta"]["time_variants"] = list(TIME_VARIANTS.keys())
    json.dump(out, open(out_path, 'w'), indent=2)
    print(f"\nDone. {count} new routes. Total apartments: {len(out['routes'])}")

if __name__ == "__main__":
    main()
