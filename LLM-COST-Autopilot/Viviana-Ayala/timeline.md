Project repo: https://github.com/Vayala13/LLM-COST-Autopilot.git

## Timeline

- 2026-07-23 — Phase 1.1–1.3: Built app/providers/ (ModelConfig registry, Response object, unified send_request). Ran 10 baseline prompts via scripts/baseline_test.py. Live smoke test passed on Anthropic; OpenAI/Ollama skipped gracefully. Set up project foundation (.env, config.py, venv) and a portfolio devlog site.
- - 2026-07-24 — Phase 1.3: Reinstalled Ollama (fixed empty app bundle blocker), pulled llama3.2, started daemon. Ran full 10-prompt baseline across claude-sonnet, claude-haiku, and llama-local (30 records logged to data/baseline_results.json). Cost totals: Sonnet $0.0386, Haiku $0.0061 (−84%), Llama $0.00. Added Gemini provider (gemini-flash works as a Tier 2 model; gemini-pro dropped due to 429 quota). Installed Figma plugin and drafted an architecture diagram.
  - - 2026-07-24 — Phase 2.1: Defined the 3 complexity tiers (configs/complexity_tiers.yaml) with distinguishing signals and a 4-provider set (claude-sonnet, claude-haiku, gemini-flash, llama-local). Disabled invalid OpenAI key in .env so baseline runs skip cleanly.
   
    - ## Current Status (as of 2026-07-24)
    - Phase 2 of 6 — Complexity Classifier (in progress). Next: Phase 2.2 — write 200+ hand-labeled example prompts across the 3 tiers and extract features (token count, instruction verbs, constraint count, context provided, output-format complexity).
    - 
