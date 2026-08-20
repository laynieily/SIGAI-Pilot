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








---

## Issue: Proposed Fixes for Hallucinated Answers Didn't Hold Up to Scrutiny (Week 4)

### Problem

The first suggested fixes for the LLM inventing technical specs — having it hedge with "this is only an approximation," and reading more raw text from search results — both sounded reasonable but didn't actually solve the problem.

### Investigation

Questioned each proposal before implementing it. Ran a controlled test with only the hedging instruction changed, and manually opened the pages driving the raw-text idea, to see what each fix would realistically accomplish.

### Resolution

The hedging instruction alone was too easy to satisfy without really fixing anything, and reading more text mostly just meant reading more navigation menu. Replaced both with something backed by evidence: a stricter no-loophole instruction, and a filter built after testing showed what was actually eating the character budget.

### Lessons Learned

A fix that sounds reasonable isn't the same as a fix that's been tested against the actual failure.

---

## Issue: Web Search Still Doesn't Reliably Get the System Real Information

### Problem

Even after adding a way to read full page content instead of just search snippets, the system still regularly answers with either invented specifics or an honest "I don't know" — both cases where the real answer was sitting on the page it fetched.

### Investigation

Opened the same source pages by hand and confirmed the requested information was present in plain text, not hidden behind anything unusual. The real problem is how much of the fetched page is navigation clutter versus actual content, which varies a lot page to page.

### Resolution

Improved the filtering enough to cut a meaningful amount of that clutter, but it's a heuristic, not a guarantee — it still fails on some pages.

### Lessons Learned

This isn't solved yet. A proper fix would need a dedicated content-extraction approach, not more tuning of a quick filter.

---

## Issue: Escalation State Wasn't Cleared After a Resume (Week 5)

### Problem

After a paused run got approved and continued, it immediately paused again with the exact same reason — a one-subtask plan needed three approvals in a row to finish what should've taken one.

### Investigation

Traced it to the escalation node never resetting its own trigger reason once a run continued past it, so the very next step saw the old value and mistook it for a brand new escalation.

### Resolution

Clear the reason whenever the run is actually continuing, and keep a separate, never-cleared list just for the final summary — so clearing it for routing doesn't also erase it from the report.

### Lessons Learned

Isolated tests checked the right decision in isolation but never simulated a full multi-step run, so they couldn't have caught this — only running it live did.