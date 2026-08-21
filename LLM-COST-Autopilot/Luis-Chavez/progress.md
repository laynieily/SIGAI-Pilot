# [AI] Progress & Work Queue

[AI] Written by the AI assistant on 2026-07-28 at Luis Chavez's request.
[AI] Every line in this file is `[AI]`-authored unless later edited and marked `[LC]`.
[AI] Purpose: a running snapshot of where Phase 1 stands and what order the
[AI] remaining work gets done in. Companion to `plan.md` (the design) and
[AI] `Documentation.md` (the narrative session log). This file is the checklist.

---

## [AI] Where the project stands — 2-week catch-up, recorded 2026-08-19

[AI] **This section covers roughly two weeks of work (2026-08-02 to 08-19), not
[AI] one day.** Recording fell behind during that period, so the progress below
[AI] accumulated across several sessions and is being written up in one pass
[AI] rather than backfilled as separate thin entries.

[AI] **A note on the dates in this file.** The `DONE 2026-08-19` stamps on items
[AI] 9-17 are the dates work **landed in the repository**, not the dates it was
[AI] conceived or carried out. They cluster on 08-19 because that is when the
[AI] backlog was consolidated and committed — items 9 and 10, for instance, were
[AI] found on 08-03 tracing `router.py` line by line, and the thinking behind
[AI] several of the others predates the commit that closed them. Read the stamps
[AI] as "in the repo by", and `git log` as the record of when things were
[AI] committed, not when they were worked out.

[AI] Work-queue items **9 and 10 are closed**, the repo has a **test suite** for
[AI] the first time (item 11), items 13-17 came out of an audit pass, and
[AI] `_send_anthropic` has run live. Nothing in the codebase had gone stale over
[AI] the gap — the only breakage was environmental, below.

[AI] **Environment finding, recorded because it blocked the restart.**
[AI] This machine could not run the project at all: `llama3.2` was no longer
[AI] pulled into Ollama (the local models present were `qwen3:8b`, `gemma4:12b`,
[AI] `mistral-nemo:12b`), there was no virtualenv, and `httpx` was not installed.
[AI] The 2026-08-02 commit subject — "switching machines" — is the cause. So the
[AI] pre-work baseline was worse than the 2026-08-03 notes below describe: all
[AI] four prompts failed, not two. Fixed by `ollama pull llama3.2` and a fresh
[AI] `.venv`; the setup steps are now written down in the README so the next
[AI] machine costs nothing.

[AI] **Changed across the catch-up period:**
[AI] - `Tier` is an `IntEnum` (`models.py`), not a bare `str`. Ordered, so the
[AI]   code can ask "what is the next tier up?" — item 10's root cause.
[AI] - `config.above()` / `ladder()` / `top()` — the registry now answers tier
[AI]   questions, so the router does not need to know how many tiers exist.
[AI] - `route()`'s fallback is one loop over the ladder. No per-tier branches.
[AI] - `classify()` returns a `Classification` record, not `(tier, prose)`.
[AI] - `main.py` prints a routing-signal tally and an explicit caveat about the
[AI]   savings headline; stdout is reconfigured to UTF-8 (Windows `cp1252` was
[AI]   rendering the em-dashes in our own error strings as mojibake).
[AI] - `tests/` — 81 tests, no network, runs in ~13 ms.
[AI] - Ten audit questions answered in `ai_questions.md`, yielding items 12–14:
[AI]   quality measurement (**not built**, deliberately), the capacity/context
[AI]   window split, and signals for truncated or partially-dropped replies.
[AI] - Items 15-17: routing accuracy is measured for the first time (50% on a
[AI]   deliberately adversarial corpus, 0% on every adversarial class), empty
[AI]   replies now escalate, and pricing carries a date and a source.

[AI] **Also in this period:** an API key was obtained and `_send_anthropic`
[AI] made its first live request. Items 9, 10, and 11 were worked *before* that,
[AI] because none of them needed a key — they were the part of the backlog no
[AI] external dependency could block, which is why they were the right place to
[AI] pick the project back up.

[AI] **Unchanged:** the MVP scope note below. Quality-based escalation is still
[AI] not built, and item 15 now puts a number on what that costs.

---

## [AI] Where the project stood (2026-07-31)

[AI] Phase 1 is the unified model interface: `send_request(config, prompt) -> Response`.
[AI] That function now exists and works. A live `llama3.2` call returns a populated
[AI] `Response` — real text, real token counts, real latency — and `main.py` sends the
[AI] same prompt to both configs through one loop that cannot tell them apart.

[AI] **Done:**
[AI] - `Response` dataclass — build order step 1.
[AI] - `ModelConfig` dataclass *and both instances* — build order step 2 complete.
[AI] - Cost formula placed on `ModelConfig.price()` rather than duplicated per adapter.
[AI]   The pricing rates live on the config, so the formula that consumes them lives
[AI]   there too; `Response.cost` stores the resulting number as a fact about one call.
[AI] - `requirements.txt` manifest — `httpx`, `python-dotenv`; direct dependencies only.
[AI] - `.gitignore` covers `__pycache__/` and `*.py[cod]` — bytecode is a derived
[AI]   artifact, regenerated on import, machine- and interpreter-version-specific.
[AI] - **Ollama adapter + `send_request` dispatcher** — build order step 3 (item 5).
[AI] - **`Response.summary()`** — item 2b, unblocked by having a real response to format.

[AI] - **Anthropic adapter** (item 6) and **config registry** (item 7) — see below.
[AI] - **The router** (`router.py`) — Phase 2, and the project's actual goal.

---

## [AI] SCOPE CHANGE 2026-07-31 — wrapping up as an MVP

[AI] LC said he is "not too passionate about this project as I anticipated" and
[AI] wants to close it out with an MVP rather than continue the phased buildout.
[AI] `plan.md` still describes the original full plan; **this section, not
[AI] `plan.md`, is the current intent.** Work stopped at the smallest thing that
[AI] satisfies the goal in `plan.md`'s opening line.

[AI] **What the MVP is:** `python main.py` sends four prompts through
[AI] `router.route()`. For each one it prints the tier chosen, the reason it was
[AI] chosen, the answer, and the cost against an always-expensive baseline.

[AI] **Deliberately NOT built** (state plainly rather than quietly finish):
[AI] - *Quality-based escalation.* The router falls back when the cheap call
[AI]   **fails** (provider down, no key, HTTP error) — never because the answer
[AI]   was poor. Judging "was the cheap answer good enough" is the actual hard
[AI]   problem and is not solved here. This is the MVP's central limitation and
[AI]   the demo shows it (see the observed failure below).
[AI] - *A real routing model.* `COMPLEXITY_KEYWORDS` is a hand-written word list.
[AI]   It is inspectable and tunable, not principled.
[AI] - *A `.env` / real API key.* Everything is written and wired; nothing has
[AI]   been run against the live Anthropic API. See "untested" below.

[AI] **Observed on 2026-07-31, worth keeping.** Before the demo prompt was
[AI] lengthened past the 400-char threshold, a genuinely hard question (async
[AI] refactor of a rate-limited pipeline) scored "simple" and routed to
[AI] `llama3.2`, which answered confidently and wrongly — it invented
[AI] `asyncio.ThreadPoolExecutor`, constructed a client per row, and put `await`
[AI] in a non-async `def main()`. Nothing in the system noticed. That is the
[AI] limitation above, demonstrated by accident rather than argued for.

