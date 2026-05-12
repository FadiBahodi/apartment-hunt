#!/usr/bin/env python3
"""Fetch real driving routes from OSRM. Free, no key.

For each apartment, query OSRM for the actual driving route from apt → CVH.
Returns: route geometry (for isochrone-like display) + real duration + distance.
"""
import json, urllib.request, urllib.parse, time, sys, re, os

CVH = (43.5594410, -79.7037121)
OSRM = "https://router.project-osrm.org/route/v1/driving"
UA = "apartment-hunt/1.0 (fadi.bahodi@medportal.ca)"

def route(lat, lng, dest=CVH):
    url = f"{OSRM}/{lng:.5f},{lat:.5f};{dest[1]:.5f},{dest[0]:.5f}?overview=simplified&geometries=geojson"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.loads(r.read().decode())
                if d.get("code") == "Ok" and d.get("routes"):
                    rt = d["routes"][0]
                    return {
                        "duration_min": round(rt["duration"]/60, 1),
                        "distance_km": round(rt["distance"]/1000, 2),
                        "geometry": rt.get("geometry")  # GeoJSON LineString [lng,lat]
                    }
        except Exception as e:
            print(f"  retry {i+1}: {e}", file=sys.stderr)
            time.sleep(3)
    return None

def load_apartments():
    apts = []
    # Hand-curated from data.js — parse out id, lat, lng
    with open('/Users/rawproductivity/apartment-hunt/data.js') as f:
        text = f.read()
    # Find blocks like { id: "...", ..., lat: X, lng: Y, ... }
    blocks = re.findall(r'\{\s*id:\s*"([^"]+)"[^}]*?lat:\s*([\-\d.]+),\s*lng:\s*([\-\d.]+)', text, re.DOTALL)
    for id_, lat, lng in blocks:
        apts.append({"id": id_, "lat": float(lat), "lng": float(lng), "source": "data.js"})
    # JSONL files
    for fn in ['/Users/rawproductivity/apartment-hunt/data/more_listings.jsonl',
               '/Users/rawproductivity/apartment-hunt/data/wave2_listings.jsonl']:
        if not os.path.exists(fn): continue
        for line in open(fn):
            line = line.strip()
            if not line: continue
            try:
                d = json.loads(line)
                apts.append({"id": d["id"], "lat": d["lat"], "lng": d["lng"], "source": os.path.basename(fn)})
            except: pass
    # Dedupe by id
    seen = {}
    for a in apts:
        if a["id"] not in seen:
            seen[a["id"]] = a
    return list(seen.values())

def main():
    apts = load_apartments()
    print(f"Routing {len(apts)} apartments to CVH...")
    out = {}
    for i, a in enumerate(apts):
        if a["lat"] < 43.0 or a["lat"] > 44.5: continue
        r = route(a["lat"], a["lng"])
        if r:
            out[a["id"]] = r
        if (i+1) % 20 == 0:
            print(f"  [{i+1}/{len(apts)}] complete; success: {len(out)}")
            # Save progress
            with open('/Users/rawproductivity/apartment-hunt/data/osrm_routes.json', 'w') as f:
                json.dump(out, f)
        time.sleep(0.6)  # be polite to public OSRM
    with open('/Users/rawproductivity/apartment-hunt/data/osrm_routes.json', 'w') as f:
        json.dump(out, f)
    print(f"\nFINAL: {len(out)}/{len(apts)} routed")
    print(f"File: /Users/rawproductivity/apartment-hunt/data/osrm_routes.json")

if __name__ == "__main__":
    main()
