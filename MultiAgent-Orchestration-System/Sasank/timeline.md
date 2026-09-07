# Timeline

Chronological log, oldest first. Repo: https://github.com/sasankpanch/Agent-Orchestration-System

## Initial spec + step 1 scaffold
- Wrote initial project spec (`CLAUDE.md`): agents, orchestration model, memory schema,
  human-in-the-loop escalation, and a 5-step incremental build sequence.
- Decided on plain Python, no frameworks (no LangGraph/Celery/Redis/Docker) for v1 —
  goal is to understand agent orchestration mechanics directly, not abstract them away.
- Scaffolded step 1: supervisor + web research specialist, no reviewer yet.
  Flat file layout (`state.py`, `supervisor.py`, `web_research.py`, `main.py`) instead of
  a `specialists/` package, since a package with one module in it is scaffolding ahead
  of need — will restructure when specialist #2 is added (step 5).

## Pivot to a free/local stack
- Pivoted off the Anthropic API entirely to a fully free/local stack: Ollama
  (`llama3.1:8b`, local server) + `ddgs` (free DuckDuckGo search, no API key).
  Motivation: zero ongoing cost, and closer to the "understand the mechanics"
  goal since tool-calling and structured output are hand-rolled against Ollama's
  raw HTTP API rather than an SDK.
- Had to recreate the venv on Homebrew's Python 3.14 — the original system Python
  3.9 was linked against an old LibreSSL that couldn't do TLS 1.3, which `ddgs`
  requires.
- Found and fixed a silent failure mode: `supervisor.plan()` could return a
  schema-valid but empty step list, and the pipeline would continue anyway,
  producing a confident hallucinated answer with no research behind it. Fixed
  with a retry-until-nonempty guard (see `docs/issues.md`).
- Verified step 1 end-to-end via multiple smoke tests with real cited sources.

## Step 2: reviewer + retry loop
- Added `reviewer.py` — an LLM-as-judge that checks each specialist's
  findings against the step instruction (concrete, non-empty, cited) and
  returns `(approved, feedback)`. `web_research.run()` now takes optional
  `feedback` so a rejected attempt can be retried with the reviewer's specific
  complaint folded into the instruction, rather than just blindly re-asking
  the same question.
- Retry cap set to 2 attempts total, per `CLAUDE.md`'s escalation trigger
  ("specialist fails twice on the same subtask"). Human-in-the-loop itself is
  a later build step, so for now, failing both attempts just logs a loud
  `step_escalated` trace event and the pipeline continues with the last
  (unapproved) result — a deliberate stub, not a real escalation yet.
- Smoke tested: one step got rejected on attempt 1 (reviewer flagged
  non-authoritative sources), retried successfully on attempt 2. A second step
  failed both attempts and correctly hit the escalation log path without
  crashing the run. Confirms the full retry/escalate branch, not just the
  happy path.

## Step 3: SQLite memory
- Added `memory.py`: `tasks`/`lessons` tables per `CLAUDE.md`'s schema, plus an
  FTS5 virtual table (`tasks_fts`) for keyword-based similarity search — no
  embeddings/ChromaDB, matching the plain-Python constraint. Every reviewer
  rejection is saved as a lesson (the feedback text already says exactly what
  went wrong), so lessons come for free out of step 2's existing data.
- Before planning, `main.py` queries memory for similar past tasks/lessons and
  injects them into `supervisor.plan()`'s prompt via a new `memory_context` param.
  After a run, the task and any rejection-lessons are saved.
- Evaluated whether this measurably changes behavior, as `CLAUDE.md` asks: ran
  "tallest mountain in the world," then a similar "tallest mountain in North
  America" task. First run: every step needed at least one rejection/retry
  (0/2 approved outcome logged). Second run, with the first task's lessons
  injected: steps 1 and 2 both passed review on the *first* attempt; step 3
  still failed both attempts and escalated. Real, visible effect on two of
  three steps — not a full fix, and this is one paired observation, not a
  controlled study, but it's a genuine signal that memory injection changed
  specialist behavior rather than being inert prompt padding.
- `memory.db` is gitignored, same reasoning as `traces/`: regenerable local
  state, not source.

## Step 4: human-in-the-loop escalation
- Added `hitl.py`: replaces the earlier `step_escalated`-log-and-continue stub
  with an actual terminal prompt when a step fails review twice. Shows the
  task, the specialist's findings, sources, and the reviewer's exact rejection
  reason, then asks for `[a]pprove anyway / [r]eject and skip step / [m]odify
  instruction and retry`.
- `approve` keeps the result as-is; `reject` clears findings/sources and marks
  the step unapproved (synthesis sees an explicit "skipped" note instead of
  silently missing data); `modify` takes a human-written instruction and gives
  it one more `web_research.run()` attempt, trusted directly without going
  back through the reviewer — the human already saw the reviewer's feedback
  and is acting on it, so re-reviewing would just be circular.
