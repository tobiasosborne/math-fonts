# Fresh project boundary

The previous project is deprecated in full under `archive/`.
Treat everything there, including agent skills, handoffs, plans, tests, and
verification protocols, as historical reference rather than active instructions.
Preserve the snapshot; do not run generators that overwrite archived outputs.

The research round is documented in `research/typography/`, with the proposed
rubric in `docs/rubric.md` and implementation plan in `docs/hillclimb-plan.md`.
An active design/patch pipeline and a completed bounded campaign now exist;
a complete newly authored math family remains future work.
The initial T3 Code council smoke round and its harness live in
`runs/smoke-2026-10-29/` and `tools/`; see its coordinator review and audit.
The user-authorized three-round campaign is now complete, with the subagent
owning the redesign and the parent orchestrating nine one-shot judge evaluations.
Round 2 (0.152) is retained; rounds 1 and 3 were not promoted. See
`runs/campaign-2026-10-29/summary.md` and `delivery.json` for artifacts and gaps.
The seed was explicitly copied into the active pipeline; archive and smoke
records remain immutable. No fourth round or judge retries are authorized. Rubric
version 0.3 adopts the user’s absolute standard: grade against the hypothetical
perfect math font, justify every score, and explain the gap to a featured new
design in a leading typography periodical. Expert calibration is not a
prerequisite for running the council or hillclimb.
Adopt archived lessons or artifacts explicitly, not by default.

The user has subsequently authorized a separate **three-round lowercase Greek
campaign** starting from retained 0.152, with typographer-style working-size,
distance, negative-space and grid proofs, followed by a Font evolution visual
history. The designer subagent owns design/proof implementation; the parent
orchestrates at most nine evaluator tasks using the same three judges and
fixed 0.3 anchors plus `council/greek-focus.md`. Earlier experiments remain
immutable. No fourth Greek round or automatic evaluator retry is authorized.

The user then expanded the work to **four separate PNG-inspired vector fonts
and an arena tournament**, explicitly asking for designer subagents and both
enlarged and realistic Baskerville page proofs. Greek rounds1–2 completed with
six evaluations and no promotion; the remaining single-candidate work moves
to `runs/arena-2026-10-29/`. Do not claim the original three-round Greek campaign
completed. The new arena contract fixes four entrants, two local design passes
each, two semifinals and a final, three judges per match (nine tasks maximum),
no retry/debate/fourth match. Preserve every earlier experiment. The parent
orchestrates; separate designer subagents own the four font revisions. Deliver
all four real OTFs and Font evolution after the tournament. Generated foundry
PNGs are inspiration, not ground-truth glyphs or foundry-authored designs.

LATEST USER DIRECTION: the shown vector pass was rejected as visually poor,
especially alpha. The user explicitly stopped all subagents and ordered a
fresh start, asking for glyph-by-glyph bitmap-to-smooth-vector fitting using
high-resolution rendering, downsampling and multiple measurement methods.
The arena is stopped before any evaluator task. All subagents must remain
stopped; do not reactivate them under the earlier arena authorization. Preserve
concept sheets and rejected fonts, but do not use warped inherited outlines
as the geometry for the fresh pipeline. Start with a measured alpha pilot in
`runs/bitmap-fit-2026-10-29/`, actual cubic curves, raster fidelity, smoothness
and working-size proofs. Earlier technical checks did not establish design
quality. Do not claim the failed arena completed or a font was promoted.

The subsequent solo image trial is complete in
`runs/glyph-consistency-2026-10-29/`: one fixed master plus 32 independent
enlargements (alphabet and variants), 33 image calls total, no retries or
correction generations. Local Potrace tracing produced 32 filled SVGs and real
handle views, plus a six-glyph small/upscaled/generated benchmark. Read its
README and measurements for scope and limitations. These are outline studies,
not a compiled font or a promotion. All subagents remain stopped. Do not run
additional image corrections or restart the arena automatically.

NEW NORTH STAR (subsequent user direction): continue the accepted current
image-derived design and develop a consistent, thematically unified Baskerville
math package with standard AMS mathematics coverage. The active pipeline is
Baskerville references → family specimen → independent glyph enlargements →
measured local tracing → optical/font engineering → math proofs. The user now
explicitly authorizes fresh subagents for durable pipeline documentation,
coverage research/inventory and implementation planning (Sols for technical
work, Terras where useful for visual/computer work). This supersedes the blanket
stop only for the new scoped work; the rejected arena and its designers remain
stopped. Do not begin an unbounded generation/council campaign. Existing Greek
PNG/SVG trial outputs remain immutable design evidence. See the new durable
pipeline and package planning documents when present.

