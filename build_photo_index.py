#!/usr/bin/env python3
"""
Build photo provenance index for apartment-hunt site.

Strategy:
1. Parse manifest.js -> {building_id: [photo_paths]}
2. Parse data.js + listings jsonl -> universe of building IDs (~300)
3. Classify each photo via:
   - MD5 hash signatures (OSM 403 streetmap = 731a0344c0a7379163b703daf4636120)
   - Manifest position pattern (_1.jpg + _2.png pair = satellite + streetmap)
   - Manifest size: 3+ entries = real photos likely
4. Compute per-building tier
"""
import json
import re
import hashlib
import os
from pathlib import Path

ROOT = Path("/Users/rawproductivity/apartment-hunt")
PHOTOS = ROOT / "photos"
OUT = ROOT / "data" / "photo_index.json"

# Known hash signatures
HASH_STREETMAP_OSM_BLOCKED = "731a0344c0a7379163b703daf4636120"

# Vision-verified classifications (manual spot checks done earlier)
# These OVERRIDE heuristics
KNOWN = {
    # Real interiors / exteriors / amenities
    "arc_erin_mills_1.jpg": "real_interior",      # lobby
    "battleford_glen_erin_1.jpg": "promo_card",   # ONE MONTH FREE overlay (kitchen)
    "battleford_glen_erin_4.jpg": "real_interior",
    "battleford_glen_erin_6.jpg": "real_interior",
    "battleford_glen_erin_7.jpg": "real_interior",
    "dialogue_confederation_1.jpg": "promo_card", # Up to Two Months Free
    "dialogue_confederation_3.jpg": "real_interior",
    "eau_du_soleil_1.jpg": "real_exterior",
    "eau_du_soleil_3.jpg": "real_interior",       # pool
    "james_90_1.jpg": "promo_card",               # Greenwin 1 MONTH FREE
    "james_90_2.jpg": "real_interior",            # kitchen
    "mill_road_340_1.jpg": "real_exterior",
    "reid_drive_1.jpg": "promo_card",
    "skyrise_ref_1.jpg": "promo_card",
    "1011_lorne_park_1.jpg": "satellite",
    "1011_lorne_park_2.png": "streetmap",
    "ann_5_1.jpg": "satellite",
    "ann_5_2.png": "streetmap",
}


