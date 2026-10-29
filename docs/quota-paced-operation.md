# Quota-paced autonomous operation

The user authorized slow autonomous progress for eight hours from approximately
2026-10-29 20:12 UTC, with roughly three percentage points of pace tolerance,
regular commits/pushes, and timers. Deadline: **2026-10-30 04:12 UTC**
(05:12 Europe/Berlin). The fixed image ceiling remains 33 calls: three root
designs, 24 pilot enlargements and six pooled corrections. The ceiling does
not override quota, quality gates or the deadline.

Run `.venv/bin/python tools/quota_pace.py --deadline 2026-10-30T04:12:00Z`
before costly work. It invokes the user's installed `quota --json`, keeps a
sanitized ignored cache, respects a five-minute minimum poll interval, and
uses trusted server time advanced with CLOCK_BOOTTIME. Weekly target usage is
elapsed/window length. Dispatch only at/below that target; the user's three
points remain a buffer for unknown action costs and measurement quantization.
Stop costly calls when ahead, at low remaining allowance, locked, stale or at
deadline. Observe all relevant windows and concurrent account consumption.
No credits or banked resets are used. Report observed usage, not estimated
per-image percentages, as actual data.

Read `runs/overnight-2026-10-29/state.json` for the current stage and call ledger.
Persist dispatch before every image call; interrupted/unknown calls still use
their budget slot. Save exact prompt/references, original output and hashes.
Review the unified master before enlarging its glyphs. Do not independently
design category sheets, resume the arena, or run a new council campaign.

T3 scheduled work resumes this thread without a busy sleep loop. The ignored
`.local/overnight-scheduler.json` stores the exact scheduled task ID. A wake
first checks quota and deadline. If quota is ahead, update the next interval
from `next_eligible_at`; otherwise perform one bounded step and schedule a
later continuation (normally 15 minutes for a single enlargement, longer when
quota/inspection requires it). Never duplicate timers. At the deadline or a major
unrecoverable blocker, disable the task by its stored ID and write a final
progress/blocker report. Each step commits/pushes a reviewable checkpoint.

The repository is public AGPL-3.0. Never stage commercial font binaries,
embedded-font proofs, private quota/account records, local source references
or the historical backup. Upstream source snapshots retain their own notices.
An unrelated pre-existing deletion of `assets/icon.svg` is left untouched.