The planning/audit pass is now recorded in `docs/image-to-font-pipeline.md`,
`docs/baskerville-math-plan.md`, `docs/ams-glyph-inventory.md` and
`docs/math-package-engineering.md`. The new scoped subagents have completed.
`design/unified-master.json` records the mandatory single unified design image;
the family-wide image remains planned, while the accepted Greek seed is frozen.
Every new design starts from that unified root. Include substantial actual
Storm Baskerville 10 Pro regular/italic/bold/bolditalic samples in the prompt
(`design/storm-reference.json`), not merely a foundry name. Thin measured guides
must remain removable overlays/masks; trace clean ink only. The Greek prompt
said regular italic, but visual weight is unresolved and requires matched-size
calibration against Storm italic/bolditalic before assigning its weight.
The durable exporter reproduced 32 filled + 32 handle SVGs byte for byte; frozen
coverage source inputs are in `research/coverage/2026-10-29/`. The inventory is
planning scope, not completed coverage or an image-call authorization. Continue
the current design, not the rejected arena.

SUBSEQUENT AUTONOMOUS AUTHORIZATION: the user authorized slow progress for
eight hours, quota pacing within roughly three percentage points, scheduled
wakeups, regular commits/pushes, and a public AGPL repository. The bounded run
contract/state is in `runs/overnight-2026-10-29/`; stop at 2026-10-30 04:12 UTC.
This authorizes only that finite new pipeline campaign, not old rounds/arena.
The first 24-target unified foundation is provisionally accepted for the pilot
in `design/unified-master.json`; one image call used. Read its review/issues.
Full-component tracing is in `tools/math_trace.py`; all intended components
must survive, and source pinholes require explicit review, not silent cleanup.
Use `tools/quota_pace.py`, keep account state in ignored `.local/`, and update
the existing scheduled task rather than creating duplicate timers. The public
remote is https://github.com/tobiasosborne/math-fonts; do not publish licensed
font binaries/private proofs or the old backup. The user-supplied Comic Sans
style guide is saved in `design/future/comic-sans-math/` for later consideration,
not as the active design direction.

LATEST SOURCING CORRECTION: the user wants existing Baskerville glyphs reused,
including ordinary Latin letters and numerals, rather than generated anew.
See `docs/glyph-reuse-policy.md` and `design/glyph-sourcing.json`. A/H/O generated
studies remain evidence only, not release outlines. Existing glyph cells in the
unified image are reference anchors; all NEW drawings still derive from that
one root. Retain custom Greek design. Audit existing math signs before drawing
replacements, and engineer growth/layout separately. Use externally supplied
Storm files through explicit tested font configuration; do not copy commercial
outlines into the public AGPL payload. The timer remains disabled; the earlier
eight-hour authorization is not extended by this plan correction.

RENEWED IMPLEMENTATION AUTHORIZATION (2026-10-30): the user now directs us to
get the full pipeline running and present intermittent results. This renews
active work beyond the expired overnight window. Reuse ordinary Storm glyphs,
retain the single unified root and custom Greek, and make a real end-to-end
font/rendering pilot. Technical Sol assistance is within the previously
requested delegation scope. Check quota before expensive work, preserve the
roughly three-point tolerance, use bounded image calls and checkpoint commits.
Do not reactivate the obsolete overnight timer or rejected arena. No new image
call is needed for stock Latin/numerals. Public payload excludes Storm binaries.

RUNNING PILOT: `runs/pipeline-2026-10-30/README.md` is the current concrete
delivery. Six regular-companion Greek enlargements are retained and registered
to the same frozen root. `tools/run_math_pipeline.py` builds the authored CFF/
MATH OTF, reuses original external Storm Latin/numeral faces via the loader,
and proves both engines with actual per-glyph font-use checks. The public
font contains no Storm letter/figure outlines. Private proofs embed Storm and
remain excluded. Full AMS coverage and final optical acceptance are not done;
finite growth forms/scripts remain provisional. Do not silently extend the
completed six-image-call run or restart old timers/arena work.