---

## [AI] Owed by LC

[AI] `Documentation.md` and `ai_questions.md` entries for the catch-up period.
[AI] Those two files are LC's by standing decision — the AI does not write entries in
[AI] them, because the point is to record LC's experience rather than an invented one.
[AI] `Documentation.md` also states "one entry per commit", and nothing has been
[AI] committed since the adapter work began.

[AI] **Still owed as of 2026-08-19**, and deliberately left empty rather than
[AI] filled in by the assistant. Entries are outstanding for the 2026-08-02,
[AI] 2026-08-03, and 2026-08-19 sessions. The last `Documentation.md` entry is
[AI] dated 2026-07-29.

[AI] The catch-up write-up has the most to record: the environment breakage on
[AI] a second machine, items 9/10/11, the audit that produced 12-17, and the
[AI] first live run of the hosted adapter — spread across the two-week period,
[AI] not a single sitting.

[AI] `ai_questions.md` holds ten entries (`1-2026-08-19` … `10-2026-08-19`) from
[AI] the audit. **Verdicts and notes are intentionally blank** — LC's call: this
[AI] was a catch-up pass, and the verdict vocabulary (`used`/`adapted`/
[AI] `rejected`/`deferred`) was built for "I asked how to do X, here is what I
[AI] did with the answer". These are audit questions, where the finding *is* the
[AI] deliverable and there is no suggestion to accept or reject. Not a debt.

[AI] Those entries carry a `**Finding:**` field, an addition to the template,
[AI] marked `[AI & LC]`: LC set the questions, the assistant wrote the answers
[AI] against the codebase. The mark is documented at the top of that file.

[AI] Also owed: `corpus.py`'s labels are AI-authored and marked provisional
[AI] (item 15). Reviewing them is what turns the 50% accuracy figure from a draft
[AI] into a result.

---

## [AI] RESOLVED 2026-08-19 — `_send_anthropic` has now run live

[AI] **The section below is history.** A key was minted, `.env` created, and
[AI] `python main.py` ran with all four prompts succeeding. Every claim the old
[AI] text listed as "from documentation, not observation" is now observed:

[AI] - `content` **is** a list of typed blocks; the prose **is** in the first
[AI]   `{"type": "text"}` entry.
[AI] - Token counts **do** arrive as `usage.input_tokens` / `usage.output_tokens`.
[AI] - No change to `_send_anthropic` was needed. The shape was right.

[AI] **`plan.md` build-order step 4 is now demonstrated, not asserted.** Swapping
[AI] only the `ModelConfig` changed which provider answered, with zero changes at
[AI] the call site — observed, in one run, across two providers.

[AI] **Finding 1 — the model alias resolves, and the adapter was right to read it
[AI] from the reply.** We request `claude-haiku-4-5`; the response says
[AI] `claude-haiku-4-5-20251001`. `adapters.py` already read `model` from the
[AI] reply rather than the config, with a comment noting that Ollama echoed the
[AI] requested string verbatim "the point is that the reply stays the source of
[AI] truth if that ever stops being so." For Anthropic it has stopped being so.
[AI] The design decision paid off observably rather than theoretically, and the
[AI] demo output now names the exact dated model that answered.

[AI] **Finding 2 — `max_tokens=1000` truncated both expensive answers.** Both
[AI] hosted calls returned *exactly* 1000 output tokens, and the printed text ends
[AI] mid-expression (`await asyncio.wrap_future`). The cap is not a safety margin
[AI] here, it is the binding constraint: every expensive call bills the full 1000
[AI] output tokens at $5.00/M whether or not the answer was finished. This is now
[AI] the largest single lever on the cost figures below, and it is a
[AI] `ModelConfig` default nobody chose deliberately.

[AI] **Finding 3 — `usage` carries cache fields** (`cache_read_input_tokens`,
[AI] `cache_creation_input_tokens`) that `Response` does not map and `price()`
[AI] does not know about. Not a bug — cached input is billed at a different rate,
[AI] so a future cost model would need them. Recorded, not built.

---

## [AI] UNTESTED (historical — resolved above, kept for the record)

[AI] `_send_anthropic` has **never made a real request.** It is written, it
[AI] compiles, and its missing-key path is verified, but every claim about the
[AI] live response shape is from documentation, not observation. Specifically
[AI] unverified: that `content` is a list of typed blocks with the prose in the
[AI] first `{"type": "text"}` entry, and that token counts arrive as
[AI] `usage.input_tokens` / `usage.output_tokens`.

[AI] To finish: mint a key at the Anthropic Console, add credits, `cp
[AI] .env.example .env`, paste it in, and run `python main.py`. Measured cost of
[AI] a full demo run is well under a cent. If the response shape differs from the
[AI] above, the fix is confined to the last ten lines of `_send_anthropic`.

[AI] **Still true as of 2026-08-19.** None of the items 9-17 work needed the
[AI] key, and none of it changed `_send_anthropic`. Two consequences that
[AI] should not be glossed:
[AI] - `plan.md` build-order **step 4 remains asserted, not demonstrated.** The
[AI]   claim "swapping only the `ModelConfig` changes which provider answers" is
[AI]   true of the code as written and has never been observed end to end.
[AI] - The savings headline **cannot be meaningful yet.** Every successful call so
[AI]   far is a free local one, and a failed call prices $0, so the figure reads
[AI]   100% by construction. `main.py` now prints this caveat at runtime instead
[AI]   of leaving it for a reader to discover in this file.

---

## [AI] First live end-to-end run (recorded 2026-08-19)

[AI] Both providers, all four prompts answered, nothing failed:

```
=== "What is the capital of France?"
CHEAP     <- short (30 chars), no complexity keywords
  OK  llama3.2                   40 tok (32 in / 8 out)      $0.000000  [2578 ms]
=== "Design a distributed rate limiter using consistent hashing..."
EXPENSIVE <- complexity keyword(s): design, trade
  OK  claude-haiku-4-5-20251001  1025 tok (25 in / 1000 out) $0.005025  [5631 ms]
=== "Name three primary colors."
CHEAP     <- short (26 chars), no complexity keywords
  OK  llama3.2                   48 tok (30 in / 18 out)     $0.000000  [2625 ms]
=== "I have a Python service that reads rows from Postgres..."
EXPENSIVE <- long prompt (495 chars >= 400)
  OK  claude-haiku-4-5-20251001  1115 tok (115 in / 1000 out) $0.005115 [7853 ms]

4 prompts
  routed cost              $0.010140
  always-expensive (est.)  $0.010332
  saved                    $0.000192 (2%)
```

[AI] **The savings figure is 2%, and that number is the honest one.** Every
[AI] previous run reported 100%, which this file already warned was an artifact of
[AI] free local calls being the only successes. Now that a paid call succeeds, the
[AI] real shape of the result is visible, and it is worth stating plainly rather
[AI] than burying:

[AI] - **An expensive-routed prompt saves exactly nothing, by construction.** Its
[AI]   baseline *is* its actual cost — same model, same tokens. Two of four
[AI]   prompts contribute $0.000000 in savings.
[AI] - **All the savings come from the cheap-routed prompts, and they are the
[AI]   cheap prompts.** "What is the capital of France?" would have cost
[AI]   $0.000072 at Haiku rates. Short questions are cheap *everywhere*, so
[AI]   routing them to a free model saves a rounding error.
[AI] - **The bill is dominated by the expensive tier** — $0.010140 of $0.010140.
[AI]   Which is the uncomfortable finding: on this corpus the router's savings
[AI]   (2%) are almost entirely swamped by the calls it decided *not* to reroute.

[AI] **What this actually says about the project.** The 2% is not a failure of the
[AI] implementation; it is a measurement of the corpus. Savings scale with the
[AI] fraction of *expensive-looking* prompts a cheap model could have handled —
[AI] and this router, by design, never finds those, because it decides before the
[AI] call and never checks whether the cheap answer would have been good enough.
[AI] The number puts a figure on the limitation the MVP scope note already named:
[AI] **quality-based escalation is where the savings actually live.** A demo
[AI] corpus with four prompts cannot show more than that, and should not be
[AI] presented as if it could.

[AI] *Also confirmed by this run:* the 2026-07-31 observation still holds in the
[AI] other direction. Prompt 4 is the async-refactor question that `llama3.2`
[AI] previously answered confidently and wrongly; routed to Haiku it came back
[AI] correct (batching, a semaphore-based limiter, retry on 503) — though
[AI] truncated at the 1000-token cap.

---

## [AI] Work queue — easiest to hardest

[AI] Ordered so each item is independently runnable and verifiable before the next
[AI] one starts. Items 1–3 are cleanup that removes friction from items 4–7; doing
[AI] them first means the adapter work isn't fighting avoidable papercuts.

### [AI] 1. Dependency manifest — `requirements.txt` — DONE 2026-07-28

[AI] *Problem:* a fresh clone cannot run the project. `httpx` is installed only
[AI] inside `.venv/`, which is gitignored (correctly — virtualenvs are not portable).
[AI] *Resolved:* direct dependencies only (`httpx==0.28.1`), transitive deps left to
[AI] pip. A `pip freeze` would have pinned all 16 venv packages including FastAPI and
[AI] Pydantic, which the code does not import and which `plan.md` explicitly defers.
[AI] Verified by dry-run: the single pin resolves anyio, certifi, h11, httpcore, idna.
[AI] *Update 2026-07-29:* `python-dotenv==1.2.2` is now declared — it became a real
[AI] dependency at item 4 exactly as predicted, consumed by `config.py`'s `load_dotenv()`.
[AI] *Open item for LC:* `fastapi`, `starlette`, and `pydantic` remain installed in
[AI] `.venv` but unused and undeclared. `pydantic` is deferred by `plan.md` until
[AI] configs load from a file (item 7); the FastAPI stack appears to be a leftover
[AI] from other work.

### [AI] 2. `Response.total_tokens` — stored field to computed property — DONE 2026-07-28

[AI] *Problem:* `total_tokens` was derived from `prompt_tokens + completion_tokens`
[AI] but stored independently, so the three could disagree.
[AI] *Real risk, not hypothetical:* Ollama and Anthropic return only the two
[AI] component counts, while OpenAI returns its own `usage.total_tokens`. The natural
[AI] result is some adapters computing the total and others passing the provider's
[AI] through — so one contract field would mean two different things depending on who
[AI] answered. Phase 2 compares responses *across* providers, so that makes the
[AI] comparison invalid while still producing plausible-looking numbers.
[AI] *Resolved:* `total_tokens` is now a `@property`. One definition for every
[AI] provider. Provider-reported totals remain available in `raw`.
[AI] *Verified:* computes correctly, absent from the constructor field list, and
[AI] passing `total_tokens=` now raises `TypeError` — the drift is unrepresentable.
[AI] *Implementation note:* the `total_tokens: int` annotation had to be deleted, not
[AI] merely shadowed. `@dataclass` builds fields from `__annotations__` and uses the
[AI] class attribute of that name as the field default, so keeping both would make the
[AI] property object the default and break every construction with
[AI] `AttributeError: can't set attribute`.

### [AI] 2b. `Response.summary()` — human-readable output — DONE 2026-07-31

[AI] *Why:* the generated `__repr__` prints fields only, so `total_tokens` no longer
[AI] appears when printing a `Response`. `plan.md` step 1's "done when" was a clean
[AI] `print()`, and LC judged readable output important enough to preserve rather than
[AI] trade away.
[AI] *Decision (LC):* add a small `summary()` method rather than write a custom
[AI] `__repr__` — keeps the dataclass-generated repr as the faithful debug view and
[AI] gives human-readable output its own separate method.
[AI] *Deferred to:* after the adapter work, once there is a real `Response` from a
[AI] live call to format. Phase 1's exit criteria is a side-by-side comparison print,
[AI] so this is the method that will render it.
[AI] *Resolved:* one metrics line (`model`, `total_tokens` split in/out, `cost`,
[AI] `latency_ms`) followed by the completion text, with an early return for the
[AI] `ok=False` case — a failed call has no tokens or cost worth printing, only an
[AI] error and the time it burned before giving up.
[AI] *Detail worth keeping:* cost is formatted to **6** decimals. A short cheap call
[AI] lands around $0.0001, so the conventional 2 decimals would render every routing
[AI] decision as `$0.00` and hide the exact quantity Phase 2 exists to compare.
[AI] *Open for LC:* the format itself is taste, not architecture. Column widths and
[AI] whether the full completion text belongs inline are yours to change.

### [AI] 3. `Response` failure-path ergonomics — DONE 2026-07-28

[AI] *Problem:* constructing a failed `Response` required supplying every numeric
[AI] field before reaching `ok=False`, turning each adapter's `except` block into a
[AI] wall of placeholder zeros — written four times across items 5 and 6.
[AI] *Resolved:* a `Response.failure(model, error, latency_ms, raw=None)` classmethod.
[AI] An error path is now one line: `return Response.failure(config.model, str(e), elapsed)`.
[AI] A `@classmethod` rather than a regular method because there is no instance yet —
[AI] this *is* the construction. It is an alternative constructor.

[AI] *Rejected alternative — defaults on the numeric fields.* Two reasons:
[AI] - Mechanical: `@dataclass` requires every field after a defaulted one to also
[AI]   have a default, so defaulting `prompt_tokens` forces defaults onto
[AI]   `completion_tokens`, `cost`, and `latency_ms`. All-or-nothing without reordering.
[AI] - Substantive: defaults apply to the **success** path too. An adapter that forgot
[AI]   to set `cost` would silently emit a successful response claiming the call was
[AI]   free. `Response.cost` is the exact number Phase 2 optimizes, so a silent `0.0`
[AI]   makes an expensive model look free and the router would route everything to it
[AI]   while reporting perfect savings. The classmethod keeps the success path strict.

