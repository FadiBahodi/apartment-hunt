#!/usr/bin/env python3
"""Build target-area map data and Google traffic snapshots.

This is intentionally area-centre based: it answers "what does living around
this exact micro-area feel like for CVH?" before a final building address is
known. Per-building routes still live in google_routes.json/google_ranges.json.
"""

from __future__ import annotations

import calendar
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "target_areas.json"
ENV_PATH = ROOT / ".env"
TORONTO = ZoneInfo("America/Toronto")
CVH = {"name": "Credit Valley Hospital", "lat": 43.5594, "lng": -79.7037}


AREAS = [
    {
        "id": "liberty_village_core",
        "tier": "1 primary",
        "label": "1 Liberty Village core",
        "name": "Liberty Village core",
        "short_label": "LIBERTY",
        "search": "liberty",
        "priority": "highest young/social + best condo/parking odds",
        "center": {"lat": 43.6388, "lng": -79.4146, "label": "East Liberty St / Western Battery Rd"},
        "neighbourhoods": ["Fort York-Liberty Village", "Liberty Village", "Exhibition Place edge"],
        "streets": [
            "East Liberty St",
            "Western Battery Rd",
            "Lynn Williams St",
            "Hanna Ave",
            "Atlantic Ave",
            "Jefferson Ave",
            "Strachan Ave",
            "King St W",
            "Ordnance St",
        ],
        "coords": [
            [43.6350, -79.4240],
            [43.6418, -79.4260],
            [43.6428, -79.4142],
            [43.6405, -79.4050],
            [43.6352, -79.4068],
            [43.6335, -79.4160],
        ],
        "links": {
            "strava": "https://www.strava.com/heatmap#14/-79.4146/43.6388/hot/run",
        },
    },
    {
        "id": "king_dufferin_west_queen",
        "tier": "1 primary",
        "label": "2 King-Dufferin / West Queen West",
        "name": "King-Dufferin / West Queen West",
        "short_label": "KING-DUFF",
        "search": "king west",
        "priority": "youngest/social highest-upside zone; parking must be verified",
        "center": {"lat": 43.6419, "lng": -79.4286, "label": "Queen St W / Dufferin St"},
        "neighbourhoods": ["West Queen West", "South Parkdale east edge", "Little Portugal west edge"],
        "streets": [
            "Queen St W",
            "King St W",
            "Dufferin St",
            "Gladstone Ave",
            "Sudbury St",
            "Dovercourt Rd",
            "Shaw St",
            "Ossington Ave",
        ],
        "coords": [
            [43.6368, -79.4385],
            [43.6443, -79.4400],
            [43.6507, -79.4238],
            [43.6460, -79.4145],
            [43.6392, -79.4202],
            [43.6358, -79.4315],
        ],
        "links": {
            "strava": "https://www.strava.com/heatmap#14/-79.4286/43.6419/hot/run",
        },
    },
    {
        "id": "little_portugal_ossington_west",
        "tier": "2 social stretch",
        "label": "3 Little Portugal / Ossington west",
        "name": "Little Portugal / Ossington west",
        "short_label": "OSSINGTON",
        "search": "dufferin",
        "priority": "best social radius; CVH/parking are the tradeoff",
        "center": {"lat": 43.6493, "lng": -79.4210, "label": "Dundas St W / Ossington Ave"},
        "neighbourhoods": ["Little Portugal", "Dufferin Grove edge", "Dovercourt Village south"],
        "streets": [
            "Dundas St W",
            "Ossington Ave",
            "Dovercourt Rd",
            "Dufferin St",
            "College St",
            "Queen St W",
            "Dundas W Station reach",
        ],
        "coords": [
            [43.6428, -79.4310],
            [43.6548, -79.4290],
            [43.6570, -79.4120],
            [43.6490, -79.4075],
            [43.6422, -79.4192],
        ],
        "links": {
            "strava": "https://www.strava.com/heatmap#14/-79.4210/43.6493/hot/run",
        },
    },
    {
        "id": "humber_bay_park_lawn",
        "tier": "1 practical fallback",
        "label": "4 Humber Bay / Park Lawn",
        "name": "Humber Bay / Park Lawn",
        "short_label": "HUMBER BAY",
        "search": "humber bay",
        "priority": "cleaner commute, easier parking, waterfront running, less downtown energy",
        "center": {"lat": 43.6235, "lng": -79.4804, "label": "Lake Shore Blvd W / Park Lawn Rd"},
        "neighbourhoods": ["Humber Bay Shores", "Mimico-Queensway", "Park Lawn condo cluster"],
        "streets": [
            "Lake Shore Blvd W",
            "Park Lawn Rd",
            "Marine Parade Dr",
            "Annie Craig Dr",
            "Shore Breeze Dr",
            "Silver Moon Dr",
            "Brookers Ln",
            "Legion Rd N",
            "Manitoba St",
        ],
        "coords": [
            [43.6210, -79.4930],
            [43.6350, -79.4880],
            [43.6330, -79.4775],
            [43.6280, -79.4710],
            [43.6170, -79.4730],
            [43.6142, -79.4865],
        ],
        "links": {
            "strava": "https://www.strava.com/heatmap#14/-79.4804/43.6235/hot/run",
        },
    },
    {
        "id": "mimico_royal_york",
        "tier": "2 practical fallback",
        "label": "5 Mimico / Royal York",
        "name": "Mimico / Royal York",
        "short_label": "MIMICO",
        "search": "mimico",
        "priority": "quieter lakeshore backup with better parking odds",
        "center": {"lat": 43.6138, "lng": -79.4970, "label": "Royal York Rd / Lake Shore Blvd W"},
        "neighbourhoods": ["Mimico", "Mimico Village", "New Toronto east edge"],
        "streets": [
            "Royal York Rd",
            "Lake Shore Blvd W",
            "Mimico Ave",
            "Superior Ave",
            "Manitoba St",
            "Hillside Ave",
            "Stanley Ave",
        ],
        "coords": [
            [43.6010, -79.5150],
            [43.6170, -79.5180],
            [43.6220, -79.4930],
            [43.6150, -79.4840],
            [43.6035, -79.4850],
            [43.5980, -79.4980],
        ],
        "links": {
            "strava": "https://www.strava.com/heatmap#14/-79.4970/43.6138/hot/run",
        },
    },
    {
        "id": "high_park_dundas_west",
        "tier": "3 special-unit backup",
        "label": "6 High Park / Dundas West",
        "name": "High Park / Dundas West",
        "short_label": "HIGH PARK",
        "search": "high park",
        "priority": "excellent running and transit; more settled/family-coded",
        "center": {"lat": 43.6553, "lng": -79.4639, "label": "Bloor St W / High Park Ave"},
        "neighbourhoods": ["High Park North", "Roncesvalles north", "Dundas West Station edge"],
        "streets": [
            "Bloor St W",
            "High Park Ave",
            "Keele St",
            "Dundas St W",
            "Roncesvalles Ave",
            "Howard Park Ave",
            "Indian Rd",
            "Pacific Ave",
            "Glenlake Ave",
        ],
        "coords": [
            [43.6475, -79.4755],
            [43.6585, -79.4775],
            [43.6658, -79.4595],
            [43.6585, -79.4455],
            [43.6480, -79.4480],
            [43.6442, -79.4615],
        ],
        "links": {
            "strava": "https://www.strava.com/heatmap#14/-79.4639/43.6553/hot/run",
        },
    },
    {
        "id": "junction_triangle_west_bend",
        "tier": "3 special-unit backup",
        "label": "7 Junction Triangle / West Bend",
        "name": "Junction Triangle / West Bend",
        "short_label": "JUNCTION TRI",
        "search": "junction",
        "priority": "renter-heavy west-end compromise; block-by-block inspection matters",
        "center": {"lat": 43.6632, "lng": -79.4534, "label": "Perth Ave / Wallace Ave"},
        "neighbourhoods": ["Junction Triangle", "West Bend", "Junction-Wallace Emerson"],
        "streets": [
            "Dundas St W",
            "Dupont St",
            "Perth Ave",
            "Symington Ave",
            "Wallace Ave",
            "Sterling Rd",
            "Lansdowne Ave",
            "Bloor St W",
        ],
        "coords": [
            [43.6565, -79.4655],
            [43.6708, -79.4690],
            [43.6760, -79.4440],
            [43.6620, -79.4380],
            [43.6555, -79.4500],
        ],
        "links": {
            "strava": "https://www.strava.com/heatmap#14/-79.4534/43.6632/hot/run",
        },
    },
]

