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

Edit `shared/style/style.md` to define your email tone and writing conventions.

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
├── company/          ← who this company is (identity, org map)
├── engine/
│   ├── sense/        ← market intel (scaffold — build for your context)
│   ├── decide/       ← strategy, methodologies (scaffold)
│   ├── create/       ← products, content (scaffold)
│   ├── deliver/      ← comms, publishing, sales (fully wired)
│   └── learn/        ← knowledge updates (fully wired)
├── shared/           ← cross-loop: document agent, QA agent, style guide
├── knowledge/        ← company memory: contacts
└── scripts/          ← all CLI tools
```

## Instantiating for a new company

1. Run `bash scripts/setup.sh`
2. Fill in `company/identity.md` and `shared/style/style.md`
3. Add your first contact: `add-contact-note "Acme Corp" "Initial meeting"`
4. Push first notes: `push-notes path/to/notes.md`

## Extending to other loops

Each unpopulated loop (sense, decide, create) follows the same pattern:

1. Write a role definition in `engine/<loop>/roles/`
2. Write an agent prompt in `engine/<loop>/agents/`
3. Write a workflow in `engine/<loop>/workflows/`
4. Register the path in `scripts/config.py`
5. Add the command to `COMMANDS.md` and `PLAYBOOK.md`

## License

MIT
