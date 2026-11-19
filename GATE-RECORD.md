# GATE RECORD — news-image-20261119 challenger

## Competition
- Competition: `news-image-20261119` — "Sum up 19 November's world news
  in one image" ($250; 1st $50, 2nd $30, 3rd $15, 4th–10th $5, 11th–50th $3).
- Date: Thursday 19 November 2026. Deadline: 21 Nov 2026 07:00 WIB
  (2026-11-21T00:00:00Z).
- Limits: PNG/JPEG, ≤ 1 MiB, ≤ 1024×1024, no network, two runs must
  write identical bytes. At most 10 submissions/day, 20 total.
- Attempts used / left: 1 used of 20 total, 19 left (live entry
  "Elegant Foundry" submitted 19 Nov ~19:34 WIB; this challenger is
  BUILD ONLY — never submitted, no submit command run).

## This entry
- Workdir: `/home/hatch/workspace/makefun/news-image-20261119-challenger/`
- Title: "THE WORLD IN ONE DAY — Thursday 19 November 2026"
- Content: 41 stories (3 illustrated heroes + 10 illustrated mains +
  28 numbered briefs), 7 regions, 6-number stat strip, region-count bar,
  dotted world map with 13 numbered pins, REPORTED / CLAIM / FORECAST
  legend, DATE CHECK strip (6 excluded near-miss stories).
- Image: `assets/entry.png` — 1024×1024 PNG, 363,389 bytes (≤ 1 MiB).
- sha256: `f8904c6f74625fcde5e3e3c0336cbb235f4a6ff3d2ba2fbf62410dfa773bf81a`
- Determinism: rendered twice after the final art revision; both runs
  produced the identical sha256 above. `main.ts` copy also verified to
  produce identical bytes.
- Layout guards: `tools/render.py` FAILS the build on page overflow
  (>1024px either axis) or any clipped `.clip` text. Final render:
  guards pass, no clipping. Final PNG read visually: no overlapping or
  clipped text, all 13 illustrations fill their cells, map pins and
  legend legible.

## Kit check (19 Nov 2026, `makefun check --repo <workdir> --worktree`,
## no --transcripts — transcript rows skipped, as expected)
- 4 passed: competition_open, snapshot (7 files, 431,332 bytes),
  license_osi (MIT), entrypoint (main.ts, node22).
- 1 failed: transcripts_present — no transcripts were supplied to the
  local check. Expected: transcripts are bundled by the coordinator at
  submit time (`makefun bundle`), not by this build. This is the only
  failure and it is a packaging step, not a defect in the entry.
- 14 skipped (all transcript checks — nothing parsed without a bundle).
- 5 checked at submission (repo_public, repo_owner,
  repo_created_after_open, commit_in_repo, duplicate_snapshot) — all
  for the coordinator to satisfy at submit time (public repo created
  after the 19 Nov 00:00 UTC opening, owner claim, pushed commit).
- Verdict of the check run: "not ready: fix transcripts_present, then
  check again" — i.e. bundle transcripts, then submit. Nothing else
  to fix in the entry itself.

## 5-gate self-review (vs Top-10 line: judge 990.123; live entry 959.408)

### 1. Competition fit — PASS
One day's news, date dominant ("Thursday 19 November 2026" is the
largest text on the page). 41 stories across 7 regions and every beat
(summit, courts, war, weather, markets, tech, science, sport). Every
story happened or was first reported 19 Nov; six near-misses are
explicitly excluded in the DATE CHECK strip (Van Gogh sale, Pew report,
Hegseth deal, EU €45bn loan, Jeffries vote, Qeshm strikes). Voyager 1
is framed only as the 19 Nov NASA confirmation, never as reaching the
milestone that day. COP31 is never confused with COP30.

### 2. Judge-facing presentation — PASS
Masthead + huge date + red sub-headline (Shenzhen / ICJ / GTA VI).
Stat strip (6 big numbers), region bar (7/8/11/3/4/2/6 = 41), 13
code-drawn SVG illustrations (heroes fill their cells edge to edge
after the wide-strip redesign), dotted world map with 13 numbered pins
and a pin key, numbered briefs list, confidence legend, date check,
footer count. Headlines legible at ~300px: hero headlines 16.5px,
main headlines 11.5px, briefs 8.8px bold leads.

### 3. Originality — PASS (with a noted limit)
The design mirrors the top-10 entries' proven structure (the analysis
found #8 and #10 share this exact shape: ~40 stories, 12–13 drawn,
map + numbered briefs) — that is deliberate, because the judge rewards
that structure, and the text, facts, illustrations and layout code are
all written fresh for this entry. The art is original flat-vector work
drawn in code; nothing is copied from the live entry or from any top
entry's image. Limit: the art is simple by design (flat shapes, no
shading); it reads clearly but is not as rich as a hand-drawn panel.

### 4. Execution quality — PASS
Layout guards pass; PNG read visually with no clipping, overlap or
garbled text; deterministic bytes; 363 KB ≤ 1 MiB; 1024×1024 exact.
Facts verified story-by-story in VERIFICATION.md with sources and date
evidence; claims tagged CLAIM (Gulf), forecasts tagged FORECAST
(Akvan landfall); "targets" not "hit"; "ISSUED" not "signed" for the
Shenzhen declaration; Fed HELD, never "hiked"; UK drones, not cruise
missiles; Bangladesh toll is the police figure (two), not "4 killed";
Florida "300+ rescues" correctly NOT used (that was calls for help).

