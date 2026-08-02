## Issues Log

- OpenAI API key invalid (401 error) → disabled in `.env`. Not currently required; GPT-4o pricing stays in the model registry for the planned Phase 4.3 cost comparison. Routing map lists `gpt-4o` / `gpt-4o-mini` as YAML alternatives only (2026-07-31 Phase 2.4). Phase 3.1+ judge/reference/escalation models use `claude-sonnet` until OpenAI is enabled (2026-08-01).
- Ollama local install had an empty app bundle, blocking local model access → resolved by reinstalling Ollama and pulling `llama3.2`.
- `gemini-pro` returned 429 (free tier has a zero-request quota) → dropped `gemini-pro` from the provider set; `gemini-flash` works fine as a Tier 2 model.
- `requirements.txt` used `>=` version ranges (supply-chain risk — a bad upstream release could break or compromise builds) → pinned all dependencies to exact installed versions (2026-07-29 security pass).
- `data/prompt_features.json` (a generated artifact) was committed to git, producing 3,400+ line diffs on every feature change → added to `.gitignore` and untracked with `git rm --cached`; regenerate with `python -m scripts.inspect_dataset`.
- `joblib.load` can execute code from untrusted model files → documented that `load_classifier` must only load bundles produced by this project's trainer (2026-07-31 security pass on Phase 2.3).
- Cloud agent could not post GitHub PR review/approve on own PR (403 / "cannot approve your own pull request") → parent posts review comment + Bugbot; human or parent merge required (2026-08-01 Phases 3.1–3.2).
- PR #5 opened as draft → blocked squash-merge until marked ready for review (2026-08-01 Phase 3.2).
- Bugbot on Phase 3.2: substring field coverage false positives; judge parser latching onto scale “1”; label punctuation mismatch → fixed with whole-word match, last in-range number, punctuation strip before merge (2026-08-01).
- Cloud agent ManagePullRequest `post_comment` failed after merge (PR URL / branch deleted) and `gh pr comment` returned 403 “Resource not accessible by integration” → self-review captured in agent report; parent may re-post if desired (2026-08-02 Phase 3.3).
- Cloud agent cannot push to `laynieily/SIGAI-Pilot` (403) → parent applies SIGAI doc updates after each merge (2026-08-02).
- Routing-failure JSONL stores only `prompt_hash` → Phase 3.4 writes training prompts to a separate gitignored `data/feedback_prompts.jsonl` at failure time while the prompt is still in memory (2026-08-02).
- Cloud agent `gh pr comment` / ManagePullRequest comment returned 403 “Resource not accessible by integration” on PR #8 → self-review captured in agent report (2026-08-02 Phase 3.4).

- Current blockers: none as of 2026-08-02.
