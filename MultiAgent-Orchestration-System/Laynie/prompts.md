# Claude Prompts Log

## Getting Started

- Asked for a general background rundown on agentic AI before starting, to build context for the project.
- Shared the full Project 15 spec and initially asked for help getting the repo scaffolded.
- Decided against having it fully built for me — switched to a guided approach: scaffolds with TODOs, I write the actual implementation, code gets verified by running it rather than trusting it at a glance.

## Phase 1 — Agent Architecture

- Built core Pydantic schemas (`SubTask`, `ExecutionPlan`, `SpecialistResult`, `ReviewResult`, `EscalationEvent`, etc.) in `src/schemas/models.py`.
- Built the tool registry (`src/tools/registry.py`) with per-agent authorization, rate limiting, and call logging.
- Built built-in tools (`web_search`, `file_read`/`file_write`, `code_execution`, `db_query`, `api_call`) in `src/tools/builtin.py`.
- Built the Reviewer, Supervisor, and Specialist agents.
- Built `MockLLM` and a provider selector (`get_llm`) so the whole system runs for free during development and swaps to a real model automatically when an API key is present.
- Fixed a long list of bugs surfaced by actually running the code: enum casing/value mismatches, an inverted authorization check, a rate-limit boolean/string bug, an early-return bug in `web_search`, and several typos.

## Phase 2 — Memory System

- Chose in-memory/embedded stand-ins over real infra (no Redis, no external vector DB) — deferred to a later Docker phase.
- Built short-term working memory (`WorkingMemoryStore`) as a per-task in-memory dict.
- Built long-term semantic memory (`LongTermMemoryStore`) on ChromaDB: recording task summaries, querying similar past tasks, an importance score (access count decayed by age), stale-memory expiration, and a dashboard view.
- Wired long-term memory into the Supervisor's planning prompt so past tasks inform future plans.
- Skipped memory consolidation (merging duplicate memories) as out of scope for now.

## Phase 3 — Human-in-the-Loop

- Converted escalation stubs into real pause/resume behavior using LangGraph's `interrupt()` and `Command(resume=...)`, backed by `MemorySaver` and a `thread_id`.
- Built `escalate_plan` (low-confidence plans get routed to a human for approve/reject) and `escalate_subtask` (subtasks that exhaust retries get routed to a human for accept/take-over/abort).
- Debugged extensively: state keys silently dropped because they weren't declared in the `OrchestratorState` TypedDict, routing functions wired to the wrong conditional edges, a missing `else` branch that treated "abort" the same as "accept," and a case where an entire `return` statement went missing during a cleanup edit.
- Verified all four resolution paths (reject, approve, abort, take-over) end to end before moving on.

## API Layer (FastAPI)

- Designed a backend exposing task creation and the approval queue over HTTP: `POST /tasks`, `GET /approvals`, `GET /approvals/{id}`, `POST /approvals/{id}/resolve`.
- Key design point: the compiled LangGraph app and `ApprovalQueue` have to be process-wide singletons (not rebuilt per request), since `MemorySaver` checkpoints only live in that one instance.
- Added a `/chat` endpoint and a WebSocket endpoint for live updates (broadcasting still needs to be wired up).
- Verified the full pause/resume loop over real HTTP with PowerShell — submit a task, see it pause, list the approval, resolve it, confirm the graph resumes and completes.
- Found and fixed several bugs along the way: a missing `prefix` argument to `new_id()`, a `persist_dir=...` placeholder left in as literal code, `provider.py` and `mock.py` having gotten their contents swapped at some point, and a missing `TaskHistoryItem` import that broke the whole app at startup.

## Frontend (React)

- Chose React over Streamlit for the review UI.
- Built `Dashboard`, `Chat`, `Approvals`, and `Escalations` pages with React Router.
- Debugged frontend/backend contract mismatches: wrong API paths (`/api/...` prefixes that don't exist), a resolve payload using the wrong field name and value (`action`/`"approve"` instead of `decision`/`"approved"` — which would have silently treated every approval as a rejection), and response fields that didn't match what the backend actually returns.
- Extended `Approvals.tsx` to branch on escalation level and show different action buttons: Approve/Reject for plan-level escalations, Accept/Take-over/Abort for subtask-level ones.
- Added request history to the Dashboard (backend tracks each request's text and status; frontend lists them).
- Ran a full-repository audit to catch anything not yet exercised by manual testing — found a code-execution tool authorization mismatch, a `web_search` bug that silently capped results at 1, and a stray `Ellipsis`-named folder from the `persist_dir` bug.

## Still Open

- Wire up WebSocket broadcasting so the Approvals page updates live instead of only on page load.
- Decide the fate of `Escalations.tsx` (currently dead code pointing at nonexistent routes) — likely repurpose it into a resolved-history view using the already-built `GET /approvals/history` endpoint.
- Docker Compose, observability/tracing, and final portfolio polish (Phases 4–6 of the original plan) haven't been started yet.