TIME_SLOTS = [
    {"id": "mon_0630_to_cvh", "label": "Mon 6:30a -> CVH", "weekday": calendar.MONDAY, "hour": 6, "minute": 30, "direction": "to_cvh"},
    {"id": "mon_1430_to_cvh", "label": "Mon 2:30p -> CVH", "weekday": calendar.MONDAY, "hour": 14, "minute": 30, "direction": "to_cvh"},
    {"id": "mon_2230_to_cvh", "label": "Mon 10:30p -> CVH", "weekday": calendar.MONDAY, "hour": 22, "minute": 30, "direction": "to_cvh"},
    {"id": "mon_1530_from_cvh", "label": "Mon 3:30p CVH -> home", "weekday": calendar.MONDAY, "hour": 15, "minute": 30, "direction": "from_cvh"},
    {"id": "tue_0730_from_cvh", "label": "Tue 7:30a CVH -> home", "weekday": calendar.TUESDAY, "hour": 7, "minute": 30, "direction": "from_cvh"},
    {"id": "sat_1000_to_cvh", "label": "Sat 10:00a -> CVH", "weekday": calendar.SATURDAY, "hour": 10, "minute": 0, "direction": "to_cvh"},
]

MODELS = ["optimistic", "best_guess", "pessimistic"]


