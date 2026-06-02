# Handoff: build the `quickglobe.github.io` hub landing page

## Goal
Turn this repo (`quickglobe/quickglobe.github.io`, the GitHub Pages **user
site** served at the domain root `https://quickglobe.github.io/`) into a
curated **hub / portfolio landing page** that links to my deployed projects —
and, as a side effect, fix the Safari Favourites icon bug described below.

## Why this repo exists (the bug it also fixes)
iOS Safari has two separate icon-fetch paths:
- **Add to Home Screen / share tray** parses the loaded page's relative
  `<link rel="apple-touch-icon">` — this already works for each project.
- **Favourites / Start-page grid** uses a background fetcher that ignores the
  page and requests icons only from the **domain root**:
  `https://quickglobe.github.io/apple-touch-icon.png` and `/favicon.ico`.

My projects live on subpaths (`/playground/`, `/Cheat-Sheets/`) and there was
no user-site repo, so the root 404'd and Favourites showed grey letter tiles.
(Proof: `blob-squish` shows its real icon because it's on its own domain
`blob-squish.com`.) This repo *is* that domain root, so serving an icon set
here fixes the Favourites grid for every subpath project at once.

Consequence to remember: all subpath projects **share** this one root icon on
the Favourites grid — they can't have distinct Favourites icons while sharing
the domain. That's why the root gets its own **umbrella** icon (not the
Playground "P").

## What to build
A single static `index.html` at the repo root: a hub with one card per live
project. No build step, vanilla HTML/CSS/JS.

Cards to include (skip anything private/undeployed):
- **Playground** -> `./playground/`  (experiments index)
- **Cheat Sheets** -> `./Cheat-Sheets/`  (note the capitalization + hyphen; it's
  served at `https://quickglobe.github.io/Cheat-Sheets/`)
- **Blob Squish** -> `https://blob-squish.com`  (external, own domain)
- Do NOT list `Hello-World` (private).

Open question for the user before finalizing: curated cards only (recommended),
or also an auto-generated section that lists all public repos via
`api.github.com/users/quickglobe/repos` (subject to ~60 req/hr unauthenticated
rate limit)? Default to curated unless told otherwise.

## Files this repo must contain at its root
- `index.html` (the hub)
- `apple-touch-icon.png` (180x180, RGB, **no alpha**, flattened onto a solid bg)
- `favicon.ico` (multi-res 16/32/48), `favicon.svg`
- `favicon-16x16.png`, `favicon-32x32.png`, `favicon-48x48.png`
- `android-chrome-192x192.png`, `android-chrome-512x512.png`
- `site.webmanifest`, `browserconfig.xml`

The `<head>` icon block + `theme-color` meta, all with **relative** hrefs
(at the domain root, relative resolves correctly; still avoid leading `/`).

## Design conventions (match the Playground landing page)
Lift the look from `playground/index.html`. Ask the user to grant this session
access to the `quickglobe/playground` repo so you can copy its card CSS and
existing icon set as a starting point. Key rules (from playground's CLAUDE.md):
- **No emoji** anywhere (HTML/CSS/JS) — plain text labels only.
- **Relative asset paths only** (`favicon.svg`, never `/favicon.svg`).
- **Dark mode follows OS** via `prefers-color-scheme`; **no manual toggle**.
- Cards use the **Lisse squircle `clip-path`** pattern: border via a wrapper
  div whose background shows through padding (CSS borders get clipped by the
  squircle); depth via `filter: drop-shadow()` not `box-shadow`; hover lift via
  `translate()` only (no rotate). Gate `:hover`/`:active` behind
  `@media (hover: hover) and (pointer: fine)` so touch devices don't get sticky
  hover.
- Equal-height grid cards: the inner card must be `height: 100%` inside its
  frame wrapper, or short cards show a phantom dark band ("drop shadow") on
  desktop. See playground CLAUDE.md "Framed cards in an equal-height grid".

## Umbrella favicon (new icon, not the Playground P)
Hand-author `favicon.svg` on a `512x512` viewBox, rounded-square style
`rx="115"` like the other project icons, themed to represent the whole site
(suggest a globe/orbit mark to echo "quickglobe", or whatever the user
prefers — confirm colors with them). Then generate rasters with `cairosvg` +
`pillow` (available via pip):
- `favicon-16x16.png`, `favicon-32x32.png`, `favicon-48x48.png`
- `apple-touch-icon.png` 180x180 — render and **flatten onto the solid bg
  color** so iOS's rounded mask has no transparent/black corners
- `favicon.ico` — render at 256, save with `sizes=[(16,16),(32,32),(48,48)]`
- `android-chrome-192x192.png`, `android-chrome-512x512.png`

## Decisions to confirm with the user up front
1. Umbrella icon concept + color palette.
2. Curated-only vs. curated + auto repo list.
3. Whether the hub should also have a short intro/tagline header.

## Setup + verification
1. Repo must be named exactly `quickglobe.github.io` on the `quickglobe`
   account (already done if you're reading this here).
2. Settings -> Pages -> Deploy from branch -> `main` / root. Wait for deploy.
3. Verify `https://quickglobe.github.io/apple-touch-icon.png` returns the
   umbrella icon directly.
4. Preview the branch before merge via raw.githack (single self-contained file):
   `https://raw.githack.com/quickglobe/quickglobe.github.io/<branch>/index.html`
   Put the bare URL on its own line so the phone client auto-links it. Add
   `?v=N` cache-buster if it looks stale.
5. Device check on iPhone for the actual fix: in Safari, **remove the existing
   Playground favourite and re-add it** (Safari caches favourite icons hard, so
   in-place refresh won't pick it up) — it should now show the umbrella icon.
   The same applies to Cheat Sheets.
6. Headless/desktop can verify layout, dark mode, and card geometry before the
   device check.

## Working style
Keep a PR open and iterate on the same branch until confirmed working on
device; merge only once verified. End with the clickable githack preview link
on its own line.
