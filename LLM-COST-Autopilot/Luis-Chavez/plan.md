# LLM Optimizer — Plan

## Goal

Reroute expensive LLM requests to cheaper/simpler models when the cheaper model
is "good enough," falling back to the expensive one when it isn't. To decide
*anything* about routing, the system first needs to talk to more than one model
through a single, uniform interface. That's Phase 1.

---

## Phase 1 — Unified Model Interface

**Objective:** call any model (local Ollama, hosted API) through one function,
`send_request(config, prompt) -> Response`, where the caller never has to know
which provider is behind it. This is the foundation the router (Phase 2) sits on.

The two contracts below are the whole point of Phase 1.

### ModelConfig — what defines a provider/model?

One instance = one callable model endpoint. The router will hold several of these
and choose between them.

| field         | type            | why it exists |
|---------------|-----------------|---------------|
| `name`        | `str`           | logical handle the router uses, e.g. `"cheap-local"`, `"smart-cloud"`. Not the model string. |
| `provider`    | `str` / enum    | `"ollama"`, `"openai"`, `"anthropic"` — selects which adapter formats the request/parses the response. |
| `model`       | `str`           | the actual model id, e.g. `"llama3.2"`, `"claude-haiku-4-5-20251001"`. |
| `base_url`    | `str`           | host root, e.g. `"http://localhost:11434"`. The adapter appends its own path (`/api/generate`, `/v1/messages`) — the path is provider-specific, same as headers. |
| `api_key`     | `str \| None`   | `None` for local. Load from env (`.env` is already gitignored) — store the value, not the key name, so the adapter doesn't do env lookups. |
| `tier`        | `str` / enum    | `"cheap"` / `"expensive"` (or an int). The single field routing decisions read; keeps Phase 2 from re-deriving cost. |
| `cost_in_per_million`  | `float`  | $ per 1M **input** (prompt) tokens (0.0 for local). |
| `cost_out_per_million` | `float`  | $ per 1M **output** (completion) tokens (0.0 for local). Input and output are billed at different rates, so both are needed to compute real cost. |
| `max_tokens`  | `int`           | cap on generation. |
| `timeout`     | `int`           | seconds. Your first bug was a too-short default — make it explicit here. |

*Start with a `@dataclass`.* Skip Pydantic until you actually load configs from a
file and want validation — don't pay for it before Phase 1 needs it.

### Response — what does `send_request` always return?

The contract that makes providers interchangeable. **Every** adapter returns this
exact shape regardless of the raw JSON the provider sent back. The router and any
logging code only ever see this.

| field               | type            | why it exists |
|---------------------|-----------------|---------------|
| `text`              | `str`           | the completion. What a caller usually wants. |
| `model`             | `str`           | which model *actually* answered (for logs + verifying a reroute happened). |
| `prompt_tokens`     | `int`           | input token count, from provider usage. Ollama reports it as `prompt_eval_count` — no estimation needed. |
| `completion_tokens` | `int`           | output token count. |
| `total_tokens`      | `int`           | convenience; `prompt + completion`. |
| `cost`              | `float`         | `(prompt_tokens / 1_000_000) * config.cost_in_per_million + (completion_tokens / 1_000_000) * config.cost_out_per_million`. The number Phase 2 optimizes. |
| `latency_ms`        | `float`         | wall-clock time of the call. Cheap models should win here too. |
| `ok`                | `bool`          | did the call succeed? |
| `error`             | `str \| None`   | message when `ok` is False, so one failing provider doesn't crash the router. |
| `raw`               | `dict`          | untouched provider JSON. Escape hatch for debugging + fields you didn't map yet. |

**Design rule:** all provider-specific weirdness dies inside the adapter. Anything
downstream of `send_request` reads `Response`, never `raw` (except when debugging).

---

## Build order

Each step is small and independently runnable — matches how you like to work
(write it, break it, fix it). "Done when" is the check that lets you move on.

1. **`Response` dataclass**
   *Done when:* you can hand-build one from a dict and `print()` it cleanly.
   Define the destination before anything has to produce it.

2. **`ModelConfig` dataclass + two instances** (one Ollama, one hosted)
   *Done when:* both instantiate without network calls; the hosted one pulls its
   `api_key` from env and doesn't crash when the key is missing.

3. **Ollama adapter — refactor `main.py` into `send_request(config, prompt)`**
   *Done when:* your existing local `llama3.2` call returns a populated `Response`
   (real `text`, `latency_ms`, `raw`) instead of printing a raw dict.

4. **Second adapter (Anthropic or OpenAI) behind the same signature**
   *Done when:* swapping only the `ModelConfig` passed to `send_request` changes
   which provider answers — zero changes at the call site. This is the proof the
   abstraction holds.

5. **Config registry / lookup**
   *Done when:* configs live in one place (dict now, file later) and you can fetch
   one by `name`. This is the handle Phase 2's router will reach for.

**Phase 1 exit criteria:** a loop that sends the same prompt to the cheap config
and the expensive config and prints both `Response`s side by side — same shape,
different `model`/`cost`/`latency_ms`. Once you can *see* that comparison, you have
everything the router needs to start choosing.

---

## Phase 2 (sketch — not now)

The router: given a prompt, decide cheap vs expensive *before* calling. Options to
weigh later — prompt heuristics (length/keywords), a cheap-model-first + escalate-on-
low-confidence cascade, or a small classifier. Phase 1 deliberately gives this phase
clean inputs (`ModelConfig.tier`) and clean feedback (`Response.cost`/`latency_ms`)
so the routing logic has nothing to untangle.
