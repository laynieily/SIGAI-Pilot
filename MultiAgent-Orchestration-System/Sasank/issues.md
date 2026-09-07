# Issues

Running log of bugs, blockers, and unexpected behavior. For each entry: what went wrong,
how it was diagnosed, how it was resolved (if applicable), and any lessons learned.

## Supervisor occasionally plans zero steps, and the pipeline silently continued anyway
**What went wrong:** In a smoke test, `supervisor.plan()` (llama3.1:8b via Ollama, JSON-schema
constrained output) returned `{"steps": []}` — schema-valid, but empty. `main.py`'s step loop
then had nothing to iterate, so `web_research.run()` never executed and no search happened.
`supervisor.synthesize()` was still called with an empty `step_results` list and produced a
fully confident-sounding answer straight from the model's training data (dated ~2023) with no
indication anything had gone wrong.

**How it was diagnosed:** The final answer's "as of my last update in 2023" phrasing looked
wrong for a research-backed answer. Checked `traces/run_*.json` and found `"plan": []` and no
`step_completed` events — confirmed the loop never ran research at all.

**How it was resolved:** `supervisor.plan()` now retries (up to 3 attempts) if the model
returns zero steps, and raises `RuntimeError` if every attempt comes back empty, instead of
letting the pipeline continue on empty state.

**Lesson learned:** JSON-schema-constrained output guarantees the *shape* is valid, not that
the *content* is non-degenerate — an 8B local model can satisfy the schema with an empty array.
Any step whose output feeds a loop (`for step in state.plan`) needs an explicit non-empty
check; a schema constraint alone isn't enough to catch this failure mode. Also: a pipeline
stage that silently no-ops (empty loop) is worse than one that errors — the synthesis step
happily produced a plausible-looking answer with zero real inputs, which is a much more
dangerous failure than a crash.

## Specialist narrates a tool call as text instead of actually invoking it, and can fabricate data as a result
**What went wrong:** During the first chained web_research + data_analysis smoke test,
`llama3.1:8b` responded to a tool-calling prompt with plain text describing what it intended
to do (`"I'll call the search_web tool... {"name": "search_web", "parameters": {...}}"`)
instead of using Ollama's actual `tool_calls` mechanism. Both `web_research.run()` and
`data_analysis.run()` check `message.get("tool_calls")` and treat an empty list as "the model
is done, this is the final answer" — so this narrated-but-unexecuted call was accepted as a
real finding. Step 1's "research" came back essentially empty. Step 2 (data analysis) then had
no real data to compute from, and rather than surfacing that, the model **invented** plausible
US city population numbers ("Let's say the numbers are... 8,420,527...") and ran real,
correct math on that fabricated data — a confident-looking, internally-consistent, entirely
made-up result.

**How it was diagnosed:** Caught by reading a HITL escalation transcript, not by an automated
check. The reviewer actually did its job correctly on both steps (flagged "no actual results"
on step 1, "missing source citation" on step 2) and both escalated to the terminal prompt as
designed — but the test script blindly piped `a` (approve) to every prompt without a human
reading them, so the fabricated numbers sailed through to the final synthesized answer anyway.

**How it was resolved:** Added `_looks_like_unexecuted_tool_call()` to both `web_research.py`
and `data_analysis.py` — a heuristic check (tool name plus `"parameters"`/`"arguments"`/`"name"`
substrings) that runs whenever `tool_calls` comes back empty. If the content looks like a
narrated-but-unexecuted call, it's not accepted as final; instead a corrective message is
appended ("use the tool-calling mechanism directly, don't write the call as JSON text") and
the loop retries, consuming one of `MAX_TOOL_ROUNDS` rather than exiting early. Re-ran the same
task that triggered the bug: no recurrence — both specialists produced real, tool-backed
results (genuine search URLs, a computed figure that doesn't match naive hand-rounding of the
inputs), and the two escalations that did occur were the reviewer legitimately wanting tighter
citations, not fabrication.

**Lesson learned:** Two separate things went wrong at two separate layers, and both matter:
(1) tool-calling APIs don't guarantee the model actually uses them — same *shape-vs-content*
class of bug as the empty-plan issue above, just one layer further from the initial fix, and
worth a code-level guard rather than relying solely on the reviewer to catch it downstream.
(2) HITL is a real safety mechanism, not a checkpoint that can be rubber-stamped — this run
is a concrete demonstration of what happens when a human approves without reading: fabricated
data reaches the final answer looking exactly as credible as real data.

## Supervisor split a coder task into "write code" then "run code" as two separate steps, which the architecture can't support
**What went wrong:** First full-pipeline test of the coder specialist. The task needed one
`coder` step (research populations, then compute a percentage). The supervisor instead planned
*two* consecutive `coder` steps: step 2 "Write code... to calculate the percentage" and step 3
"Run the Python script written by coder... to get the final result." But each specialist call
in this system is a fresh, stateless conversation — a step only receives the *findings text*
of prior steps as context (see `run_specialist()` in `main.py`), never the literal code from an
earlier step. Step 3's specialist had no real code to run, so it fabricated a plausible excuse
("The code I provided earlier resulted in a syntax error...") about code it had never actually
seen. The reviewer correctly rejected both coder steps and escalated to HITL each time — the
final synthesis recovered a roughly correct answer anyway (~68%, in the right ballpark) by
just redoing the calculation itself, but only by accident, not because the pipeline worked as
designed.

