# Adding / updating repository cards

`index.html` is a single self-contained static page (no build step). Every
repository card is generated from the `REPOS` array in the `<script>` block
near the bottom of the file. To add, remove, reorder, or refresh a card you
edit that array — nothing else.

## The `REPOS` array

```js
const REPOS = [
  { id:"blob-squish", title:"blob-squish", cat:"Game", code:"R-01",
    desc:"Repository for blob-squish.com — a squishy little browser game.",
    lang:"HTML", updated:"2026-05-26", icon:"blob",
    url:"https://github.com/quickglobe/blob-squish" },
  ...
];
```

| Field     | Meaning | Notes |
|-----------|---------|-------|
| `id`      | Stable internal key | lowercase, unique; not shown to users |
| `title`   | Card heading | usually the repo name as it appears on GitHub |
| `cat`     | Category chip text | short, e.g. `Game`, `Experiments`, `Reference` |
| `code`    | Index badge (bottom-right) | `R-01`, `R-02`, … in display order |
| `desc`    | One-line description | the repo's GitHub description, lightly cleaned up |
| `lang`    | Primary language | shown in the spec strip |
| `updated` | **ISO date** (`YYYY-MM-DD`) of the repo's last push | relative time ("3d", "2w", "1mo") is computed at load — never hard-code "2w" |
| `icon`    | Which line icon to draw | one of the keys in `ICONS` (see below) |
| `url`     | Link target | the GitHub repo page; opens in a new tab |

Cards render in array order. The `code` badges and the meta-strip `repos`
count and `updated` value are all derived automatically, so keep `code`
sequential and order the array however you want the cards to appear.

## Steps to add a card for a new repo

1. **Get the real last-push date.** Do not guess. Use the GitHub MCP tools
   (`search_repositories` with `user:quickglobe`, or `list_commits` on the
   repo) and read the repo's `pushed_at` field. Use the date portion only,
   e.g. `2026-05-26`. The page converts it to "today / 3d / 2w / 5mo / 1y"
   relative to the visitor's clock, so it stays accurate over time.
2. **Pick or add an icon** (see below).
3. **Append an entry** to `REPOS` with the next `code` (`R-04`, …), or insert
   it where you want it and renumber the `code`s.
4. **Skip private repos** (e.g. `Hello-World` is private — do not list it).
5. Preview, then commit and push.

### Refreshing timestamps

There's nothing to refresh by hand for relative wording — it recomputes on
every load. You only edit `updated` when a repo gets a new push; set it to the
new `pushed_at` date.

## Icons

Icons are inline SVG (48×48 viewBox, single-stroke drafting style, 2px stroke)
stored in the `ICONS` map in the same `<script>`. Available keys:

- `globe` — orbit/globe mark (fallback, also the site avatar motif)
- `blob`  — blobby shape with two dots (blob-squish)
- `play`  — framed shapes / playground
- `sheets`— stacked sheets (reference / cheat-sheets)

To add a new icon, add a key to `ICONS` whose value is an SVG string using
`class="lineicon"`. Use `class="acc"` on a shape for a filled blue accent and
`class="acc-stroke"` for a blue outline. Keep it to a 48×48 viewBox so it
centers in the 64px slot. No emoji anywhere.

## Things you should NOT need to touch

- **The blueprint grid.** The grid size is fit to the viewport in the small
  IIFE in `<head>` (`TARGET = 26`): it rounds `innerWidth / 26` to an integer
  column count, then stretches `--cell` to fill exactly, and snaps the content
  column's width and left margin to whole cells so its edges land on grid
  lines. Minor + major lines are drawn as a **single repeating gradient per
  axis** so the bold (major) lines can't drift out of alignment with the minor
  ones while scrolling. Leave this alone unless changing the grid itself.
- **Card geometry** — widths, paddings, and min-heights are all multiples of
  `--cell`. On top of that, `snapBlocks()` rounds each top-level block's height
  (header, meta strip, every card, footer) up to a whole number of cells after
  layout and after web fonts load, so every block's top and bottom edge lands
  on a grid line. Blocks are marked with the `data-snap` attribute; cards get
  it automatically when created. You don't need to manage heights by hand.

## Preview

It's a single static file. Open `index.html` locally, or preview a branch via
githack on its own line so phone clients auto-link it:

```
https://raw.githack.com/quickglobe/quickglobe/<branch>/index.html
```

Add `?v=N` to bust a stale cache. Check desktop and a narrow (≈390px) width —
on mobile the column collapses to a 1-cell gutter each side.
