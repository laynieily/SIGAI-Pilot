## Prompts Log

This project uses Fable (Cursor's coding assistant) guided by a persistent AGENTS.md context file rather than one-off prompts. Representative prompts are logged below as they come up.

### 2026-08-01

- **"continue" / Phase 3 via `/in-cloud`** — spawned cloud agents per phase step; coding-guidelines + security-best-practices before commit/push; pr-review after each phase; new branch + different agent per step. Phase 3.1 quality thresholds → PR #4 merged. Standing rule: after each phase merges, update these SIGAI-Pilot docs (`issues.md`, `prompts.md`, `timeline.md`).
- **"make sure to update issues.md prompts.md and timeline.md in my SIGAI-Pilot files as well after each phase is merged"** — recorded as standing process; backfilled Phase 3.1 into these three files.

### 2026-07-31 (evening)

- **"do phase 2.4 … /security-best-practices, /coding-guidelines, /pr-review … push to main and SIGAI-Pilot"** — built tier→model routing YAML + loader; ran security + coding-guidelines; opened PR and full pr-review before merge; updated these SIGAI docs.

### 2026-07-31

- **"do phase 2.3 … then /security-best-practices, /coding-guidelines, /pr-review … update SIGAI docs"** — trained logistic regression vs random forest (both 88.2% held-out; LR winner). Ran security + coding-guidelines before commit; opened a PR and reviewed it. Updated these three SIGAI docs.

### 2026-07-29

- **"/security-best-practices"** — ran a security review of the repo. Outcome: no critical/high findings; secrets confirmed git-ignored and untracked. Actioned the one real item by pinning `requirements.txt` to exact versions.
- **"/pr-review 1"** — reviewed PR #1 (Phase 2.2 feature signals). Outcome: approve with nits; the key fix was to stop committing the generated `data/prompt_features.json` (added to `.gitignore` + `git rm --cached`).
