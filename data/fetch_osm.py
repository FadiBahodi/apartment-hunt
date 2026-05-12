#!/usr/bin/env python3
"""Fetch real OSM trail + park GeoJSON via Overpass API."""
import json, urllib.request, urllib.parse, time, sys

ENDPOINT = "https://overpass-api.de/api/interpreter"
UA = "apartment-hunt/1.0 (fadi.bahodi@medportal.ca)"

def overpass(query, retries=3):
    for i in range(retries):
        try:
            data = urllib.parse.urlencode({"data": query}).encode()
            req = urllib.request.Request(ENDPOINT, data=data, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            print(f"  retry {i+1}: {e}", file=sys.stderr)
            time.sleep(5)
    return {"elements": []}

# West-GTA bbox: south, west, north, east
BBOX_LARGE = "43.40,-79.95,43.75,-79.25"
BBOX_MISS = "43.45,-79.85,43.65,-79.50"

# Trail queries — (display_name, regex, bbox, attrs)
TRAILS = [
    ("David J. Culham Trail", "Culham", BBOX_MISS, {"length_km": 11.2, "winter_maintained": False, "surface": "paved+boardwalk+dirt", "note": "Best off-road trail near CVH. Streetsville to Burnhamthorpe. Reddit: 'only one car-street crossing'. NOT winter-maintained."}),
    ("Sawmill Valley Trail", "Sawmill Valley", BBOX_MISS, {"length_km": 5, "winter_maintained": False, "surface": "paved", "note": "Connects to Culham. UTM-edge route."}),
    ("Mississauga Waterfront Trail", "Waterfront Trail", "43.45,-79.65,43.60,-79.45", {"length_km": 16.9, "winter_maintained": False, "surface": "paved + boardwalk", "note": "Etobicoke Creek mouth to Jack Darling. Rattray Marsh prohibits bikes."}),
    ("Martin Goodman Trail", "Martin Goodman", "43.58,-79.55,43.66,-79.20", {"length_km": 22, "winter_maintained": True, "surface": "paved", "note": "ONLY year-round-cleared trail in west GTA. Plowed within 6-8h of >5cm snow."}),
    ("Etobicoke Creek Trail", "Etobicoke Creek", "43.55,-79.60,43.70,-79.50", {"length_km": 11, "winter_maintained": False, "surface": "paved + dirt", "note": "Marie Curtis to Centennial Park. Markland Wood golf BREAKS continuity Dundas-Burnhamthorpe."}),
    ("Burnhamthorpe Trail", "Burnhamthorpe Trail", BBOX_MISS, {"length_km": 11, "winter_maintained": True, "surface": "paved", "note": "Mississauga's main winter-maintained paved trail."}),
    ("Cooksville Creek Trail", "Cooksville Creek", BBOX_MISS, {"length_km": 6, "winter_maintained": True, "surface": "paved", "note": "Square One area winter option."}),
    ("Mimico Creek Trail", "Mimico Creek", "43.60,-79.55,43.68,-79.45", {"length_km": 8, "winter_maintained": False, "surface": "paved", "note": "Connects Humber Bay to Stonegate."}),
    ("Humber River Trail (south)", "Humber River", "43.62,-79.50,43.68,-79.43", {"length_km": 10, "winter_maintained": True, "surface": "paved", "note": "Lake to Old Mill section."}),
    ("Glen Erin Trail", "Glen Erin", BBOX_MISS, {"length_km": 4, "winter_maintained": False, "surface": "paved", "note": "Sawmill Valley/Culham connector."}),
]

# Parks
PARKS = [
    ("Erindale Park", "Erindale Park", BBOX_MISS, {"area_acres": 222, "note": "222-acre Mississauga's largest park; Culham trailhead"}),
    ("Centennial Park (Etobicoke)", "Centennial Park", "43.60,-79.62,43.68,-79.55", {"area_acres": 525, "note": "525-acre Toronto park; ski hill, Etobicoke Creek connector"}),
    ("Humber Bay Park East", "Humber Bay Park East", "43.61,-79.50,43.65,-79.46", {"area_acres": 50, "note": "Doorstep for Vita/Lago condos"}),
    ("Humber Bay Park West", "Humber Bay Park West", "43.61,-79.50,43.65,-79.46", {"area_acres": 40, "note": "Sheldon Lookout"}),
    ("Marie Curtis Park", "Marie Curtis", "43.57,-79.55,43.60,-79.52", {"area_acres": 60, "note": "Etobicoke Creek mouth at Lake Ontario"}),
    ("Colonel Samuel Smith Park", "Colonel Samuel Smith", "43.58,-79.55,43.62,-79.50", {"area_acres": 90, "note": "Per Great Runs, BEST west-GTA dog/run park"}),
    ("Rattray Marsh", "Rattray Marsh", "43.50,-79.65,43.54,-79.61", {"area_acres": 200, "note": "NO BIKES rule (CVC) — quiet runner haven"}),
    ("Jack Darling Memorial Park", "Jack Darling", "43.49,-79.63,43.52,-79.60", {"area_acres": 33, "note": "Major off-leash dog park"}),
    ("Riverwood Conservancy", "Riverwood", "43.56,-79.72,43.60,-79.67", {"area_acres": 150, "note": "Most-reviewed Mississauga trails (1,578 AllTrails reviews)"}),
    ("Sawmill Valley Park", "Sawmill Valley Park", BBOX_MISS, {"area_acres": 50, "note": "Trailhead for Culham/UTM connector"}),
    ("Bronte Creek Provincial Park", "Bronte Creek", "43.39,-79.74,43.43,-79.70", {"area_acres": 1700, "note": "Weekend option; 50m ravine"}),
    ("Lakefront Promenade Park", "Lakefront Promenade", "43.54,-79.56,43.57,-79.52", {"area_acres": 35, "note": "Mississauga waterfront tempo runs"}),
    ("Sheridan Park", "Sheridan Park", "43.52,-79.70,43.55,-79.65", {"area_acres": 100, "note": "Research woodlands in Sheridan"}),
    ("Garnetwood Park", "Garnetwood", "43.59,-79.62,43.62,-79.58", {"area_acres": 20, "note": "Applewood-adjacent green space"}),
    ("West Deane Park", "West Deane", "43.65,-79.59,43.68,-79.55", {"area_acres": 25, "note": "Mimico Creek corridor"}),
    ("South Common Park", "South Common", BBOX_MISS, {"area_acres": 15, "note": "Erin Mills South Common area"}),
    ("Riverwood Park", "Riverwood Park", BBOX_MISS, {"area_acres": 100, "note": "Conservancy land"}),
]

def fetch_trail(name, regex, bbox, attrs):
    q = f'[out:json][timeout:45];way["name"~"{regex}",i]({bbox});out geom;'
    print(f"Fetching trail: {name}")
    r = overpass(q)
    ways = [e for e in r.get("elements", []) if e.get("type") == "way" and e.get("geometry")]
    if not ways:
        print(f"  NO MATCH for {name}")
        return None
    # Sort by point count, take longest first, then merge contiguous ones
    ways.sort(key=lambda w: -len(w["geometry"]))
    # Build a MultiLineString of all way geometries
    coords = []
    for w in ways[:20]:  # cap to 20 longest segments
        geom = [[pt["lon"], pt["lat"]] for pt in w["geometry"]]
        if len(geom) >= 2:
            coords.append(geom)
    time.sleep(2)
    return {"name": name, "type": "trail", **attrs, "geometry": {"type": "MultiLineString", "coordinates": coords}}

def fetch_park(name, regex, bbox, attrs):
    q = f'[out:json][timeout:45];(way["name"~"{regex}",i]["leisure"]({bbox});relation["name"~"{regex}",i]["leisure"]({bbox}););out geom;'
    print(f"Fetching park: {name}")
    r = overpass(q)
    elements = r.get("elements", [])
    # Prefer parks/nature_reserve over other leisure types
    parks = [e for e in elements if e.get("tags", {}).get("leisure") in ("park", "nature_reserve", "garden", "common")]
    if not parks:
        parks = elements  # fallback
    parks.sort(key=lambda e: -(len(e.get("geometry", [])) if e.get("type") == "way" else sum(len(m.get("geometry", [])) for m in e.get("members", [])) if e.get("type") == "relation" else 0))
    if not parks:
        print(f"  NO PARK MATCH for {name}")
        return None
    e = parks[0]
    if e.get("type") == "way":
        ring = [[pt["lon"], pt["lat"]] for pt in e["geometry"]]
        if ring and ring[0] != ring[-1]:
            ring.append(ring[0])
        geometry = {"type": "Polygon", "coordinates": [ring]}
    else:  # relation
        # Take the outer members
        rings = []
        for m in e.get("members", []):
            if m.get("role") in ("outer", "") and m.get("geometry"):
                ring = [[pt["lon"], pt["lat"]] for pt in m["geometry"]]
                if ring and ring[0] != ring[-1]:
                    ring.append(ring[0])
                if len(ring) >= 4:
                    rings.append(ring)
        if not rings:
            return None
        geometry = {"type": "Polygon", "coordinates": rings[:1]}  # outer ring
    time.sleep(2)
    return {"name": name, "type": "park", **attrs, "geometry": geometry}

def main():
    out = {"trails": [], "parks": []}
    for spec in TRAILS:
        t = fetch_trail(*spec)
        if t: out["trails"].append(t)
    for spec in PARKS:
        p = fetch_park(*spec)
        if p: out["parks"].append(p)
    with open("/Users/rawproductivity/apartment-hunt/data/osm_geo.json", "w") as f:
        json.dump(out, f)
    print(f"\nFINAL: trails={len(out['trails'])}, parks={len(out['parks'])}")
    print(f"Total coords: trails={sum(sum(len(line) for line in t['geometry']['coordinates']) for t in out['trails'])}, parks={sum(len(p['geometry']['coordinates'][0]) for p in out['parks'])}")

if __name__ == "__main__":
    main()
