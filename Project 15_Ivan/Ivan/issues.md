# Issues

---

## Issue: Missing Schema Models (Week 1)

### Problem

The project imports `src.schemas.models`, but the file does not yet exist.

### Investigation

Reviewed `mock.py` and `provider.py` to determine which models were expected.

### Resolution

Identified the required Pydantic models:

- ExecutionPlan
- SubTask
- ReviewResult
- Complexity
- SpecialistName

Implementation postponed until development begins.

### Lessons Learned

The schema models define the structured communication contract between agents and the LLM.

---

## Issue: Duplicate Mock Implementation

### Problem

`provider.py` and `mock.py` currently contain identical implementations.

### Investigation

Analyzed the purpose of each file and compared their responsibilities.

### Resolution

No implementation changes yet.

Need to verify whether the duplication is intentional or temporary with the team.

### Lessons Learned

The provider should likely act as a factory instead of duplicating the mock implementation.

