## Issues Log

- OpenAI API key invalid (401 error) → disabled in `.env`. Not currently required; GPT-4o pricing stays in the model registry for the planned Phase 4.3 cost comparison.
- Ollama local install had an empty app bundle, blocking local model access → resolved by reinstalling Ollama and pulling `llama3.2`.
- `gemini-pro` returned 429 (free tier has a zero-request quota) → dropped `gemini-pro` from the provider set; `gemini-flash` works fine as a Tier 2 model.
- `requirements.txt` used `>=` version ranges (supply-chain risk — a bad upstream release could break or compromise builds) → pinned all dependencies to exact installed versions (2026-07-29 security pass).
- `data/prompt_features.json` (a generated artifact) was committed to git, producing 3,400+ line diffs on every feature change → added to `.gitignore` and untracked with `git rm --cached`; regenerate with `python -m scripts.inspect_dataset`.
- `joblib.load` can execute code from untrusted model files → documented that `load_classifier` must only load bundles produced by this project's trainer (2026-07-31 security pass on Phase 2.3).

- Current blockers: none as of 2026-07-31.
