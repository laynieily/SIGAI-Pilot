# SIGAI PILOT Project Documentation Repository

This repository serves as a shared documentation space for all SIGAI project work. Its purpose is to keep our approaches, experiments, and development processes transparent, organized, and easy to reference across the team.

Each project has its own dedicated folder, and within each project folder, every team member has a personal documentation space containing three Markdown files:

# Repository Structure
```
/
├── Project-Name/
│   ├── Member-Name/
│   │   ├── issues.md
│   │   ├── prompts.md
│   │   └── timeline.md
│   ├── Member-Name/
│   │   ├── issues.md
│   │   ├── prompts.md
│   │   └── timeline.md
│   └── ...
│
├── Another-Project/
│   ├── Member-Name/
│   │   ├── issues.md
│   │   ├── prompts.md
│   │   └── timeline.md
│   └── ...
│
└── ...
```

# Folder Purpose

## Project Folder
Each project gets its own top-level directory. This keeps documentation separated and makes it easy to track progress across multiple intiatives.

## Member Folder
Inside each project folder, every contributor has a personal directory. This allows members to document their individual approaches, challenges, and workflows without overwriting or conflicting with others.

# Required Markdown Files
Each member folder contains three standardized Markdown files:

### issues.md
A running log of problems, bugs, blockers, or unexpected behavior encountered during the project.
Use this file to document:

- What went wrong
- How you diagnosed it
- How it was resolved (if applicable)
- Any lessons learned

### prompts.md
A record of prompts submitted to Claude (or other LLMs) during development.
Include:

- The prompt
- The model’s response (optional)
- Notes on how the response influenced your work

This helps us understand how AI tools shaped our decision-making.

### timeline.md
A chronological overview of your personal workflow throughout the project.
This may include:

- Milestones
- Tasks completed
- Key decisions
- Shifts in approach
- Anything relevant to your development process

Also important to add a link to your project repo in the beginning.



# Goals of This Repository
 - Maintain clear, version-controlled documentation for all projects
 - Improve collaboration by making individual approaches visible
 - Support onboarding by showing how past projects were executed
 - Encourage reflective development practices
 - Provide a shared reference for future improvements and research

# Contributing
When starting a new project:

1. Create a new project folder at the root level.
2. Add a folder with your name inside the project directory.
3. Include the three required Markdown files.
4. Link the repo to your project in the beginning of timeline.md
5. Update them regularly as the project progresses.