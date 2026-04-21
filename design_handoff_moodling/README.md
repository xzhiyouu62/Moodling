# Handoff: Moodling — Frontend Redesign

## Overview
Moodling is a Korean music recommender that matches tracks to a user's emotional state. This handoff covers a complete frontend redesign of the app — three distinct pages (Home, Form, Results) — with a warm, editorial, independent-brand aesthetic.

The existing backend (`/api/recommend`) is already wired and returns `{ recommendations[], explanations[], user_state }`. This redesign replaces the existing `frontend/index.html` and `static/css/style.css`.

---

## About the Design Files
`Moodling v2.html` is a **high-fidelity design reference** built in plain HTML + React (Babel, no bundler). It shows final colors, typography, spacing, layout, and interactions.

Your task is to **recreate this design in the existing codebase** — using whatever stack the project already uses (Flask templates, React, etc.) — not to ship the HTML file directly. Use the HTML prototype as a pixel-level reference.

---

## Fidelity
**High-fidelity.** Colors, type, spacing, and interactions are final. Recreate as closely as possible. The only things that are mock/placeholder:
- Song data (use real API response)
- The "loading" spinner replaces a real fetch

---

## Design Tokens

### Colors
```
--bg:     #fdfaf6   /* warm off-white paper */
--paper:  #f5f0e8   /* slightly darker warm surface */
--text:   #111111   /* near-black */
--muted:  #7a7570   /* secondary text */
--faint:  #c8c3bc   /* disabled / decorative */
--border: #e0dbd4   /* all borders and dividers */
```

### Typography
```
Font 1: "DM Serif Display" (Google Fonts) — italic, weight 400
Font 2: "DM Sans" (Google Fonts) — weights 300, 400, 500, 600
```

| Role           | Font              | Size   | Weight | Style   | Tracking     |
|----------------|-------------------|--------|--------|---------|--------------|
| Brand mark     | DM Serif Display  | 17px   | 400    | italic  | -0.01em      |
| Hero headline  | DM Serif Display  | clamp(52px,8vw,80px) | 400 | italic | -0.02em |
| Page title     | DM Serif Display  | 34–38px | 400  | normal/italic | -0.01em |
| Question label | DM Serif Display  | 20px   | 400    | italic  | normal       |
| Song title     | DM Serif Display  | 26px   | 400    | normal  | normal       |
| Body / labels  | DM Sans           | 12–14px | 300–500 | normal | 0.03–0.10em |
| Caps / nav     | DM Sans           | 10–11px | 500–600 | normal | 0.08–0.10em |

### Spacing (consistent base)
- Page padding: `40px 56px` (form/results), `32px 48px` (home)
- Side panel width: `240px`
- Section gap: `44px` above headers, `32px` between questions
- Question bottom padding: `32px` with `1px solid #e0dbd4` border

### Input: Range Slider
- Track height: `1px`, track color: gradient `#111 → <value>% → #e0dbd4`
- Thumb: `13×13px`, `border-radius: 0` (square), `background: #111`
- Thumb hover: `transform: scale(1.2)`

### Input: Pill Button (selected)
```
border: 1px solid #111111
background: #111111
color: #ffffff
```
### Input: Pill Button (unselected)
```
border: 1px solid #e0dbd4
background: transparent
color: #7a7570
padding: 7px 16px
```

---

## Screens & Views

### 1. Home Page (`/`)

**Layout:**
- Full viewport height (`100vh`)
- Flex column, `padding: 32px 48px`
- Content justified to `flex-end` (bottom-anchored)
- Max content width: `640px`

**Elements:**
| Element | Details |
|---|---|
| Brand mark top-left | `Moodling.` — DM Serif italic 17px, #111 |
| Top-right meta | `Korean Music Guide` + `01 — 03` — DM Sans 10px uppercase, #c8c3bc, tracking 0.08–0.10em |
| Background decoration | Large `♪` character, DM Serif italic 360px, color `#e0dbd4`, absolute right edge, vertically centered |
| Hero headline | DM Serif italic, clamp(52px,8vw,80px), `line-height: 0.93`, `letter-spacing: -0.02em`, `text-wrap: pretty` — "Shape your / mood with / music." |
| Thin rule | `48px wide × 1px`, `background: #e0dbd4`, `margin-bottom: 22px` |
| Subtitle | DM Sans 14px, #7a7570, weight 300, `line-height: 1.7`, max-width 340px |
| Begin button | Inline with subtitle row, right side. DM Serif italic 19px, #111, no border/bg. Arrow `→` translates `+4px` on hover |
| Footer rule | `border-top: 1px solid #e0dbd4`, `margin-top: 32px`, `padding-top: 20px` |
| Footer text | `© 2026 Moodling Project · NCCU` — DM Sans 11px, #c8c3bc. Right: Analytics + History links |

**Page entrance animation:** `fadeUp` — `opacity: 0 → 1`, `translateY: 14px → 0`, duration `0.4s`, `cubic-bezier(.22,1,.36,1)`. Staggered children: delays `0s, 0.05s, 0.12s, 0.20s, 0.28s, 0.36s`.

---

### 2. Form Page (`/form` or hash state)

**Layout:**
- Full viewport height, `display: flex`, `overflow: hidden`
- Left: **Side Panel** (240px fixed, `border-right: 1px solid #e0dbd4`)
- Right: scrollable content area, `padding: 40px 56px 64px`

**Side Panel:**
- `padding: 32px 28px`
- Brand mark (`Moodling.`) as a back-navigation button
- `1px solid #e0dbd4` horizontal rule
- Label: `"Your session"` — DM Sans 10px uppercase, #c8c3bc, tracking 0.10em
- Body copy below: DM Sans 12px, #c8c3bc, weight 300, explaining the app
- Bottom: page indicator `02 — 03` — DM Sans 10px, #c8c3bc

