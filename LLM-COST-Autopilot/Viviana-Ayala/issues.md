## Issues Log

- OpenAI API key invalid (401 error) → disabled in `.env`. Not currently required; GPT-4o pricing stays in the model registry for the planned Phase 4.3 cost comparison. Routing map lists `gpt-4o` / `gpt-4o-mini` as YAML alternatives only (2026-07-31 Phase 2.4). Phase 3.1 judge/reference models use `claude-sonnet` until OpenAI is enabled (2026-08-01).
- Ollama local install had an empty app bundle, blocking local model access → resolved by reinstalling Ollama and pulling `llama3.2`.
- `gemini-pro` returned 429 (free tier has a zero-request quota) → dropped `gemini-pro` from the provider set; `gemini-flash` works fine as a Tier 2 model.
- `requirements.txt` used `>=` version ranges (supply-chain risk — a bad upstream release could break or compromise builds) → pinned all dependencies to exact installed versions (2026-07-29 security pass).
- `data/prompt_features.json` (a generated artifact) was committed to git, producing 3,400+ line diffs on every feature change → added to `.gitignore` and untracked with `git rm --cached`; regenerate with `python -m scripts.inspect_dataset`.
- `joblib.load` can execute code from untrusted model files → documented that `load_classifier` must only load bundles produced by this project's trainer (2026-07-31 security pass on Phase 2.3).
- Cloud agent could not post GitHub PR review/approve on own PR (403 / "cannot approve your own pull request") → parent posted review comment + Bugbot; human merge still required (2026-08-01 Phase 3.1).

- Current blockers: none as of 2026-08-01.
