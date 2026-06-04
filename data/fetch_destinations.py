#!/usr/bin/env python3
"""Fetch OSRM driving routes to multiple relevant destinations.

Destinations matter for a 27-year-old single attending starting at CVH:
- CVH (work) — already in osrm_routes.json
- King West (date spot + downtown core social)
- Yorkville (high-end date spot, brunch culture)
- Harbourfront (his old life, casual dates, runs)
- Pearson Airport YYZ (US trips, soured-by-NYC factor)
- Mississauga Hospital / Trillium (cross-coverage med community)
"""
import json, urllib.request, urllib.parse, time, sys, re, os

OSRM = "https://router.project-osrm.org/route/v1/driving"
UA = "apartment-hunt/1.0 (fadi.bahodi@medportal.ca)"

DESTINATIONS = {
    "king_west": {"name": "King West / Wellington-Bathurst", "lat": 43.6437, "lng": -79.4030},
    "yorkville": {"name": "Yorkville / Bay-Bloor", "lat": 43.6705, "lng": -79.3940},
    "harbourfront": {"name": "Harbourfront (11 Charlotte)", "lat": 43.6432, "lng": -79.4006},
    "yyz_pearson": {"name": "Pearson Airport YYZ Terminal 1", "lat": 43.6777, "lng": -79.6248},
    "trillium_mississauga_hospital": {"name": "Trillium Mississauga Hospital", "lat": 43.5891, "lng": -79.5950},
    "toronto_general": {"name": "Toronto General Hospital", "lat": 43.6589, "lng": -79.3892},
}

def route(lat, lng, dest_lat, dest_lng):
    url = f"{OSRM}/{lng:.5f},{lat:.5f};{dest_lng:.5f},{dest_lat:.5f}?overview=false"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                d = json.loads(r.read().decode())
                if d.get("code") == "Ok" and d.get("routes"):
                    rt = d["routes"][0]
                    return {"duration_min": round(rt["duration"]/60, 1), "distance_km": round(rt["distance"]/1000, 2)}
        except Exception as e:
            print(f"  retry {i+1}: {e}", file=sys.stderr)
            time.sleep(2)
    return None

def load_apartments():
    apts = []
    with open('/Users/rawproductivity/apartment-hunt/data.js') as f:
        text = f.read()
    for id_, lat, lng in re.findall(r'\{\s*id:\s*"([^"]+)"[^}]*?lat:\s*([\-\d.]+),\s*lng:\s*([\-\d.]+)', text, re.DOTALL):
        apts.append({"id": id_, "lat": float(lat), "lng": float(lng)})
    for fn in ['/Users/rawproductivity/apartment-hunt/data/more_listings.jsonl',
               '/Users/rawproductivity/apartment-hunt/data/wave2_listings.jsonl']:
        if not os.path.exists(fn): continue
        for line in open(fn):
            line = line.strip()
            if not line: continue
            try:
                d = json.loads(line)
                apts.append({"id": d["id"], "lat": d["lat"], "lng": d["lng"]})
            except: pass
    seen = {}
    for a in apts:
        if a["id"] not in seen:
            seen[a["id"]] = a
    return list(seen.values())

def main():
    apts = load_apartments()
    print(f"Routing {len(apts)} apartments to {len(DESTINATIONS)} destinations = {len(apts)*len(DESTINATIONS)} routes")
    out = {}
    for i, a in enumerate(apts):
        if a["lat"] < 43.0 or a["lat"] > 44.5: continue
        out[a["id"]] = {}
        for dkey, d in DESTINATIONS.items():
            r = route(a["lat"], a["lng"], d["lat"], d["lng"])
            if r: out[a["id"]][dkey] = r
            time.sleep(0.5)
        if (i+1) % 10 == 0:
            print(f"  [{i+1}/{len(apts)}] complete")
            with open('/Users/rawproductivity/apartment-hunt/data/destinations.json', 'w') as f:
                json.dump({"meta": {"destinations": DESTINATIONS}, "routes": out}, f)
    with open('/Users/rawproductivity/apartment-hunt/data/destinations.json', 'w') as f:
        json.dump({"meta": {"destinations": DESTINATIONS}, "routes": out}, f)
    print(f"\nFINAL: {len(out)} apartments × {len(DESTINATIONS)} destinations")

if __name__ == "__main__":
    main()
