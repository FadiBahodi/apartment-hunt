#!/usr/bin/env python3
"""Build more_listings.jsonl with geocoded apartment data."""
import json, time, urllib.request, urllib.parse, math, sys, os

CVH_LAT, CVH_LNG = 43.5594, -79.7037
UNION_LAT, UNION_LNG = 43.6453, -79.3806

def haversine(lat1, lng1, lat2, lng2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1); dl = math.radians(lng2-lng1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

def geocode(addr):
    """Nominatim geocode. Rate limit 1/sec. Returns (lat,lng) or (None,None)."""
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
        "q": addr, "format": "json", "countrycodes": "ca", "limit": 1
    })
    req = urllib.request.Request(url, headers={"User-Agent": "apartment-hunt/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"GEOCODE FAIL {addr}: {e}", file=sys.stderr)
    return None, None

# Listings: (id, name, address, zone, rent_low, rent_high, sqft_low, sqft_high, listing_url, running_hint, transit_hint)
# All 1-bed/1+den. Many from Zumper neighborhood pages (May 2026 snapshot).
LISTINGS = [
    # COOKSVILLE
    ("camilla_2070", "2070 Camilla Road", "2070 Camilla Rd, Mississauga, ON L5A 2J7", "Cooksville/Mineola", 1795, 2450, 600, 750,
     "https://www.zumper.com/apartment-buildings/p1568331/2070-camilla-road-cooksville-mississauga-on", "Mary Fix Creek trail nearby", "Cooksville GO 1.5km"),
    ("paisley_95", "95 Paisley Boulevard West", "95 Paisley Blvd W, Mississauga, ON L5B 1E7", "Cooksville", 1899, 2516, 600, 750,
     "https://www.zumper.com/apartment-buildings/p420475/95-paisley-boulevard-west-cooksville-mississauga-on", "Cooksville Creek 600m", "Cooksville GO 800m"),
    ("the_huron_2475", "The Huron (2475 Hurontario)", "2475 Hurontario St, Mississauga, ON L5A 0A9", "Cooksville/Hurontario", 2049, 2962, 580, 720,
     "https://www.zumper.com/apartment-buildings/p457899/the-huron-cooksville-mississauga-on", "Cooksville Creek trail", "Cooksville GO 1.2km, Hurontario LRT"),
    ("seville_75", "Seville East & West", "75 Seville Cres W, Mississauga, ON L5B 1E6", "Cooksville", 1799, 2199, 580, 720,
     "https://www.zumper.com/apartment-buildings/p466151/seville-west-cooksville-mississauga-on", "Cooksville Creek nearby", "Cooksville GO 1km"),
    ("royal_tower_121", "Royal Tower", "121 Agnes St, Mississauga, ON L5B 2H4", "Cooksville", 1850, 1950, 580, 700,
     "https://www.zumper.com/apartment-buildings/p213453/royal-tower-cooksville-mississauga-on", "Cooksville Creek", "Cooksville GO 700m"),
    ("argyle_2590", "2590 Argyle Rd", "2590 Argyle Rd, Mississauga, ON L5B 1V3", "Cooksville", 1799, 2349, 600, 750,
     "https://www.zumper.com/apartment-buildings/p216090/2590-argyle-rd-cooksville-mississauga-on", "Cooksville Creek", "Cooksville GO 900m"),
    ("argyle_2570", "2570 Argyle Rd", "2570 Argyle Rd, Mississauga, ON L5B 1V2", "Cooksville", 1799, 2349, 600, 750,
     "https://www.zumper.com/apartment-buildings/p216077/2570-argyle-rd-cooksville-mississauga-on", "Cooksville Creek", "Cooksville GO 900m"),
    ("nsr_275", "275 North Service Rd", "275 North Service Rd, Mississauga, ON L5A 1A7", "Cooksville", 1562, 1915, 550, 700,
     "https://www.zumper.com/apartment-buildings/p218138/275-north-service-road-apartments-cooksville-mississauga-on", "Cooksville Creek 300m", "Cooksville GO 600m"),
    ("nsr_535", "535 North Service Rd", "535 North Service Rd, Mississauga, ON L5A 1B4", "Cooksville", 1600, 1999, 550, 700,
     "https://www.zumper.com/apartment-buildings/p216071/535-north-service-rd-cooksville-mississauga-on", "Cooksville Creek 200m", "Cooksville GO 400m"),
    ("dundas_120e", "120 Dundas St E", "120 Dundas St E, Mississauga, ON L5A 1W6", "Cooksville", 1776, 2599, 580, 720,
     "https://www.zumper.com/apartment-buildings/p237673/120-dundas-st-e-cooksville-mississauga-on", "Cooksville Creek 400m", "Cooksville GO 1.2km"),
    ("hurontario_2247", "2247 Hurontario Street", "2247 Hurontario St, Mississauga, ON L5A 2G2", "Cooksville/Hurontario", 2200, 2550, 600, 750,
     "https://www.zumper.com/apartment-buildings/p535573/apartment-for-rent-at-2247-hurontario-street-cooksville-mississauga-on", "Cooksville Creek", "Cooksville GO 600m, Hurontario LRT"),
    ("promenade_court", "Promenade Court (2235 Hurontario)", "2235 Promenade Crt, Mississauga, ON L5A 2G1", "Cooksville/Hurontario", 1899, 2317, 580, 720,
     "https://www.zumper.com/apartment-buildings/p764325/promenade-court-apartments-cooksville-mississauga-on", "Cooksville Creek", "Cooksville GO 600m, Hurontario LRT"),

    # FAIRVIEW / SQUARE ONE / MISSISSAUGA VALLEY
    ("kaneff_3575", "3575 Kaneff Crescent", "3575 Kaneff Cres, Mississauga, ON L5A 3Y5", "Fairview/Square One", 1899, 2299, 600, 750,
     "https://www.zumper.com/apartment-buildings/p219536/3575-kaneff-crescent-fairview-mississauga-on", "Cooksville Creek trail", "Cooksville GO 1.2km, MiWay BRT"),
    ("one_eighty_five", "One Eighty Five", "185 Enfield Pl, Mississauga, ON L5B 0R3", "Square One", 2240, 2800, 550, 700,
     "https://www.zumper.com/apartment-buildings/p1172861/one-eighty-five-fairview-mississauga-on", "Kariya Park 400m", "MiWay BRT/Hurontario LRT"),
    ("the_omeath_30", "The Omeath", "30 Central Pky W, Mississauga, ON L5B 1L3", "Fairview", 1959, 2519, 600, 750,
     "https://www.zumper.com/apartment-buildings/p214741/30-central-parkway-west-fairview-mississauga-on", "Cooksville Creek 500m", "Cooksville GO 1km"),
    ("lolita_620", "600 & 620 Lolita Gardens", "620 Lolita Gardens, Mississauga, ON L5A 3K7", "Fairview", 1975, 2299, 600, 750,
     "https://www.zumper.com/apartment-buildings/p218294/600-620-lolita-gardens-fairview-mississauga-on", "Cooksville Creek trail", "Cooksville GO 1.5km"),
    ("kaneff_3620", "Mississauga Place (3620 Kaneff)", "3620 Kaneff Cres, Mississauga, ON L5A 3X1", "Fairview", 2300, 2620, 700, 850,
     "https://www.zumper.com/apartment-buildings/p318303/mississauga-place-fairview-mississauga-on", "Cooksville Creek trail", "Cooksville GO 1.3km, MiWay BRT"),
    ("valleywoods_1423", "The Valleywoods", "1423 Mississauga Valley Blvd, Mississauga, ON L5A 4A5", "Mississauga Valley", 1950, 2599, 600, 800,
     "https://www.zumper.com/apartment-buildings/p231111/the-valleywoods-fairview-mississauga-on", "Cooksville Creek 200m, Mississauga Valley Park", "MiWay BRT"),
    ("forestwoods_1547", "The Forestwoods", "1547 Mississauga Valley Blvd, Mississauga, ON L5A 3X8", "Mississauga Valley", 1999, 2599, 600, 800,
     "https://www.zumper.com/apartment-buildings/p231118/the-forestwoods-fairview-mississauga-on", "Cooksville Creek + Mississauga Valley Park", "MiWay BRT"),
    ("maplewoods_1477", "The Maplewoods", "1477 Mississauga Valley Blvd, Mississauga, ON L5A 3Y4", "Mississauga Valley", 2100, 2599, 600, 800,
     "https://www.zumper.com/apartment-buildings/p231113/the-maplewoods-fairview-mississauga-on", "Cooksville Creek + park", "MiWay BRT"),
    ("elmwoods_30", "The Elmwoods", "30 Elm Dr E, Mississauga, ON L5A 4C3", "Square One/Fairview", 1950, 2599, 600, 800,
     "https://www.zumper.com/apartment-buildings/p231119/the-elmwoods-fairview-mississauga-on", "Kariya Park 600m, Cooksville Creek", "Hurontario LRT, MiWay BRT"),
    ("arista_3665", "The Arista", "3665 Arista Way, Mississauga, ON L5A 4A3", "Mississauga Valley", 1995, 2599, 600, 800,
     "https://www.zumper.com/apartment-buildings/p231124/the-arista-fairview-mississauga-on", "Cooksville Creek trail", "MiWay BRT"),

    # ERIN MILLS / CENTRAL ERIN MILLS / SHERIDAN
    ("collegeway_2375", "2375 The Collegeway", "2375 The Collegeway, Mississauga, ON L5L 2E8", "Erin Mills", 2199, 2526, 700, 850,
     "https://www.zumper.com/apartment-buildings/p946928/2375-the-collegeway-erin-mills-mississauga-on", "Sawmill Valley Trail 400m", "Clarkson GO 4km"),
    ("collegeway_2445", "2445 The Collegeway", "2445 The Collegeway, Mississauga, ON L5L 2E5", "Erin Mills", 2299, 2992, 700, 900,
     "https://www.zumper.com/apartment-buildings/p946929/2445-the-collegeway-erin-mills-mississauga-on", "Sawmill Valley Trail adjacent", "Clarkson GO 4.5km"),
    ("skyrise_2550", "Skyrise Rentals", "2550 Eglinton Ave W, Mississauga, ON L5M 0Y2", "Central Erin Mills", 2250, 2875, 600, 800,
     "https://www.zumper.com/apartment-buildings/p538512/skyrise-rentals-central-erin-mills-mississauga-on", "Sawmill Valley/Credit River 1km", "MiWay 2km to Erin Mills GO/Streetsville GO"),
    ("daniels_gateway_5625", "Daniels Gateway Annex", "5625 Glen Erin Dr, Mississauga, ON L5M 6V1", "Central Erin Mills", 2200, 2700, 650, 800,
     "https://www.zumper.com/apartment-buildings/p830853/daniels-gateway-annex-central-erin-mills-mississauga-on", "Erin Meadows trails", "MiWay to Streetsville GO"),
    ("daniels_gateway_2900", "Daniels Gateway Erin Centre", "2900 Rio Crt, Mississauga, ON L5M 7H5", "Central Erin Mills", 2200, 2700, 650, 800,
     "https://www.zumper.com/apartment-buildings/p830855/daniels-gateway-erin-centre-central-erin-mills-mississauga-on", "Erin Meadows trails", "MiWay to Streetsville GO"),
    ("roche_2150", "2150 Roche Court", "2150 Roche Crt, Mississauga, ON L5K 1T5", "Sheridan/Clarkson", 2149, 2525, 650, 800,
     "https://www.zumper.com/apartment-buildings/p572273/2150-roche-sheridan-mississauga-on", "Sheridan Park trails", "Clarkson GO 2km"),
    ("sheridan_park_2215", "2215 Sheridan Park Drive", "2215 Sheridan Park Dr, Mississauga, ON L5K 0B2", "Sheridan", 2147, 2693, 650, 800,
     "https://www.zumper.com/apartment-buildings/p872415/2215-sheridan-park-drive-sheridan-mississauga-on", "Sheridan Park research woodlands", "Clarkson GO 2km"),
    ("fowler_1980", "1980 Fowler Dr", "1980 Fowler Dr, Mississauga, ON L5K 1B6", "Sheridan", 2082, 2855, 650, 800,
     "https://www.zumper.com/apartment-buildings/p432168/1980-fowler-dr-sheridan-mississauga-on", "Sawmill Creek trail", "Clarkson GO 2.5km"),
    ("fowler_1970", "1970 Fowler Dr", "1970 Fowler Dr, Mississauga, ON L5K 1B5", "Sheridan", 2049, 2999, 650, 800,
     "https://www.zumper.com/apartment-buildings/p432167/1970-fowler-dr-sheridan-mississauga-on", "Sawmill Creek trail", "Clarkson GO 2.5km"),
    ("homelands_2250", "2250 Homelands Dr", "2250 Homelands Dr, Mississauga, ON L5K 1G8", "Sheridan", 1942, 2692, 650, 800,
     "https://www.zumper.com/apartment-buildings/p294021/2250-homelands-dr-sheridan-mississauga-on", "Sawmill Creek + Sheridan Park", "Clarkson GO 2km"),
    ("sheridan_park_2185", "2185 Sheridan Park Dr", "2185 Sheridan Park Dr, Mississauga, ON L5K 1C7", "Sheridan", 1943, 2650, 650, 800,
     "https://www.zumper.com/apartment-buildings/p294022/2185-sheridan-park-dr-sheridan-mississauga-on", "Sheridan Park woodlands", "Clarkson GO 2km"),

    # MEADOWVALE / CHURCHILL MEADOWS
    ("brightstone_6570", "Brightstone Townhomes", "6570 Glen Erin Dr, Mississauga, ON L5N 0H4", "Meadowvale", 2250, 2570, 700, 900,
     "https://www.zumper.com/apartment-buildings/p1138021/brightstone-townhomes-meadowvale-mississauga-on", "Lake Aquitaine Trail 800m", "Meadowvale GO 2km"),
    ("bristol_court_6550", "Bristol Court", "6550 Glen Erin Dr, Mississauga, ON L5N 3S1", "Meadowvale", 2360, 2830, 700, 900,
     "https://www.zumper.com/apartment-buildings/p320058/bristol-court-meadowvale-mississauga-on", "Lake Aquitaine Trail 600m", "Meadowvale GO 2km"),
    ("waterford_2645", "Waterford Tower", "2645 Battleford Rd, Mississauga, ON L5N 3R8", "Meadowvale", 2295, 2580, 650, 850,
     "https://www.zumper.com/apartment-buildings/p318306/waterford-tower-meadowvale-mississauga-on", "Lake Aquitaine + Lake Wabukayne loops", "Meadowvale GO 1.5km"),
    ("lakeside_place_2699", "Lakeside Place", "2699 Battleford Rd, Mississauga, ON L5N 3R9", "Meadowvale", 2029, 3129, 650, 850,
     "https://www.zumper.com/apartment-buildings/p213220/lakeside-place-apartments-meadowvale-mississauga-on", "Lake Aquitaine Trail 200m", "Meadowvale GO 1.5km"),
    ("lakeview_place_2770", "Lakeview Place", "2770 Aquitaine Ave, Mississauga, ON L5N 3K5", "Meadowvale", 2190, 2650, 650, 850,
     "https://www.zumper.com/apartment-buildings/p213506/2770-aquitaine-avenue-meadowvale-mississauga-on", "Lake Aquitaine loop adjacent", "Meadowvale GO 1.8km"),
    ("battleford_2797", "2797 Battleford Road", "2797 Battleford Rd, Mississauga, ON L5N 2W2", "Meadowvale", 2050, 2400, 650, 800,
     "https://www.zumper.com/apartment-buildings/p213202/2797-battleford-road-meadowvale-mississauga-on", "Lake Aquitaine Trail", "Meadowvale GO 1.5km"),
    ("meadowvale_gardens_2869", "Meadowvale Gardens", "2869 Battleford Rd, Mississauga, ON L5N 2S6", "Meadowvale", 2200, 2900, 650, 850,
     "https://www.zumper.com/apartment-buildings/p231112/meadowvale-gardens-meadowvale-mississauga-on", "Lake Aquitaine + Wabukayne", "Meadowvale GO 1.3km"),

    # STREETSVILLE
    ("queen_south_190", "190 Queen Street South", "190 Queen St S, Mississauga, ON L5M 1L3", "Streetsville", 2142, 2899, 650, 850,
     "https://www.zumper.com/apartment-buildings/p849568/190-queen-street-south-streetsville-mississauga-on", "Credit River Trail 200m", "Streetsville GO 600m"),
    ("reid_18", "18 Reid Dr", "18 Reid Dr, Mississauga, ON L5M 2A9", "Streetsville", 2000, 2350, 600, 800,
     "https://www.zumper.com/apartment-buildings/p421023/18-reid-dr-streetsville-mississauga-on", "Credit River Trail 500m", "Streetsville GO 1.2km"),

    # PORT CREDIT
    ("ann_5", "5 Ann Street", "5 Ann St, Mississauga, ON L5G 3E8", "Port Credit", 1897, 2297, 580, 720,
     "https://www.zumper.com/apartment-buildings/p1209894/5-ann-street-port-credit-mississauga-on", "Waterfront Trail 400m, Credit River", "Port Credit GO 600m"),
    ("park_70e", "70 Park Street East", "70 Park St E, Mississauga, ON L5G 1M5", "Port Credit", 2310, 2455, 600, 750,
     "https://www.zumper.com/apartment-buildings/p821293/70-park-street-east-port-credit-mississauga-on", "Waterfront Trail 500m", "Port Credit GO 700m"),
    ("elizabeth_28n", "Elizabeth Tower", "28 Elizabeth St N, Mississauga, ON L5G 2Z6", "Port Credit", 2025, 2375, 580, 750,
     "https://www.zumper.com/apartment-buildings/p593995/elizabeth-tower-port-credit-mississauga-on", "Waterfront Trail 700m", "Port Credit GO 500m"),
    ("rivergate_35", "The Rivergate", "35 Front St S, Mississauga, ON L5H 2C6", "Port Credit", 1849, 2400, 600, 750,
     "https://www.zumper.com/apartment-buildings/p501273/the-rivergate-port-credit-mississauga-on", "Credit River + Waterfront Trail", "Port Credit GO 1km"),
    ("park_55e", "55 Park Street East", "55 Park St E, Mississauga, ON L5G 1L9", "Port Credit", 1949, 2750, 600, 750,
     "https://www.zumper.com/apartment-buildings/p294016/55-park-st-east-port-credit-mississauga-on", "Waterfront Trail 500m", "Port Credit GO 600m"),
    ("helene_28n", "28 Helene Street North", "28 Helene St N, Mississauga, ON L5G 3B7", "Port Credit", 1874, 2666, 600, 750,
     "https://www.zumper.com/apartment-buildings/p422698/28-helene-street-north-port-credit-mississauga-on", "Waterfront Trail 800m", "Port Credit GO 600m"),
    ("oakwood_8n", "8 Oakwood Avenue North", "8 Oakwood Ave N, Mississauga, ON L5G 3L7", "Port Credit", 1900, 2400, 580, 750,
     "https://www.zumper.com/apartment-buildings/p483265/8-oakwood-ave-port-credit-mississauga-on", "Waterfront Trail 600m", "Port Credit GO 700m"),
    ("lakeshore_212e", "212 Lakeshore Road East", "212 Lakeshore Rd E, Mississauga, ON L5G 1G4", "Port Credit", 1898, 2200, 580, 700,
     "https://www.zumper.com/apartment-buildings/p446080/212-lakeshore-road-east-port-credit-mississauga-on", "Waterfront Trail 200m", "Port Credit GO 1km"),
    ("lakeshore_206e", "206 Lakeshore Road East", "206 Lakeshore Rd E, Mississauga, ON L5G 1G4", "Port Credit", 1649, 2265, 550, 720,
     "https://www.zumper.com/apartment-buildings/p449018/206-lakeshore-road-east-port-credit-mississauga-on", "Waterfront Trail 200m", "Port Credit GO 1km"),
    ("elizabeth_7n", "7 Elizabeth Street North", "7 Elizabeth St N, Mississauga, ON L5G 2Y8", "Port Credit", 1999, 2700, 580, 750,
     "https://www.zumper.com/apartment-buildings/p294017/7-elizabeth-street-north-port-credit-mississauga-on", "Waterfront Trail 700m", "Port Credit GO 500m"),
    ("high_30e", "30 High Street East", "30 High St E, Mississauga, ON L5G 1J8", "Port Credit", 1999, 2750, 600, 750,
     "https://www.zumper.com/apartment-buildings/p512687/30-high-street-apartment-rentals-port-credit-mississauga-on", "Waterfront Trail + Credit River", "Port Credit GO 700m"),
    ("park_52e", "52 Park Street East", "52 Park St E, Mississauga, ON L5G 1M1", "Port Credit", 1899, 2200, 580, 720,
     "https://www.zumper.com/apartment-buildings/p527748/52-park-street-east-port-credit-mississauga-on", "Waterfront Trail 500m", "Port Credit GO 700m"),
    ("elizabeth_20n", "20 Elizabeth Street N", "20 Elizabeth St N, Mississauga, ON L5G 2Z1", "Port Credit", 1900, 2400, 580, 720,
     "https://www.zumper.com/apartment-buildings/p917176/20-elizabeth-street-n-port-credit-mississauga-on", "Waterfront Trail 700m", "Port Credit GO 500m"),
    ("park_26e", "26 Park Street", "26 Park St E, Mississauga, ON L5G 1L6", "Port Credit", 1900, 2200, 580, 720,
     "https://www.zumper.com/apartment-buildings/p549521/26-park-street-apartments-in-mississauga-port-credit-mississauga-on", "Waterfront Trail 500m", "Port Credit GO 700m"),
    ("park_12e", "12 Park St E", "12 Park St E, Mississauga, ON L5G 1L5", "Port Credit", 1900, 2100, 580, 720,
     "https://www.zumper.com/apartment-buildings/p1538628/12-park-st-e-port-credit-mississauga-on", "Waterfront Trail 500m", "Port Credit GO 800m"),

    # LAKEVIEW
    ("orchard_1015", "1015 Orchard (Orchard Court)", "1015 Orchard Rd, Mississauga, ON L5E 2N8", "Lakeview", 2049, 2599, 600, 800,
     "https://www.zumper.com/apartment-buildings/p213450/orchard-court-lakeview-mississauga-on", "Waterfront Trail 600m, Marie Curtis Park 1.5km", "Long Branch GO 2.5km"),
    ("lakewood_ii_1285", "Lakewood Apartments II", "1285 Lakeshore Rd E, Mississauga, ON L5E 1G4", "Lakeview", 1875, 2200, 550, 700,
     "https://www.zumper.com/apartment-buildings/p448376/lakewood-apartments-ii-lakeview-mississauga-on", "Waterfront Trail 300m", "Long Branch GO 3km"),
    ("caven_1110", "1110 Caven St", "1110 Caven St, Mississauga, ON L5G 4N4", "Lakeview", 1999, 2799, 600, 800,
     "https://www.zumper.com/apartment-buildings/p428565/1110-caven-st-lakeview-mississauga-on", "Waterfront Trail 700m", "Port Credit GO 1.8km"),
    ("seneca_1051", "1051-1061 Seneca Avenue", "1051 Seneca Ave, Mississauga, ON L5G 3X6", "Lakeview", 1799, 2099, 550, 700,
     "https://www.zumper.com/apartment-buildings/p527761/1051-seneca-ave-lakeview-mississauga-on", "Waterfront Trail 800m", "Port Credit GO 1.5km"),

    # CLARKSON
    ("inverhouse_920", "920 Inverhouse", "920 Inverhouse Dr, Mississauga, ON L5J 4B5", "Clarkson", 1831, 2499, 650, 850,
     "https://www.zumper.com/apartment-buildings/p420467/920-inverhouse-clarkson-mississauga-on", "Rattray Marsh 1.5km, Sheridan Creek", "Clarkson GO 2km"),
    ("park_royal_2360", "Park Royal Village", "2360 Bonner Rd, Mississauga, ON L5J 2C7", "Clarkson", 1725, 2230, 600, 800,
     "https://www.zumper.com/apartment-buildings/p288647/park-royal-village-apartments-clarkson-mississauga-on", "Bonner Park, Rattray Marsh 2km", "Clarkson GO 1.2km"),
    ("bromsgate_2150", "The Bromsgate", "2150 Bromsgrove Rd, Mississauga, ON L5J 4B3", "Clarkson", 1651, 2480, 600, 800,
     "https://www.zumper.com/apartment-buildings/p250349/the-bromsgate-southdown-mississauga-on", "Sheridan Creek + Rattray Marsh 1.8km", "Clarkson GO 1.5km"),
    ("forestview_2077", "Forestview Townhomes", "2077 Barsuda Dr, Mississauga, ON L5J 1V6", "Clarkson", 2700, 2959, 800, 1000,
     "https://www.zumper.com/apartment-buildings/p456737/2020-2077-barsuda-drive-2025-ambridge-court-clarkson-mississauga-on", "Sheridan Creek trail", "Clarkson GO 1km"),

    # APPLEWOOD
    ("linwood_1785", "Linwood Apartments", "1785 Bloor St, Mississauga, ON L4X 1S8", "Applewood", 1825, 2400, 580, 720,
     "https://www.zumper.com/apartment-buildings/p213449/linwood-apartments-applewood-mississauga-on", "Etobicoke Creek trail 800m", "Dixie GO 2.5km"),
    ("bristol_arms_1745", "Bristol Arms", "1745 Bloor St, Mississauga, ON L4X 1S6", "Applewood", 1775, 2400, 580, 720,
     "https://www.zumper.com/apartment-buildings/p213455/bristol-arms-apartments-applewood-mississauga-on", "Etobicoke Creek trail 800m", "Dixie GO 2.5km"),
    ("bridgewood_1867", "Bridgewood Place", "1867 Bloor St, Mississauga, ON L4X 1T4", "Applewood", 2009, 2389, 580, 720,
     "https://www.zumper.com/apartment-buildings/p214739/1867-bloor-street-applewood-mississauga-on", "Etobicoke Creek trail 1km", "Dixie GO 2.7km"),
    ("havenwood_3410", "Havenwood Apartments", "3410 Havenwood Dr, Mississauga, ON L4X 2M5", "Applewood", 1850, 2300, 580, 720,
     "https://www.zumper.com/apartment-buildings/p529329/havenwood-apartments-applewood-mississauga-on", "Etobicoke Creek 1km", "Dixie GO 2.5km"),
    ("westwood_1465", "Westwood Apartments", "1465 Tyneburn Cres, Mississauga, ON L4X 1P7", "Applewood", 1850, 2400, 580, 720,
     "https://www.zumper.com/apartment-buildings/p469615/westwood-apartments-applewood-mississauga-on", "Etobicoke Creek 800m", "Dixie GO 2.3km"),
    ("strathroy_1470", "Strathroy Manor", "1470 Williamsport Dr, Mississauga, ON L4X 1T5", "Applewood", 2025, 2375, 580, 720,
     "https://www.zumper.com/apartment-buildings/p215399/strathroy-manor-applewood-mississauga-on", "Etobicoke Creek 700m", "Dixie GO 2.4km"),
    ("applewood_towers_1055", "Applewood Towers", "1055 Bloor St, Mississauga, ON L4Y 2N5", "Applewood", 1930, 2700, 580, 720,
     "https://www.zumper.com/apartment-buildings/p288772/applewood-towers-apartments-applewood-mississauga-on", "Etobicoke Creek + Burnhamthorpe trail", "Dixie GO 1.8km"),
    ("bloor_1475", "1475 Bloor Street", "1475 Bloor St, Mississauga, ON L4X 1R7", "Applewood", 1849, 2700, 580, 720,
     "https://www.zumper.com/apartment-buildings/p489891/1475-bloor-street-applewood-mississauga-on", "Etobicoke Creek 700m", "Dixie GO 2.4km"),

    # MIMICO / NEW TORONTO / LONG BRANCH (Etobicoke side)
    ("annie_craig_38", "Eau du Soleil West (38 Annie Craig)", "38 Annie Craig Dr, Toronto, ON M8V 0C9", "Humber Bay Shores", 2200, 2400, 480, 600,
     "https://condos.ca/toronto/humber-bay-shores", "Martin Goodman Trail at door", "Mimico GO 1.5km, 501 streetcar"),
    ("shore_breeze_30", "Eau du Soleil East (30 Shore Breeze)", "30 Shore Breeze Dr, Toronto, ON M8V 0J1", "Humber Bay Shores", 2200, 2400, 480, 600,
     "https://condos.ca/toronto/humber-bay-shores", "Martin Goodman Trail + Humber Bay Park", "Mimico GO 1.5km"),
    ("legion_185", "185 Legion Road North", "185 Legion Rd N, Toronto, ON M8Y 0A1", "Mimico", 2150, 2400, 580, 700,
     "https://condos.ca/toronto/mimico", "Martin Goodman Trail 600m, Mimico Linear Park", "Mimico GO 1km"),
    ("legion_165", "165 Legion Road North", "165 Legion Rd N, Toronto, ON M8Y 0B6", "Mimico", 2100, 2400, 550, 700,
     "https://condos.ca/toronto/mimico", "Martin Goodman + Mimico Linear Park", "Mimico GO 1km"),
    ("western_battery_15", "15 Western Battery / Liberty Central", "15 Western Battery Rd, Toronto, ON M6K 3V8", "Mimico/Liberty Village edge", 2200, 2500, 500, 650,
     "https://condos.ca/toronto", "Martin Goodman trail 800m", "Exhibition GO 800m"),
    ("lakeshore_2230", "2230 Lake Shore Boulevard West", "2230 Lake Shore Blvd W, Toronto, ON M8V 0B5", "Humber Bay Shores", 2200, 2500, 500, 650,
     "https://condos.ca/toronto/humber-bay-shores", "Humber Bay Park + Martin Goodman", "Mimico GO 1.2km, 501 streetcar"),
    ("lakeshore_2212", "2212 Lake Shore Boulevard West", "2212 Lake Shore Blvd W, Toronto, ON M8V 0C2", "Humber Bay Shores", 2200, 2500, 500, 650,
     "https://condos.ca/toronto/humber-bay-shores", "Humber Bay Park + Martin Goodman", "Mimico GO 1.2km, 501 streetcar"),
    ("marine_parade_58", "58 Marine Parade Drive (Waterscapes)", "58 Marine Parade Dr, Toronto, ON M8V 4G1", "Humber Bay Shores", 2200, 2500, 550, 700,
     "https://condos.ca/toronto/humber-bay-shores", "Humber Bay Park West, Martin Goodman", "Mimico GO 1.5km"),
    ("marine_parade_15", "15 Marine Parade Drive (Grenadier Landing)", "15 Marine Parade Dr, Toronto, ON M8V 3Z1", "Humber Bay Shores", 2200, 2500, 580, 720,
     "https://condos.ca/toronto/humber-bay-shores", "Humber Bay Park + Martin Goodman at door", "Mimico GO 1.5km, 501 streetcar"),
    ("marine_parade_3", "3 Marine Parade Drive (Hearthstone)", "3 Marine Parade Dr, Toronto, ON M8V 3Z5", "Humber Bay Shores", 2100, 2400, 580, 720,
     "https://condos.ca/toronto/humber-bay-shores", "Humber Bay Park + Martin Goodman at door", "Mimico GO 1.5km, 501 streetcar"),
    ("park_lawn_36", "36 Park Lawn Road", "36 Park Lawn Rd, Toronto, ON M8V 0E5", "Humber Bay Shores", 2200, 2500, 550, 700,
     "https://condos.ca/toronto/humber-bay-shores", "Humber Bay Park + Martin Goodman 400m", "Mimico GO 2km, 501 streetcar"),
    ("palace_pier_1", "Palace Pier (1 Palace Pier Court)", "1 Palace Pier Crt, Toronto, ON M8V 3W9", "Humber Bay Shores", 2300, 2700, 700, 900,
     "https://condos.ca/toronto/humber-bay-shores", "Martin Goodman + Humber River trails", "Mimico GO 2km, Old Mill subway 3km"),

    # LONG BRANCH
    ("lake_promenade_240", "Lake Promenade Community 240", "240 Lake Promenade, Toronto, ON M8W 1B7", "Long Branch", 1900, 2400, 550, 750,
     "https://www.zumper.com/apartments-for-rent/toronto-on/long-branch", "Marie Curtis Park + Waterfront Trail at door", "Long Branch GO 800m"),
    ("lake_promenade_220", "Lake Promenade Community 220", "220 Lake Promenade, Toronto, ON M8W 1B5", "Long Branch", 1900, 2400, 550, 750,
     "https://www.zumper.com/apartments-for-rent/toronto-on/long-branch", "Marie Curtis Park + Waterfront Trail", "Long Branch GO 800m"),
    ("lakeshore_3845", "3845 Lake Shore Blvd W", "3845 Lake Shore Blvd W, Toronto, ON M8W 1R3", "Long Branch", 1850, 2300, 550, 720,
     "https://www.apartments.com/3845-lake-shore-blvd-w-toronto-on/ynbrmwt/", "Waterfront Trail 400m, Marie Curtis Park 1km", "Long Branch GO 600m"),
    ("lakeshore_3650", "3650 Lake Shore Blvd W", "3650 Lake Shore Blvd W, Toronto, ON M8W 1P1", "Long Branch", 1900, 2400, 580, 720,
     "https://www.zumper.com/apartments-for-rent/toronto-on/long-branch", "Waterfront Trail 300m", "Long Branch GO 1.2km"),
    ("long_branch_30", "30 Long Branch Avenue", "30 Long Branch Ave, Toronto, ON M8W 3J7", "Long Branch", 1850, 2200, 550, 700,
     "https://www.zumper.com/apartments-for-rent/toronto-on/long-branch", "Waterfront Trail + Marie Curtis Park", "Long Branch GO 100m"),

    # NEW TORONTO
    ("lakeshore_3590", "3590 Lake Shore Blvd W", "3590 Lake Shore Blvd W, Toronto, ON M8W 1N6", "New Toronto", 1900, 2400, 580, 720,
     "https://www.zumper.com/apartments-for-rent/toronto-on/new-toronto", "Waterfront Trail 300m, Humber College Lakeshore", "Long Branch GO 1.5km"),
    ("lakeshore_3479", "3479 Lake Shore Blvd W", "3479 Lake Shore Blvd W, Toronto, ON M8W 1N3", "New Toronto", 1900, 2300, 580, 720,
     "https://www.zumper.com/apartments-for-rent/toronto-on/new-toronto", "Waterfront Trail + Colonel Sam Smith Park", "Long Branch GO 2km"),
    ("birmingham_45", "45 Birmingham Street", "45 Birmingham St, Toronto, ON M8V 3N6", "New Toronto", 1850, 2200, 550, 700,
     "https://www.zumper.com/apartments-for-rent/toronto-on/new-toronto", "Colonel Sam Smith Park 800m", "Mimico GO 1.5km"),
    ("eighth_24", "24 Eighth Street", "24 Eighth St, Toronto, ON M8V 3C1", "New Toronto", 1850, 2150, 550, 700,
     "https://www.zumper.com/apartments-for-rent/toronto-on/new-toronto", "Waterfront Trail 600m", "Mimico GO 1km"),
    ("kipling_50_s", "50 Kipling Avenue South", "50 Kipling Ave S, Toronto, ON M8V 3N5", "New Toronto", 1900, 2300, 580, 700,
     "https://www.zumper.com/apartments-for-rent/toronto-on/new-toronto", "Colonel Sam Smith Park 1km", "Mimico GO 1.5km"),

    # STONEGATE / SUNNYLEA / OLD MILL / KINGSWAY
    ("park_lawn_15", "15 Park Lawn Crescent", "15 Park Lawn Cres, Toronto, ON M8Y 3H8", "Stonegate-Queensway", 1950, 2400, 600, 750,
     "https://www.zumper.com/apartments-for-rent/etobicoke-on/stonegate-queensway", "Humber River Recreational Trail 500m", "Mimico GO 2km, 501 streetcar"),
    ("queensway_955", "955 The Queensway", "955 The Queensway, Toronto, ON M8Z 1N9", "Stonegate-Queensway", 2100, 2700, 580, 750,
     "https://www.zumper.com/apartments-for-rent/etobicoke-on/stonegate-queensway", "Mimico Creek trail 200m", "Royal York subway 2.5km"),
    ("queensway_1430", "1430 The Queensway", "1430 The Queensway, Toronto, ON M8Z 1S5", "Stonegate-Queensway", 2050, 2500, 580, 720,
     "https://www.zumper.com/apartments-for-rent/etobicoke-on/stonegate-queensway", "Mimico Creek trail", "Kipling subway 3km"),
    ("bloor_4001", "4001 Bloor Street West", "4001 Bloor St W, Toronto, ON M9B 1L4", "Markland Wood/Six Points", 1950, 2500, 580, 720,
     "https://www.zumper.com/apartments-for-rent/etobicoke-on/markland-wood", "Bloor West Village + Humber River 2km", "Islington subway 200m"),
    ("kingsway_old_mill_2", "Old Mill 2 (2 Old Mill Drive)", "2 Old Mill Dr, Toronto, ON M8X 1G6", "Old Mill/Kingsway", 2400, 2800, 600, 750,
     "https://condos.ca/toronto/old-mill", "Humber River Recreational Trail at door", "Old Mill subway 200m"),

    # MARKLAND WOOD / WEST MALL / KIPLING
    ("bloor_3939", "3939 Bloor Street West", "3939 Bloor St W, Toronto, ON M9B 1M3", "Markland Wood", 1850, 2300, 580, 720,
     "https://www.zumper.com/apartments-for-rent/etobicoke-on/markland-wood", "Centennial Park 2km", "Islington subway 600m"),
    ("west_mall_400", "400 The West Mall", "400 The West Mall, Toronto, ON M9C 1E2", "West Mall", 1850, 2300, 600, 750,
     "https://www.zumper.com/apartments-for-rent/etobicoke-on/west-mall", "Centennial Park 1km", "Kipling subway 2.5km"),
    ("west_mall_350", "350 The West Mall", "350 The West Mall, Toronto, ON M9C 1E8", "West Mall", 1850, 2300, 600, 750,
     "https://www.zumper.com/apartments-for-rent/etobicoke-on/west-mall", "Centennial Park trails 1km", "Kipling subway 2.5km"),
    ("west_mall_320", "320 The West Mall", "320 The West Mall, Toronto, ON M9C 1E7", "West Mall", 1850, 2300, 600, 750,
     "https://www.zumper.com/apartments-for-rent/etobicoke-on/west-mall", "Centennial Park 1km", "Kipling subway 2.5km"),
    ("west_mall_390", "390 The West Mall", "390 The West Mall, Toronto, ON M9C 1E1", "West Mall", 1850, 2300, 600, 750,
     "https://www.zumper.com/apartments-for-rent/etobicoke-on/west-mall", "Centennial Park 1km", "Kipling subway 2.5km"),
    ("markland_dr_3", "3 Markland Drive", "3 Markland Dr, Toronto, ON M9C 1M2", "Markland Wood", 1900, 2400, 600, 750,
     "https://www.zumper.com/apartments-for-rent/etobicoke-on/markland-wood", "Markland Wood Golf area, Etobicoke Creek 1km", "Kipling subway 3km"),
]

def main():
    out_path = "/Users/rawproductivity/apartment-hunt/data/more_listings.jsonl"
    # Truncate
    open(out_path, "w").close()
    written = 0
    for L in LISTINGS:
        (lid, name, addr, zone, rl, rh, sl, sh, url, run, transit) = L
        lat, lng = geocode(addr)
        time.sleep(1.05)  # rate limit
        if lat is None:
            # fallback: approximate from postal/city — skip with placeholder near zone center
            lat, lng = CVH_LAT, CVH_LNG
            geocoded = False
        else:
            geocoded = True
        km_cvh = round(haversine(lat, lng, CVH_LAT, CVH_LNG), 1)
        km_union = round(haversine(lat, lng, UNION_LAT, UNION_LNG), 1)
        # rough drive times: 1.5 min/km off-peak, 2.5 min/km peak (urban GTA average)
        off = max(5, round(km_cvh * 1.6))
        peak = max(8, round(km_cvh * 2.6))
        union_off = max(15, round(km_union * 1.5))
        # rating heuristic
        rent_mid = (rl + rh) / 2
        if km_cvh <= 8 and rent_mid <= 2400:
            rating = "GOOD"
        elif km_cvh <= 12 and rent_mid <= 2600:
            rating = "FINE"
        elif km_cvh <= 18:
            rating = "POTENTIAL"
        else:
            rating = "STRETCH"
        # Pet status — most large apartment buildings in Ontario allow pets (no-pet clauses unenforceable in residential tenancy)
        # Condos vary by board rules
        if "condos.ca" in url or "condo" in name.lower() or "palace pier" in name.lower():
            pets = "Per-unit/condo board rules — verify before signing"
            pet_status = "verify-condo-rules"
        else:
            pets = "Likely yes — Ontario RTA Section 14 voids no-pet clauses; verify breed/weight restrictions"
            pet_status = "verify-specifics"
        # Pros/cons heuristics
        pros = []
        cons = []
        if "Waterfront Trail" in run or "Martin Goodman" in run or "Marie Curtis" in run:
            pros.append("Direct waterfront trail access for runs")
        if "Credit River" in run or "Sawmill" in run or "Sheridan Park" in run:
            pros.append("Credit River/Sheridan trails for long runs")
        if "Lake Aquitaine" in run:
            pros.append("Lake Aquitaine loop ideal for daily runs")
        if "Cooksville Creek" in run:
            pros.append("Cooksville Creek trail nearby")
        if km_cvh <= 6:
            pros.append(f"Short {km_cvh}km commute to CVH")
        if km_cvh > 15:
            cons.append(f"Long {km_cvh}km commute to CVH")
        if rent_mid > 2500:
            cons.append("Top of budget")
        if "Hurontario" in zone or "LRT" in transit:
            cons.append("Hurontario LRT construction noise — verify")
        if "Square One" in zone:
            cons.append("Dense urban core; less green space")
        if not pros:
            pros.append("Standard apartment amenities")
        if not cons:
            cons.append("Verify in-person")

        obj = {
            "id": lid,
            "name": name,
            "address": addr,
            "zone": zone,
            "rent_1bed_low": rl,
            "rent_1bed_high": rh,
            "sqft_low": sl,
            "sqft_high": sh,
            "pets": pets,
            "pet_status": pet_status,
            "drive_to_cvh_km": km_cvh,
            "drive_to_cvh_min_offpeak": off,
            "drive_to_cvh_min_peak": peak,
            "drive_to_union_min_offpeak": union_off,
            "running": run,
            "transit": transit,
            "promo": None,
            "red_flags": None if geocoded else "Geocoding failed — verify address",
            "rating": rating,
            "listing_url": url,
            "lat": round(lat, 5),
            "lng": round(lng, 5),
            "pros": pros,
            "cons": cons,
        }
        with open(out_path, "a") as f:
            f.write(json.dumps(obj) + "\n")
        written += 1
        print(f"[{written}] {lid} {km_cvh}km", flush=True)
    print(f"DONE: {written} written")

if __name__ == "__main__":
    main()