**How it was diagnosed:** Read the HITL transcript, noticed step 3's instruction ("Run the
Python script written by coder") implied state that doesn't exist in this architecture, then
confirmed by inspecting `traces/run_20260825T025147Z.json`'s `plan` array directly — two
separate `coder`-specialist steps for what should have been one.

**How it was resolved:** Clarified `supervisor.py`'s `_PLAN_SYSTEM` prompt: the `coder`
specialist description now explicitly states it writes AND executes code within a single
step, and instructs the model never to split "write the code" and "run the code" into
separate steps.

**Lesson learned:** This is a different failure class from the previous two — not a model
executing incorrectly, but the *supervisor's plan* assuming architecture that doesn't exist
(persistent code/state across steps). Schema-constrained planning guarantees each step is a
well-formed `{instruction, specialist}` pair; it says nothing about whether the *sequence* of
steps is achievable given how specialists actually communicate (findings text only, no shared
state). Worth remembering for specialist #4+ or the distributed-machines phase: any time a new
capability is added, the planning prompt needs to explicitly state what context does and
doesn't carry between steps, not just what the specialist is generically capable of.

## Supervisor's plan sometimes echoed the specialist name as the whole instruction
**What went wrong:** Sampling `supervisor.plan()` repeatedly on the same coder-involving task
surfaced a second, unrelated bug: in 3 of 4 runs, at least one step came back with
`instruction` set to literally just the specialist's own name (e.g. `"web_research"`, with
nothing else) — schema-valid, but content-free. This is the same shape-vs-content gap as the
original empty-plan bug, just showing up per-step now that steps carry two fields instead of
one.

**How it was diagnosed:** Ran `supervisor.plan()` directly (bypassing the full pipeline) on the
same task several times in a row and printed each plan's raw steps — the pattern was frequent
enough (3/4) to be systematic, not a one-off.

**How it was resolved:** Two layers: (1) added `_is_degenerate_instruction()` — a runtime check
in `plan()`'s retry loop that rejects any step whose instruction is under 10 characters or
exactly matches a specialist name, forcing a retry the same way the empty-plan check does.
(2) A structural fix at the schema level: added `"minLength": 15` to the `instruction`
property in `_PLAN_SCHEMA`. Verified directly that Ollama's grammar-constrained decoder
actually enforces this (it does) — the model becomes structurally unable to emit a
14-character-or-shorter string, not just likely to avoid it. After both fixes: 0 degenerate
instructions across several repeated re-runs of the same task that previously failed 3/4 times.

**Lesson learned:** When a runtime heuristic check and a JSON-schema constraint can both catch
the same failure, the schema constraint is strictly better — it prevents the bad output at
generation time instead of detecting it after the fact and spending a retry. Worth checking
first, for any future "the model produced valid-but-degenerate content" bug, whether the
degeneracy is expressible as a schema constraint (`minLength`, `pattern`, `not: {const: ...}`)
before reaching for a runtime heuristic.

## Coder specialist can genuinely execute correct code and still misstate the real result
**What went wrong:** During coder-specialist smoke testing, found the model sometimes writes
correct code, gets a correct result from `run_python` (e.g. real captured stdout `675.93`), and
then states a *different, wrong* number in its final plain-text answer (e.g. "67.59%" — its own
correct result divided by 10, for no evident reason). This happened in 2 of 3 repeated trials
on the same task. A related but separate issue also showed up 3/3 times: the model would
mistranscribe a large comma-formatted number from the instruction into code (`122,407,682` in
the prompt became `12407682` in the code — a dropped digit), so even a "correct" execution was
sometimes computing on already-corrupted input.

**How it was diagnosed:** Instrumented `coder.run()`'s loop directly (temporary script printing
each round's tool call, real captured stdout, and the model's final text) across several runs,
and compared the real captured `stdout` value against the number stated in the final answer —
they didn't always match, even when execution succeeded cleanly (`returncode: 0`, no error).

**How it was resolved:** Not fixed — logged as a known, accepted limitation. Two structural
fixes were already added first (both real, working fixes, not addressing this specific issue):
`coder.py`/`data_analysis.py` now track `had_successful_execution` and refuse to accept a final
answer until at least one real, error-free tool call has happened (previously a model could
finalize an answer after zero successful executions). That closes the "answered with literally
no real computation" gap, but doesn't guarantee the final paraphrase is *faithful* to the real
result once a successful execution does occur — that would need extracting the real value from
captured stdout programmatically and templating it into the findings directly, rather than
trusting the model to restate a number it already computed, which is a genuinely bigger
architectural change (shifting from "the LLM writes the summary" to "code post-processes the
LLM's tool output"). Decided not to build this now — HITL is the intended backstop for exactly
this kind of thing, and a human reading the escalation prompt can sanity-check a stated
percentage against the numbers shown.

**Lesson learned:** "The model called the right tool and got the right answer" is necessary but
not sufficient for a trustworthy final result — the last, easy-to-overlook link in the chain is
whether the model's own closing sentence actually reflects what the tool returned. Three
distinct failure layers exist for tool-using specialists, each needing a different kind of
fix: (1) not calling the tool at all (narrated JSON — code-level pattern guard), (2) calling it
zero times successfully before answering (no execution at all — code-level state tracking,
`had_successful_execution`), (3) calling it successfully but misreporting the result in
prose (paraphrase drift — not closeable without bypassing the model's own summary for the
number itself). Each layer needed a different, increasingly invasive fix; this project is
stopping at layer 2 for v1 and documenting layer 3 as a known local-model characteristic rather
than chasing it further.
