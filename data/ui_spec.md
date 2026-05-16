# Apartment Hunt — Redesign Spec

**Status:** Opinionated. Paste-ready. Cite-as-you-go.
**Verdict on current site:** It reads as "dark-mode dashboard built in two evenings." Tells: muted navy + candy-orange combo, badge-pip-pill triplication, 64px square thumbnail in card row (mid-2010s admin-panel tic), modal-on-dim-overlay for everything, stats-strip pill bar, emoji in headings, and a neutral-gray Leaflet OSM tile that immediately signals "default settings."

The site has real density and real data — that's the asset. We're not redesigning Linear; we're redesigning a private research workspace for a real apartment hunt. The reference points that matter are **Linear** (calm density, restraint, monochrome with one accent), **Vercel** (typographic confidence, neutrals + black CTA, no decoration), **Padmapper/Zillow** (map-as-figure, list-as-ground, photo-first listing card), **Airbnb** (4:3 photo ratio with overlaid micro-meta), and **Stripe** (data-forward microcopy — specific numbers over vague claims). We are explicitly **not** chasing Hellolanding's "warm hospitality" — wrong register for a power-tool.

The single biggest move: **kill the orange-on-charcoal admin look. Go light-mode-default with one electric accent and an actually-styled map.** That alone moves it from "generic AI dashboard" to "personal research tool I actually use." Dark mode stays available but is no longer the default.

---

## Design language

### Color palette

Two themes. Default is light because Padmapper/Zillow/Airbnb all run light for listings — photos pop, map reads, no eyestrain in a 2pm browse session. Dark is opt-in.

**Light (default):**
```
--bg:           #FAFAF7   /* warm paper, not pure white — Vercel uses #FFF, we warm 3pts so photos don't feel surgical */
--surface:      #FFFFFF   /* card / panel */
--surface-2:    #F4F3EE   /* hover, sunken */
--border:       #E7E5DE   /* hairline */
--border-strong:#1A1A1A   /* selected / focus / CTA outline — black, not gray */
--text:         #111111   /* near-black, never pure */
--text-muted:   #6B6B66   /* not #888 — slightly warm */
--text-dim:     #9A9994
--accent:       #1652F0   /* electric blue, the ONLY chromatic accent — Coinbase/Linear-blue cousin */
--accent-soft:  #EAF0FE
--good:         #0E7C3A   /* deep, not neon */
--warn:         #B45309   /* burnt amber, not candy */
--bad:          #B91C1C   /* deep red, not pink */
--map-overlay:  rgba(255,255,255,.92)
```

**Dark (opt-in via `[data-theme="dark"]`):**
```
--bg:           #0E0E0E   /* true near-black, not navy-blue-tinted */
--surface:      #161616
--surface-2:    #1E1E1E
--border:       #262626
--border-strong:#F5F5F5
--text:         #F5F5F5
--text-muted:   #9A9A93
--accent:       #5B8DEF
--accent-soft:  rgba(91,141,239,.14)
```

**Why:** Linear and Vercel both moved away from blue-tinted darks toward true grays/blacks because tinted darks read "skinned." The current site's `#0a0c10` is navy — fix it. One accent, used sparingly, beats five semantic colors fighting for attention. Padmapper uses red sparingly for a reason.

### Type scale

