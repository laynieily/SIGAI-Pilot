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