[AI] *Design note:* `latency_ms` is a required parameter, not defaulted to `0.0`. A
[AI] call that times out after 60 seconds genuinely took 60 seconds, and Phase 2 should
[AI] be able to tell a slow-failing provider from an instantly-failing one. The zeros
[AI] that *are* hardcoded (`text`, token counts, `cost`) are honest values, not
[AI] placeholders — a failed call returned no text and consumed no billable tokens.
[AI] *Verified:* `failure()` returns a well-formed `Response` with `ok=False`, and
[AI] omitting `cost` on the normal constructor still raises `TypeError`.

### [AI] 4. Two `ModelConfig` instances — finishes build order step 2 — DONE 2026-07-29

[AI] *Task:* one local Ollama config, one hosted config. The hosted one reads its
[AI] key from the environment.
[AI] *Key mechanic:* `os.environ.get()` returns `None` when the variable is unset
[AI] instead of raising, as `os.getenv()` does — it is the same call, `os.getenv` being
[AI] a thin wrapper. That is precisely why `api_key` is typed `str | None`; the
[AI] dataclass already anticipates a missing key.
[AI] *Resolved:* `config.py` holds `CHEAP_LOCAL` (Ollama/`llama3.2`) and `SMART_CLOUD`
[AI] (Anthropic/`claude-haiku-4-5`, $1.00/$5.00 per 1M). Kept out of `models.py` so that
[AI] file stays "what a config is" and `config.py` becomes "which configs exist" — the
[AI] natural home for item 7's registry.

[AI] *Decision (LC + AI):* `base_url` is the **host root**, not a full endpoint.
[AI] `plan.md` originally specified `http://localhost:11434/api/generate`; that pins one
[AI] path per config and breaks the moment a provider needs a second one (Ollama's
[AI] `/api/chat`, streaming). The path is provider-specific, so by the design rule it
[AI] belongs in the adapter alongside the headers. `plan.md` corrected to match.

[AI] *Note:* no `.env` exists — LC has no API key yet, and Phase 1 runs on Ollama until
[AI] one is available. This is not a blocker: `load_dotenv()` returns `False` and no-ops
[AI] when the file is absent, and `os.environ.get()` yields `None`, so `SMART_CLOUD`
[AI] constructs cleanly with `api_key=None`. A committed `.env.example` documents the
[AI] variable name. Rejecting a `None` key is the **adapter's** job, returned as
[AI] `Response.failure(...)` rather than raised — the config layer stays permissive so
[AI] one unusable provider cannot crash the router.
[AI] *Verified:* `python config.py` prints both configs and exits 0 with no network
[AI] call; `SMART_CLOUD.api_key` is `None` and nothing raises.

### [AI] 5. Ollama adapter — `send_request(config, prompt)` — DONE 2026-07-31

[AI] *This is the first real test of the abstraction.* Provider-specific handling
[AI] that will come up:
[AI] - `max_tokens` has no equivalent in Ollama's API. It is `options: {"num_predict": N}`,
[AI]   nested. This is the design rule in action: `ModelConfig` holds neutral vocabulary,
[AI]   the adapter translates into provider dialect. Wanting to rename the field to
[AI]   `num_predict` is a sign the abstraction is leaking backwards.
[AI] - Token counts arrive as `prompt_eval_count` and `eval_count`. `prompt_eval_count`
[AI]   can be **absent** when Ollama has the prompt cached, so use `.get(key, 0)` —
[AI]   otherwise the second run of an identical prompt raises `KeyError`.
[AI] - Measure latency with `time.perf_counter()`, not Ollama's `total_duration`.
[AI]   That field is nanoseconds and covers server-side generation only, excluding the
[AI]   network round trip. Phase 2 compares local against cloud, where network latency
[AI]   is the dominant term — trusting the provider's number would silently bias every
[AI]   future routing decision.
[AI] - Three failure modes to convert into `ok=False`: Ollama not running
[AI]   (`httpx.ConnectError`), timeout (`httpx.TimeoutException`), non-200
[AI]   (`raise_for_status()` raising `HTTPStatusError`).
[AI] *Done when:* the local `llama3.2` call returns a populated `Response` with real
[AI] `text`, `latency_ms`, and `raw` instead of printing a dict.

[AI] *Resolved.* `adapters.py` holds `send_request` (dispatch on `config.provider`)
[AI] and `_send_ollama` (the dialect). All four predictions above held in practice.
[AI] *Verified against live Ollama:* `python main.py` returns wizard text,
[AI] 40 in / 48 out tokens, `$0.000000`, ~507 ms. All three failure modes produce
[AI] `ok=False` with honest latency — unreachable host 3 ms, `timeout=1` 1004 ms,
[AI] `model="not-a-real-model"` HTTP 404 in 4 ms. Nothing raised out of `send_request`.

[AI] *Deviation from `plan.md` (flagged for LC).* The plan said "refactor `main.py`
[AI] into `send_request`". It went into a new `adapters.py` instead, and `main.py`
[AI] became the entry point that calls it. Reason: items 6 and 7 both need to import
[AI] `send_request`, and importing from the file that holds `if __name__ == "__main__"`
[AI] means the entry point re-executes on import. It also continues the split the
[AI] project already uses — `models.py` = what a thing is, `config.py` = which ones
[AI] exist, `adapters.py` = how to call them. Reversible if you disagree.

[AI] *Correction to this file's own claim about `prompt_eval_count`.* Item 5 asserted
[AI] the field is absent when the prompt is cached. Ran the identical prompt twice on
[AI] 2026-07-31: present both times (`32`). Unreproduced on this Ollama version. The
[AI] `.get(key, 0)` read stays — a defensive read costs nothing and a `KeyError`
[AI] that only appears on a rerun is expensive — but it is now labelled in the code
[AI] as guarding an unconfirmed behaviour, not as a fix for an observed crash.

[AI] *Second correction, same session.* An `[AI]` comment initially claimed Ollama
[AI] resolves `"llama3.2"` to `"llama3.2:latest"` in its reply. It does not — the
[AI] request string is echoed verbatim. Comment rewritten to state what was observed.
[AI] `Response.model` still reads from the reply rather than the config, because the
[AI] contract field means "who actually answered" and a config is only what was asked.