Drop Inter. **Use Geist** (Vercel's open-source sans, free via Google Fonts) for UI, and **Geist Mono** for tabular numbers, addresses, timing. Geist has the same metrics as Inter but feels less SaaS-default in 2026 — Inter is now the "I read a Medium article on type" choice. Fallback to system if Geist fails.

```
font-family: 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
font-family-mono: 'Geist Mono', 'SF Mono', Menlo, monospace;
```

Scale (px / line-height / weight / tracking):
```
--text-display:   32 / 36 / 600 / -0.02em   /* page hero (NEW: there isn't one yet) */
--text-h1:        20 / 26 / 600 / -0.015em  /* detail panel building name */
--text-h2:        15 / 22 / 600 / -0.005em  /* section heads in detail */
--text-body:      14 / 21 / 400 / 0          /* default */
--text-meta:      12 / 18 / 500 / 0          /* card sub-info */
--text-micro:     11 / 14 / 500 / 0.02em    /* labels, eyebrows — NOT uppercase */
--text-tabular:   13 / 18 / 500 / -0.01em   /* prices, distances; font-variant-numeric: tabular-nums */
```

**Kill all `text-transform: uppercase`.** It's the single loudest "I'm trying" tic in the current CSS. Linear uses zero uppercase. Vercel uses zero uppercase. Stripe uses zero uppercase in product chrome. Letter-spaced uppercase micro-labels are the 2018 admin-panel signature. Replace with sentence-case at a smaller weight.

### Spacing scale

4px base. Tighter than current (which is fine) but with a clearer rhythm.
```
--s-0: 2px; --s-1: 4px; --s-2: 8px; --s-3: 12px; --s-4: 16px;
--s-5: 24px; --s-6: 32px; --s-7: 48px; --s-8: 64px;
```

### Border radius

Current uses 4/6/10 — fine, but inconsistent in use. Standardize:
```
--r-1: 4px;   /* buttons, inputs, chips */
--r-2: 8px;   /* cards, panels */
--r-3: 12px;  /* modals, sheets, hero images */
--r-pill: 999px;
```
**Photos: 8px.** No more. Airbnb uses 12px on cards but they're hero-sized; ours are not.

### Shadow scale

The current site has effectively zero shadow. Light mode needs them; we use them rarely and softly.
```
--shadow-sm: 0 1px 2px rgba(17,17,17,.04), 0 0 0 1px rgba(17,17,17,.04);
--shadow-md: 0 4px 12px rgba(17,17,17,.06), 0 0 0 1px rgba(17,17,17,.05);
--shadow-lg: 0 12px 32px rgba(17,17,17,.10), 0 0 0 1px rgba(17,17,17,.06);
--shadow-pop: 0 8px 24px rgba(17,17,17,.12); /* map popups, floating UI */
```
Note the "ring" component on every shadow — Linear technique; replaces the hairline border when an element is hovered/elevated.

### Motion

Current uses `0.12s/0.18s ease`. Fine but flavorless. Replace with named curves:
```
--ease-out: cubic-bezier(0.2, 0.7, 0.2, 1);   /* default — Linear's curve */
--ease-spring: cubic-bezier(0.32, 0.72, 0, 1); /* sheets, drawers — Vercel */
--d-1: 120ms;  /* hover, focus */
--d-2: 200ms;  /* card select, panel toggle */
--d-3: 320ms;  /* sheet slide */
```

Rule: **no scale transforms on hover.** No `transform: scale(1.02)`. Linear, Vercel, Stripe — none use it. Hover affordance is via border-color shift + tiny background tint. Save scale for click feedback only.

---

## Layout shifts

### Header — change

Current header is fine structurally but visually weak. The `<span class="wordmark">apartment</span>/hunt` move is cute but reads cheap. Replace.

```html
<header class="topbar">
  <div class="brand">
    <span class="brand-mark">AH</span>
    <span class="brand-text">Apartment Hunt</span>
    <span class="brand-sub">Toronto · July 2026</span>
  </div>
  <div class="countdown">
    <span class="countdown-num" id="days-to-move">—</span>
    <span class="countdown-label">days to move-in</span>
  </div>
  <nav class="topnav">
    <button class="nav-btn" data-view="shortlist">Shortlist</button>
    <button class="nav-btn" data-view="favorites">Saved <span class="nav-count" id="fav-count">0</span></button>
    <button class="nav-btn" data-view="compare">Compare</button>
    <button class="nav-btn" data-view="timeline">Timeline</button>
    <button class="nav-btn nav-icon" data-view="help" aria-label="Help">?</button>
    <button class="nav-btn nav-icon theme-toggle" aria-label="Toggle theme">◐</button>
  </nav>
</header>
```

Key moves vs current:
- Brand becomes a small mark (`AH`) + wordmark — proper logo lockup, not orange/gray text play
- **Countdown is now a hero number** (32px) — borrowed from Stripe's data-forward technique. "127 days to move-in" is the most important number on the page; treat it like one
- Kill the stats-strip below header. It's the third "header" element and it's noise
- Theme toggle present from day one — not a setting buried elsewhere

### Sidebar list — rebuild card

**Current card problems (be specific):**
1. 64px square thumbnail = admin panel. Photos this small can't sell a place; remove or go large
2. Three-column grid (`64px 1fr auto`) crams everything; rent right-aligned floats orphaned
3. Badge + pip + uppercase label = three competing visual systems for the same job
4. Border radius 6px is the awkward "not a designer" choice — should be 8px
5. Selected state uses orange fill — too loud for "I clicked a thing"

**Replacement card — photo-first, Airbnb-influenced, Padmapper-dense:**

```html
<article class="lcard" data-id="..." tabindex="0">
  <div class="lcard-photo" style="background-image:url(...)">
    <button class="lcard-fav" aria-label="Save">♥</button>
    <span class="lcard-fit" data-tier="good">82</span>
  </div>
  <div class="lcard-body">
    <div class="lcard-row1">
      <h3 class="lcard-name">123 Main Street</h3>
      <span class="lcard-rent">$1,950</span>
    </div>
    <div class="lcard-row2">
      <span class="lcard-zone">Port Credit · 1BR · 720sf</span>
    </div>
    <div class="lcard-row3">
      <span class="lcard-stat"><span class="lcard-k">CVH</span> 12m</span>
      <span class="lcard-stat"><span class="lcard-k">Union</span> 22m</span>
      <span class="lcard-stat lcard-pet"><span class="lcard-k">Pet</span> ✓</span>
    </div>
  </div>
</article>
```

```css
.lcard {
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: 12px;
  padding: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-2);
  margin-bottom: 6px;
  cursor: pointer;
  transition: border-color var(--d-1) var(--ease-out), background var(--d-1) var(--ease-out);
}
.lcard:hover { border-color: #C9C7BE; background: var(--surface-2); }
.lcard.is-selected { border-color: var(--border-strong); box-shadow: var(--shadow-sm); }
.lcard-photo {
  position: relative;
  width: 96px; height: 96px;
  border-radius: var(--r-2);
  background: var(--surface-2) center/cover no-repeat;
  overflow: hidden;
}
.lcard-fav {
  position: absolute; top: 6px; right: 6px;
  width: 24px; height: 24px;
  background: rgba(255,255,255,.92);
  border: 0; border-radius: 999px;
  font-size: 13px; cursor: pointer;
  display: grid; place-items: center;
  backdrop-filter: blur(8px);
}
.lcard-fit {
  position: absolute; bottom: 6px; left: 6px;
  background: var(--text); color: var(--bg);
  font: 600 11px/1 'Geist Mono', monospace;
  padding: 3px 6px; border-radius: var(--r-1);
  font-variant-numeric: tabular-nums;
}
.lcard-fit[data-tier="good"] { background: var(--good); color: white; }
.lcard-fit[data-tier="warn"] { background: var(--warn); color: white; }
.lcard-fit[data-tier="bad"]  { background: var(--bad);  color: white; }
.lcard-body { min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.lcard-row1 { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.lcard-name {
  margin: 0; font: 600 14px/1.3 'Geist', sans-serif;
  letter-spacing: -0.01em;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.lcard-rent {
  font: 500 14px/1 'Geist Mono', monospace;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
  flex-shrink: 0;
}
.lcard-zone { color: var(--text-muted); font: 400 12px/1.4 'Geist', sans-serif; }
.lcard-row3 { display: flex; gap: 12px; margin-top: 2px; }
.lcard-stat { font: 500 12px/1 'Geist Mono', monospace; color: var(--text); }
.lcard-stat .lcard-k { color: var(--text-dim); margin-right: 3px; font-weight: 400; }
.lcard-pet { color: var(--good); }
```

Why this works: photo-first matches Padmapper/Zillow; fit-score-on-photo is Airbnb's price-tag move; the three-stat row uses **monospace numerals** which makes scanning down a 60-item list instantly readable (currently it's not, because Inter proportional digits jitter). Rent on the same row as name, not right-floated — fewer eye-jumps.

