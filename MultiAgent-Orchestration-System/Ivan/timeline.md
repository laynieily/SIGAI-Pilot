# Timeline

**Project Repository:** <https://github.com/IvanIbarra18/Project-15>

---

## Week 1 - July 23, 2026

### Initial Project Analysis

- Read the project guidelines.
- Studied the overall project architecture.
- Reviewed the three-layer agent hierarchy.
- Contacted Laynie to discuss the project structure.
- Contacted Cassandra regarding project coordination.

### Architecture Analysis

- Identified the responsibilities of the Supervisor, Specialist Agents, and Reviewer.
- Analyzed the purpose of the mock LLM provider.
- Investigated the relationship between `provider.py`, `mock.py`, and the future schema models.
- Studied the expected implementation order for Phase 1.

### Design Decisions

- Determined that implementing the schema models is the first development blocker.
- Identified `provider.py` as a potential abstraction layer between real and mock LLM implementations.
- Planned to focus on understanding the complete architecture before implementing code.

### AI Workflow Improvement

- Updated the prompt used with Claude to better match my preferred learning style.
- Shifted toward architecture-first explanations before implementation.

---

## Week 2 - July 30, 2026

### Architecture Analysis

- Traced the full execution flow end to end: intake → planning → specialist execution → review → synthesis, including where human escalation and memory retrieval/writeback are meant to fit.
- Studied LangGraph internals directly in the installed package source: `StateGraph`, `Pregel`, `CompiledStateGraph`, and channels (`LastValue`); confirmed `app.invoke()` returns a plain `dict`, not an `AgentState` instance.
- Clarified that `StateGraph(AgentState)` is parameterization, not inheritance (comparable to Java generics).
- Worked through the `-m` flag, `sys.argv` vs. `input()`, and the difference between `MockLLM.invoke()` and a real LangChain model's `invoke()` (which returns an `AIMessage`, not a plain string).
- Refined the mental model of `AgentState`: it is the data flowing through the graph (the "tape"), not the execution pointer — LangGraph's internal loop is what moves between nodes and decides what runs next.

### Implementation

- Implemented `LLMProvider.get_llm()`: selects `MockLLM`, `ChatAnthropic`, or `ChatOpenAI` based on `USE_MOCK` / `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`.
- Fixed `Supervisor.py` and implemented `Researcher.py`, `Analyst.py`, `Writer.py`, and `Reviewer.py`.
- Added `AgentState` to `src/schemas/models.py` as the shared state schema for the graph.
- Built `src/graph/graph.py`, wiring all agents into a runnable LangGraph state machine.
- Built `scripts/run_demo.py` as a minimal terminal entry point to run a request end to end.
- Added a sixth specialist, `CodeExecutor`, with its own `code_execution` tool, and updated the mock plan to include it.
- Built a formal Tool Registry (`src/tools/registry.py`, `src/tools/setup.py`) — tool name, description, allowed specialists, and rate limits, with per-call logging — and routed `Researcher`, `Writer`, and `CodeExecutor` through it instead of importing tools directly.
- Added three conditional edges to the graph: low-confidence escalation (stub), retry-on-specialist-failure (capped), and reviewer-rejects → loop back to Writer (capped) — tuned so the current mock LLM stays on the happy path.
- Set up `.env` and `.env.example` with documented environment variables.
- Wrote a full `README.md`: status-by-phase table, architecture diagram (Mermaid), tech stack, setup/run instructions, project structure, and known caveats.

### Debugging & Fixes

- Fixed a broken `provider.py` stub that referenced an undefined `settings` object.
- Fixed a bug where `Researcher`/`Writer` imported optional dependencies (`serpapi`, `markitdown`) at module load time; switched to lazy imports so the demo runs without them installed.
- Diagnosed a `ModuleNotFoundError: No module named 'dotenv'` caused by a partial `pip install -r requirements.txt`; resolved by reinstalling.
- Flagged that `requirements.txt` was saved in UTF-16 (likely from `pip freeze` in PowerShell) as a portability risk for future contributors.

### Design Decisions

- Scoped the first working version to a linear "happy path" before adding conditional edges, in order to get an end-to-end demo running within a single session.
- Decided the Tool Registry should mediate every tool call (permissions, rate limits, logging) instead of specialists importing tools directly.
- Tuned the new conditional edges so two of the three branches are deterministically dormant under `MockLLM` by construction, and capped the third (content-dependent) branch with a retry limit as a safety net.

### AI Workflow Improvement

- Continued refining Claude's explanation style: architecture-first (responsibility, caller, callee, why it exists), short diagrams over long paragraphs, explicit class-vs-instance distinctions, Java comparisons, and incremental build order (concept → diagram → small example → real example → code).
- Used a "reconstruct execution backwards" approach (who calls this, where does this come from) to build a deeper mental model of LangGraph, including reading the actual installed library source code for grounding rather than relying on assumptions.

---


