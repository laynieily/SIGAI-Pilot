# AI Development Prompts

This file documents important prompts used during development and how AI suggestions influenced project decisions.

---

## 07/17-07/20/2026

## Project Architecture Questions

### Prompt:

What problem is this project trying to solve?

### AI Influence:

Helped define the goal of the project as an LLM routing system that reduces unnecessary AI costs by selecting appropriate models while maintaining acceptable response quality.

### Prompt:

How should the project be organized?

### AI Influence:

Suggested separating responsibilities into components such as Model Registry, Router, Providers, routing logic, logging, and future dashboard functionality.

### Prompt:

What is a Model Registry and what are some examples that help visualize this concept?

### AI Influence:

Helped me understand that the Model Registry acts as a centralized source of truth for available models, storing information such as model name, provider, cost, latency, and quality.

### Prompt:

Why use a Python dataclass and when should it be used?

### AI Influence:

Helped me decide to use dataclasses for structured objects such as ModelConfig and LLMResponse because they keep related data organized.

---

## 07/21/2026

## Provider Architecture Questions

### Prompt:

Should I connect to a real API now or wait?

### AI Influence:

Recommended validating the architecture with MockProvider first before connecting to paid APIs. This allowed testing without API costs.

### Prompt:

What is the purpose of MockProvider?

### AI Influence:

Helped me understand that MockProvider simulates an LLM provider so routing, testing, and response handling can be developed without external dependencies.

### Prompt:

Why should I use an Abstract Base Class?

### AI Influence:

Helped me create BaseProvider so all providers follow the same interface and future providers can be added without changing the Router.

### Prompt:

Why should every provider return the same response object?

### AI Influence:

Influenced the creation of LLMResponse as a shared response format so the rest of the system does not depend on provider-specific responses.

---

## 07/23/2026

## Architecture Planning Questions

### Prompt:

Should I immediately build the machine learning classifier?

### AI Influence:

Helped me decide to create a rule-based classifier first as a baseline before moving toward machine learning.

### Prompt:

Why not connect to a real API before building the routing logic?

### AI Influence:

Helped me continue using MockProvider until the architecture and routing workflow were tested successfully.

### Prompt:

Should I finish the architecture before adding more features?

### AI Influence:

Reinforced the decision to build the system incrementally and stabilize the architecture before adding advanced features.

### Prompt:

What should the next milestone be?

### AI Influence:

Helped establish the next goal of completing the architecture, documenting progress, and implementing the complexity classifier.

---

## 07/27-07/28/2026

## Complexity Classifier Questions

### Prompt:

What features should the complexity classifier use to determine prompt difficulty?

### AI Influence:

Helped identify useful classification features such as keywords, reasoning requirements, formatting requirements, and prompt complexity.

### Prompt:

Why should YAML be used for configuration instead of storing rules directly in Python?

### AI Influence:

Helped me separate configuration from application logic so classification rules can be modified without changing Python code.

### Prompt:

How should complexity keywords be weighted?

### AI Influence:

Led to using weighted keywords because different actions represent different levels of difficulty.

### Prompt:

How should I handle a test failure where the expected complexity tier does not match the classifier result?

### AI Influence:

Helped me analyze whether failures were caused by code problems or whether the scoring design needed improvement.

---

## 07/28-07/29/2026

## Router Integration Questions

### Prompt:

Why should the Router use the ComplexityClassifier instead of deciding complexity itself?

### AI Influence:

Helped separate responsibilities by allowing the classifier to determine complexity while the Router focuses on selecting models.

### Prompt:

Why does the Model Registry need a get_model function?

### AI Influence:

Helped keep model lookup logic inside the registry instead of allowing other components to directly access internal data.

### Prompt:

Why should routing decisions be stored in a separate YAML file?

### AI Influence:

Helped make routing behavior configurable without modifying Python code.

### Prompt:

How should the Router receive the components it depends on?

### AI Influence:

Led to using dependency injection so the Router can work with different providers and classifiers during testing.

---

## 07/30/2026

## Model Selection Strategy

### Prompt:

Should the Router only select models based on cost, or should it consider additional factors?

### AI Influence:

