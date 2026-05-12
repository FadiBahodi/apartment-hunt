#!/usr/bin/env python3
"""Fallback approximate coordinates for GTA addresses by postal FSA + street.
Accurate to ~500m for routing/distance purposes."""
# Format: postal FSA prefix -> (approx lat, approx lng) for that area
FSA_COORDS = {
    "L5A": (43.5800, -79.6080),  # Cooksville/Hurontario corridor
    "L5B": (43.5915, -79.6440),  # Square One area
    "L5C": (43.5900, -79.6620),  # Erindale
    "L5E": (43.5740, -79.5550),  # Lakeview
    "L5G": (43.5530, -79.5840),  # Port Credit
    "L5H": (43.5500, -79.6010),  # Mineola/SE Mississauga
    "L5J": (43.5135, -79.6310),  # Clarkson
    "L5K": (43.5200, -79.6630),  # Sheridan
    "L5L": (43.5470, -79.6970),  # Erin Mills
    "L5M": (43.5800, -79.7370),  # Streetsville/Central Erin Mills
    "L5N": (43.5990, -79.7530),  # Meadowvale
    "L4X": (43.6010, -79.5660),  # Applewood (north of Bloor/Dixie)
    "L4Y": (43.6060, -79.5740),  # Applewood (Bloor)
    "L4W": (43.6450, -79.6300),  # Airport area
    "M8V": (43.6090, -79.5040),  # Mimico/New Toronto
    "M8W": (43.5970, -79.5410),  # Long Branch
    "M8X": (43.6480, -79.4960),  # Old Mill/Kingsway
    "M8Y": (43.6280, -79.4970),  # Stonegate area
    "M8Z": (43.6235, -79.5160),  # Queensway/Stonegate W
    "M9B": (43.6470, -79.5380),  # Six Points/Islington
    "M9C": (43.6360, -79.5650),  # West Mall/Markland Wood
    "M6K": (43.6395, -79.4250),  # Liberty Village
    "M6P": (43.6555, -79.4640),  # High Park
}

