# Timeline

## Initial Research
I first reviewed the BASWE AI Engineering Projects, specifically **Project 15**, and read through the guide outlining what the team should research and understand. This helped me get a clear picture of the system we're building:

> A multi‑agent orchestration platform where a supervisor agent decomposes complex tasks, delegates subtasks to specialized tool‑using agents, maintains persistent memory across interactions, and escalates to a human operator when confidence is low or approval is required — with full visibility into every agent decision.

---

## July 22
I scaffolded the local project environment.

- Created and activated a virtual environment  
- Set up the folder structure (`src/schemas`, `src/tools`, `src/agents`, etc.)  
- Installed dependencies using the requirements Claude generated  
- Wrote a README documenting setup for both Windows and macOS/Linux  
- Built the first real piece of Phase 1: a mock LLM layer (`mock.py` and `provider.py`)

---

## July 24
The team held the first weekly meeting.  
We mainly discussed documentation standards, which led to the creation of the Markdown files in this shared repository.

---

## July 27
I created the shared repository and wrote a README detailing its organization and purpose.

---

## July 28
I cleaned up my documentation so it was deliverable and tangible.  
Afterward, I returned to the project and continued Phase 1 of the BASWE guide.

---

## July 29
I followed the guide and began implementing the project models.  
Successfully created auto‑generated IDs for each task and subtask.

---

## July 31
I created the `ExecutionPlan` class based on the BaseModel structure.  
Also submitted additional documentation updates.

---

## August 1 – August 21
Worked through the remaining phases of the BASWE guide, closing out Phase 1 and completing Phases 2 and 3, then extending the project with a full API and frontend layer.

- Finished Phase 1: built out the tool registry and core tool set (web search, file read/write, code execution, database query, API call), each scoped to specific agents with rate limiting and full call logging, and wired together the Reviewer, Supervisor, and Specialist agents
- Built the memory system — short-term working memory for a single task's execution, and long-term semantic memory backed by ChromaDB so the system recalls similar past tasks when planning new ones
- Implemented true human-in-the-loop behavior using LangGraph's interrupt/resume pattern, so the system pauses and waits for a real approval when plan confidence is low or a subtask keeps failing review
- Built a FastAPI backend exposing task submission and the approval queue, and verified the full pause-and-resume flow end to end over real HTTP requests
- Built a React frontend (Dashboard, Chat, Approvals) for submitting requests and reviewing/resolving escalations, including branching the approval UI between plan-level (approve/reject) and subtask-level (accept/take-over/abort) decisions
- Ran a full audit across the codebase to catch remaining bugs — including a broken import that prevented the API from starting, an authorization mismatch that silently failed every code-execution subtask, and a search tool bug that capped results at one — before moving into the next phase
