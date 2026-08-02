# Issues log

# Writing standard
This file uses ASD-STE100 Simplified Technical English (controlled style).
Technical names (file paths, model IDs, commands) stay unchanged.

## Open and closed issues

- The OpenAI API key is not valid (401). The key is off in `.env`. OpenAI is not required now. GPT-4o prices stay in the model registry for the Phase 4.3 cost comparison. The routing map lists `gpt-4o` and `gpt-4o-mini` as YAML alternatives only (2026-07-31, Phase 2.4). Judge, reference, and escalation models use `claude-sonnet` until OpenAI is on (2026-08-01).
- The local Ollama install had an empty app bundle. Local model access did not work. The fix was a new Ollama install and a pull of `llama3.2`.
- `gemini-pro` returned 429. The free tier has a zero-request quota. The team removed `gemini-pro`. `gemini-flash` works as a Tier 2 model.
- `requirements.txt` used `>=` version ranges. A bad upstream release can break or harm builds. The team pinned all dependencies to exact installed versions (2026-07-29 security pass).
- `data/prompt_features.json` is a generated file. A commit of this file made very large diffs. The team added it to `.gitignore` and ran `git rm --cached`. Regenerate with `python -m scripts.inspect_dataset`.
- `joblib.load` can run code from untrusted model files. The docs say `load_classifier` must load only bundles from this project trainer (2026-07-31 security pass, Phase 2.3).
- A cloud agent cannot approve its own GitHub PR (403). The parent agent posts the review comment and Bugbot. A human or the parent must merge (2026-08-01, Phases 3.1–3.2).
- PR #5 opened as a draft. Squash merge did not run until the PR was ready for review (2026-08-01, Phase 3.2).
- Bugbot on Phase 3.2 found three defects: substring field-coverage false matches, judge parser that took scale value 1, and label punctuation mismatch. The fixes are whole-word match, last in-range number, and punctuation strip before merge (2026-08-01).
- After merge, cloud agent comment tools returned 403. The self-review is in the agent report. The parent can post the comment again if needed (2026-08-02, Phase 3.3).
- A cloud agent cannot push to `laynieily/SIGAI-Pilot` (403). The parent updates SIGAI docs after each merge (2026-08-02).
- The routing-failure JSONL stores only `prompt_hash`. Phase 3.4 writes training prompts to gitignored `data/feedback_prompts.jsonl` while the prompt is still in memory (2026-08-02).
- Cloud agent PR comments returned 403 on PR #8. The self-review is in the agent report (2026-08-02, Phase 3.4).
- Cloud agent review comments returned 403 on PR #9 (Phase 4.1). The self-review is in the agent report. Squash merge with `gh pr merge` succeeded (2026-08-02).
- The Phase 4.1 audit database stores `prompt_hash` and metrics only. It does not store raw prompts or secrets. `data/requests.db` is gitignored. All writes use parameterized SQL (2026-08-02).
- Phase 4.2 GPT-4o counterfactual: use tokens times registry prices when tokens exist. If tokens are missing, use 500 input and 250 output (2026-08-02).
- The Phase 4.2 dashboard binds Streamlit to localhost. It shows aggregate values only. It does not show raw prompts (2026-08-02).
- The Claude Sonnet list price is higher than GPT-4o. On some days, actual cost is higher than the GPT-4o counterfactual. The full mix still saves about 37% on the demo seed (2026-08-02).
- Phase 4.3 primary metric is `cost_reduction_pct` vs all GPT-4o. `show_savings --demo` uses a temporary database. It does not write an empty `data/requests.db` (2026-08-02).
- The Phase 4.3 dashboard HTML path inserts only float and USD aggregates from metrics. It does not insert user content (2026-08-02).
- Phase 5.1 FastAPI is local and has no auth (portfolio use). There is no wildcard CORS. Debug and reload are not default. The audit stores `prompt_hash` only. The client `model` field is rejected (2026-08-02).
- Escalation on the completions hot path is still a TODO. Verify stays async. The response path must not wait (2026-08-02, Phase 5.1).
- Phase 5.2 `PUT /v1/routing-config` has no auth for local portfolio use. The gate is `ALLOW_ROUTING_CONFIG_WRITE` (default on). This gate is not real auth (2026-08-02).
- Phase 5.2 routing writes go only to project `configs/` paths. Model keys must match the registry (2026-08-02).
- The Phase 5.3 compose API binds to localhost and has no auth. Do not expose it on a public network without real auth. Put secrets only in `.env`. Do not put secrets in the image (2026-08-02).
- The Phase 5.3 worker is not a cross-process verify queue. In-memory asyncio stays in the API. The worker watches shared `./data` and can retrain (2026-08-02).
- Cloud Agent usage limits stopped some cloud runs. The team completed Phase 6.2 on the local agent (2026-08-02).
- The Phase 6.1 load test is offline. Provider costs come from the registry mock. Live API dollar totals will change when keys are on (2026-08-02).
- Phase 6.2 quality text uses the 3.2% escalation rate in the offline test plus the verify and escalate design. It is not a live LLM-as-judge pass rate for all 750 prompts (2026-08-02).

## Current blockers

- There are no blockers as of 2026-08-02.
- The build plan is complete.
