## Prompts Log

This project uses Fable (Cursor's coding assistant) guided by a persistent AGENTS.md context file rather than one-off prompts. Representative prompts are logged below as they come up.

### 2026-07-29

- **"/security-best-practices"** — ran a security review of the repo. Outcome: no critical/high findings; secrets confirmed git-ignored and untracked. Actioned the one real item by pinning `requirements.txt` to exact versions.
- **"/pr-review 1"** — reviewed PR #1 (Phase 2.2 feature signals). Outcome: approve with nits; the key fix was to stop committing the generated `data/prompt_features.json` (added to `.gitignore` + `git rm --cached`).
