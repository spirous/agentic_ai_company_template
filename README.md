# Agentic Company Template

A production-ready folder structure and agent system for running a company (or department) with AI-native workflows. Built for Claude Code and Anthropic's API, with optional local inference via Ollama.

## Architecture

This template organises company work as five intelligence loops — each loop feeds the next, and Learn feeds back into Sense:

| Loop | Purpose | Status |
| :--- | :--- | :--- |
| **Sense** | Market signals, customer intel, competitive monitoring | Scaffolded |
| **Decide** | Strategy, prioritisation, innovation assessment | Scaffolded |
| **Create** | Products, content, proposals, solutions | Scaffolded |
| **Deliver** | Communication, publishing, sales, operations | Fully wired |
| **Learn** | Feedback, performance, knowledge base updates | Fully wired |

## What's included

- **Deliver loop** — fully wired: meeting notes → Confluence, email drafting, contact intelligence, weekly review dashboard
- **Learn loop** — knowledge update agent that organically enriches contact files after every meeting or email
- **Shared** — document publishing agent, QA agent, style guide, email pattern library
- **Scripts** — all CLI tools ready to use after running setup

## Prerequisites

- Python 3.11+
- Claude Code CLI: `npm install -g @anthropic-ai/claude-code`
- A Confluence Cloud account with API token
- (Optional) Ollama for local inference: https://ollama.ai

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/YOUR_ORG/agentic-company-template.git
cd agentic-company-template
pip install -r requirements.txt
```

### 2. Run interactive setup

```bash
bash scripts/setup.sh
```

This writes your `.env`, updates `company/identity.md`, and optionally adds `scripts/` to `$PATH`.

### 3. Fill in your company identity

Edit `company/identity.md` with your company's mission, voice, and values.

Edit `company/style/style.md` to define your email tone and writing conventions.

## Command reference

| Command | What it does |
| :--- | :--- |
| `push-notes <file>` | Meeting notes → AI transform → Confluence |
| `push-notes <file> --to SPACE/'Parent'` | Custom Confluence destination |
| `follow-up "Company"` | Fetch contact intel → draft follow-up email |
| `meet-prep "Company"` | Meeting prep brief → Apple Notes |
| `add-contact-note "Company" "note"` | Append dated note to contact file |
| `export-note "keyword"` | Export Apple Note → push to Confluence |
| `python3 scripts/weekly_review.py` | Weekly review → Confluence dashboard + local drafts |

Full documentation: `PLAYBOOK.md`

## Folder structure

```
├── dashboards/       ← YOU: all interactive HTML boards
├── knowledge/        ← YOU: contacts, people, opportunities, initiatives
├── references/       ← YOU: drop PDFs and books here
├── .claude/skills/   ← one skill per command (machinery)
├── agents/           ← all agent prompt files, flat (machinery)
├── methodologies/    ← distilled frameworks: kth-irl, mom-test (machinery)
├── work/             ← per-workflow outputs, templates, archives (machinery)
├── company/          ← identity, brand voice, email style (machinery)
└── scripts/          ← all CLI tools (reached via shell aliases)
```

## Instantiating for a new company

1. Run `bash scripts/setup.sh`
2. Fill in `company/identity.md` and `company/style/style.md`
3. Add your first contact: `add-contact-note "Acme Corp" "Initial meeting"`
4. Push first notes: `push-notes path/to/notes.md`

## Adding a new capability

1. Write an agent prompt in `agents/` (note which business loop it serves in the file header)
2. Create a workflow folder in `work/<name>/` for its outputs and templates
3. Create a skill in `.claude/skills/<command>/SKILL.md`
4. Register the path in `scripts/config.py` if scripts need it
5. Add one row to the routing table in `CLAUDE.md` and update `PLAYBOOK.md`

## License

MIT
