## Issues Log

- OpenAI API key invalid (401 error) -> disabled in .env. Not currently required; GPT-4o pricing stays in the model registry for the planned Phase 4.3 cost comparison.
- - Ollama local install had an empty app bundle, blocking local model access -> resolved by reinstalling Ollama and pulling llama3.2.
  - - gemini-pro returned 429 (free tier has zero-request quota) -> dropped gemini-pro from the provider set; gemini-flash works fine as a Tier 2 model.
   
    - Current blockers: none as of 2026-07-24.
    - 
