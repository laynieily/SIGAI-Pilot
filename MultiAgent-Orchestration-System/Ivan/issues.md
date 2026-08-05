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






## Issue: Broken `provider.py` Stub (Week 2)

### Problem

`provider.py` referenced a configuration object and a class that were never defined or imported anywhere in the project.

### Investigation

Reviewed the file directly and confirmed it was an incomplete stub, not a working implementation.

### Resolution

Implemented a real factory that returns the mock or a real model depending on which API key is available.

### Lessons Learned

The provider's job is to choose an implementation, not to contain any logic of its own.

---

## Issue: Incomplete Dependency Install After Merging

### Problem

Running the project failed with a missing-module error after merging with a separate GitHub repository, even though other dependencies clearly worked.

### Investigation

Traced the error to a package listed near the end of the requirements file, suggesting the install had stopped partway through.

### Resolution

Installed the missing package directly and flagged the likely cause for a full reinstall later.

### Lessons Learned

A partial install can look identical to a forgotten one — where the missing package sits in the list can be the real clue.

---

## Issue: Merge Made It Look Like Files Had Changed

### Problem

After the same merge, several core files appeared modified, suggesting the merge may have altered working code.

### Investigation

Compared the changes line by line and found they were only differences in line endings, not actual content.

### Resolution

Confirmed no real changes had occurred; nothing needed fixing.

### Lessons Learned

A large diff after a merge isn't proof that something broke — check for formatting-only changes first.




---

## Issue: Real LLM Responses Didn't Match the Expected Format (Week 3)

### Problem

Switching from the mock to a real model broke the pipeline, since a real model returns a structured message object instead of plain text.

### Investigation

Compared how the mock and the real model each responded to the same call and found the mismatch.

### Resolution

Added a small helper that extracts plain text regardless of which type of response comes back.

### Lessons Learned

Code written against a mock needs to be checked against the real thing before assuming it behaves the same way.

---

## Issue: Real Plan Skipped a Specialist and Crashed the Graph

### Problem

The first real end-to-end run failed because the generated plan didn't include every specialist, which the graph assumed would always be present.

### Investigation

Traced the crash back to a lookup that expected to always find a match.

### Resolution

Updated the lookup to skip gracefully when a specialist isn't needed, instead of failing.

### Lessons Learned

A real model won't always follow the same fixed pattern a hardcoded mock does — the system needs to tolerate that variation.

---