Helped me realize that cost alone does not represent the best model choice. The Router should consider quality, cost, and latency together.

### Prompt:

How can the Router compare models with different strengths?

### AI Influence:

Led to creating a scoring system that combines multiple model attributes into one selection score.

### Prompt:

Why should model selection consider quality and latency?

### AI Influence:

Helped explain that a slightly more expensive model may be a better choice if it provides higher quality or faster responses.

### Prompt:

How can routing decisions be recorded for later analysis?

### AI Influence:

Influenced adding selection_score to LLMResponse so routing decisions can be analyzed later.

### Prompt:

How can I verify that the Router is selecting models correctly?

### AI Influence:

Helped me create integration tests that verify the complete workflow:

Prompt → Complexity Classifier → Router → Model Selection → Provider Response.

---

## 08/05-08/06/2026

## Testing and Logging Improvements

### Prompt:

Why did the quality scoring test fail even though the scoring formula worked?

### AI Influence:

Helped me see that the test compared two real models that differed in quality, cost, and latency all at once, so it couldn't isolate the effect of quality alone.

### Prompt:

How should I test the quality component of the scoring system on its own?

### AI Influence:

Led me to use synthetic test models with identical cost and latency but different quality levels, so the test measures only the quality bonus.

### Prompt:

Why did the routing logger break after I added it to the Router?

### AI Influence:

Helped me trace it to the logger expecting a full ModelConfig object while the Router was passing just the model ID string.

### Prompt:

Should the Router pass the model object or the model ID to the logger?

### AI Influence:

Confirmed the Router should pass the full model object, since the logger already extracts the ID from it internally.

---

## 08/07-08/09/2026

## Logging Schema, ML Classifier, and Verification System

### Prompt:

What parts of the project still need improvement?

### AI Influence:

Helped me review the project phase by phase instead of feature by feature, which revealed components that were built but never connected, and requirements that hadn't been started.

### Prompt:

What information should be included in the routing logs, and why add a prompt hash?

### AI Influence:

Helped me extend the logs with cost, latency, quality score, escalation status, and a prompt hash — the hash avoids storing raw prompt text indefinitely and gives a stable identifier for future dashboard queries.

### Prompt:

Why should I add SQLite alongside the JSON logs?

### AI Influence:

Helped me see that JSON is fine for simple records, but SQLite makes it much easier to query and analyze routing data as it grows.

### Prompt:

How should I replace the rule-based classifier with a machine learning model?

### AI Influence:

Guided me through building a labeled dataset, extracting numeric features from each prompt, training a classifier, and keeping the exact same classify(prompt) interface so it could swap in without changing the Router.

### Prompt:

How should the system verify whether a selected model's response was actually good enough?

### AI Influence:

Helped me design a verifier that compares the routed response against a reference model's response and escalates when they disagree too much.

### Prompt:

How can I connect the new ML classifier and verifier to the Router without redesigning the project?

### AI Influence:

Reinforced using dependency injection again — pass the classifier and verifier in as constructor arguments, same as the provider.

---

## 08/11-08/15/2026

## Building the FastAPI Service (Phase 5)

### Prompt:

How should I structure the FastAPI service around the Router I already built?

### AI Influence:

Helped me keep the API as a thin layer that reuses the existing Router instead of rebuilding routing logic inside the endpoints.

### Prompt:

How should FastAPI's dependency injection work with my Router?

### AI Influence:

Helped me build the Router once at module level and use Depends(get_router) so every request reuses the same instance instead of rebuilding it.

### Prompt:

How should the API expose model information and routing statistics without leaking internal details?

### AI Influence:

Helped me design dedicated Pydantic response models instead of returning internal dataclasses directly, so I control exactly what an API caller sees.

### Prompt:

How should I handle the server starting up without a trained model.joblib file?

### AI Influence:

Helped me decide to fail fast with a clear error message telling the user how to generate the model, rather than silently auto-training on startup.

### Prompt:

How should I test the API automatically instead of relying only on /docs and curl?

### AI Influence:

Introduced FastAPI's TestClient so I could turn the manual checks I was already doing into permanent automated tests.

---

## 08/17/2026

## Roadmap Check-In

### Prompt:

What's the next part of completing the project?