### Map — switch tile provider

This is the single biggest visual upgrade. **Default Leaflet OSM tiles are the #1 "default settings" tell.** Switch to:

**Primary: CARTO Voyager (light)** — free, no key needed for non-commercial, looks like a designed product, has subtle labels.
```js
L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; <a href="https://carto.com">CARTO</a> &copy; <a href="https://openstreetmap.org">OSM</a>',
  subdomains: 'abcd', maxZoom: 20
}).addTo(map);
```

**For dark mode: CARTO Dark Matter**
```js
'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
```

If you want to spend later: Mapbox Studio with a custom monochrome style (Linear-grade), or Stadia AlidadeSmooth (cheaper than Mapbox, similar quality). **Do not stay on default OSM.**

Pin redesign: stop using `divIcon` with emoji glyphs (✓!✕·). Use SVG circle pins with a single character or no character, color = tier, white halo. Match the lcard-fit chip language. Selected pin gets a 2px black ring + 4px white halo (Padmapper move).

### Detail panel — reorder

Current order: name → addr → 2x2 photo grid → 2-col stat grid → headings → reviews → cost → notes → externals.

**New order (highest-decision-value first):**
1. **Hero photo** (full-width 16:9, 240px tall) with overlay title bar (name + fit chip)
2. **Quick verdict bar** — single sentence editorial (e.g. "Pet-OK condo, 12m to CVH, $1,950 — but 22m to Union") in 16px italic
3. **Three stats inline** (Rent · CVH · Union) — large, monospace, no boxes around them
4. **Photo strip** (horizontal scroll, 3-up at 100px tall) — not the awkward 2-col grid
5. **Cost decoder table** — keep, but use simple `<dl>` not `<table>`
6. **Pros / Cons** — two columns, no bullets, just colored hairline-left items
7. **Reviews / notes** below the fold
8. **External links** as text links at the very bottom (`zillow ↗  ·  realtor ↗  ·  google ↗`), not buttons

Why: the panel currently leads with photos before saying anything. Padmapper/Zillow lead with price+address+key stats. Lead with the decision, support with photos.

### Modals → sheets

**Kill the `position:fixed; rgba(0,0,0,.85)` modal pattern.** It's the most universally-recognized "AI dashboard" tic of 2024-2026. Replace with:

- **Shortlist / Favorites / Compare → right-side sheet** (480-720px wide depending on content), slide-in from right, dimmer at 0.4 not 0.85, body remains visible
- **Timeline → full bleed view** (replace the layout grid temporarily, like Linear's "issue detail" view) — not a modal
- **Help → popover** anchored to the `?` button, not a modal — like Vercel's "shortcut sheet"

```css
.sheet {
  position: fixed; top: 0; right: 0; bottom: 0;
  width: min(640px, 92vw);
  background: var(--surface);
  border-left: 1px solid var(--border);
  box-shadow: var(--shadow-lg);
  transform: translateX(100%);
  transition: transform var(--d-3) var(--ease-spring);
  z-index: 100;
  overflow-y: auto;
}
.sheet.is-open { transform: translateX(0); }
.sheet-backdrop {
  position: fixed; inset: 0;
  background: rgba(17,17,17,.32);
  opacity: 0; pointer-events: none;
  transition: opacity var(--d-2) var(--ease-out);
  z-index: 99;
}
.sheet-backdrop.is-open { opacity: 1; pointer-events: auto; }
```

---

## Specific things to KILL

- **`.stats-strip` (line 233-235, 307)** — duplicate header, classic dashboard cruft
- **`.badge .dot` system** — pip + dot + badge is one signal in three forms. Pick one (chip with leading dot)
- **`text-transform: uppercase` everywhere** — sort labels, stat labels, section heads (`#detail h3`, line 127), legend headers, badge text, action-row buttons. All of it
- **Emoji in headings** (`⭐ The Honest Shortlist`, `❤️ Your Favorites`, `⚖️ Compare`, `📅 Timeline`) — biggest amateur tell on the page. Use icon SVGs or no glyph
- **`.wordmark` orange/gray play in `<h1>`** (line 240) — clever-monkey branding
- **64px thumbnail squares** — go 96px and photo-first, or go zero and use a colored letter tile
- **Orange-fill selected state** (`.card.selected` line 76) — replace with black border + shadow ring
- **`--accent: #ff7a45` orange entirely** — it is The AI Site Color. Move to electric blue (#1652F0) which still pops but doesn't trigger "ChatGPT skin"
- **Navy-tinted background `#0a0c10`** — go true gray in dark mode
- **The `◯` placeholder glyph + "Select a building" centered block** (line 348-353) — feels like a Figma kit. Replace with empty-state illustration or just empty
- **`✕ Close` text buttons on modals** — use a single `×` SVG icon button, top-right, ghost style
- **Filter buttons as monochrome chips with caps text** — replace with rounded segment buttons; only ONE can have the accent fill at a time

---

## Specific NEW patterns to ADOPT

### 1. The "data poster" detail header
Where: top of detail panel. Why: Stripe's "$1.9tn processed" pattern — lead with the number. Code:
```html
<div class="detail-hero">
  <div class="detail-hero-photo" style="background-image:url(...)"></div>
  <div class="detail-hero-bar">
    <div>
      <h1 class="detail-h1">123 Main Street</h1>
      <div class="detail-addr">Port Credit, Mississauga</div>
    </div>
    <span class="lcard-fit" data-tier="good" style="font-size:14px;padding:6px 10px">82 / 100</span>
  </div>
</div>
```
```css
.detail-hero { position: relative; margin: -16px -24px 16px; }
.detail-hero-photo {
  height: 240px; background: var(--surface-2) center/cover no-repeat;
}
.detail-hero-bar {
  position: absolute; left: 0; right: 0; bottom: 0;
  padding: 20px 24px;
  background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,.65) 100%);
  display: flex; justify-content: space-between; align-items: flex-end;
  color: white;
}
.detail-h1 { margin: 0; font: 600 22px/1.2 'Geist'; letter-spacing: -0.02em; }
.detail-addr { font: 400 12px/1.4 'Geist Mono'; opacity: .85; margin-top: 2px; }
```

### 2. Inline-prose stats (kill the stat-box grid)
Where: detail panel, replacing the current `.stats` 2x2 grid. Why: Linear shows metadata inline as text, not as boxes. Box-laden UIs read juvenile.
```html
<p class="detail-tldr">
  <span class="tldr-rent">$1,950</span><span class="tldr-unit">/mo</span>
  <span class="tldr-sep">·</span>
  <span class="tldr-stat"><b>12m</b> CVH</span>
  <span class="tldr-sep">·</span>
  <span class="tldr-stat"><b>22m</b> Union</span>
  <span class="tldr-sep">·</span>
  <span class="tldr-stat"><b>720</b>sf</span>
</p>
```
```css
.detail-tldr { font: 400 14px/1.6 'Geist'; color: var(--text-muted); margin: 0 0 16px; }
.tldr-rent { font: 600 24px/1 'Geist'; color: var(--text); letter-spacing: -0.02em; }
.tldr-unit { font-size: 14px; color: var(--text-muted); margin-right: 6px; }
.tldr-sep { color: var(--text-dim); margin: 0 6px; }
.tldr-stat b { color: var(--text); font-weight: 600; font-variant-numeric: tabular-nums; }
```

### 3. Keyboard-first command palette
Where: cmd+K opens. Why: Linear, Vercel, GitHub all have one. For a research tool used daily, it's the right interaction model.
```html
<div class="cmdk" hidden>
  <input class="cmdk-input" placeholder="Search buildings, jump to view, filter…">
  <div class="cmdk-list"></div>
</div>
```
Hook `Cmd/Ctrl+K` to open; ESC to close. Searches buildings + offers filter shortcuts ("pet OK", "rent < 2000", "open timeline"). This replaces the in-sidebar `#search` for power use; sidebar search stays.

### 4. Sticky filter bar with single-active-chip pattern
Where: top of sidebar, sticky on scroll. Why: Zumper/Padmapper sticky-filter. Single-active = clearer mental model than multi-select chips.
```css
.filterbar {
  position: sticky; top: 0; z-index: 5;
  background: var(--bg);
  padding: 12px 0 8px;
  border-bottom: 1px solid var(--border);
  margin: 0 -12px 8px; padding-left: 12px; padding-right: 12px;
}
```

### 5. Map popup redesign — Airbnb price-pin
Where: every map pin. Why: text-on-pin reads at a glance; circle pins force a second click. For listings with rent, show rent on pin.
```js
const pinHtml = `<div class="pricepin pricepin--${tier}">$${Math.round(rent/100)/10}k</div>`;
L.divIcon({ html: pinHtml, className: 'pricepin-wrap', iconSize: [44, 22] });
```
```css
.pricepin {
  background: white; color: var(--text);
  padding: 4px 8px; border-radius: 999px;
  font: 600 12px/1 'Geist Mono'; font-variant-numeric: tabular-nums;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  white-space: nowrap;
  transition: transform var(--d-1) var(--ease-out);
}
.pricepin:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.pricepin.is-selected { background: var(--text); color: white; border-color: var(--text); }
.pricepin--bad { color: var(--bad); }
```

### 6. Micro-copy: drop the dashboard voice
- "Sort: Fit Score (best→)" → "Sort by fit"
- "Hard avoid · documented" → "Avoided buildings"
- "Top picks" / "Saved" / "Compare" stays (good already)
- "Select a building" empty state → "Pick a building from the list or map." (sentence + period)
- "Move-in Jul 1 2026 · 127 days" → owned by the new countdown unit; drop from header

---

## Concrete CSS to drop in

Replace lines 9-236 of `index.html` with this `<style>` block. It assumes you also add `<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">` in `<head>`.

```html
<style>
:root {
  /* Color — light default */
  --bg: #FAFAF7;
  --surface: #FFFFFF;
  --surface-2: #F4F3EE;
  --border: #E7E5DE;
  --border-strong: #1A1A1A;
  --text: #111111;
  --text-muted: #6B6B66;
  --text-dim: #9A9994;
  --accent: #1652F0;
  --accent-soft: #EAF0FE;
  --good: #0E7C3A;
  --good-soft: #E6F2EB;
  --warn: #B45309;
  --warn-soft: #FBF1E4;
  --bad: #B91C1C;
  --bad-soft: #FBE9E9;
  --map-overlay: rgba(255,255,255,.92);

  /* Type */
  --font-sans: 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'Geist Mono', 'SF Mono', Menlo, monospace;

  /* Space */
  --s-0: 2px; --s-1: 4px; --s-2: 8px; --s-3: 12px; --s-4: 16px;
  --s-5: 24px; --s-6: 32px; --s-7: 48px; --s-8: 64px;

  /* Radius */
  --r-1: 4px; --r-2: 8px; --r-3: 12px; --r-pill: 999px;

  /* Shadow */
  --shadow-sm: 0 1px 2px rgba(17,17,17,.04), 0 0 0 1px rgba(17,17,17,.04);
  --shadow-md: 0 4px 12px rgba(17,17,17,.06), 0 0 0 1px rgba(17,17,17,.05);
  --shadow-lg: 0 12px 32px rgba(17,17,17,.10), 0 0 0 1px rgba(17,17,17,.06);
  --shadow-pop: 0 8px 24px rgba(17,17,17,.12);

  /* Motion */
  --ease-out: cubic-bezier(0.2, 0.7, 0.2, 1);
  --ease-spring: cubic-bezier(0.32, 0.72, 0, 1);
  --d-1: 120ms; --d-2: 200ms; --d-3: 320ms;
}

[data-theme="dark"] {
  --bg: #0E0E0E;
  --surface: #161616;
  --surface-2: #1E1E1E;
  --border: #262626;
  --border-strong: #F5F5F5;
  --text: #F5F5F5;
  --text-muted: #9A9A93;
  --text-dim: #5E5E58;
  --accent: #5B8DEF;
  --accent-soft: rgba(91,141,239,.14);
  --good: #4ADE80;
  --good-soft: rgba(74,222,128,.10);
  --warn: #FBBF24;
  --warn-soft: rgba(251,191,36,.10);
  --bad: #F87171;
  --bad-soft: rgba(248,113,113,.10);
  --map-overlay: rgba(22,22,22,.88);
  --shadow-sm: 0 1px 2px rgba(0,0,0,.4), 0 0 0 1px rgba(255,255,255,.04);
  --shadow-md: 0 4px 12px rgba(0,0,0,.5), 0 0 0 1px rgba(255,255,255,.05);
  --shadow-lg: 0 12px 32px rgba(0,0,0,.6), 0 0 0 1px rgba(255,255,255,.06);
}

* { box-sizing: border-box; }
html, body {
  font-feature-settings: "ss01","cv11","tnum","cv05";
}
body {
  margin: 0;
  font-family: var(--font-sans);
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
::selection { background: var(--accent-soft); color: var(--text); }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 999px; border: 2px solid var(--bg); }
::-webkit-scrollbar-thumb:hover { background: var(--text-dim); }

/* ====== TOPBAR ====== */
.topbar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: var(--s-5);
  padding: var(--s-3) var(--s-5);
  border-bottom: 1px solid var(--border);
  background: var(--bg);
  height: 60px;
}
.brand { display: flex; align-items: center; gap: var(--s-3); }
.brand-mark {
  width: 28px; height: 28px;
  display: grid; place-items: center;
  background: var(--text); color: var(--bg);
  border-radius: var(--r-1);
  font: 700 12px/1 var(--font-mono);
  letter-spacing: -0.02em;
}
.brand-text { font: 600 14px/1 var(--font-sans); letter-spacing: -0.01em; }
.brand-sub { font: 400 12px/1 var(--font-mono); color: var(--text-muted); }
.countdown {
  display: flex; align-items: baseline; gap: 6px;
  justify-self: center;
}
.countdown-num {
  font: 600 28px/1 var(--font-sans);
  letter-spacing: -0.03em;
  font-variant-numeric: tabular-nums;
  color: var(--text);
}
.countdown-label { font: 400 12px/1 var(--font-mono); color: var(--text-muted); }
.topnav { display: flex; gap: 4px; }
.nav-btn {
  font: 500 13px/1 var(--font-sans);
  color: var(--text-muted);
  background: transparent;
  border: 1px solid transparent;
  padding: 7px 12px;
  border-radius: var(--r-1);
  cursor: pointer;
  display: inline-flex; align-items: center; gap: 6px;
  transition: color var(--d-1) var(--ease-out), background var(--d-1) var(--ease-out), border-color var(--d-1) var(--ease-out);
}
.nav-btn:hover { color: var(--text); background: var(--surface-2); }
.nav-btn.is-active { color: var(--text); background: var(--surface); border-color: var(--border); box-shadow: var(--shadow-sm); }
.nav-btn.nav-icon { padding: 7px 9px; }
.nav-count {
  font: 600 11px/1 var(--font-mono);
  background: var(--text); color: var(--bg);
  padding: 2px 5px; border-radius: var(--r-1);
  font-variant-numeric: tabular-nums;
}

/* ====== LAYOUT ====== */
.layout {
  display: grid;
  grid-template-columns: 380px 1fr 460px;
  height: calc(100vh - 60px);
}
@media (max-width: 1400px) {
  .layout { grid-template-columns: 360px 1fr; }
  #detail {
    position: absolute; right: 0; top: 60px; bottom: 0;
    width: 460px; max-width: 92vw;
    background: var(--surface);
    border-left: 1px solid var(--border);
    box-shadow: var(--shadow-lg);
    transform: translateX(100%);
    transition: transform var(--d-3) var(--ease-spring);
    z-index: 50;
  }
  #detail.is-open { transform: translateX(0); }
}
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; height: auto; }
  #map-wrap { height: 50vh; }
}

/* ====== SIDEBAR ====== */
#sidebar {
  overflow-y: auto;
  border-right: 1px solid var(--border);
  padding: var(--s-3);
  background: var(--bg);
}
.filterbar {
  position: sticky; top: 0; z-index: 5;
  background: var(--bg);
  padding-bottom: var(--s-2);
  margin-bottom: var(--s-3);
  border-bottom: 1px solid var(--border);
}
.search-wrap { position: relative; margin-bottom: var(--s-2); }
#search {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 9px 12px 9px 34px;
  border-radius: var(--r-1);
  font: 400 13px/1 var(--font-sans);
  transition: border-color var(--d-1) var(--ease-out), box-shadow var(--d-1) var(--ease-out);
}
#search::placeholder { color: var(--text-dim); }
#search:focus {
  outline: none;
  border-color: var(--text);
  box-shadow: 0 0 0 3px rgba(17,17,17,.08);
}
.search-wrap::before {
  content: ''; position: absolute; left: 11px; top: 50%;
  transform: translateY(-50%); width: 14px; height: 14px;
  background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236B6B66' stroke-width='2' stroke-linecap='round'><circle cx='11' cy='11' r='7'/><path d='m21 21-4.3-4.3'/></svg>") no-repeat center / contain;
}
.filters { display: flex; flex-wrap: wrap; gap: 4px; }
.filters button {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  padding: 5px 11px;
  border-radius: var(--r-pill);
  cursor: pointer;
  font: 500 12px/1.4 var(--font-sans);
  transition: all var(--d-1) var(--ease-out);
}
.filters button:hover { color: var(--text); border-color: var(--text-dim); }
.filters button.is-active {
  background: var(--text); color: var(--bg); border-color: var(--text);
}
.sort-control {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: var(--s-3);
  font: 400 12px/1 var(--font-sans);
  color: var(--text-muted);
}
.sort-control select {
  background: transparent; color: var(--text);
  border: 1px solid var(--border);
  padding: 5px 22px 5px 9px;
  border-radius: var(--r-1);
  font: 500 12px/1 var(--font-sans);
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236B6B66' stroke-width='2' stroke-linecap='round'><path d='m6 9 6 6 6-6'/></svg>");
  background-repeat: no-repeat;
  background-position: right 6px center;
  background-size: 12px;
}

/* ====== LISTING CARD (new) ====== */
.lcard {
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: 12px;
  padding: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-2);
  margin-bottom: 6px;
  cursor: pointer;
  transition: border-color var(--d-1) var(--ease-out), background var(--d-1) var(--ease-out), box-shadow var(--d-1) var(--ease-out);
}
.lcard:hover { border-color: #C9C7BE; background: var(--surface-2); }
.lcard.is-selected {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-sm), 0 0 0 1px var(--border-strong);
}
.lcard-photo {
  position: relative;
  width: 96px; height: 96px;
  border-radius: var(--r-2);
  background: var(--surface-2) center/cover no-repeat;
  overflow: hidden;
  flex-shrink: 0;
}
.lcard-fav {
  position: absolute; top: 6px; right: 6px;
  width: 26px; height: 26px;
  background: var(--map-overlay);
  border: 0; border-radius: 999px;
  font-size: 13px; cursor: pointer;
  display: grid; place-items: center;
  color: var(--text-muted);
  backdrop-filter: blur(8px);
  transition: color var(--d-1) var(--ease-out);
}
.lcard-fav:hover, .lcard-fav.is-on { color: var(--bad); }
.lcard-fit {
  position: absolute; bottom: 6px; left: 6px;
  background: var(--text); color: var(--bg);
  font: 600 11px/1 var(--font-mono);
  padding: 3px 6px; border-radius: var(--r-1);
  font-variant-numeric: tabular-nums;
}
.lcard-fit[data-tier="good"] { background: var(--good); color: white; }
.lcard-fit[data-tier="warn"] { background: var(--warn); color: white; }
.lcard-fit[data-tier="bad"]  { background: var(--bad);  color: white; }
.lcard-body { min-width: 0; display: flex; flex-direction: column; gap: 3px; padding: 2px 0; }
.lcard-row1 {
  display: flex; justify-content: space-between;
  align-items: baseline; gap: 8px;
}
.lcard-name {
  margin: 0;
  font: 600 14px/1.3 var(--font-sans);
  letter-spacing: -0.01em;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.lcard-rent {
  font: 500 14px/1 var(--font-mono);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
  flex-shrink: 0; color: var(--text);
}
.lcard-zone {
  color: var(--text-muted);
  font: 400 12px/1.4 var(--font-sans);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.lcard-row3 { display: flex; gap: 10px; margin-top: 4px; flex-wrap: wrap; }
.lcard-stat {
  font: 500 12px/1 var(--font-mono);
  color: var(--text);
  font-variant-numeric: tabular-nums;
}
.lcard-stat .lcard-k {
  color: var(--text-dim);
  margin-right: 3px;
  font-weight: 400;
}
.lcard-pet { color: var(--good); }

/* ====== MAP ====== */
#map-wrap { position: relative; }
#map { height: 100%; background: var(--surface-2); }
.leaflet-popup-content-wrapper {
  background: var(--surface); color: var(--text);
  border-radius: var(--r-2);
  box-shadow: var(--shadow-pop);
  padding: 4px;
}
.leaflet-popup-tip { background: var(--surface); }
.leaflet-control-attribution {
  background: var(--map-overlay) !important;
  font: 400 10px/1.4 var(--font-mono) !important;
  color: var(--text-muted) !important;
  padding: 2px 6px !important;
}
.pricepin-wrap { background: transparent !important; border: 0 !important; }
.pricepin {
  background: var(--surface); color: var(--text);
  padding: 4px 8px; border-radius: 999px;
  font: 600 12px/1 var(--font-mono);
  font-variant-numeric: tabular-nums;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  white-space: nowrap; cursor: pointer;
  transition: transform var(--d-1) var(--ease-out), box-shadow var(--d-1) var(--ease-out);
}
.pricepin:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.pricepin.is-selected {
  background: var(--text); color: var(--bg);
  border-color: var(--text);
}
.pricepin--bad { color: var(--bad); }
.pricepin--warn { color: var(--warn); }
.pricepin--good { color: var(--good); }
.legend {
  position: absolute; top: 12px; right: 12px;
  background: var(--map-overlay);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  padding: 10px 12px;
  border-radius: var(--r-2);
  font: 400 12px/1.6 var(--font-sans);
  z-index: 1000;
  box-shadow: var(--shadow-sm);
}
.legend-head {
  font: 500 11px/1 var(--font-sans);
  color: var(--text-muted);
  margin-bottom: 4px;
}
.legend .row { display: flex; align-items: center; gap: 6px; }
.legend .dot { width: 8px; height: 8px; border-radius: 50%; }

/* ====== DETAIL PANEL ====== */
#detail {
  overflow-y: auto;
  border-left: 1px solid var(--border);
  padding: var(--s-4) var(--s-5);
  background: var(--bg);
}
#detail .placeholder {
  color: var(--text-muted); text-align: center;
  margin-top: 80px;
  font: 400 13px/1.6 var(--font-sans);
}
#detail .placeholder strong {
  display: block; font: 500 15px/1.4 var(--font-sans);
  color: var(--text); margin-bottom: 4px;
}
.detail-hero {
  position: relative;
  margin: calc(var(--s-4) * -1) calc(var(--s-5) * -1) var(--s-4);
}
.detail-hero-photo {
  height: 240px;
  background: var(--surface-2) center/cover no-repeat;
}
.detail-hero-bar {
  position: absolute; left: 0; right: 0; bottom: 0;
  padding: var(--s-5);
  background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,.7) 100%);
  display: flex; justify-content: space-between; align-items: flex-end;
  color: white; gap: var(--s-3);
}
.detail-h1 {
  margin: 0;
  font: 600 22px/1.2 var(--font-sans);
  letter-spacing: -0.02em;
  color: white;
}
.detail-addr {
  font: 400 12px/1.4 var(--font-mono);
  opacity: .9; margin-top: 4px;
}
.detail-tldr {
  font: 400 14px/1.6 var(--font-sans);
  color: var(--text-muted); margin: 0 0 var(--s-4);
}
.tldr-rent {
  font: 600 26px/1 var(--font-sans);
  color: var(--text);
  letter-spacing: -0.03em;
  font-variant-numeric: tabular-nums;
}
.tldr-unit { font-size: 14px; color: var(--text-muted); margin-right: 8px; }
.tldr-sep { color: var(--text-dim); margin: 0 6px; }
.tldr-stat b {
  color: var(--text); font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.photo-strip {
  display: flex; gap: 4px;
  overflow-x: auto;
  margin: 0 calc(var(--s-5) * -1) var(--s-4);
  padding: 0 var(--s-5);
  scrollbar-width: none;
}
.photo-strip::-webkit-scrollbar { display: none; }
.photo-strip img {
  height: 120px; width: auto; flex-shrink: 0;
  border-radius: var(--r-2);
  object-fit: cover;
  background: var(--surface-2);
}
#detail h3 {
  font: 500 13px/1.4 var(--font-sans);
  color: var(--text);
  margin: var(--s-5) 0 var(--s-2);
  letter-spacing: -0.005em;
}
#detail h3 + * { margin-top: 0; }
#detail p { font: 400 13px/1.6 var(--font-sans); margin: 4px 0; }
#detail ul { padding-left: 16px; margin: 4px 0; font: 400 13px/1.6 var(--font-sans); }
#detail .pros li { color: var(--good); }
#detail .cons li { color: var(--bad); }

/* External link strip — text not buttons */
#detail .external {
  display: flex; gap: var(--s-3); flex-wrap: wrap;
  margin-top: var(--s-4);
  padding-top: var(--s-3);
  border-top: 1px solid var(--border);
}
#detail .external a {
  color: var(--text-muted);
  text-decoration: none;
  font: 500 12px/1 var(--font-sans);
  transition: color var(--d-1) var(--ease-out);
}
#detail .external a::after { content: ' ↗'; opacity: .5; }
#detail .external a:hover { color: var(--accent); }

/* Cost decoder — flat dl, not boxed table */
.cost-table {
  width: 100%; border-collapse: collapse;
  font: 400 13px/1.6 var(--font-sans);
  margin: var(--s-2) 0;
}
.cost-table td {
  padding: 6px 0;
  border-bottom: 1px solid var(--border);
}
.cost-table td:first-child { color: var(--text-muted); }
.cost-table td:last-child {
  text-align: right;
  font: 500 13px/1.6 var(--font-mono);
  font-variant-numeric: tabular-nums;
  color: var(--text);
}
.cost-table tr.total td {
  border-bottom: none; border-top: 1px solid var(--text);
  padding-top: 10px;
  font-weight: 600; color: var(--text); font-size: 14px;
}
.cost-table tr.total td:first-child { color: var(--text); }

.notes-area {
  width: 100%; min-height: 80px;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 10px 12px;
  border-radius: var(--r-2);
  font: 400 13px/1.5 var(--font-sans);
  resize: vertical;
  transition: border-color var(--d-1) var(--ease-out), box-shadow var(--d-1) var(--ease-out);
}
.notes-area:focus {
  outline: none; border-color: var(--text);
  box-shadow: 0 0 0 3px rgba(17,17,17,.08);
}
.action-row { display: flex; gap: 4px; flex-wrap: wrap; margin: var(--s-2) 0; }
.action-row button {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 6px 11px;
  border-radius: var(--r-1);
  cursor: pointer;
  font: 500 12px/1 var(--font-sans);
  transition: all var(--d-1) var(--ease-out);
}
.action-row button.is-on {
  background: var(--text); color: var(--bg); border-color: var(--text);
}
.action-row button:hover:not(.is-on) { border-color: var(--text-dim); }

/* ====== AVOID BLOCK ====== */
.avoid-block {
  margin-top: var(--s-5);
  padding: var(--s-3);
  border: 1px solid var(--bad);
  border-radius: var(--r-2);
  background: var(--bad-soft);
}
.avoid-block h3 {
  margin: 0 0 var(--s-2);
  font: 500 12px/1 var(--font-sans);
  color: var(--bad);
}

/* ====== SHEETS (replace modals) ====== */
.sheet {
  position: fixed; top: 0; right: 0; bottom: 0;
  width: min(720px, 92vw);
  background: var(--surface);
  border-left: 1px solid var(--border);
  box-shadow: var(--shadow-lg);
  transform: translateX(100%);
  transition: transform var(--d-3) var(--ease-spring);
  z-index: 100;
  overflow-y: auto;
  padding: var(--s-5);
}
.sheet.is-open { transform: translateX(0); }
.sheet-backdrop {
  position: fixed; inset: 0;
  background: rgba(17,17,17,.32);
  opacity: 0; pointer-events: none;
  transition: opacity var(--d-2) var(--ease-out);
  z-index: 99;
}
.sheet-backdrop.is-open { opacity: 1; pointer-events: auto; }
.sheet-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--s-4);
  padding-bottom: var(--s-3);
  border-bottom: 1px solid var(--border);
}
.sheet-title {
  margin: 0;
  font: 600 18px/1.2 var(--font-sans);
  letter-spacing: -0.015em;
}
.sheet-close {
  width: 32px; height: 32px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--r-1);
  cursor: pointer;
  display: grid; place-items: center;
  color: var(--text-muted);
  transition: all var(--d-1) var(--ease-out);
}
.sheet-close:hover { color: var(--text); border-color: var(--text-dim); }

/* ====== COMPARE TABLE ====== */
.cmp-table {
  width: 100%; border-collapse: collapse;
  font: 400 13px/1.5 var(--font-sans);
}
.cmp-table th, .cmp-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  text-align: left; vertical-align: top;
}
.cmp-table th {
  background: var(--bg);
  font: 500 12px/1.4 var(--font-sans);
  color: var(--text-muted);
  position: sticky; top: 0;
}
.cmp-table .cell-good { color: var(--good); font-weight: 500; }
.cmp-table .cell-bad { color: var(--bad); }
.cmp-table img {
  width: 80px; height: 56px;
  object-fit: cover; border-radius: var(--r-2);
}

/* ====== TIMELINE ====== */
.tl-phase {
  margin-bottom: var(--s-5);
  padding: var(--s-4);
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--text);
  border-radius: var(--r-2);
}
.tl-phase h3 {
  margin: 0 0 var(--s-1);
  color: var(--text);
  font: 600 15px/1.3 var(--font-sans);
  letter-spacing: -0.01em;
}
.tl-phase .range {
  color: var(--text-muted);
  font: 400 12px/1.4 var(--font-mono);
  margin-bottom: var(--s-3);
}
.tl-item {
  display: flex; gap: var(--s-3); align-items: flex-start;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}
.tl-item:last-child { border-bottom: none; }
.tl-item input[type=checkbox] { margin-top: 4px; cursor: pointer; accent-color: var(--text); }
.tl-item .when {
  color: var(--text-muted);
  font: 400 12px/1.4 var(--font-mono);
  min-width: 80px;
}
.tl-item .what { flex: 1; font: 400 13px/1.5 var(--font-sans); }
.tl-item.is-done .what { text-decoration: line-through; color: var(--text-muted); }
.tl-item .urg {
  font: 500 10px/1 var(--font-mono);
  padding: 2px 5px; border-radius: var(--r-1);
}
.tl-item .urg-critical { color: var(--bad); background: var(--bad-soft); }
.tl-item .urg-high { color: var(--warn); background: var(--warn-soft); }
.tl-item .urg-normal { color: var(--text-muted); }

/* ====== CMD+K ====== */
.cmdk {
  position: fixed; top: 15vh; left: 50%;
  transform: translateX(-50%);
  width: min(560px, 92vw);
  background: var(--surface);
  border-radius: var(--r-3);
  box-shadow: var(--shadow-lg);
  z-index: 200;
  overflow: hidden;
}
.cmdk-input {
  width: 100%; padding: 16px 20px;
  background: transparent;
  border: 0; border-bottom: 1px solid var(--border);
  font: 400 15px/1.4 var(--font-sans);
  color: var(--text);
}
.cmdk-input:focus { outline: none; }
.cmdk-list { max-height: 50vh; overflow-y: auto; padding: 6px; }
.cmdk-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 14px;
  border-radius: var(--r-1);
  cursor: pointer;
  font: 400 13px/1.4 var(--font-sans);
}
.cmdk-item.is-active { background: var(--surface-2); }
.cmdk-item .kbd {
  font: 500 11px/1 var(--font-mono);
  color: var(--text-muted);
}

/* ====== FOCUS ====== */
:focus { outline: none; }
button:focus-visible, a:focus-visible, select:focus-visible,
.lcard:focus-visible, [role="button"]:focus-visible, input:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: var(--r-1);
}

/* ====== PRINT ====== */
@media print {
  body { background: #fff; color: #000; }
  .topbar, .filters, #map-wrap, .sheet, .cmdk, .action-row { display: none !important; }
  .layout { display: block; height: auto; }
  #sidebar { border: none; padding: 0; }
  .lcard { border-color: #ccc; box-shadow: none; break-inside: avoid; }
}
</style>
```

Plus, in JS: switch the Leaflet tile to CARTO Voyager (see Map section above), update the marker creation to emit `.pricepin` divIcons, rename `.show` → `.is-open` on detail/modal, swap `.card` → `.lcard` class names, swap `.modal` containers for `.sheet` + `.sheet-backdrop`.

---

## 3 patterns I DECIDED AGAINST (and why)

1. **Bento-grid hero section** (Vercel/Apple-style multi-card hero). Tempting because it's the dominant 2025-2026 aesthetic, but this app has no "hero" use case — it's a tool, not a marketing page. The home view IS the working view. Forcing a bento intro would mean adding a screen you'd skip every time. Real research tools (Linear, Notion, Reflect) all open directly into work.

2. **Gradient mesh accents / glassmorphism backgrounds.** Padmapper, Zillow, and Streeteasy all use flat surfaces. Glassmorphic backgrounds on listing tools fight the map (which is itself colorful and information-dense). The one gradient I kept is the photo-overlay gradient on the detail hero — functional, not decorative. Decorative gradients on a research tool age in months; the current site has a `linear-gradient` on the header that already feels dated and I deleted it.

3. **Animated fit-score donut / circular progress ring** on each card. The classic "make data look smart" move. Reasons against: (a) Airbnb/Padmapper/Zillow show price, not score, on cards because price is what the user is actually deciding on; (b) a 96px card with a 28px ring eats real estate that should hold a photo; (c) the score is already legible as a 2-digit number in a colored chip — that's the same info pattern as Rotten Tomatoes scores, which has been proven to scan instantly. A donut is dressing that adds 200ms of "what am I looking at" per card across a 60-card list.