def load_env_key() -> str | None:
    key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if key:
        return key
    if not ENV_PATH.exists():
        return None
    for raw in ENV_PATH.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == "GOOGLE_MAPS_API_KEY":
            return v.strip().strip("'\"")
    return None


def next_departure(slot: dict) -> tuple[int, str]:
    now = datetime.now(TORONTO)
    days = (slot["weekday"] - now.weekday()) % 7
    candidate = (now + timedelta(days=days)).replace(
        hour=slot["hour"], minute=slot["minute"], second=0, microsecond=0
    )
    if candidate <= now:
        candidate += timedelta(days=7)
    return int(candidate.timestamp()), candidate.isoformat()


def fetch_route(api_key: str, origin: tuple[float, float], dest: tuple[float, float], departure: int, model: str) -> dict | None:
    params = urllib.parse.urlencode(
        {
            "origins": f"{origin[0]},{origin[1]}",
            "destinations": f"{dest[0]},{dest[1]}",
            "departure_time": str(departure),
            "traffic_model": model,
            "mode": "driving",
            "key": api_key,
        }
    )
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?{params}"
    try:
        payload = json.load(urllib.request.urlopen(url, timeout=20))
        element = payload.get("rows", [{}])[0].get("elements", [{}])[0]
        if payload.get("status") != "OK" or element.get("status") != "OK":
            return None
        duration = element.get("duration_in_traffic") or element.get("duration") or {}
        distance = element.get("distance") or {}
        return {
            "duration_min": round(duration.get("value", 0) / 60.0, 1),
            "distance_km": round(distance.get("value", 0) / 1000.0, 2),
        }
    except Exception:
        return None


def add_links(area: dict) -> None:
    lat = area["center"]["lat"]
    lng = area["center"]["lng"]
    query = urllib.parse.quote_plus(f"{area['name']} Toronto")
    area.setdefault("links", {})
    area["links"].update(
        {
            "google_maps": f"https://www.google.com/maps/search/?api=1&query={query}&center={lat},{lng}",
            "route_to_cvh": f"https://www.google.com/maps/dir/?api=1&origin={lat},{lng}&destination={CVH['lat']},{CVH['lng']}&travelmode=driving",
            "street_view": f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat},{lng}",
        }
    )


def main() -> int:
    api_key = load_env_key()
    slots = []
    for slot in TIME_SLOTS:
        dep, iso = next_departure(slot)
        enriched = dict(slot)
        enriched["departure_time"] = dep
        enriched["departure_iso"] = iso
        slots.append(enriched)

    areas = json.loads(json.dumps(AREAS))
    call_count = 0

    for area in areas:
        add_links(area)
        area["route_times"] = {}
        if not api_key:
            continue
        for slot in slots:
            if slot["direction"] == "to_cvh":
                origin = (area["center"]["lat"], area["center"]["lng"])
                dest = (CVH["lat"], CVH["lng"])
            else:
                origin = (CVH["lat"], CVH["lng"])
                dest = (area["center"]["lat"], area["center"]["lng"])

            models = {}
            distance_km = None
            for model in MODELS:
                result = fetch_route(api_key, origin, dest, slot["departure_time"], model)
                if result:
                    models[model] = result["duration_min"]
                    distance_km = result["distance_km"]
                    call_count += 1
                time.sleep(0.04)

            if models:
                values = list(models.values())
                area["route_times"][slot["id"]] = {
                    "label": slot["label"],
                    "direction": slot["direction"],
                    "departure_iso": slot["departure_iso"],
                    "distance_km": distance_km,
                    "models": models,
                    "best_min": models.get("best_guess"),
                    "range_min": [round(min(values), 1), round(max(values), 1)],
                }

    payload = {
        "generated_at": datetime.now(TORONTO).isoformat(),
        "source": "Google Distance Matrix for route snapshots; manually curated Toronto micro-area centres/polygons from local listing geography.",
        "timezone": "America/Toronto",
        "destination": CVH,
        "time_slots": slots,
        "areas": areas,
        "meta": {
            "route_api": "google_distance_matrix" if api_key else "missing_google_maps_api_key",
            "api_calls": call_count,
            "route_note": "Times are area-centre snapshots. Verify final shortlisted addresses individually.",
        },
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"wrote": str(OUT_PATH), "areas": len(areas), "api_calls": call_count, "route_api": payload["meta"]["route_api"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