### 5. Competitive comparison vs the ~990.1 Top-10 line — PASS, narrow
Live entry "Elegant Foundry" (959.408, #5,989) had zero pictures, no
map, no ICJ, no Florida, no Suneung, no Colombia, no Australia 4.9%,
no Indonesia law, no stat strip, no region bar, no date check, no
confidence tags. This challenger closes every one of those gaps — the
exact gaps the top-10 analysis identified — and its structure matches
the #8 (990.296, "40 stories, 7 regions, 12 drawn") and #10 (990.123,
"42 stories, 3 heroes, date masthead, map + numbered briefs") entries
almost one-for-one, with 41 stories and 13 drawn. That is the evidence
it can plausibly reach ~990: it is not merely better than 959, it has
the same feature set as the entries already sitting on the 990 line.
Residual risk: art simplicity (flat SVG vs richer panels) and a coarse
hand-drawn dot map (South America reads thin) could cost a point or
two against the most polished top entries — but neither is a criterion
the judge weights above breadth, faithfulness and legibility, where
this entry is strong.

## Verdict: GO
The challenger is ready to submit as the new final entry (replacing
"Elegant Foundry") once the coordinator bundles transcripts and the
user orders the submit. No further revision is required for the
Top-10 chase; any further art polish would be diminishing returns
against the 21 Nov 07:00 WIB deadline and the 19-submission budget.

---

## Coordinator addendum (19 Nov 2026, ~23:05 WIB — verification + packaging)

### Independent verification by the coordinator
- Read the final PNG myself: 1024×1024, 363,389 bytes, sha256
  `f8904c6f74625fcde5e3e3c0336cbb235f4a6ff3d2ba2fbf62410dfa773bf81a`
  (matches the builder's hash). Masthead + "Thursday 19 November 2026"
  correct and dominant; stat strip, region bar (7/8/11/3/4/2/6 = 41),
  3 hero illustrations, 10 main illustrations, dotted world map with 13
  numbered pins + pin key, 28 numbered briefs, REPORTED/CLAIM/FORECAST
  legend, DATE CHECK strip (6 excluded near-misses), footer count
  "41 STORIES · 7 REGIONS" — all present, no clipped or overlapping text
  observed. Framing traps avoided in the visible text: Shenzhen
  declaration "toward Peace" (no "signed"/ended-the-war claim), Gulf
  "targets" (tagged CLAIM), UK "1,000+ strike drones" (not cruise
  missiles), Florida "70+ rescued from one flooded Hollywood block"
  (no "300+ rescues"), Bangladesh toll per police figure, COP31 (never
  COP30), Voyager 1 only as a 19 Nov NASA confirmation.
- Determinism: builder-verified (rendered twice after the final art
  revision, identical sha256 both times; main.ts copy test identical).
- Top-10 analysis: full write-up in `TOP10-ANALYSIS.md` in this repo
  (leaderboard 8,317 entries; Top-10 line judge 990.123; every top-10
  image carries drawn illustrations, a world map with numbered pins, a
  stat strip, a DATE CHECK footer, a confidence legend and a region bar;
  ICJ Myanmar ruling is the top-4 story in every top-10 image and was
  missing from the live entry).

### Transcript bundle + full kit check (coordinator)
- Usage rows: `~/.makefun/muse-usage-news-image-20261119-challenger.jsonl`
  (6 rows: 3 research subagents × 1, coordinator × 2, builder × 1 —
  the expected shape; each subagent contributes exactly its final
  message's row, as in the news-image-20261118 file's 12 one-row agents).
- Bundle: `makefun bundle --no-discover` with 5 sessions (builder,
  coordinator, 3 research subagents) + `--muse-usage` + `--harness Muse
  --harness-version 1 --provider meta --model muse-spark-1.3 --effort
  default --mcp none --parent-session <main-chat session>
  --prompt-file (bos's words: "kerjain ulang sampe masuk 10 besar yg
  image 19", handed-off). The parent session is required by the bundle
  tool (a handed-off prompt must carry its parent chain); it is carried
  whole under context-sessions/ (45 MB raw), which makes the bundle
  14.4 MB — the tool's own behaviour, not a hand edit. Prompt recorded
  verbatim; 6 usage rows attached; secrets redacted by the tool.
- Full check with transcripts: **13 passed, 0 failed, 6 skipped, 5
  checked at submission** — "ok: every check run here passes".
  transcripts_present, thinking_wellformed, thinking_in_window,
  thinking_reproduces (58.3% authored, ≥30% required), thinking_priced
  (6 records), thinking_revised (main.ts from 2 messages),
  transcripts_run_record all PASS. thinking_own_work is a note, not a
  rejection (sessions fetched our OWN live entry's artifact
  01a1f3cd — Elegant Foundry — for the top-10 comparison).
- Remaining at-submission checks (NOT done — build only, no submit):
  repo_public, repo_owner, repo_created_after_open (public repo created
  after 19 Nov 00:00 UTC), commit_in_repo, duplicate_snapshot. At
  submit time: create a public repo under dillahhhh, push this commit,
  add `.makefun/owner.json` naming an entry wallet, submit that commit.
- Local git: first commit `49e19e9` (9 files); this addendum +
  TOP10-ANALYSIS.md committed on top before the final bundle. The final
  bundle sha + persistent copy are recorded in the coordinator's report
  to the parent (bundle file itself is not part of the repo).

### Attempts / deadline
- Attempts: 1 used of 20 total (live entry only), 19 left; 9 left today
  (day cap 10). Deadline: 21 Nov 2026 07:00 WIB.
- Status: BUILD ONLY. No submit command run. Submit needs bos's explicit
  order on this exact entry + a fresh Ting review.