[AI] *Known gap, deliberately not built (LC's call to keep or close).* A 2xx response
[AI] carrying a non-JSON body would make `.json()` raise straight out of
[AI] `send_request`, past the failure contract. `raise_for_status()` already catches
[AI] every non-2xx, so this needs a proxy or a corrupted local server to trigger.
[AI] Left unhandled rather than pre-emptively wrapped — you have flagged AI
[AI] "correcting for errors that don't exist yet" as a pattern you dislike, so it is
[AI] recorded here as a known hole instead of quietly padded with a catch-all.

### [AI] 6. Second adapter — WRITTEN 2026-07-31, VERIFIED LIVE 2026-08-19

[AI] *Task:* Anthropic or OpenAI, same `send_request` signature.
[AI] *Done when:* swapping only the `ModelConfig` changes which provider answers,
[AI] with zero changes at the call site. This is the proof the abstraction holds.
[AI] *Note:* model IDs and per-token prices should be verified against current
[AI] provider documentation at the time of writing, not recalled from memory or
[AI] copied out of `plan.md` — those values change.

[AI] *Verification done 2026-07-31* (against current Anthropic docs, not recall):
[AI] `claude-haiku-4-5` is a current model ID, and Haiku 4.5 is priced at **$1.00
[AI] input / $5.00 output per 1M tokens**. `config.py`'s `SMART_CLOUD` constants
[AI] match exactly — `cost_in_per_million=1.00`, `cost_out_per_million=5.00`.
[AI] Nothing to correct.

[AI] *Refinement 2026-08-03 (re-verified against the current models page).* Prices
[AI] still match. But "`claude-haiku-4-5` is a current model ID" was imprecise: the
[AI] docs list **two** identifiers for this model — API **ID** `claude-haiku-4-5-20251001`
[AI] and API **alias** `claude-haiku-4-5`. For pre-4.6-generation models the alias is a
[AI] convenience pointer that resolves to the dated ID. `config.py:33` uses the alias.

[AI] **Prediction to test on the first live call** (write the answer down either way —
[AI] this is exactly the kind of unobserved claim this item's UNTESTED note is about):
[AI] `data["model"]` returns `claude-haiku-4-5-20251001` while `config.model` still
[AI] reads `claude-haiku-4-5`. The docs confirm the alias resolves to a snapshot; they
[AI] do **not** state what the response body echoes back, so this is unverified. If it
[AI] holds, `adapters.py:122`'s read-from-the-reply choice pays for itself on call one.

[AI] *Open for LC — pin the snapshot?* Setting `config.model` to
[AI] `claude-haiku-4-5-20251001` would make cost figures stable across a future alias
[AI] rollover, and would make `data["model"] == config.model` an assertion worth
[AI] writing. An alias that can silently move is a liability in a project whose whole
[AI] output is a cost comparison. One-word change; LC's call.

[AI] *Blocker clarified 2026-07-31 — a Claude Pro subscription does NOT include
[AI] API access.* LC asked whether his Pro plan could mint the key. It cannot.
[AI] Anthropic bills the consumer plans (Free/Pro/Max) and the API as separate
[AI] products, and the API accepts exactly two credential types: a static
[AI] `sk-ant-api...` key minted in the Console, or Workload Identity Federation.
[AI] Pro includes Claude Code, which authenticates with the *subscription login* —
[AI] not a key that can go in `.env` for `httpx` to use. Getting one means a
[AI] separate Console signup with its own prepaid credit balance.

[AI] *Cost of unblocking, measured rather than guessed:* the live Ollama call was
[AI] 40 in / 48 out. At Haiku's verified rates that is ~$0.0003 per call — about
[AI] three hundredths of a cent, or ~$0.30 per thousand test calls. Cost is not a
[AI] real obstacle to item 6; having a key at all is.

### [AI] 7. Config registry / lookup — DONE 2026-07-31

[AI] *Task:* configs in one place, fetched by `name`. A dict now, a file later.
[AI] *Done when:* Phase 2's router has a single handle to reach for.
[AI] *Resolved:* `config.REGISTRY` (name -> config) plus `get(name)` and
[AI] `by_tier(tier)`. The router calls `by_tier`, never a module constant, so
[AI] adding a third model is a one-line change in `config.py` and nothing else.
[AI] *Note on the raise-vs-failure split:* these raise `KeyError` (listing the
[AI] valid names), unlike the adapter layer which returns `Response.failure`.
[AI] Different kinds of wrong — an unknown config name is a typo in our own
[AI] code with nothing to degrade into, whereas an unreachable provider is a
[AI] runtime condition the router must survive.
[AI] *Verified:* both lookups resolve, and both bad-key paths raise with the
[AI] valid names listed.

[AI] **CORRECTION 2026-08-03 — the "one-line change" claim above is false.** Adding a
[AI] third model is *not* a one-line change in `config.py`. Two independent reasons,
[AI] found separately:

[AI] 1. **`by_tier` returns the first tier match** and `REGISTRY` (`config.py:48`)
[AI]    preserves the insertion order of that tuple. A second config sharing an
[AI]    existing tier silently shadows the incumbent depending on where it lands in
[AI]    the tuple — no error, no warning. Nothing marks a config as "reference-only,
[AI]    never routed to", so the router can reach a config that cannot be called.
[AI] 2. **`router.py:113`'s `tier == "cheap"` gate stops escalating.** See item 10.

[AI] The claim holds only while every tier has exactly one member. `plan.md:32`
[AI] already hedged that `tier` could be an int; that hedge is now load-bearing.

---

### [AI] 8. The router — `router.py` — DONE 2026-07-31 (Phase 2, MVP scope)

[AI] *Task:* given a prompt, choose cheap vs expensive **before** calling.
[AI] `plan.md`'s first listed option — prompt heuristics — chosen because it
[AI] needs no extra model, no extra request, and no training data.
[AI] *Shape:* `classify(prompt) -> (tier, reason)` then
[AI] `route(prompt) -> RouteResult`. `classify` returns the *reason* alongside
[AI] the tier so the demo can show why a prompt routed as it did — a router
[AI] whose decisions can't be inspected can't be tuned.
[AI] *Two tier fields on `RouteResult`, on purpose:* `routed_tier` is what
[AI] `classify` decided, `tier` is what actually answered. They differ only on
[AI] escalation. Caught by running it: the first version printed the *final*
[AI] tier next to the reason for the *original* choice, so an escalated result
[AI] read `EXPENSIVE <- short (26 chars), no complexity keywords`.
[AI] *Savings are an estimate, and the caveat is load-bearing:* `baseline_cost`
[AI] reprices the tokens the chosen model actually produced at the expensive
[AI] tier's rates. The expensive model would have produced a different number of
[AI] them. A true baseline means paying for both calls — the exact cost the
[AI] router exists to avoid — so the estimate is the honest trade, not a shortcut.
[AI] *Verified:* all three `classify` branches (keyword, length, cheap default);
[AI] "improve" correctly does **not** trip the "prove" rule (whole-word matching,
[AI] not substring); escalation fires and reports correctly with Ollama
[AI] unreachable; end-to-end `python main.py` run against live Ollama.

---

## [AI] Items 9 & 10 — found 2026-08-03 tracing `router.py` with LC

[AI] Both came out of walking the router line by line rather than reading its
[AI] output. Neither needs an API key. Both are small. Recorded as work, not done.

[AI] **Both closed 2026-08-19**, plus item 11 (tests) which came out of doing
[AI] them. The "neither needs an API key" note above is why these were the right
[AI] work to pick up after the gap — they were the part of the backlog that no
[AI] external dependency could block.

### [AI] 9. `classify` discards the structure it computes — DONE 2026-08-19

[AI] *Problem:* `classify` cannot report that **both** signals fired, so you cannot
[AI] find out whether `LONG_PROMPT_CHARS` has ever changed a single routing decision.
[AI] Demonstrated: a 500-char prompt containing "design" — 100 chars over the
[AI] threshold — reports only `complexity keyword(s): design`. Keyword hits mask the
[AI] length signal completely, and every prompt where both fire is credited to
[AI] keywords.

[AI] *Two distinct blockers, different in kind:*
[AI] - The early `return` in the keyword branch makes the length check **unreachable**
[AI]   whenever a keyword hits. This blocks *evaluating* both signals.
[AI] - `reason: str` is a presentation type. Even after fixing the above, answering
[AI]   "how many prompts fired length but no keyword?" means regexing English prose
[AI]   out of your own log output. This blocks *analyzing* the result.

[AI] *Structural note worth keeping:* both branches return `"expensive"`, so swapping
[AI] the two `if` blocks changes **zero** routing decisions — only which explanation
[AI] prints. `classify` is a boolean OR across two independent triggers
[AI] (`expensive if (hits or too_long) else cheap`); the two-branch shape exists to
[AI] *report*, not to decide. It is not a "double check" — the second signal can
[AI] neither confirm nor overturn the first, only widen the net.

[AI] *Precedent in this codebase:* `Response.raw` (`adapters.py:130`) keeps the
[AI] untouched provider JSON specifically so nothing downstream re-parses formatted
[AI] output. `classify` has no equivalent — it throws the structure away and returns
[AI] the press release.

[AI] *Done when:* the demo can answer "does the 400-char rule ever route something the
[AI] keyword list would have missed?" If the answer turns out to be *never*, delete
[AI] the rule — the system gets simpler at zero cost. That finding is currently
[AI] unreachable, which is the actual defect.

[AI] *Not in scope:* making the classifier **good**. LC's point stands that the search
[AI] space for a robust classifier is enormous and keyword lists don't generalize —
[AI] `plan.md` parks that in a later phase. This item is instrumentation, not
[AI] modelling. The order matters: you cannot improve a classifier you cannot observe.

[AI] **RESOLVED 2026-08-19.** `classify` now returns a frozen `Classification`
[AI] record — `tier`, `keyword_hits`, `length_chars`, `over_length` — with `reason`
[AI] demoted to a property derived from those fields. Both blockers are gone: the
[AI] early `return` is replaced by evaluating both signals and OR-ing them, and the
[AI] analysis questions are now boolean properties (`length_only`, `both_fired`,
[AI] `keyword_fired`) rather than prose to regex.

[AI] **And the question it existed to answer now has an answer: yes, the 400-char
[AI] rule earns its place.** The demo's own corpus, run 2026-08-19:

```
routing signals
  keyword only     1
  length only      1   <- what the keyword list missed
  both fired       0
  neither (cheap)  2
```

[AI] Prompt 4 (the async-refactor question, 495 chars) contains no word in
[AI] `COMPLEXITY_KEYWORDS` — "walk me through the concrete changes" is not in the
[AI] list and arguably should not be. Length is the *only* reason it routed
[AI] expensive. So `LONG_PROMPT_CHARS` is doing real work, and the "if it never
[AI] fires, delete it" branch of this item does not apply.

[AI] *Caveat on that finding, stated because 4 prompts is not a corpus:* this
[AI] shows the rule fires **at least once** on a set chosen to exercise all three
[AI] branches of `classify`. It does not show the rule is well-*calibrated* — 400
[AI] is still an unjustified constant, and whether it fires on the right prompts
[AI] is unmeasured. The instrumentation is what was missing; it is now there, and
[AI] the tuning it enables has not been done.

### [AI] 10. `tier` is an unordered string, so escalation is hardcoded — DONE 2026-08-19

[AI] *Finding:* `router.py:113`'s `and tier == "cheap"` is **redundant today.**
[AI] `REGISTRY` stores config instances, so `by_tier("expensive")` returns the
[AI] identical object every call. When the expensive tier fails, the guard two lines
[AI] below — `if expensive is not config:` — already evaluates `False` and skips the
[AI] retry. Verified by identity check: same `id()`. Deleting `and tier == "cheap"`
[AI] changes nothing. The demo's two failing prompts are caused by `is not`, not by
[AI] the tier gate.

[AI] *Why it still matters — it is a latent bug, not dead weight.* Add a third tier
[AI] (`"medium"`) and the two versions diverge:
[AI] - **With** the gate: a medium failure never escalates. `tier == "cheap"` is
[AI]   False, the whole block is skipped. Fails **silently** — `escalated=False`, a
[AI]   failed response, and a savings figure that still looks fine.
[AI] - **Without** it: `SMART_CLOUD is not MEDIUM_CONFIG` → True → it escalates,
[AI]   which is the behaviour you would want.

[AI] So the same line is either redundant or a bug depending purely on how many tiers
[AI] exist. This is the second reason item 7's "one-line change" claim is false.

[AI] *Root cause (LC's read, and it is the right one):* the fix is **not** more `if`
[AI] branches — that way lies a hardcoded case per tier pair. `tier` is a bare `str`
[AI] with no ordering, so the code cannot ask "what is the next tier up?" and
[AI] escalation has to be special-cased.

[AI] *Done when:* `route`'s fallback reads "try the next tier up, repeat until one
[AI] answers or you run out" — one loop, any number of tiers, no per-tier branches.
[AI] `plan.md:32` already floated `tier` as an int, which is what makes that possible.
[AI] *Note:* this touches the `RouteResult.escalated` bool too — with N tiers,
[AI] "did it escalate" becomes "how far did it climb."

[AI] **RESOLVED 2026-08-19.** `Tier` is an `IntEnum` (`models.py`) — ordered like
[AI] the int `plan.md:32` floated, but keeping a readable `.name` for output, which
[AI] a bare int would have cost. Values are spaced 10/90 rather than 0/1 so
[AI] inserting a `MEDIUM` does not mean renumbering configs already written.

[AI] The registry gained `above(tier)`, `ladder(tier)`, and `top()`. Those
[AI] questions belong to the registry, not the router — the router should not know
[AI] how many tiers exist, which was the whole complaint. `route`'s fallback is now:

```python
for config in registry.ladder(classification.tier):
    response = send_request(config, prompt)
    attempts.append(response)
    if response.ok:
        break
```

[AI] `escalated` and `climbed` are both properties derived from `attempts`, which
[AI] is kept in full — the failed rungs' errors and latencies survive instead of
[AI] being discarded the moment a retry succeeds. `RouteResult.cost` sums every
[AI] rung rather than billing only the winner.

[AI] **The latent bug was confirmed real before it was fixed**, by replaying the
[AI] old fallback against a synthetic three-tier registry:

```
OLD: escalated=False  answered=False   <- silent failure, savings still looked fine
NEW: escalated=True   answered=True    climbed=1
```

[AI] That scenario is now a regression test
[AI] (`tests/test_router.py::test_middle_tier_failure_escalates`), so the bug
[AI] cannot come back the next time a tier is added. Note what this means about
[AI] review: the defect was invisible in a two-tier registry and needed a third
[AI] tier to surface — reading the two-tier code could not have caught it, which
[AI] is why it survived until the line-by-line trace on 2026-08-03.

[AI] *Still not done, and deliberately:* the ladder only climbs **up**. An
[AI] expensive-tier failure still returns no answer, because there is nothing
[AI] above it. Answering with a *worse* model rather than failing is a different
[AI] product decision, listed in `architecture.md` as a missing piece and not
[AI] taken here. `tests/test_router.py::test_top_tier_failure_has_nowhere_to_climb`
[AI] pins the current behaviour so the choice stays visible rather than becoming
[AI] an accident.

---

### [AI] 11. Test suite — `tests/` — DONE 2026-08-19

[AI] *Why it was added:* the repo had **zero** tests, and items 9 and 10 were both
[AI] the kind of defect that reading the code had already failed to catch once.
[AI] Item 10 in particular was invisible until a third tier existed — exactly what
[AI] a test can construct and a two-tier registry cannot show.

[AI] *What it covers:* 34 tests at the time of writing, across
[AI] `tests/test_contracts.py` (pricing arithmetic, the `Response` contract,
[AI] registry lookups, the tier ladder) and `tests/test_router.py`
[AI] (classification signals, escalation, cost accounting). Items 13 and 14 later
[AI] added `tests/test_capacity.py`, and items 15-17 added
[AI] `tests/test_evaluation.py`, bringing the suite to **81**.

[AI] *Design choices worth stating:*
[AI] - **Stdlib `unittest`, not pytest.** `requirements.txt` says "direct
[AI]   dependencies only"; spending a dependency to assert arithmetic buys
[AI]   nothing this suite needs. `python -m unittest discover -s tests -t .`
[AI] - **No network, ever.** Every test stubs `router.send_request`. The whole
[AI]   suite runs in ~2 ms with Ollama stopped and no API key — which is what
[AI]   makes it runnable by anyone who clones the repo, including a grader.
[AI] - The single patch point is possible *because* of the Phase 1 abstraction.
[AI]   `send_request` being one function with one signature is what makes the
[AI]   router testable; that payoff was not the reason for the design, but it is
[AI]   a real one and worth noticing.

[AI] *Not covered, stated plainly:* the adapters themselves. `_send_ollama` and
[AI] `_send_anthropic` are exercised only by running `main.py` against live
[AI] providers. Testing them properly means either recorded fixtures of real
[AI] provider JSON or a stub HTTP transport, and neither was built. That is the
[AI] largest remaining hole in the suite.

---

## [AI] Items 12–14 — from the audit questions (catch-up period)

[AI] Ten questions in `ai_questions.md` (`Q-0819-1` … `Q-0819-10`) audited the
[AI] system against features it was assumed to have. Most answers were "it does
[AI] not." Three of those gaps became work items; the rest are recorded in
[AI] `ai_questions.md` and deliberately not built.

### [AI] 12. Nothing measures answer quality — OPEN, and this is the big one

[AI] *From `ai_questions` Q-2 and Q-8, which are the same gap from two sides.*

[AI] Cost is measured to six decimals. Quality is not measured at all. The
[AI] asymmetry biases in exactly one direction: a cheap route that produced a
[AI] wrong answer is indistinguishable, in every number the demo prints, from one
[AI] that produced a right answer. Savings look free because the failure mode is
[AI] invisible.

[AI] *Why this is not fixable by trying harder at the classifier:* routing is
[AI] decided **before** the call, so a false positive (complex prompt → cheap
[AI] model) is structurally undetectable. Nothing ever looks at the answer. The
[AI] one datapoint in the whole project — the 2026-07-31 `llama3.2` failure — was
[AI] found by a human reading the output, not by the system.

[AI] *Done when:* a run can report a quality number next to the cost number, so
[AI] the headline reads "N% cheaper, M% quality delta" instead of "N% cheaper"
[AI] with the second half missing.

[AI] *Explicitly NOT attempted.* This is the hard open problem the MVP
[AI] scope note already names, and a half-built version would be worse than none:
[AI] a bad quality metric would license exactly the confident claims this project
[AI] is trying to avoid making. The cheapest honest first step is probably a
[AI] fixed labelled prompt set with human-marked answers — instrumentation, like
[AI] item 9 was, not modelling.

### [AI] 13. Context window was conflated with complexity — DONE 2026-08-19

[AI] *From `ai_questions` Q-5.* `LONG_PROMPT_CHARS = 400` was the project's only
[AI] length number, doing duty as a complexity proxy while the question "will
[AI] this prompt physically fit?" went unasked. Those are different axes.

[AI] *Built:* `ModelConfig.context_window`, `models.estimate_tokens()` (4 chars ≈
[AI] 1 token, rounding up, because underestimating is the dangerous direction),
[AI] and `ModelConfig.fits()` which reserves `max_tokens` for the reply rather
[AI] than letting prompt and completion both claim the whole window. `route()`
[AI] filters the ladder by `fits()` and records what it dropped in
[AI] `RouteResult.skipped_for_capacity`.

[AI] **The genuinely interesting finding, and it is about the local model.**
[AI] `/api/show` reports `llama3.2`'s window as **131072** tokens. That is not
[AI] what it was being served: Ollama applies its own default `num_ctx` unless a
[AI] request overrides it, and nothing here was overriding it — so every local
[AI] call in this project's history ran in a window a fraction of the advertised
[AI] size, silently. The adapter now sends `num_ctx` from the config, which makes
[AI] `ModelConfig.context_window` true rather than aspirational. It is set to
[AI] 8192, not 131072, because the KV cache is real memory on a local GPU.

[AI] **Honest limitation, found by a test that failed.** With today's constants
[AI] the capacity filter **never fires on the demo path**. Overflowing an 8192
[AI] window needs ~29,000 characters; `LONG_PROMPT_CHARS` is 400, so any prompt
[AI] that large was routed expensive by the complexity rule roughly seventy times
[AI] earlier, and the cheap config is never on the ladder to be skipped. The
[AI] first draft of `test_capacity_filter_never_fires_on_the_real_registry`
[AI] asserted the opposite and failed, which is how this was caught.

[AI] So item 13 is a **guard, not a feature in use** — the same shape as item
[AI] 10's finding. It becomes load-bearing the moment a smaller local model, a
[AI] third tier, or a raised `LONG_PROMPT_CHARS` arrives. Both behaviours are
[AI] pinned by tests so the distinction stays visible.

### [AI] 14. Successful calls could be silently degraded — DONE 2026-08-19

[AI] *From `ai_questions` Q-10, plus the truncation finding from the first live
[AI] run.* Two different ways a call returned `ok=True` while the answer was
[AI] quietly wrong, neither of which anything recorded.

[AI] **Truncation.** Both hosted calls in the first live run returned *exactly*
[AI] 1000 output tokens with answers cut off mid-sentence. `ok=True` was the only
[AI] signal available, so a truncated answer was indistinguishable from a
[AI] complete one — while billing the full cap. `Response.truncated` now carries
[AI] it, normalized across providers: Anthropic says `stop_reason == "max_tokens"`,
[AI] Ollama says `done_reason == "length"`. Same fact, two vocabularies, resolved
[AI] inside the adapters exactly as `plan.md`'s design rule requires. Confirmed
[AI] live: the demo now prints `⚠ 2/4 answers TRUNCATED (2000 output tok billed
[AI] at the cap)`.

[AI] **Dropped content blocks.** The Anthropic parser took the **first**
[AI] `{"type": "text"}` block and discarded the rest with no trace — two bugs in
[AI] one line: a reply split across several text blocks lost all but the first,
[AI] and a reply carrying `tool_use` or `thinking` blocks returned empty or
[AI] partial text while still reporting success. Now every text block is joined
[AI] and every non-text type is recorded in `Response.dropped_blocks`.

[AI] *Scope note:* this does **not** add tool-calling support. It stops tool
[AI] calls vanishing quietly, which is the honest half. Actually handling them is
[AI] a later-phase question and is not built. Worth noting `/api/show` reports
[AI] `llama3.2` as tools-capable, so the cheap tier could participate if that
[AI] phase ever happens.

[AI] *Deliberately not built from the audit:* per-request options / SLAs (Q-7)
[AI] and conversation history (Q-9). Both are real gaps; both are features of a
[AI] product this MVP is not trying to be, and adding either would reopen the
[AI] phased buildout the 2026-07-31 scope change closed.

---

## [AI] Items 15–17 — built from the audit questions (catch-up period)

### [AI] 15. Routing accuracy is now measured — DONE 2026-08-19

[AI] *From `ai_questions` Q-2 and Q-8.* Item 12 says measuring answer *quality*
[AI] is unsolved and stays unsolved. This is the step that was available anyway:
[AI] measure whether the router's tier choice agrees with a human judgement of
[AI] which tier the task needed. A proxy for quality, and a coarse one, but the
[AI] project had **no** accuracy number at all before this.

[AI] *Built:* `corpus.py` — 30 hand-labelled prompts, each with the tier it needs
[AI] and a one-line argument for why — and `evaluate.py`, which grades
[AI] `classify()` against them. **No network, no API key, no cost:** `classify()`
[AI] is pure, so the entire routing decision grades offline in milliseconds. The
[AI] part of the system that decides where the money goes is the part that can be
[AI] measured for free.

[AI] **The result, and it is not flattering:**

```
corpus size        30 prompts
correct            15  (50%)
false-cheap        8    <- complex prompt sent to the weak model (dangerous)
false-expensive    7    <- money spent where free would have worked

BY CATEGORY
  obvious              13/13  (100%)
  long-but-simple       0/3   (0%)
  keyword-but-simple    0/4   (0%)
  short-but-hard        0/6   (0%)
  borderline            2/4   (50%)
```

[AI] **50% on a binary decision is a coin flip.** But the flat number is the
[AI] least interesting part — the breakdown is the finding:

[AI] - **100% on the obvious cases.** "What is the capital of France?" routes
[AI]   cheap, "prove √2 is irrational" routes expensive. The heuristic works
[AI]   perfectly where you would not need a router.
[AI] - **0% on every adversarial class.** All six short-but-hard prompts
[AI]   ("Why is my mutex deadlocking?", "Is this SQL injection safe?") route
[AI]   CHEAP, because they are under 400 characters and contain no keyword.
[AI]   These are precisely the prompts where a confidently wrong answer from a 3B
[AI]   model does damage — the failure mode recorded on 2026-07-31, reproduced
[AI]   here six times on demand instead of once by accident.
[AI] - **The two signals fail in opposite directions.** Length produces
[AI]   false-*expensive* (three chatty but trivial prompts routed to Haiku);
[AI]   keywords produce false-expensive too ("What does the word 'refactor'
[AI]   mean?" → EXPENSIVE). Meanwhile nothing at all catches the false-*cheap*
[AI]   cases, which are the costly ones.

[AI] *What this does NOT say.* It does not say the router is 50% wrong in
[AI] production — the corpus is deliberately adversarial, so it is a stress test,
[AI] not a representative sample. It does not measure answer quality; no model
[AI] was called. And it grades against one set of labels, which is the next
[AI] point.

[AI] **Methodological problem, stated rather than buried: the labels were written
[AI] by the AI assistant, not by LC.** That is ground truth authored by an AI,
[AI] grading a router built with AI assistance, in a project whose stated purpose
[AI] includes honesty about where AI was used. `corpus.py` says so at the top and
[AI] `evaluate.py` prints a PROVISIONAL banner on every run. **Every number above
[AI] is a draft until LC reviews the labels.** Disagreements are the valuable
[AI] output — a label LC overturns teaches more than one he accepts, and the
[AI] `borderline` cases were included specifically to provoke that.

[AI] *Done when (still open):* `LABEL_AUTHOR` in `corpus.py` reads `LC` or
[AI] `LC-reviewed`, at which point the banner disappears and the number means
[AI] something.

[AI] **A bug in the corpus itself, caught by a test.** The first draft of the
[AI] `long-but-simple` cases were 322–396 characters against a 400-character
[AI] threshold — one missed by *four characters*. That category scored 100% while
[AI] testing nothing, and the flat accuracy read 60% instead of 50%. Fixed, and
[AI] `test_long_but_simple_cases_actually_exceed_the_threshold` now fails if it
[AI] regresses. A corpus that quietly stops being adversarial is worse than no
[AI] corpus: it produces a flattering number instead of an obviously missing one.

### [AI] 16. An empty reply counted as a successful answer — DONE 2026-08-19

[AI] *From `ai_questions` Q-4.* The router escalated on transport failure only.
[AI] A model that returned `""` satisfied `ok=True`, so the router treated it as
[AI] a successful cheap route and reported 100% savings on nothing.

[AI] *Built:* `Response.has_answer` (`ok` **and** non-whitespace text), and
[AI] `route()`'s loop now breaks on `has_answer` rather than `ok`.

[AI] *Scope, stated narrowly on purpose:* this is the smallest honest reading of
[AI] "low confidence". Empty is not a quality judgement — it is the **absence**
[AI] of a response. Deciding whether a non-empty answer was any *good* is item 12
[AI] and is still unsolved. This must not be mistaken for it.

[AI] *Nice consequence:* it composes with item 14. A reply consisting only of a
[AI] `tool_use` block parses to `text=""`, which now correctly reads as "this
[AI] tier did not answer" and escalates, instead of returning an empty success.

### [AI] 17. Pricing had no provenance — DONE 2026-08-19

[AI] *From `ai_questions` Q-6.* The rates were two hand-typed floats. If a
[AI] provider changed pricing, every cost figure this project publishes would
[AI] become silently wrong and nothing would notice.

[AI] *Built:* `ModelConfig.pricing_updated` (ISO date) and `pricing_source`, plus
[AI] `pricing_age_days()` / `pricing_is_stale()`. `main.py` prints a warning
[AI] **before** the run, not after — every dollar figure below it depends on
[AI] those rates, so a reader should be warned before reading the numbers.

[AI] *Honest about what it is:* nothing here fetches live prices. This does not
[AI] keep pricing correct; it makes the claim **checkable** rather than implicit.
[AI] An undated rate is an unfalsifiable one. The 90-day staleness threshold is a
[AI] placeholder — nothing has measured how often these rates actually move.

[AI] *Worth noting:* the Haiku rates were cross-checked against the billed demo
[AI] run — 1000 output tokens at $5.00/M matched the $0.005025 the config
[AI] computed. That cross-check is why they are trustworthy today; the date is
[AI] how you know when to stop trusting them. The default is the epoch, so a
[AI] config nobody dated reads as maximally stale rather than quietly trusted.

---

## [AI] Phase 1 exit criteria (from `plan.md`)

[AI] One loop sends the same prompt to the cheap config and the expensive config and
[AI] prints both `Response`s side by side: same shape, different `model`, `cost`, and
[AI] `latency_ms`. Once that comparison is visible on screen, the router has every
[AI] input it needs and Phase 2 can begin.
