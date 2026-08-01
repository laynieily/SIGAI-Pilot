# [AI] Session Log

## [AI] Attribution Convention
[AI] Lines marked `[AI]` were written by the AI assistant.
[AI] Lines marked `[LC]` were written by me (Luis Chavez).
[AI] Unmarked lines are mine by default.

---

## [AI] Split with `ai_questions.md`

[AI] `ai_questions.md` records **what was asked and what was done with it** —
[AI] one entry per question, with a one-word verdict. This file records **why,
[AI] what broke, and what was learned**. Verdicts are not restated here; entries
[AI] cite question IDs (`Q-MMDD-n`) instead.

[AI] Cadence: one entry per commit.

---

## [AI] Entry Template

[AI] Copy the block below for each new log entry.

```
### [LC] Entry — <date>

**Commit:** <commit subject line — the SHA is greppable from this later>

**What I was doing:**


**What happened (error, success, decision):**


**Questions resolved:** Q-YYYYMMDD-n, Q-YYYYMMDD-n


**What I'd tell a freshman about this:**
<optional>
```

---

### [LC] Entry — 2026-07-15


**What I was doing:**
I was writing a simple test post request to the llama server on my machine.

**What happened (error, success, decision):**
I ran into some syntax and python specific errors, including .venv setup and installation mishaps.
I wrote main.py post request on my own and had Sonnet 5 review it. I'm not as experienced in python as I am in Rust/C++
so my simple function had many errors. I had a timeout bug, didn't set the timeout past the default (5 seconds) so timeout happened before
the model could respond.
I got it working shortly on my own after a little review and a few claude questions.

**What I asked AI, and what I did with the answer (used it, adapted it, rejected it):**
I asked claude about the errors, it provided me with a details 5 item list about each issue.
I attempted fixing the issues based on claude's response and reviewed some docs for POST syntax.
I accepted all of the AIs advice about syntax, I rejected its incorrect advice about the .venv as it was missing context. (wrong directory)

**What I'd tell a freshman about this:**
Making sure you understand every line of your code starts like this (especially with new concepts). Writing ugly functions, they break, you fix them and ask questions when you get stuck. Claude could've done this in seconds, but by doing this myself and having it review, I have the foundation.
Don't build your projects on a fragile base of understanding from reading output, have a strong foundation (for me it's writing new
concepts entirely on my own) (method might change/update in later entries).

---

### [LC] Entry — 2026-07-21

(no previous entry due to it just being a folder restructuring)
**What I was doing:**
Generating a plan for the initial steps of the project using Opus based on some Fable architecture suggestions.

**What happened (error, success, decision):**
Opus generated a plan with a few flaws that I fixed.

**What I asked AI, and what I did with the answer (used it, adapted it, rejected it):**
I asked Fable about the plan's structure, architecturally it fit well but it had one major issue. In the model config dataclass, it had one field -> cost_per_1k instead of having input and output costs each as individual fields. It additionally had the wrong formula using this variable when calculating cost in the Response section. I recognized this from prior knowledge since I know models have differnet output/input costs as the computational power necessary to generate an output is far higher than the cost to read a prompt. I accepted most of Opus's initial draft save for that bug with the ModelConfig as most of the first output passed the scrutiny test.

**What I'd tell a freshman about this:**
The goal is always to build expertise in whatever you are working with. Applying general scrutiny to model output is always good practice. If you aren't sure about something, consult the docs, consult a stronger model, and when working with AI including the model in the planning phase is certainly important.

---

### [LC] Entry — 2026-07-28

**What I was doing:**
I was restructuring the Response and Model Config dataclasses while discussing with claude proper next steps. 

**What happened (error, success, decision):**
Leading with the Response structure question in ai_questions.md, we ended on a refactor of the response and model config dataclasses themselves. Some of the main issues in design were that model config shouldn't delegate the price calculation to response, as in the previous design Response's cost function was passing in a model config and grabbing values from it. Leave a one time price calculation to the model config dataclass, and reuse that as intended. Another important issue was that response was not built for provider specifications. As detailed in the plan.md, the purpose of the adapter is to handle all of the provider "weirdness", and here's an example. OpenAI precalculates total tokens, while providers like Anthropic and Ollama do not. The solution we landed on was to always have response calculate total tokens itself. Additionally, reponse did not have a clean way to indicate a failure. You needed to supply a ton of numerical fields before reaching the ok=False. Fixed with an @classmethod that that does not rely on a class instance.

**What I asked AI, and what I did with the answer (used it, adapted it, rejected it):**
AI suggested a lot of the changes that I implemented here. Though I did feel as if Claude was getting ahead of itself a bit on some of the design decisions. For example, I felt as if I kept claude running and just asked it to re-review the code each time it would constantly try to correct for errors that don't exist yet. I manually reuqested a summary() function for human-readable output in the later phases.

**What I'd tell a freshman about this:** 
None

---

### [LC] Entry — 2026-07-29

**Commit:** Config and Env Example.

**What I was doing:**
Working on Config.py and some environment decisions. 

**What happened (error, success, decision):**
I don't have an API key yet, so I was planning with Claude on how to move forward and work around it for now. We concluded it isn't a blocker and worked on how to delegate missing key failures. We decided to have provider roots in url and having the adapter handle the appending of the "provider specific weirdness" as described in the plan. We set up the .env.example for the API key in the future too. Looking forward we discussed the adapters and I asked clarifying questions about their structure, specifically the choice between many different adapters. 


**Questions resolved:** 1-2026-07-29, 2-2026-07-29, 3-2026-07-29.