# More precise overrides for specific addresses (lat, lng)
SPECIFIC = {
    # Cooksville
    "2070 Camilla Rd": (43.5807, -79.6017),
    "95 Paisley Blvd W": (43.5862, -79.6326),
    "2475 Hurontario St": (43.5867, -79.6470),
    "75 Seville Cres W": (43.5875, -79.6356),
    "121 Agnes St": (43.5848, -79.6363),
    "2590 Argyle Rd": (43.5910, -79.6362),
    "2570 Argyle Rd": (43.5905, -79.6360),
    "275 North Service Rd": (43.5795, -79.6188),
    "535 North Service Rd": (43.5810, -79.6280),
    "120 Dundas St E": (43.5786, -79.6217),
    "2247 Hurontario St": (43.5778, -79.6457),
    "2235 Promenade Crt": (43.5773, -79.6450),
    # Fairview/Square One/Mississauga Valley
    "3575 Kaneff Cres": (43.5750, -79.6420),
    "185 Enfield Pl": (43.5907, -79.6443),
    "30 Central Pky W": (43.5850, -79.6403),
    "620 Lolita Gardens": (43.5765, -79.6265),
    "3620 Kaneff Cres": (43.5752, -79.6428),
    "1423 Mississauga Valley Blvd": (43.5840, -79.6280),
    "1547 Mississauga Valley Blvd": (43.5850, -79.6300),
    "1477 Mississauga Valley Blvd": (43.5845, -79.6290),
    "30 Elm Dr E": (43.5905, -79.6420),
    "3665 Arista Way": (43.5840, -79.6270),
    # Erin Mills/Sheridan/Central Erin Mills
    "2375 The Collegeway": (43.5470, -79.6920),
    "2445 The Collegeway": (43.5485, -79.6970),
    "2550 Eglinton Ave W": (43.5760, -79.7350),
    "5625 Glen Erin Dr": (43.5715, -79.7340),
    "2900 Rio Crt": (43.5760, -79.7320),
    "2150 Roche Crt": (43.5230, -79.6680),
    "2215 Sheridan Park Dr": (43.5240, -79.6680),
    "1980 Fowler Dr": (43.5185, -79.6610),
    "1970 Fowler Dr": (43.5180, -79.6610),
    "2250 Homelands Dr": (43.5235, -79.6720),
    "2185 Sheridan Park Dr": (43.5240, -79.6685),
    # Meadowvale
    "6570 Glen Erin Dr": (43.5985, -79.7480),
    "6550 Glen Erin Dr": (43.5980, -79.7475),
    "2645 Battleford Rd": (43.5970, -79.7560),
    "2699 Battleford Rd": (43.5970, -79.7570),
    "2770 Aquitaine Ave": (43.6020, -79.7510),
    "2797 Battleford Rd": (43.5975, -79.7585),
    "2869 Battleford Rd": (43.5980, -79.7610),
    # Streetsville
    "190 Queen St S": (43.5840, -79.7080),
    "18 Reid Dr": (43.5810, -79.7170),
    # Port Credit
    "5 Ann St": (43.5535, -79.5840),
    "70 Park St E": (43.5538, -79.5810),
    "28 Elizabeth St N": (43.5542, -79.5830),
    "35 Front St S": (43.5520, -79.5860),
    "55 Park St E": (43.5538, -79.5815),
    "28 Helene St N": (43.5548, -79.5820),
    "8 Oakwood Ave N": (43.5540, -79.5790),
    "212 Lakeshore Rd E": (43.5530, -79.5775),
    "206 Lakeshore Rd E": (43.5530, -79.5777),
    "7 Elizabeth St N": (43.5540, -79.5830),
    "30 High St E": (43.5545, -79.5825),
    "52 Park St E": (43.5538, -79.5813),
    "20 Elizabeth St N": (43.5541, -79.5830),
    "26 Park St E": (43.5538, -79.5814),
    "12 Park St E": (43.5538, -79.5817),
    # Lakeview
    "1015 Orchard Rd": (43.5670, -79.5560),
    "1285 Lakeshore Rd E": (43.5680, -79.5470),
    "1110 Caven St": (43.5610, -79.5710),
    "1051 Seneca Ave": (43.5650, -79.5680),
    # Clarkson
    "920 Inverhouse Dr": (43.5145, -79.6280),
    "2360 Bonner Rd": (43.5170, -79.6380),
    "2150 Bromsgrove Rd": (43.5125, -79.6240),
    "2077 Barsuda Dr": (43.5180, -79.6310),
    # Applewood
    "1785 Bloor St": (43.6020, -79.5640),
    "1745 Bloor St": (43.6020, -79.5650),
    "1867 Bloor St": (43.6020, -79.5620),
    "3410 Havenwood Dr": (43.6040, -79.5640),
    "1465 Tyneburn Cres": (43.6010, -79.5680),
    "1470 Williamsport Dr": (43.6020, -79.5660),
    "1055 Bloor St": (43.6080, -79.5790),
    "1475 Bloor St": (43.6035, -79.5705),
    # Mimico/HBS/New Toronto/Long Branch (Etobicoke)
    "38 Annie Craig Dr": (43.6225, -79.4790),
    "30 Shore Breeze Dr": (43.6230, -79.4790),
    "185 Legion Rd N": (43.6225, -79.4870),
    "165 Legion Rd N": (43.6225, -79.4865),
    "15 Western Battery Rd": (43.6395, -79.4218),
    "2230 Lake Shore Blvd W": (43.6230, -79.4815),
    "2212 Lake Shore Blvd W": (43.6230, -79.4825),
    "58 Marine Parade Dr": (43.6230, -79.4790),
    "15 Marine Parade Dr": (43.6230, -79.4775),
    "3 Marine Parade Dr": (43.6225, -79.4775),
    "36 Park Lawn Rd": (43.6260, -79.4800),
    "1 Palace Pier Crt": (43.6285, -79.4760),
    # Long Branch
    "240 Lake Promenade": (43.5900, -79.5430),
    "220 Lake Promenade": (43.5900, -79.5440),
    "3845 Lake Shore Blvd W": (43.5900, -79.5390),
    "3650 Lake Shore Blvd W": (43.5945, -79.5400),
    "30 Long Branch Ave": (43.5910, -79.5410),
    # New Toronto
    "3590 Lake Shore Blvd W": (43.5970, -79.5430),
    "3479 Lake Shore Blvd W": (43.5990, -79.5340),
    "45 Birmingham St": (43.6050, -79.5180),
    "24 Eighth St": (43.6020, -79.5100),
    "50 Kipling Ave S": (43.6040, -79.5160),
    # Stonegate/Queensway
    "15 Park Lawn Cres": (43.6280, -79.4970),
    "955 The Queensway": (43.6260, -79.5040),
    "1430 The Queensway": (43.6210, -79.5180),
    "4001 Bloor St W": (43.6440, -79.5360),
    "2 Old Mill Dr": (43.6488, -79.4955),
    # Markland Wood/West Mall
    "3939 Bloor St W": (43.6440, -79.5345),
    "400 The West Mall": (43.6360, -79.5650),
    "350 The West Mall": (43.6370, -79.5650),
    "320 The West Mall": (43.6375, -79.5650),
    "390 The West Mall": (43.6360, -79.5650),
    "3 Markland Dr": (43.6310, -79.5660),
}

def lookup(addr):
    """Return (lat, lng) or (None, None)."""
    # Try specific match first
    for key, (lat, lng) in SPECIFIC.items():
        if addr.startswith(key):
            return lat, lng
    # Fallback to FSA
    for fsa, (lat, lng) in FSA_COORDS.items():
        if f" {fsa} " in addr or addr.endswith(fsa):
            return lat, lng
    return None, None

if __name__ == "__main__":
    print(lookup("2070 Camilla Rd, Mississauga, ON L5A 2J7"))
    print(lookup("Some random address, ON L5J 4M9"))