**Main area header:**
- H2: DM Serif 34px, `letter-spacing: -0.01em` — "How are you / feeling right now?"
- Subtitle: DM Sans 13px, #7a7570, weight 300

**Questions (5 total):**
Each question row:
- `padding-bottom: 32px`, `margin-bottom: 32px`, `border-bottom: 1px solid #e0dbd4`
- Number label: DM Sans 10px, #c8c3bc, tracking 0.08em (e.g. "01")
- Question text: DM Serif italic 20px, #111, `line-height: 1.1`
- Input below

| # | Question | Input Type |
|---|---|---|
| 01 | How do you feel today? | Slider (1–10), lo="Sad" hi="Happy" |
| 02 | What's your stress level? | Slider (1–10), lo="Chill" hi="Busy" |
| 03 | How's your energy? | Slider (1–10), lo="Tired" hi="Energetic" |
| 04 | The atmosphere outside. | Pills: Sunny / Cloudy / Rainy / Snowy |
| 05 | What time is it? | Pills: Morning / Afternoon / Evening / Night |

**Submit button (right-aligned):**
```
background: #111111
color: #ffffff
padding: 14px 36px
font: DM Sans 12px, weight 500, uppercase, tracking 0.08em
text: "Ask Moodling →"
hover: opacity 0.8
```

**Loading state:** Centered spinner (`36×36px` circle, `border: 1px solid #e0dbd4`, top border `#111`, spin animation), below: DM Serif italic 20px "Moodling is thinking…" at 50% opacity.

**API call:** `POST /api/recommend` with `{ mood, stress, fatigue (=energy), weather (lowercase), time_preference (lowercase snake_case) }`. Response: `{ recommendations[], explanations[], user_state }`.

---

### 3. Results Page (`/results` or hash state)

**Layout:** Same two-column shell as Form Page.

**Side Panel (results state):**
- Brand mark → navigates back to Home
- Label: `"Session result"`
- Table of submitted values: Mood, Stress, Energy, Atmosphere, Time — each row `padding: 8px 0`, `border-bottom: 1px solid #e0dbd4`, DM Sans 12px, label #7a7570, value #111
- Page indicator: `03 — 03`

**Main area header:**
- Date stamp: DM Sans 10px uppercase, #c8c3bc, e.g. "Monday, April 21"
- H2: DM Serif italic 38px — "Curated / Selection." (`line-height: 1.0`)
- Subtitle: DM Sans 13px, #7a7570, weight 300 — "3 tracks matched to your mood right now."

**Song cards (one per recommendation):**
Each: `padding: 24px 0`, `border-bottom: 1px solid #e0dbd4`
3-column grid: `44px | 1fr | 40px`

| Column | Content |
|---|---|
| Rank | DM Serif italic 22px, #c8c3bc |
| Info | Title (DM Serif 26px, #111) + romanization (DM Sans 11px italic, #c8c3bc) + artist/meta (DM Sans 12px, #7a7570) + "Why this?" toggle button |
| Play | 38×38px square button, `border: 1px solid #e0dbd4`. Hover: `background: #111, color: #fff` |

**"Why this?" button:**
```
border: 1px solid #e0dbd4
padding: 4px 12px
font: DM Sans 11px, tracking 0.04em
color: #7a7570
hover: border-color #111, color #111
```
On click: expands explanation panel below the card row (padded left 44px to align with info column):
```
padding: 14px 18px
background: #f5f0e8
border-left: 2px solid #e0dbd4
font: DM Serif italic 13px, #7a7570, line-height 1.8
content: `"<explanation text>"`
animation: fadeIn .25s ease
```

**Footer:**
- `border-top: 1px solid #e0dbd4`, `margin-top: 44px`, `padding-top: 32px`
- Left: `© 2026 Moodling Project · NCCU` — DM Sans 11px, #c8c3bc
- Right: "New session →" button — DM Sans 11px, uppercase, #7a7570, border `1px solid #e0dbd4`. Hover: border/text → #111

---

## Interactions & Behavior

### Page Navigation
- Home → Form: click "Begin →"
- Form → Home: click brand mark in side panel
- Form → Results: submit form (POST `/api/recommend`)
- Results → Home: click brand mark or "New session →"
- Persist last visited page in `localStorage` key `moodling_page`

### Animations
```css
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
/* duration: 0.4s, easing: cubic-bezier(.22,1,.36,1) */
/* Note: do NOT use fill-mode: both with staggered delays on song cards
   as this holds opacity:0 during the delay. Apply animation without delay
   to card containers. */
```

### Grain Texture (optional)
SVG feTurbulence overlay, fixed position, `opacity: 0.04`, `z-index: 9999`, `pointer-events: none`. Toggle via user preference.

---

## API Integration Notes
- Existing endpoint: `POST /api/recommend`
- Map form fields:
  - `mood` → `mood` (int 1–10)
  - `stress` → `stress` (int 1–10)
  - `energy` → `fatigue` (int 1–10) ← note the key rename
  - `weather` → `weather` (lowercase string: "sunny" / "cloudy" / "rainy" / "snowy")
  - `time` → `time_preference` (lowercase: "morning" / "afternoon" / "evening" / "night")
- Response structure:
  ```json
  {
    "recommendations": [{ "title": "", "artist": "", "album": "", "year": 0, "youtube_url": "" }],
    "explanations": [{ "song_title": "", "explanation": "" }],
    "user_state": { "mood": 5, ... }
  }
  ```
- History: save each session to `localStorage` key `moodling_history` (array, max 10 entries)

---

## Files in This Package
| File | Purpose |
|---|---|
| `Moodling v2.html` | Full interactive prototype — primary design reference |
| `README.md` | This document |
