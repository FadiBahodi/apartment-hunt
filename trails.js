// Running trails + parks GeoJSON
// Hand-curated from OSM + AllTrails + city sources. Lat/lng accurate to ~50m.
// Each trail has: name, length_km, winter_maintained, dog_policy, surface, color
window.TRAILS = [
  {
    name: "Martin Goodman Trail (W)",
    length_km: 22, winter_maintained: true, dog_policy: "leash", surface: "paved",
    color: "#10b981",
    note: "ONLY year-round-cleared trail in west GTA. Plowed within 6-8h of >5cm snow. Best winter base.",
    coords: [[43.5876,-79.5430],[43.5953,-79.5145],[43.5985,-79.5125],[43.6005,-79.5060],[43.6076,-79.4938],[43.6105,-79.4895],[43.6118,-79.4960],[43.6232,-79.4810],[43.6240,-79.4730],[43.6260,-79.4650],[43.6300,-79.4550],[43.6388,-79.4439],[43.6432,-79.4006]]
  },
  {
    name: "Mississauga Waterfront Trail",
    length_km: 16.9, winter_maintained: false, dog_policy: "leash", surface: "paved + boardwalk",
    color: "#06b6d4",
    note: "Continuous Etobicoke Creek mouth → Port Credit → Rattray Marsh (no bikes!) → Jack Darling. NOT winter-maintained.",
    coords: [[43.5860,-79.5440],[43.5680,-79.5550],[43.5612,-79.5567],[43.5640,-79.5468],[43.5612,-79.5567],[43.5519,-79.5878],[43.5480,-79.6010],[43.5350,-79.6050],[43.5160,-79.6300],[43.5093,-79.6207],[43.5060,-79.6390]]
  },
  {
    name: "David J. Culham Trail / Sawmill Valley / UTM",
    length_km: 11.2, winter_maintained: false, dog_policy: "leash", surface: "paved + boardwalk + dirt",
    color: "#a855f7",
    note: "Best off-road trail near CVH. Streetsville → UTM → Erindale Park → Burnhamthorpe. Reddit: 'only one car-street crossing'. NOT winter-maintained, unlit.",
    coords: [[43.5810,-79.7113],[43.5780,-79.7000],[43.5687,-79.6566],[43.5582,-79.6694],[43.5500,-79.6680],[43.5450,-79.6650]]
  },
  {
    name: "Etobicoke Creek Trail",
    length_km: 11, winter_maintained: false, dog_policy: "leash", surface: "paved + dirt",
    color: "#a855f7",
    note: "Marie Curtis → Centennial Park → Pearson. Markland Wood golf BREAKS continuity Dundas-Burnhamthorpe.",
    coords: [[43.5860,-79.5430],[43.5995,-79.5380],[43.6160,-79.5500],[43.6280,-79.5650],[43.6360,-79.5825],[43.6505,-79.5870],[43.6700,-79.6100]]
  },
  {
    name: "Burnhamthorpe Trail (winter spine)",
    length_km: 11, winter_maintained: true, dog_policy: "leash", surface: "paved",
    color: "#10b981",
    note: "Mississauga's main winter-maintained paved trail. Connects Square One area east-west.",
    coords: [[43.5587,-79.7114],[43.5780,-79.6700],[43.5923,-79.6420],[43.6010,-79.6100],[43.6080,-79.5900]]
  },
  {
    name: "Riverwood Trail (Yellow + Red)",
    length_km: 5.8, winter_maintained: false, dog_policy: "leash", surface: "dirt",
    color: "#a855f7",
    note: "Most-reviewed Mississauga trail (1,578 AllTrails reviews). Conservancy land in Streetsville.",
    coords: [[43.5780,-79.7000],[43.5810,-79.6960],[43.5840,-79.6900],[43.5800,-79.6850]]
  },
  {
    name: "Cooksville Creek Trail (Square One winter option)",
    length_km: 6, winter_maintained: true, dog_policy: "leash", surface: "paved",
    color: "#10b981",
    note: "Fragmented urban paths but plowed. ~2km usable continuous from Burnhamthorpe E to Dundas.",
    coords: [[43.5953,-79.6429],[43.5900,-79.6360],[43.5840,-79.6320],[43.5780,-79.6290]]
  },
  {
    name: "Rattray Marsh / Jack Darling (no bikes!)",
    length_km: 4, winter_maintained: false, dog_policy: "leash + off-leash zone",
    surface: "boardwalk + dirt",
    color: "#a855f7",
    note: "CVC bans bikes — runner+dog haven. Jack Darling has major off-leash dog park.",
    coords: [[43.5160,-79.6300],[43.5130,-79.6250],[43.5093,-79.6207]]
  }
];

window.PARKS = [
  {name: "Erindale Park", lat: 43.5687, lng: -79.6566, area_acres: 222, note: "222-acre Mississauga's largest park; Culham trailhead"},
  {name: "Centennial Park (Etobicoke)", lat: 43.6505, lng: -79.5870, area_acres: 525, note: "525-acre; ski hill, Etobicoke Creek connector"},
  {name: "Humber Bay Park", lat: 43.6230, lng: -79.4830, area_acres: 90, note: "Sheldon Lookout; doorstep for Vita/Lago/Eau du Soleil"},
  {name: "Marie Curtis Park", lat: 43.5876, lng: -79.5430, area_acres: 60, note: "Etobicoke Creek mouth; doorstep for 45 Forty Second"},
  {name: "Colonel Samuel Smith Park", lat: 43.5953, lng: -79.5145, area_acres: 90, note: "BEST west-GTA dog/run park (per Great Runs); doorstep for 90 James"},
  {name: "Rattray Marsh Conservation", lat: 43.5155, lng: -79.6300, area_acres: 200, note: "NO BIKES rule (CVC) — quiet runner haven"},
  {name: "Jack Darling Memorial Park", lat: 43.5093, lng: -79.6207, area_acres: 33, note: "Major off-leash dog park"},
  {name: "Riverwood Conservancy", lat: 43.5800, lng: -79.6900, area_acres: 150, note: "Most-reviewed Mississauga trails"},
  {name: "Sawmill Valley Park", lat: 43.5620, lng: -79.6680, area_acres: 50, note: "Trailhead for Culham/UTM connector"},
  {name: "Bronte Creek Provincial Park", lat: 43.4115, lng: -79.7240, area_acres: 1700, note: "Weekend-trail option; 50m ravine"},
  {name: "Lakefront Promenade Park", lat: 43.5570, lng: -79.5380, area_acres: 35, note: "Mississauga waterfront tempo runs"},
  {name: "Port Credit / J.J. Plaus", lat: 43.5519, lng: -79.5878, area_acres: 10, note: "Port Credit waterfront village"}
];
