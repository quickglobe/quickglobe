# quickglobe

This repo (`quickglobe/quickglobe`) serves the **portfolio landing page** at
the domain root — a single static `index.html`, no build step, vanilla
HTML/CSS/JS. It is also the GitHub profile repo.

## Layout
- `index.html` — the whole page. Repository cards are data-driven from the
  `REPOS` array in the bottom `<script>`.
- `ADDING-CARDS.md` — how to add / reorder / refresh repository cards. **Read
  this before editing the card list.**
- `.claude/commands/add-repo-card.md` — `/add-repo-card <repo>` slash command
  that fetches the real last-push date via GitHub and edits `REPOS` for you.
- `favicon.*`, `apple-touch-icon.png`, `android-chrome-*.png`,
  `site.webmanifest`, `browserconfig.xml`, `quickglobe-avatar.svg` — the icon
  set (also fixes the iOS Safari Favourites grid; see `HANDOFF.md`). The mark
  is a **circular** blueprint globe with transparent corners.
- `tools/generate-icons.py` — regenerates the whole icon set from one source
  of truth (`python3 tools/generate-icons.py`, needs `cairosvg`+`pillow`).
  Edit the globe there, not the individual PNGs. `apple-touch-icon.png` is
  rendered on a solid paper square (no alpha) because iOS masks it into a
  rounded square — a literal circle isn't possible for the Favourites tile.
- `HANDOFF.md` — historical context for why this repo + icon set exist.

## Design (current: blueprint "Repository Index")
Ink-on-paper drafting aesthetic on a two-level blueprint grid. Key rules:
- **No emoji** anywhere. **Relative asset paths only** (`favicon.svg`, not `/favicon.svg`).
- Fonts: Space Grotesk (headings), Space Mono (mono UI), Jura (accent text).
- The grid fits the viewport: round `innerWidth / 26` to an integer column
  count, stretch `--cell` to fill, and snap the content column to whole cells.
  Minor + major grid lines are one repeating gradient per axis so they stay
  aligned. All card dimensions are multiples of `--cell`.
- Light theme only (the design has no dark mode).

## TODO
- **Meta strip:** a repo metadata strip (repository count + last-updated) used
  to sit below the header. It was removed for now (mobile layout needed more
  thought) — only the Profile button was kept, on its own under the header.
  Revisit whether to bring back a count / "last updated" indicator and how it
  should behave on narrow screens. (`relShort()` for relative dates is still in
  `index.html`, used by the card spec strips.)

## Updating the page
Adding a repo card is the common task — use `/add-repo-card` or follow
`ADDING-CARDS.md`. Always pull the `updated` ISO date from the repo's real
`pushed_at` via the GitHub MCP tools; never hard-code relative times.
