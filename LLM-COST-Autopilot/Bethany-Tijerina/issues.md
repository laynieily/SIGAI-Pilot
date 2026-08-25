# Issues and Solutions


## Router Import Error: Missing get_model Function

### Problem

The Router failed during testing because it attempted to import get_model from the Model Registry, but the function did not exist.

### Diagnosis

The Model Registry stored models and had a function to retrieve all models, but the Router needed a way to retrieve one specific model.

### Solution

Added:

get_model(model_id)

This allowed the Router to request a single model configuration without directly accessing the registry.

### Lesson Learned

Components should interact through defined functions instead of depending on internal data structures.


---


## Complexity Classifier Returned Incorrect Complexity Tier

### Problem

A complex prompt test returned the wrong complexity tier.

### Diagnosis

The classifier was not checking the actual keyword values from the YAML configuration. It was checking dictionary categories instead.

### Solution

Updated the classifier to properly iterate through keyword values and added weighted scoring.

### Lesson Learned

Configuration structure directly affects program behavior. YAML files should be designed carefully because they influence application logic.


---


## Router Moderate Prompt Test Failed

### Problem

The Router selected the wrong model for a moderate complexity prompt.

### Diagnosis

The YAML routing configuration was incorrectly structured. The moderate keyword section was nested under formatting instead of being its own category.

### Solution

Fixed the YAML indentation and updated the classifier to support moderate keywords.

### Lesson Learned

Configuration files are part of the application logic. Small formatting errors can change program behavior.


---


## Router Dependency Design

### Problem

The Router originally created its own MockProvider internally.

### Diagnosis

This made the Router depend on one specific provider implementation and made testing less flexible.

### Solution

Changed the Router to receive a BaseProvider through its constructor.

### Lesson Learned

Dependency injection makes systems easier to test and allows components to be replaced without modifying existing logic.


---


## Model Selection Strategy Changed

### Problem

Previous tests expected the Router to always select the cheapest model.

### Diagnosis

The project requirements changed from cost-only selection to a scoring system that balances cost, quality, and latency.

### Solution

Created model_scoring.py and updated Router selection logic.

### Lesson Learned

When system behavior changes, tests need to represent the current design goals rather than previous assumptions.


---


## Adding Selection Score to LLMResponse

### Problem

After adding model scoring, the Router calculated a score internally but the result was not stored anywhere for analysis.

### Diagnosis

The Router selected the best model correctly, but the reasoning behind the decision was lost after the request was completed.

### Solution

Added selection_score to LLMResponse and updated the Router to return both the selected model and score from _select_best_model(). The score is now attached to the response after model selection.

### Lesson Learned

When a system makes decisions, storing the information behind those decisions improves debugging, logging, and future analysis.


---


## Quality Scoring Test Compared the Wrong Variables

### Problem

test_high_quality_model_gets_quality_bonus asserted that a higher-quality model should score above a medium-quality one, but the higher-quality model scored lower (15.7 vs 18.05).

### Diagnosis

The test compared two real registry models (gpt-4o vs gpt-4o-mini) that differed in cost and latency at the same time as quality, so the cost penalty and latency difference were canceling out the quality bonus. The scoring formula itself was not wrong — the test could not isolate what it claimed to be testing.

### Solution

Rewrote the test using two synthetic ModelConfig objects with identical cost and latency, differing only in quality_tier. This proved the quality bonus in isolation instead of asserting a specific real-model pair must always rank a certain way.

### Lesson Learned

A good test should isolate the one variable it claims to test instead of relying on unrelated differences between real objects.


---


## Routing Logger AttributeError After Adding Logging to Router

### Problem

Three router tests failed with AttributeError: 'str' object has no attribute 'model_id' after adding logging.

### Diagnosis

log_routing_decision() expected a full ModelConfig object so it could pull model_id off of it internally, but router.py was passing model.model_id — already a plain string — so calling .model_id on that string crashed.

### Solution

Passed the full model object into the logger instead of pre-extracting its id: selected_model=model.

### Lesson Learned

Check what type of object a function actually expects before passing it in, rather than assuming based on the argument name.


---


## Mock Responses Did Not Vary by Quality, Breaking Verification

### Problem

Wiring QualityVerifier into the Router escalated nearly every Medium-tier routing decision, and no threshold value fixed it.

### Diagnosis

MockProvider returned the same response text regardless of which model answered, and even after giving each quality tier its own template, the word-overlap agreement scores were not monotonic with quality — Low sometimes agreed with High more than Medium did, purely by accident of word choice. No threshold could correctly separate tiers built that way.

### Solution

Redesigned the quality response templates as strict nested word-subsets (Low words ⊆ Medium words ⊆ High words), which mathematically guarantees correct agreement ordering for any prompt length. Verified with an actual computation script instead of assuming. The original default threshold worked correctly once the templates were fixed.

### Lesson Learned

When a threshold "doesn't work" the real bug is sometimes upstream in the data feeding it, not the threshold value itself.


---


## Stale SQLite Schema Rejected New Log Columns

### Problem

Adding input_tokens/output_tokens to the routing log schema caused new inserts to crash with OperationalError.

### Diagnosis

CREATE TABLE IF NOT EXISTS does not alter an existing table, so the real project-root routing_logs.db still had the old schema from before the columns were added.

