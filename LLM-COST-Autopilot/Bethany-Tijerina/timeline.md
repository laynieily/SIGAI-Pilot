# LLM Cost Autopilot - Development Timeline

Repository:
[Bethany's GitHub Repository Link](https://github.com/BethanyTijerina/LLM-Cost-Autopilot.git)

## Project Overview

The goal of this project is to create an intelligent LLM routing system that reduces unnecessary AI costs by selecting the most appropriate model based on prompt complexity while maintaining acceptable response quality.

The system currently includes:
- Model Registry for storing model information
- Provider abstraction layer
- Mock LLM provider for testing
- Complexity classifier
- Routing system
- Model scoring system for selection decisions


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

Future work:
- Add routing logs
- Connect real API providers
- Analyze routing performance