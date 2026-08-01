# [AI] Progress & Work Queue

[AI] Written by the AI assistant on 2026-07-28 at Luis Chavez's request.
[AI] Every line in this file is `[AI]`-authored unless later edited and marked `[LC]`.
[AI] Purpose: a running snapshot of where Phase 1 stands and what order the
[AI] remaining work gets done in. Companion to `plan.md` (the design) and
[AI] `Documentation.md` (the narrative session log). This file is the checklist.

---

## [AI] Where the project stands (2026-07-29)

[AI] Phase 1 is the unified model interface: `send_request(config, prompt) -> Response`.
[AI] Both data contracts exist in `models.py`, and `config.py` now holds the two
[AI] concrete configs the router will choose between. Nothing calls a provider yet.

[AI] **Done:**
[AI] - `Response` dataclass — build order step 1.
[AI] - `ModelConfig` dataclass *and both instances* — build order step 2 complete.
[AI] - Cost formula placed on `ModelConfig.price()` rather than duplicated per adapter.
[AI]   The pricing rates live on the config, so the formula that consumes them lives
[AI]   there too; `Response.cost` stores the resulting number as a fact about one call.
[AI] - `requirements.txt` manifest — `httpx`, `python-dotenv`; direct dependencies only.
[AI] - `.gitignore` covers `__pycache__/` and `*.py[cod]` — bytecode is a derived
[AI]   artifact, regenerated on import, machine- and interpreter-version-specific.

[AI] **Not started:**
[AI] - No adapter. `main.py` is still the original throwaway POST script that
[AI]   prints a raw dict, and nothing consumes `config.py` yet.
[AI] - No config registry — `CHEAP_LOCAL` / `SMART_CLOUD` are module constants (item 7).

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

### [AI] 2b. `Response.summary()` — human-readable output — QUEUED

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

### [AI] 5. Ollama adapter — refactor `main.py` into `send_request(config, prompt)`

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

### [AI] 6. Second adapter behind the same signature

[AI] *Task:* Anthropic or OpenAI, same `send_request` signature.
[AI] *Done when:* swapping only the `ModelConfig` changes which provider answers,
[AI] with zero changes at the call site. This is the proof the abstraction holds.
[AI] *Note:* model IDs and per-token prices should be verified against current
[AI] provider documentation at the time of writing, not recalled from memory or
[AI] copied out of `plan.md` — those values change.

### [AI] 7. Config registry / lookup

[AI] *Task:* configs in one place, fetched by `name`. A dict now, a file later.
[AI] *Done when:* Phase 2's router has a single handle to reach for.

---

## [AI] Phase 1 exit criteria (from `plan.md`)

[AI] One loop sends the same prompt to the cheap config and the expensive config and
[AI] prints both `Response`s side by side: same shape, different `model`, `cost`, and
[AI] `latency_ms`. Once that comparison is visible on screen, the router has every
[AI] input it needs and Phase 2 can begin.
