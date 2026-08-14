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

- Traced the full execution flow from user request through planning, specialist execution, and review.
- Studied how LangGraph manages shared state internally and confirmed how data flows between steps.
- Clarified key design patterns behind the state machine by comparing them to familiar object-oriented concepts.

### Implementation

- Implemented the LLM provider logic to choose between a mock and a real model.
- Built out the full agent hierarchy: a supervisor, four specialist agents, and a reviewer.
- Built the shared state schema and wired all agents into a working LangGraph pipeline.
- Created a minimal terminal script to run a request end to end.
- Built a formal tool registry to manage permissions, rate limits, and logging for every tool call.
- Added conditional logic to the graph for retries, rejections, and escalation.
- Set up environment configuration and wrote a full README for the repository.

### Debugging & Fixes

- Fixed a broken provider stub that referenced an undefined configuration object.
- Fixed an import bug that crashed the app when optional dependencies weren't installed.
- Diagnosed and resolved a missing-dependency error caused by an incomplete install.
- Flagged a file encoding issue that could affect future contributors.

### Design Decisions

- Prioritized a working linear pipeline before adding conditional branching.
- Centralized all tool calls through a single registry instead of letting agents call tools directly.
- Conditional branches remain inactive when using the mock LLM, so only the main flow executes during testing.

### AI Workflow Improvement

- Continued refining Claude's explanation style toward architecture-first reasoning with diagrams and incremental examples.
- Practiced reconstructing execution flow backwards to build a deeper understanding of the system.

---

## Week 3 - August 3-4, 2026

### Architecture Analysis

- Audited Phase 1 against the original guidelines and identified remaining gaps in tool coverage.
- Reviewed the tool registry in detail to reinforce how it manages permissions and logging.
- Discovered that the planning step relies entirely on schema structure rather than an explicit prompt.
- Clarified which parts of the tech stack are mandated versus left to implementation choice.

### Implementation

- Built the two remaining tools required by the guidelines: database queries and generic API calls.
- Connected the Analyst agent to its own tool, closing a gap identified earlier.
- Documented all environment variables needed across tools and providers.
- Fixed compatibility issues so the pipeline works correctly with a real LLM instead of only the mock.
- Made the graph resilient to plans that skip a specialist.
- Switched to a cheaper model for cost-effective testing.
- Surfaced the tool call log in the demo output.
- Enabled the real LLM and ran the first successful end-to-end test.

### Debugging & Fixes

- Fixed a data-type mismatch that only appeared once a real LLM was used.
- Diagnosed a billing-related error from the LLM provider, not a code issue.
- Fixed a crash caused by a real plan skipping a specialist, a fragility flagged earlier.
- Identified a failed tool call and traced its effect on the final output quality.

### Design Decisions

- Prioritized finishing the remaining Phase 1 items over digging deeper into smaller behavior details.
- Added tool-call outputs to the demo script for debugging purposes.

### AI Workflow Improvement

- Continued tracing errors back to their root cause instead of guessing at fixes.
- Used a small real-money test to validate the system functionality.

---

## Week 4 - August 13, 2026

### Architecture Analysis

- Studied how Redis and ChromaDB fit into the system, and what actually separates short-term working memory from long-term semantic memory.
- Learned how semantic search works under the hood, connecting it back to embeddings.
- Audited Phase 2 against the codebase and scoped what could realistically be built in one session.
- Cross-checked a parallel conversation with ChatGPT against the real implementation to confirm the concepts actually held up.

### Implementation

- Built short-term working memory with a graceful fallback when no external store is configured, mirroring how the LLM provider already falls back to a mock.
- Built long-term semantic memory that persists lessons across tasks and gets queried before planning a new one.
- Added memory scoring, consolidation, and expiration, plus small scripts to inspect and delete stored memories.
- Wired memory reads and writes into the existing pipeline without disrupting prior behavior.
- Gave the research step a way to fetch real page content instead of only search-result snippets.

### Debugging & Fixes

- Fixed a shared-reference bug where the fallback memory store leaked data between unrelated tasks.
- Fixed two mistranscribed package versions blocking installation, one of which caused a real dependency conflict.
- Traced why a real query about current GPUs kept returning confident, plausible-looking, and wrong technical specs. (Using an testing prompt)
- Found that a simple text-length filter barely reduced page noise, and rebuilt it after testing showed why.

### Design Decisions

- Refused to accept the first proposed fix for hallucinated answers and instead ran a controlled test isolating whether the cause was missing data or missing instructions.
- Split the reviewer's judgment into two separate checks — writing quality and whether claims are backed by a source — so a well-written answer can still get flagged.
- Decided only reviewed and approved results get saved to memory, so unverified answers can't become a trusted precedent later.
- Connected the plan's declared task order to how the system actually executes it, instead of relying on a fixed sequence.

### AI Workflow Improvement

- Pushed back on proposed solutions and demanded root-cause analysis before allowing any implementation, which changed the fix that was eventually built.
- Verified a technical claim by opening the real source page myself, catching a case where an explanation didn't fully match reality.
- Kept the same discipline from previous weeks: trace problems to their root cause instead of guessing at fixes.