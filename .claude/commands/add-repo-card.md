---
description: Add or refresh a repository card on the quickglobe portfolio page
argument-hint: [repo name, e.g. blob-squish]
allowed-tools: Read, Edit, Bash, mcp__github__search_repositories, mcp__github__list_commits
---

You are adding (or refreshing) a repository card on the `quickglobe` portfolio
page (`index.html`). The full reference is in `ADDING-CARDS.md` — read it if you
need detail. Target repo: **$ARGUMENTS** (if empty, ask which repo).

Do this:

1. **Fetch the real last-push date.** Call `mcp__github__search_repositories`
   with query `user:quickglobe` (or `list_commits` on the repo) and read the
   target repo's `pushed_at`. Use the date portion only (`YYYY-MM-DD`). Never
   guess or hard-code a relative string like "2w" — the page computes that.
   Also confirm the repo is **public**; skip private repos (e.g. `Hello-World`).

2. **Read `index.html`** and locate the `REPOS` array in the bottom `<script>`.

3. **Edit `REPOS`:**
   - If the repo is already listed, just update its `updated` ISO date.
   - If it's new, append an entry (or insert it at the desired position) with
     the next sequential `code` (`R-04`, …), renumbering `code`s if you
     inserted in the middle. Fill `title`, `cat`, `desc` (from the repo's
     GitHub description, lightly cleaned), `lang`, `icon` (an existing key in
     `ICONS`, or add a new 48×48 single-stroke SVG icon), and `url` (the GitHub
     repo page).

4. **Sanity check:** the meta-strip count and "updated" value, and all `R-0x`
   badges, are derived automatically — don't hand-edit them.

5. Summarize what changed and remind the user to commit/push and preview via
   the githack link from `ADDING-CARDS.md`. Do not commit or push unless asked.