- Along the way, found the machine was under enough memory pressure
  (15/16GB RAM in use) to make schema-constrained Ollama calls take up to
  ~5 minutes instead of seconds, well past the old 180s request timeout.
  Confirmed with a direct timed call before assuming it was a code bug.
  Bumped the timeout to 480s in `ollama_client.py` — a resilience fix, not
  a fix to the escalation logic itself.
- Verified all three decision branches: a full pipeline run exercised
  `approve` three separate times (trace confirms `human_decision` and final
  `approved: true` on each), and `reject`/`modify` were verified directly
  against the state-mutation logic and a live `web_research.run()` call
  respectively.

## Specialist #2: data analysis + multi-specialist routing
- Chose the more ambitious of two options for how data analysis gets its
  input: chained from a preceding `web_research` step's findings, rather than
  only handling data pasted directly into the task by the user. This meant the
  supervisor now needs to route each step to the right specialist, not just
  write instructions.
- `Step` gained a `specialist` field; `supervisor.plan()`'s schema now requires
  each step to declare `"web_research"` or `"data_analysis"`, and the planning
  prompt tells the model data_analysis steps must come after the research
  step(s) that gather the numbers they need.
- Added `data_analysis.py`: one tool, `compute_stats` (mean/median/sum/min/max/
  stdev/range) over a list of numbers — deliberately not arbitrary code
  execution, since that's specialist #3, still to come. `main.py` gained a
  `run_specialist()` dispatcher that builds the data-analysis step's context
  from `state.step_results` accumulated so far, and routes reviewer/HITL/
  memory-lesson bookkeeping generically by `step.specialist` — none of those
  three needed research-specific changes, which is a good sign the step 1-4
  loop was actually built generically rather than accidentally coupled to web
  research.
- First smoke test surfaced a real bug (see `docs/issues.md`): the model
  sometimes narrates a tool call as text instead of invoking it, which let
  a data_analysis step fabricate plausible-looking city population numbers
  when its input context was empty. The reviewer actually caught both
  failures correctly and escalated to HITL — but the test script blindly
  approved everything, so the fabricated numbers reached the final answer.
  Fixed with a heuristic guard in both specialists that detects a narrated,
  unexecuted tool call and forces a retry instead of accepting it as final.
  Re-verified: no recurrence, both specialists produced real tool-backed
  results on rerun.

## Specialist #3: coder / code execution
- Before writing any code, deliberately paused on how the coder specialist
  should actually execute LLM-generated Python on this machine — a different
  risk profile than the last two specialists, since CLAUDE.md rules out Docker
  for v1 so there's no container boundary. Landed on: `subprocess.run()` with a
  10s timeout, stdout/stderr capture, and an isolated scratch `cwd`
  (`coder_scratch/`, gitignored) — accepting that true network/filesystem
  isolation isn't achievable without a container, same constraint the project
  already accepted elsewhere.
- Added `coder.py` (one tool, `run_python`) and a third `specialist` option in
  `supervisor.py`'s plan schema/prompt. Verified the execution mechanism
  directly first (success, non-zero exit, and timeout all handled correctly)
  before testing it through an LLM at all — cheaper to rule out the
  deterministic layer before debugging the probabilistic one.
- First full-pipeline test surfaced three distinct bugs, documented in full in
  `docs/issues.md`:
  1. The supervisor planned "write code" and "run code" as two separate coder
     steps — architecturally impossible, since each specialist call is
     stateless and only sees prior findings text, never another step's actual
     code. Fixed by explicitly telling the planning prompt a coder step always
     writes AND executes in one step.
  2. Fixing that surfaced a second bug hiding underneath: the model sometimes
     echoed the specialist's own name as the entire instruction (schema-valid,
     content-free) — 3 of 4 sampled runs. Fixed two ways: a runtime
     degenerate-instruction check, and (more robust) a `minLength: 15` JSON
     schema constraint, confirmed to be enforced by Ollama's grammar-decoder
     directly rather than just detected after the fact.
  3. Even with a real, correctly-executed calculation, the model sometimes
     misstated the real result in its closing paraphrase (e.g. real captured
     stdout `675.93`, final answer states `67.59`) — 2 of 3 trials. Added
     `had_successful_execution` tracking to both `coder.py` and
     `data_analysis.py` so a final answer is refused until at least one real,
     error-free tool call has happened — closes "answered with zero real
     computation," but not full paraphrase-faithfulness. Explicitly decided
     not to chase that further: fully closing it means extracting the real
     value from stdout and templating it into findings ourselves rather than
     trusting the model's restatement, a genuinely bigger architectural shift.
     Documented as a known limitation; HITL is the intended backstop.
- This is the last specialist in `CLAUDE.md`'s build sequence (steps 1-5 now
  complete) before the distributed-machines phase.
