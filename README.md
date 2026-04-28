# Apartment Hunt — Fadi & Nomi (July 2026)

Interactive map + 26 verified pet-friendly rental candidates near Credit Valley Hospital (Mississauga) and west Etobicoke / Toronto.

**Live site:** https://fadibahodi.github.io/apartment-hunt/

## Coverage
- 26 buildings across 7 zones (Central Erin Mills, Streetsville, Markland Wood, West Mall, Mimico, Humber Bay Shores, Long Branch, Stonegate, Clarkson, Lakeview)
- 100+ photos, all visually inspected
- Drive times to CVH (off-peak + peak estimates)
- Transit (GO + subway + streetcar) times to Union
- Running route notes per zone
- Pet policy verified or flagged
- Documented red-flag avoid list (1980 Fowler, 2250 Homelands, 240 Markland, Skyrise — sources: CBC, Bed Bug Registry, listings)

## Architecture
- `index.html` — single-page Leaflet map + cards + detail panel
- `data.js` — apartment data (manually compiled + agent-researched)
- `manifest.js` — building → photo path map
- `photos/` — local cached images

## Sources
Listings from Zumper, Greenwin, CAPREIT, Hazelview, Park Property, Sterling Karamar, Briarlane, Centurion, Minto. Pet policies cross-referenced. Drive times derived from Rome2Rio + GTA construction project data (Hurontario LRT, QEW Credit River bridge). Running data from AllTrails, Reddit, City of Mississauga / Toronto winter maintenance pages.

**Verify before signing:** drive Google Maps for actual shift times, get condo declaration in writing for any condo unit, tour at 11pm and 7am.
