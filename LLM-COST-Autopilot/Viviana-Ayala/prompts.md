## Prompts Log

This project uses Fable (Cursor's coding assistant) guided by a persistent AGENTS.md context file rather than one-off prompts. Representative prompts are logged below as they come up.

### 2026-08-02

- **"Phase 4.1 — Log everything (SQLite audit trail)"** via `/in-cloud` — new cloud agent on branch `cursor/phase-4-1-request-logging-c183`; `app/audit/store.py` + `log_completion` call-site helper; gitignored `data/requests.db`; smoke offline; PR #9 ready (not draft); self-review (gh/ManagePullRequest comment 403); squash-merged to main. Next Phase 4.2. SIGAI docs pushed by parent.
- **"Phase 3.4 — Feedback to classifier (LLM Cost AutoPilot)"** via `/in-cloud` — new cloud agent on branch `cursor/phase-3-4-classifier-feedback-5b99`; routing failures → labeled feedback JSONL + weekly retrain script; smoke offline; PR #8 ready (not draft); self-review (gh comment 403); squash-merged to main. Phase 3 complete → next Phase 4.1. SIGAI docs pushed by parent.
- **"Phase 3.3 — Auto-escalation (LLM Cost AutoPilot)"** via `/in-cloud` — new cloud agent on branch `cursor/phase-3-3-auto-escalation-7f9c`; escalate-on-failure with latency gate + JSONL; smoke offline; PR ready (not draft); self-review; squash-merge PR #7; SIGAI docs updated by parent (cloud agent 403 on SIGAI-Pilot). Next = Phase 3.4.

### 2026-08-01

- **"run the workflow as agents using /in-cloud per phase"** — standing cloud workflow: one new branch + one cloud agent per numbered step; coding-guidelines + security-best-practices before git add/commit/push; pr-review (Bugbot) after each PR; after merge update SIGAI-Pilot `LLM-COST-Autopilot/Viviana-Ayala/{timeline,issues,prompts}.md`. Phase 3.1 → PR #4; Phase 3.2 → PR #5; Phase 3.3 → PR #7; Phase 3.4 → PR #8 (all merged 2026-08-01/02).
- **"continue" / Phase 3 via `/in-cloud`** — spawned cloud agents per phase step; coding-guidelines + security-best-practices before commit/push; pr-review after each phase; new branch + different agent per step. Phase 3.1 quality thresholds → PR #4 merged. Standing rule: after each phase merges, update these SIGAI-Pilot docs.
- **"make sure to update issues.md prompts.md and timeline.md in my SIGAI-Pilot files as well after each phase is merged"** — recorded as standing process; parent pushes SIGAI updates when cloud agent lacks write access.

### 2026-07-31 (evening)

- **"do phase 2.4 … /security-best-practices, /coding-guidelines, /pr-review … push to main and SIGAI-Pilot"** — built tier→model routing YAML + loader; ran security + coding-guidelines; opened PR and full pr-review before merge; updated these SIGAI docs.

### 2026-07-31

- **"do phase 2.3 … then /security-best-practices, /coding-guidelines, /pr-review … update SIGAI docs"** — trained logistic regression vs random forest (both 88.2% held-out; LR winner). Ran security + coding-guidelines before commit; opened a PR and reviewed it. Updated these three SIGAI docs.

### 2026-07-29

- **"/security-best-practices"** — ran a security review of the repo. Outcome: no critical/high findings; secrets confirmed git-ignored and untracked. Actioned the one real item by pinning `requirements.txt` to exact versions.
- **"/pr-review 1"** — reviewed PR #1 (Phase 2.2 feature signals). Outcome: approve with nits; the key fix was to stop committing the generated `data/prompt_features.json` (added to `.gitignore` + `git rm --cached`).
