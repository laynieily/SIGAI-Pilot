# Prompts log

# Writing standard
This file uses ASD-STE100 Simplified Technical English (controlled style).
Quoted user prompts stay in the original words.

## How this log works

This project uses Fable (Cursor coding assistant) with a durable `AGENTS.md` file.
This log shows sample user prompts and the result of each prompt.

### 2026-08-02

- **"finish 6.2 here without cloud"** — Local Agent mode. The agent wrote `CASE_STUDY.md` with lead number 30.6% vs all GPT-4o. The agent linked README and the portfolio site. The agent updated `AGENTS.md` (Phase 6 complete). The agent updated SIGAI timeline, issues, and prompts for 6.1 and 6.2.
- **"Phase 6.1 — Realistic load test"** via `/in-cloud` — Offline load test with n=750. Reports and headline 30.6%. PR #15 had a squash merge. The parent updated SIGAI with 6.2.
- **"Phase 5.3 — Containerize & document"** via `/in-cloud` — New cloud agent on branch `cursor/phase-5-3-containerize-document-efcc`. Outputs: Dockerfile, compose (api/worker), README savings text. PR #14 was ready (not draft) and had a squash merge to `main`. Phase 5 is complete. Next was Phase 6.1. The parent pushed SIGAI docs.
- **"Phase 5.2 — Config endpoints"** via `/in-cloud` — New cloud agent on branch `cursor/phase-5-2-config-endpoints-aed4`. Outputs: GET models/stats and GET|PUT routing-config. Smoke tests grew. PR #13 was ready (not draft) and had a squash merge to `main`. Next was Phase 5.3. The parent pushed SIGAI docs.
- **"Phase 5.1 — FastAPI POST /v1/completions"** via `/in-cloud` — New cloud agent on branch `cursor/phase-5-1-fastapi-completions-92d7`. The router selects the model. Audit and TestClient smoke ran. PR #12 was ready (not draft) and had a squash merge to `main`. Next was Phase 5.2. The parent pushed SIGAI docs.
- **"Phase 4.3 — Money-shot metric"** via `/in-cloud` — New cloud agent on branch `cursor/phase-4-3-money-shot-metric-0be4`. Outputs: `cost_reduction_pct` UI and `show_savings` CLI. Offline smoke ran. PR #11 was ready (not draft) and had a squash merge to `main`. Phase 4 is complete. Next was Phase 5.1. The parent pushed SIGAI docs.
- **"Phase 4.2 — Cost dashboard"** via `/in-cloud` — New cloud agent on branch `cursor/phase-4-2-cost-dashboard-f72f`. Outputs: metrics and Streamlit dashboard. Offline smoke ran. PR #10 was ready (not draft) and had a squash merge to `main`. Next was Phase 4.3. The parent pushed SIGAI docs.
- **"Phase 4.1 — Log everything (SQLite audit trail)"** via `/in-cloud` — New cloud agent on branch `cursor/phase-4-1-request-logging-c183`. Outputs: `app/audit/store.py` and `log_completion`. Database `data/requests.db` is gitignored. Offline smoke ran. PR #9 was ready (not draft). Review comment tools returned 403. Squash merge to `main` succeeded. Next was Phase 4.2. The parent pushed SIGAI docs.
- **"Phase 3.4 — Feedback to classifier (LLM Cost AutoPilot)"** via `/in-cloud` — New cloud agent on branch `cursor/phase-3-4-classifier-feedback-5b99`. Routing failures become labeled feedback JSONL. Weekly retrain script added. Offline smoke ran. PR #8 was ready (not draft). Comment tools returned 403. Squash merge to `main` succeeded. Phase 3 is complete. Next was Phase 4.1. The parent pushed SIGAI docs.
- **"Phase 3.3 — Auto-escalation (LLM Cost AutoPilot)"** via `/in-cloud` — New cloud agent on branch `cursor/phase-3-3-auto-escalation-7f9c`. Escalate on failure with a latency gate and JSONL. Offline smoke ran. PR was ready (not draft). Self-review ran. PR #7 had a squash merge. The parent updated SIGAI docs (cloud agent got 403 on SIGAI-Pilot). Next was Phase 3.4.

### 2026-08-01

- **"run the workflow as agents using /in-cloud per phase"** — Standing cloud workflow. One new branch and one cloud agent per numbered step. Run coding-guidelines and security-best-practices before git add, commit, and push. Run pr-review (Bugbot) after each PR. After merge, update SIGAI-Pilot `LLM-COST-Autopilot/Viviana-Ayala/{timeline,issues,prompts}.md`. Phase 3.1 → PR #4. Phase 3.2 → PR #5. Phase 3.3 → PR #7. Phase 3.4 → PR #8. All merged on 2026-08-01 or 2026-08-02.
- **"continue" / Phase 3 via `/in-cloud`** — Cloud agents for each phase step. Guidelines and security checks before commit and push. PR review after each phase. New branch and different agent per step. Phase 3.1 quality thresholds → PR #4 merged. Standing rule: after each phase merges, update these SIGAI-Pilot docs.
- **"make sure to update issues.md prompts.md and timeline.md in my SIGAI-Pilot files as well after each phase is merged"** — Standing process. The parent pushes SIGAI updates when the cloud agent has no write access.

### 2026-07-31 (evening)

- **"do phase 2.4 … /security-best-practices, /coding-guidelines, /pr-review … push to main and SIGAI-Pilot"** — The team made tier-to-model routing YAML and a loader. Security and coding-guidelines ran. The team opened a PR and ran a full pr-review before merge. The team updated these SIGAI docs.

### 2026-07-31

- **"do phase 2.3 … then /security-best-practices, /coding-guidelines, /pr-review … update SIGAI docs"** — The team trained logistic regression and random forest. Each model had 88.2% held-out accuracy. Logistic regression is the selected model. Security and coding-guidelines ran before commit. The team opened a PR and reviewed it. The team updated these three SIGAI docs.

### 2026-07-29

- **"/security-best-practices"** — Security review of the repo. Result: no critical or high findings. Secrets are git-ignored and not tracked. The real fix was to pin `requirements.txt` to exact versions.
- **"/pr-review 1"** — Review of PR #1 (Phase 2.2 feature signals). Result: approve with small fixes. The key fix: stop commits of generated `data/prompt_features.json` (add to `.gitignore` and run `git rm --cached`).