### Solution

Cleared the stale local log/database files so the table would be recreated with the current schema.

### Lesson Learned

Schema changes to an existing database file need a migration step (or a reset in development) — creating the table again is not enough once it already exists.


---


## /v1/stats Crashed on a Fresh Database

### Problem

Hitting GET /v1/stats before any completion had ever been logged crashed with "no such table."

### Diagnosis

init_db() was only ever called from inside insert_routing_log(), so the routing_logs table was never created until the first log write happened — but /v1/stats read from the table directly.

### Solution

Called init_db() once at API startup, alongside the rest of the module-level dependency construction, instead of relying on it being called as a side effect of logging.

### Lesson Learned

Anything that reads from a resource should not assume something else has already created it — initialize shared resources explicitly at startup.


---


## PUT /v1/routing-config Accepted an Empty Model List

### Problem

Updating a tier's candidate models to an empty list succeeded silently, and the next request routed to that tier crashed deep inside MockProvider with AttributeError: 'NoneType' object has no attribute 'quality_tier'.

### Diagnosis

Validation checked that every submitted model name was real, but never checked that the models list wasn't empty, so _select_best_model() had nothing to choose from.

### Solution

Added an explicit empty-list check to the endpoint's validation, rejecting the update with a clear error instead of letting it fail later inside the Router.

### Lesson Learned

Invalid configuration should be rejected as early as possible, at the API boundary, instead of surfacing as a confusing crash somewhere else entirely.


---


## Missing model.joblib Crashed Tests at Collection Time

### Problem

Any test file that imported the FastAPI app crashed before a single test ran, even though a session-scoped fixture already existed to train the model.

### Diagnosis

api/main.py builds its dependencies (including the ML classifier, which loads model.joblib) at module-import time. Pytest imports test files during its collection phase, before any fixture — even an autouse one — gets a chance to run. So the crash happened before the existing fixture could help.

### Solution

Added a plain module-level guard directly in conftest.py (not a fixture), since conftest.py is always imported before sibling test files get collected.

### Lesson Learned

Module-level code can run during pytest's collection phase, before any fixture executes — a fixture can't protect against a crash that happens before fixtures are even eligible to run.


---


## Ollama Provider: Import Path and Registry ID Mismatch

### Problem

MultiProvider crashed on import with a module-not-found style error, and Ollama requests failed because of a model ID mismatch.

### Diagnosis

The first draft used a bare import (from ollama_provider import OllamaProvider), which only resolves for modules sitting directly in src/, not for a sibling module inside the same providers subfolder. Separately, the registry stored the model as llama3-local, which isn't a real Ollama tag.

### Solution

Fixed the import to the full dotted path (from providers.ollama_provider import OllamaProvider), and renamed the registry's id to the real Ollama tag llama3 across the registry, routing config, and every test referencing it.

### Lesson Learned

In a subfolder-per-concern layout, imports need the full dotted path from src/, even between two files sitting right next to each other — flat imports only work for files directly in src/.


---


## MultiProvider Required Every Provider's Credentials Up Front

### Problem

Registering OpenAIProvider in MultiProvider meant just instantiating MultiProvider() would eventually require valid credentials for every registered provider, including ones never actually used in a given run.

### Diagnosis

MultiProvider.__init__ built every registered provider eagerly. Since OpenAIProvider.__init__ constructs a real OpenAI() client that requires a valid key just to exist, this coupled unrelated providers' credential requirements together.

### Solution

Changed provider construction to be lazy — a given provider is only built the first time it's actually dispatched to.

### Lesson Learned

Wiring a new piece into an existing system can quietly break assumptions the rest of the system relied on — both of these looked fine until actually run.


---


## Automated API Tests Were Silently Making Real OpenAI Calls

### Problem

test_api.py went from instant to taking several seconds per test after MultiProvider replaced MockProvider in the app, without an obvious cause at first glance.

### Diagnosis

Confirmed the tests were making two real OpenAI calls per run (the routed model call plus the async verification's reference-model call) — silently costing money and requiring internet on every pytest run, against the project's own earlier decision to validate with MockProvider before touching real APIs.

### Solution

Added a FastAPI dependency override so test_api.py uses MockProvider while the real running app keeps using real providers.

### Lesson Learned

Swapping a core dependency (like a provider) can silently change what tests actually exercise — worth checking test behavior, not just test results, after a wiring change.


---


## Final Load Test Report Counted Historical Data as Current

### Problem

The first version of the cost-savings report mixed the load test's own results with days of unrelated prior manual testing, and a later "fixed" version still returned an impossible number — 215 verified requests out of 210 sent.

### Diagnosis

The first version queried routing_logs.db's entire history instead of only the current run. The fix that followed matched rows by prompt_hash, which still pulled in older rows whenever a prompt's exact text had been sent before (identical prompts hash identically).

### Solution

Computed cost/routing/accuracy directly from the current run's own load_test_results.jsonl output instead of the database's full history, and matched the exact rows created by this run by database id rather than by prompt hash — with an integrity check that raises an error rather than silently reporting a wrong number if anything doesn't line up.

### Lesson Learned

A report is only as trustworthy as the effort spent trying to catch it being wrong — matching by content (like a prompt or its hash) instead of an identity (like a row id) can silently pull in the wrong rows.
