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

`provider.py` referenced `settings.USE_MOCK` and `MockLLM()` without importing either — `settings` didn't exist anywhere in the project, and `MockLLM` was never imported.

### Investigation

Read the file directly; confirmed it was an incomplete stub, not a working implementation. Checked the rest of the repo for a `settings`/config module — none existed.

### Resolution

Implemented `LLMProvider.get_llm()` as a real factory: returns `MockLLM` if `USE_MOCK` is set or no API key is found, otherwise `ChatAnthropic`/`ChatOpenAI` depending on which key is present in `.env`.

### Lessons Learned

Confirms the hypothesis from Week 1's "Duplicate Mock Implementation" issue — `provider.py`'s actual job is to be a factory that *chooses* an implementation, not to contain any LLM logic itself.

---

## Issue: `git merge` Left the Environment Half-Installed

### Problem

After merging with a separate GitHub remote, running the demo failed with `ModuleNotFoundError: No module named 'dotenv'`, even though `langgraph` and `pydantic` clearly worked (later imports in the same chain succeeded).

### Investigation

The traceback showed `dotenv` failing specifically — and `python-dotenv` is the *last* line in `requirements.txt`. That pointed to `pip install -r requirements.txt` aborting partway through on some earlier package, rather than nothing being installed at all.

### Resolution

Installed `python-dotenv` directly to unblock, and flagged the likely root cause (a package earlier in the file failing to build) for a full reinstall later.

### Lessons Learned

A partial `pip install` failure can look exactly like "forgot to install dependencies" from the error message alone — the *position* of the missing package in the requirements file was the actual clue.

---

## Issue: Merge Diff Looked Like Everything Changed

### Problem

After the same `git merge`, `git status`/`git diff` showed several core files (`models.py`, `mock.py`, tool files) as modified, which looked like the merge might have silently altered working code.

### Investigation

Ran `git diff` on each flagged file and compared line by line — every "changed" line was identical content, differing only in CRLF vs. LF line endings. Checked `requirements.txt` and `.gitignore` at the byte level for BOM/encoding corruption as well.

### Resolution

Confirmed no functional changes; the diffs were pure line-ending noise from the merge. No code changes needed.

### Lessons Learned

A large `git diff` after a merge isn't proof of a real change — checking for line-ending-only diffs first avoids chasing a bug that doesn't exist.

---