def md5_of(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest():
    """Parse manifest.js into dict[building_id -> [filenames]]"""
    text = (ROOT / "manifest.js").read_text()
    # Strip JS wrapper
    text = re.sub(r"^\s*window\.PHOTO_MANIFEST\s*=\s*", "", text)
    text = text.rstrip().rstrip(";")
    data = json.loads(text)
    # Strip "photos/" prefix
    return {k: [os.path.basename(p) for p in v] for k, v in data.items()}


def parse_all_building_ids():
    """Collect building IDs from data.js + listings JSONL files."""
    ids = set()

    # data.js
    data_js = (ROOT / "data.js").read_text()
    for m in re.finditer(r'id:\s*"([a-zA-Z0-9_\-]+)"', data_js):
        ids.add(m.group(1))

    # JSONL files
    for jsonl_name in ("more_listings.jsonl", "wave2_listings.jsonl"):
        p = ROOT / "data" / jsonl_name
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if "id" in obj:
                    ids.add(obj["id"])
            except json.JSONDecodeError:
                pass

    return ids


def classify_photo(fname: str, building_id: str, manifest_entry: list[str],
                   md5_cache: dict[str, str]) -> str:
    """Classify a single photo file."""
    if fname in KNOWN:
        return KNOWN[fname]

    fpath = PHOTOS / fname
    if not fpath.exists():
        return "unknown"

    # Filename-based heuristics first
    low = fname.lower()
    if "satellite" in low or "esri" in low:
        return "satellite"
    if "streetmap" in low or "osm" in low:
        return "streetmap"
    if "promo" in low or "sterling_karamar" in low:
        return "promo_card"

    # Hash check for known synthetic signatures
    if fname not in md5_cache:
        md5_cache[fname] = md5_of(fpath)
    h = md5_cache[fname]

    if h == HASH_STREETMAP_OSM_BLOCKED:
        return "streetmap"

    # Manifest-position heuristic
    n_entries = len(manifest_entry)
    is_png = fname.lower().endswith(".png")
    is_jpg = fname.lower().endswith((".jpg", ".jpeg"))
    pos_match = re.search(r"_(\d+)\.(jpg|jpeg|png)$", fname.lower())
    pos = int(pos_match.group(1)) if pos_match else None

    # 2-entry manifest with _1.jpg + _2.png pattern: standard satellite+streetmap
    if n_entries == 2:
        if is_jpg and pos == 1:
            return "satellite"
        if is_png and pos == 2:
            return "streetmap"

    # 1-entry manifest: likely an Esri satellite if jpg with typical size
    if n_entries == 1:
        sz = fpath.stat().st_size
        if is_jpg and 80_000 < sz < 350_000:
            return "satellite"
        if is_png:
            return "streetmap"
        # Otherwise probably real
        return "real_exterior"

    # 3+ entries: real photos most likely
    # PNGs in 3+ entry manifests (e.g., elora_glen_erin) — large pngs could be real
    if n_entries >= 3:
        sz = fpath.stat().st_size
        if is_png:
            # Large PNG (>500K) likely a real screenshot/render
            if sz > 500_000:
                return "real_exterior"
            return "streetmap"
        # JPGs in 3+ entry manifests = real (no reliable promo/interior split without vision)
        # Default to real_interior since amenity/interior shots dominate
        return "real_interior"

    return "unknown"


def pick_primary_photo(photos: list[tuple[str, str]]) -> str | None:
    """Pick the best real photo to feature. Returns relative path or None.

    Priority: real_interior > real_exterior > satellite > streetmap > promo > unknown
    """
    priority = {
        "real_interior": 1,
        "real_exterior": 2,
        "satellite": 3,
        "streetmap": 4,
        "promo_card": 5,
        "unknown": 6,
    }
    real_photos = [(p, k) for p, k in photos if k in ("real_interior", "real_exterior")]
    if real_photos:
        real_photos.sort(key=lambda x: priority[x[1]])
        return f"photos/{real_photos[0][0]}"
    return None


def determine_tier(counts: dict[str, int]) -> str:
    n_real_int = counts.get("real_interior", 0)
    n_real_ext = counts.get("real_exterior", 0)
    total = sum(counts.values())
    if total == 0:
        return "tier3_none"
    if n_real_int >= 1 or n_real_ext >= 2:
        return "tier1_real"
    return "tier2_synthetic"


def determine_primary_source(counts: dict[str, int]) -> str:
    n_real_int = counts.get("real_interior", 0)
    n_real_ext = counts.get("real_exterior", 0)
    n_sat = counts.get("satellite", 0)
    n_streetmap = counts.get("streetmap", 0)
    n_promo = counts.get("promo_card", 0)

    if n_real_int + n_real_ext > 0:
        return "listing"
    if n_promo > 0 and n_promo >= n_sat:
        return "promo"
    if n_sat > 0:
        return "satellite"
    if n_streetmap > 0:
        return "streetview"  # closest label per spec
    return "none"


def main():
    manifest = parse_manifest()
    all_ids = parse_all_building_ids()
    # Merge: every building in manifest is also an id
    all_ids.update(manifest.keys())

    md5_cache: dict[str, str] = {}
    buildings_out: dict[str, dict] = {}

    for bid in sorted(all_ids):
        photos = manifest.get(bid, [])
        classified: list[tuple[str, str]] = []
        for fname in photos:
            kind = classify_photo(fname, bid, photos, md5_cache)
            classified.append((fname, kind))

        counts = {
            "n_real_interior": sum(1 for _, k in classified if k == "real_interior"),
            "n_real_exterior": sum(1 for _, k in classified if k == "real_exterior"),
            "n_satellite": sum(1 for _, k in classified if k == "satellite"),
            "n_streetmap": sum(1 for _, k in classified if k == "streetmap"),
            "n_promo_card": sum(1 for _, k in classified if k == "promo_card"),
        }
        n_unknown = sum(1 for _, k in classified if k == "unknown")
        if n_unknown:
            counts["n_unknown"] = n_unknown

        canonical_counts = {
            "real_interior": counts["n_real_interior"],
            "real_exterior": counts["n_real_exterior"],
            "satellite": counts["n_satellite"],
            "streetmap": counts["n_streetmap"],
            "promo_card": counts["n_promo_card"],
        }

        tier = determine_tier(canonical_counts)
        primary_source = determine_primary_source(canonical_counts)
        primary_photo = pick_primary_photo(classified)

        buildings_out[bid] = {
            **{k: counts[k] for k in (
                "n_real_interior", "n_real_exterior",
                "n_satellite", "n_streetmap", "n_promo_card"
            )},
            "primary_source": primary_source,
            "quality_tier": tier,
            "primary_photo": primary_photo,
        }

    summary = {
        "total_buildings": len(buildings_out),
        "tier1_real": sum(1 for b in buildings_out.values() if b["quality_tier"] == "tier1_real"),
        "tier2_synthetic": sum(1 for b in buildings_out.values() if b["quality_tier"] == "tier2_synthetic"),
        "tier3_none": sum(1 for b in buildings_out.values() if b["quality_tier"] == "tier3_none"),
    }

    out = {
        "_summary": summary,
        "_buildings": buildings_out,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"Wrote {OUT}")
    print(json.dumps(summary, indent=2))

    # Top buildings needing real photos: tier2_synthetic ordered by zone importance is hard
    # without scoring; just list 10 tier2 buildings (alphabetical) for the report.
    tier2 = [bid for bid, b in buildings_out.items() if b["quality_tier"] == "tier2_synthetic"]
    tier3 = [bid for bid, b in buildings_out.items() if b["quality_tier"] == "tier3_none"]
    print(f"\ntier2_synthetic count: {len(tier2)}")
    print(f"tier3_none count: {len(tier3)}")
    print(f"\nFirst 10 tier3_none (NO photos at all):")
    for bid in tier3[:10]:
        print(f"  - {bid}")
    print(f"\nFirst 10 tier2_synthetic (satellite/streetmap only):")
    for bid in tier2[:10]:
        print(f"  - {bid}")


if __name__ == "__main__":
    main()
