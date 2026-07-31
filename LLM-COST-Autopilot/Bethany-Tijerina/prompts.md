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