### AI Influence:

Helped me re-check the current state of the repo against the original roadmap instead of assuming — confirmed Phase 5 was genuinely complete and that real provider integration was the natural next step, since the BaseProvider interface was already designed for it.

---

## 08/20-08/21/2026

## Real Provider Integration — Ollama, MultiProvider, OpenAI Gap

### Prompt:

How should I build a real OllamaProvider using the existing BaseProvider interface?

### AI Influence:

Walked me through Ollama's REST API shape before writing any code, then helped me reuse MockProvider's timing/cost pattern for the real implementation.

### Prompt:

How can the Router use multiple real providers while still only depending on BaseProvider?

### AI Influence:

Helped me design MultiProvider — a dispatcher that also implements BaseProvider, holding each real provider in a dictionary keyed by name and forwarding requests based on the model's provider field.

### Prompt:

What should happen if a provider hasn't been implemented yet?

### AI Influence:

Helped me raise a clear "unsupported provider" error instead of letting a confusing KeyError or NoneType error happen somewhere else.

### Prompt:

How should I test a real provider without every test depending on a running server?

### AI Influence:

Helped me mock the HTTP call itself in unit tests, while still confirming the provider against a real server separately — same MockProvider philosophy applied to a real provider's tests.

---

## 08/21/2026

## Async Verification, the Feedback Loop, the Dashboard, and Docker

### Prompt:

How should verification run without slowing down every user's response?

### AI Influence:

Helped me split routing from verification — return the response immediately, then run verification afterward as a background task.

### Prompt:

How can escalation data be used to improve the classifier over time?

### AI Influence:

Helped me design a retraining script that folds escalation events back into the labeled dataset as new, corrected training examples.

### Prompt:

How should the cost dashboard be organized?

### AI Influence:

Helped me separate the data calculations from the Streamlit UI so the calculations could be tested independently of the interface.

### Prompt:

What problems should I expect running this inside Docker?

### AI Influence:

Warned me that container networking changes what "localhost" means, which led me to make Ollama's URL environment-configurable before it became a hidden bug.

---

## 08/21-08/24/2026

## Building OpenAIProvider and Wiring It In

### Prompt:

Should I get an OpenAI key or an Anthropic key first?

### AI Influence:

Helped me realize OpenAI was already further along — the SDK was installed and the registry's model IDs already matched OpenAI's real names — so finishing it made more sense than starting a second provider from scratch.

### Prompt:

How should I build OpenAIProvider using the official SDK?

### AI Influence:

Walked me through the SDK's response shape before writing code, same pattern as OllamaProvider, but simpler since the SDK handles the HTTP details directly.

### Prompt:

Why is MultiProvider requiring OpenAI credentials even when I'm not using OpenAI?

### AI Influence:

Helped me trace it to eager provider construction and move to lazy construction instead, so unused providers never require their credentials.

### Prompt:

Why did my API tests start making real OpenAI requests?

### AI Influence:

Helped me realize the real MultiProvider had replaced MockProvider app-wide, and led me to override the provider dependency specifically for tests.

---

## 08/24/2026

## Deciding to Skip Anthropic, and the Final Load Test

### Prompt:

Should I still implement AnthropicProvider?

### AI Influence:

Helped me weigh the tradeoff — the provider pattern was already proven with a cloud provider and a local provider, so a third one with the same shape wouldn't demonstrate anything new, and my remaining time was better spent finishing Phase 6.

### Prompt:

How should I perform the final load test — new prompts, or reuse what I have?

### AI Influence:

Helped me realize the existing 210-prompt labeled dataset was already diverse and balanced across all three tiers, so it could serve as a realistic evaluation set instead of generating synthetic filler.

### Prompt:

Why did my report show more verified requests than I actually sent?

### AI Influence:

Helped me catch that matching by prompt hash pulled in older historical rows with identical text, and led me to match by database id and add an integrity check instead.

### Prompt:

How should I interpret a 36.2% escalation rate — is that a problem?

### AI Influence:

Pushed me to hand-check actual escalated examples instead of reporting the number at face value — all three checked were correct answers, just phrased differently than the reference response, which pointed to a real weakness in word-overlap verification rather than a routing failure.
