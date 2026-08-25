# LLM Cost Autopilot - Development Timeline

Repository:
[Bethany's GitHub Repository Link](https://github.com/BethanyTijerina/LLM-Cost-Autopilot.git)

## Project Overview

The goal of this project is to create an intelligent LLM routing system that reduces unnecessary AI costs by selecting the most appropriate model based on prompt complexity while maintaining acceptable response quality.

The system currently includes:
- Model Registry for storing model information
- Provider abstraction layer, now backed by real Ollama and OpenAI providers behind a MultiProvider dispatcher (Mock provider still used for tests)
- A trained machine learning complexity classifier (rule-based version kept for comparison/tests)
- Routing system with a multi-factor model scoring system (cost, quality, latency)
- Asynchronous quality verification and escalation logging
- A classifier retraining feedback loop built from escalation events
- Routing decision logging to both JSON and SQLite
- A FastAPI service (`/v1/completions`, `/v1/models`, `/v1/stats`, `/v1/routing-config`, `/health`)
- A Streamlit cost dashboard
- Docker/docker-compose support for the full stack


## Day 1 (7/17-7/20/2026)

Created the project repository and established the initial architecture.

Instead of immediately implementing application logic, I focused on designing how the different components would communicate. I created the initial ModelConfig dataclass and began building the Model Registry to store information about available language models.

Key decisions:
- Use Python dataclasses for structured model information.
- Use Git from the beginning to track development progress.
- Design the architecture before implementing advanced features.


## Day 2 (7/21/2026)

Implemented the provider architecture by creating:
- LLMResponse dataclass
- BaseProvider abstract class
- MockProvider implementation

The purpose of this architecture was to allow different AI providers to follow the same interface. This allows real providers to be added later without changing the rest of the system.


## Day 3 (7/23/2026)

Created the first Router implementation.

The Router allowed the workflow:

Prompt
↓
Router
↓
MockProvider
↓
LLMResponse

I also learned that running Python tests directly can cause import issues in larger projects. I switched to using pytest from the project root for more reliable testing.


## Day 4 (7/27-7/28/2026)

Implemented the first version of the complexity classifier.

Instead of immediately using machine learning, I created a rule-based classifier as a baseline.

Implemented:
- YAML configuration for classifier rules
- Weighted keywords
- Complexity scoring system

This allowed the classification logic to be modified without changing Python code.


## Day 5 (7/28-7/29/2026)

Connected the complexity classifier to the Router.

The Router was updated so model selection was no longer hardcoded.

New workflow:

Prompt
↓
Complexity Classifier
↓
Complexity Tier
↓
Model Registry
↓
Provider
↓
Response


## Day 6 (7/29/2026)

Improved Router architecture.

Changes:
- Router now receives dependencies instead of creating them internally.
- Added configuration loading utility.
- Expanded routing configuration to support multiple candidate models.

This improved testing and made future provider expansion easier.


## Day 7 (7/30/2026)

Improved model selection by replacing simple cost-based selection with a scoring system.

The Router now considers:
- Model quality
- Cost
- Latency

Added:
- model_scoring.py
- selection_score tracking in LLMResponse

This allows routing decisions to be analyzed instead of only returning the selected model.


## Day 8 (8/05-8/06/2026)

Improved testing and added routing decision logging.

Fixed a model scoring test that had been comparing two real models differing in cost, quality, and latency all at once — rewrote it with synthetic models that differ only in quality, so it actually isolates what it claims to test.

Added `routing_logger.py` to record the prompt, complexity tier, selected model, and selection score for every routing decision. Found that the Router was passing a model ID string into the logger instead of the full model object, causing an AttributeError. Fixed by passing the object itself.

All 11 tests passed after both fixes.


## Day 9 (8/07-8/08/2026)

Expanded logging and began closing the larger architectural gaps.

Extended the routing log schema with prompt hash, cost, latency, quality score, and escalation status, then added SQLite storage alongside the existing JSON logs so routing data can be queried instead of only read line-by-line.

Began replacing the rule-based complexity classifier with a machine learning approach:
- Drafted a labeled dataset of 210 prompts (70 per tier)
- Built feature extraction (5 numeric features per prompt)
- Trained a Random Forest classifier — 83.33% accuracy on the first run, clearing the 80% bar
- Wrapped it as `MLComplexityClassifier`, matching the same `classify(prompt)` interface as the original classifier so it could swap in without touching the Router

Also built the quality verification and escalation system (`QualityVerifier`, `escalation_logger.py`) so a routed response can be checked against a reference model and escalated when they disagree too much.


## Day 10 (8/08-8/09/2026)

Connected the components that had been built separately.

Wired both `MLComplexityClassifier` and `QualityVerifier` into the Router. Along the way, found that the mock response templates didn't produce agreement scores that were monotonic with quality tier — no threshold could correctly separate them — and fixed it by redesigning the templates as strict nested word-subsets. Added a test fixture that trains the classifier automatically during testing instead of depending on a pre-existing model file.

New workflow:

Prompt
↓
ML Complexity Classifier
↓
Model Scoring
↓
Provider
↓
Routing Log (JSON + SQLite)
↓
Quality Verifier → Escalation Log (if needed)

All 20 tests passed after full integration.


## Day 11 (8/11-8/15/2026)

Built the FastAPI service (Phase 5) — the project's first real API layer.

Learned FastAPI fundamentals in a disposable playground file first, then built for real: Pydantic request/response models for `/v1/completions`, a `Depends(get_router)` pattern so the Router and its dependencies are built once at startup instead of per-request, and a fail-fast startup check for a missing trained classifier file.

Added the remaining endpoints:
- `GET /v1/models` — lists the model registry
- `GET /v1/stats` — actual cost vs. hypothetical gpt-4o-only cost
- `PUT /v1/routing-config` — updates tier-to-model mappings in memory, with validation (real tier, real model names, non-empty list)
- `GET /health`

Found and fixed several real bugs along the way: `uvicorn` needing `PYTHONPATH` set manually (unlike pytest), a stale SQLite schema rejecting new log columns, `/v1/stats` crashing on a fresh database because `init_db()` was never called at startup, and a pytest collection-time crash caused by the app building its ML classifier at import time. Wrote automated tests with `TestClient`. Phase 5 finished with 25 tests passing.


## Day 12 (8/17/2026)

Checked the project against the original roadmap before continuing, to make sure nothing had drifted. Confirmed Phase 5 was genuinely complete and that real provider integration — swapping in real APIs behind the existing `BaseProvider` interface — was the natural next step.


## Day 13 (8/20-8/21/2026)

Began real provider integration.

Built `OllamaProvider` first, since it can be tested locally with no API cost — learned Ollama's REST API shape, then implemented timing, token counting, cost calculation, and error handling, verified against a real local server.

Built `MultiProvider`, a dispatcher that also implements `BaseProvider`, so the Router can keep depending on one interface while requests get routed to the correct real provider based on the model's `provider` field. Fixed an import-path bug (a bare import instead of the full dotted path) and renamed the registry's Ollama model id to match Ollama's real model tag.

Swapped `MockProvider` for `MultiProvider` in the API and got an expected `Unsupported provider: OpenAI` error — confirmed this was the dispatcher correctly refusing to guess, not a bug, since OpenAI wasn't registered yet. Wrote provider tests using mocked HTTP calls, cutting real test time from ~48 seconds to ~0.09 seconds with zero server dependency.

Also finished the remaining structural work: made verification asynchronous (runs as a background task after the response is already returned), built the classifier retraining feedback loop from escalation events, built the Streamlit cost dashboard, and added Docker/docker-compose support. Verified Docker with an actual build and run — not just a read-through of the YAML — and caught a real `localhost`-inside-a-container networking bug in `OllamaProvider` along the way.


## Day 14 (8/21-8/24/2026)

Built `OpenAIProvider` using the official SDK, now that a real API key was available. Verified it with a real request before and after writing the implementation — correct output, real token counts, real cost and latency, which replaced the registry's placeholder latency figure.

Wiring it into `MultiProvider` surfaced two real bugs: eager provider construction meant just creating `MultiProvider()` required every registered provider's credentials, including ones not in use — fixed by making provider construction lazy. Separately, `test_api.py` started making real OpenAI calls once `MultiProvider` replaced `MockProvider` app-wide — fixed with a FastAPI dependency override so tests stay on `MockProvider`.


## Day 15 (8/24/2026)

Decided to skip implementing `AnthropicProvider` — the multi-provider pattern was already proven with a cloud provider and a local provider, so a third one of the same shape wasn't worth the remaining time versus finishing Phase 6. Removed the unused Claude models from the active routing config while keeping them in the registry, since existing tests still relied on that data.

Ran the final Phase 6 load test: sent the project's own 210-prompt labeled dataset through the real, running API. All 210 succeeded, 0 errors, under $0.50 in real API cost.

Building the savings report caught two real bugs before trusting any numbers: the first version mixed this run's data with days of prior manual testing, and the fix that followed still leaked historical rows through a prompt-hash match. Fixed by matching the exact rows from this run by database id, with an integrity check. Investigated the results instead of just reporting them — found that `gpt-4o` was 31% of requests but 98.8% of cost (token volume, not request count, drives cost), and hand-checked a suspiciously high 36.2% escalation rate, finding all three checked cases were correct answers that the word-overlap verifier had simply scored as disagreeing.

Final, clean numbers: 16.3% cost savings, 87.1% classifier accuracy, 0 request errors. Published as a case study.


## Current Stage

Phases 1 through 6 are complete. Real Ollama and OpenAI providers run behind `MultiProvider`; Anthropic was deliberately skipped. Verification is asynchronous with a working classifier-retraining feedback loop. The dashboard is live, Docker builds and runs the full stack, and a real 210-request load test against the live system produced a published case study with honestly-caveated results. 58 tests passing, 0 known failures.

Future work (not blocking):
- Replace word-overlap verification with semantic/LLM-as-judge scoring
- Feed the load test's real misclassifications into a retraining run
- Revisit Anthropic support if a concrete need for it comes up
