# Agentic Company — Playbook

## Vision
Build a small agentic company: a team of AI agents covering strategy, business development, execution, and growth — each triggered by a simple command, each owning a repeatable process end-to-end.

---

## Architecture

### The Engine Loop (how this project is organised)

```
SENSE → DECIDE → CREATE → DELIVER → LEARN → (back to SENSE)
```

Each loop has agents (capabilities), workflows (processes), and knowledge (what it produces and consumes).

### The Loading Tree (how Claude reads this project)

```
CLAUDE.md                        ← Always loaded. Routing rules + communication style only.
│
├── PLAYBOOK.md                  ← Human reference. Loaded on demand for planning.
│
├── engine/deliver/agents/       ← Deliver loop agent capabilities
│   ├── email_agent.txt
│   ├── contact_agent.txt
│   └── meeting_prep_agent.txt
│
├── engine/learn/agents/         ← Learn loop agent capabilities
│   └── knowledge_update_agent.txt
│
├── shared/agents/               ← Cross-loop capabilities
│   ├── document_agent.txt
│   └── qa_agent.txt
│
└── engine/deliver/workflows/    ← Processes using those agents
    ├── meeting-intelligence/
    ├── email-intelligence/
    └── contact-intelligence/
```

**Key principle:** Agents are capabilities (what someone knows how to do). Workflows are processes (who does what, in what order). They are always kept separate so agents can be reused across multiple workflows.

**Loading rule:** Claude reads `CLAUDE.md` → finds the workflow → loads only the specific agent files needed for that task. Nothing else.

---

## Knowledge Base Update Guardrail

Every workflow automatically proposes contact file updates after completion.
The user always confirms before anything is saved — nothing is written silently.

**Triggers:**
| Workflow | When it fires |
| :--- | :--- |
| `push-notes` | After successful Confluence publish |
| `push-notes --local` | After successful Confluence publish |
| `draft-email` | After user approves a draft |

**What gets extracted:** role/title updates, priorities, concerns, technical interests, relationship signals, open items.

**What is never extracted:** pricing, deal terms, NDA details, anything marked CONFIDENTIAL or SENSITIVE, personal data unrelated to the professional relationship.

**Agent:** `engine/learn/agents/knowledge_update_agent.txt`
**Utility:** `scripts/knowledge_utils.py` — shared across all pipelines

---

## Information Architecture — Where Things Live

| Content type | Destination | Audience | Reason |
| :--- | :--- | :--- | :--- |
| Meeting notes | Confluence (under company page) | Whole team | Team knowledge, shared visibility |
| Relationship brief (CI page) | Confluence (under company page) | Whole team | Strategic context, marked CONFIDENTIAL |
| Status dashboard | Confluence (space root) | Whole team | Useful overview for team + management |
| Email drafts | Local file on Desktop | Personal only | Operational, half-finished, never for sharing |
| Pricing / deal terms | CRM only | Sales team | Never in this workspace |
| NDA status | Personal knowledge only | — | Company-visible wiki; NDA existence is sensitive |

**The rule in one sentence:** Confluence = company knowledge; local = personal operations.

---

## AI Ecosystem Concepts

| Term | Definition |
| :--- | :--- |
| **Agent** | A capability — a prompted role that knows HOW to do one thing |
| **Skill** | A packaged, invocable agent (in Claude Code: a slash command) |
| **Tool** | A function interface (API call, file I/O, shell command) |
| **Workflow** | Orchestrates agents + tools in a defined process |
| **Knowledge Base** | Stored information agents can retrieve |

---

### Agent Roster

| Agent | File | Role | Used by |
| :--- | :--- | :--- | :--- |
| Document Agent | `shared/agents/document_agent.txt` | Raw notes → structured Confluence XHTML | `meeting-intelligence` |
| Contact Agent | `engine/deliver/agents/contact_agent.txt` | CI page → follow-up email draft | `contact-intelligence` |
| Email Agent | `engine/deliver/agents/email_agent.txt` | Clipboard / description → email draft | `email-intelligence` |
| Meeting Prep Agent | `engine/deliver/agents/meeting_prep_agent.txt` | Past notes + context → meeting brief | `meet-prep` |
| Knowledge Update Agent | `engine/learn/agents/knowledge_update_agent.txt` | Notes/email → contact file update | All pipelines |
| QA Agent | `shared/agents/qa_agent.txt` | Output quality review | In development |

---

### Workflow Map

| Workflow | Status | Input | Output | Command |
| :--- | :--- | :--- | :--- | :--- |
| `meeting-intelligence` | ✅ Active | Raw meeting notes `.md` | Confluence protocol page | `push-notes` |
| `contact-intelligence` | ✅ Active | Confluence CI page | Dashboard (Confluence) + email drafts (local) | `follow-up`, `review-contacts` |
| `email-intelligence` | ✅ Active | Clipboard / description | Interactive draft → clipboard | `draft-email` |
| `meet-prep` | ✅ Active | Company name | Brief → Apple Notes | `meet-prep` |
| `loan-agreements` | ✅ Active | Company + equipment + signatory fields | Filled .docx (local) + Confluence tracking page + email draft via Ollama | `fill-loan` |
| `irl-decision` | ✅ Active | Initiative name + guided interview | IRL profile `.md` + assessment table + dimension action plans | `irl-new`, `irl-assess`, `irl-advance`, `irl-review` |

---

## Commands

```zsh
# ── Meeting Intelligence ────────────────────────────────────────────────────
push-notes <file>                                  # cloud, default destination
push-notes <file> --to SPACE/'Parent Page'         # cloud, custom destination
push-notes <file> --local                          # local Ollama model

# ── Contact Intelligence ────────────────────────────────────────────────────
new-contact "Company" "Parent Page Title"          # create CI page in Confluence
follow-up "Company"                                # draft follow-up email (cloud)
follow-up "Company" --local                        # draft follow-up email (Ollama)
follow-up "Company" --context "context note"       # with extra context
review-contacts                                    # run weekly review (Ollama)
review-contacts --dry-run                          # preview without publishing
review-contacts --cloud                            # run with Anthropic API

# ── Email Intelligence ──────────────────────────────────────────────────────
draft-email                                        # reply to clipboard (cloud)
draft-email --local                                # reply to clipboard (Ollama)
draft-email --new "description"                    # new outbound email
draft-email --file email.txt                       # read from file

# ── Meeting Prep ────────────────────────────────────────────────────────────
meet-prep "Company"                                # brief from past notes
meet-prep "Company" "focus note"                   # with specific focus
meet-prep "Company" --local                        # via Ollama

# ── Contact Notes ────────────────────────────────────────────────────────────
add-contact-note "Company" "quick note"            # append dated note
add-contact-note "Company"                         # open file in editor
add-contact-note --list                            # show all contact files

# ── Legal — Loan Agreements ─────────────────────────────────────────────────
# Terminal command — runs entirely locally (Word fill + Confluence page + Ollama email):
fill-loan --company "Institute" --type standard --fields engine/legal/workflows/loan-agreements/active/fields_COMPANY.json --recipient "First Last" --recipient-email contact@institute.org
fill-loan ... --type ds                            # your company handles shipping both ways
fill-loan ... --skip-confluence                    # renewal — page already exists
fill-loan ... --dry-run                            # preview Confluence page without creating
# In Claude Code: type fill-loan "Company" → guided field collection → outputs fields JSON + command

# ── IRL Decision Framework ───────────────────────────────────────────────────
irl-new "Initiative Name"                          # guided interview → build initiative profile
irl-assess "Initiative Name"                       # assessment table, risk flags, priority dimension
irl-advance "Initiative Name" DIM                  # action plan + draft artifact for next level
irl-review                                         # portfolio matrix, stalled items, top priorities

# ── Cron ────────────────────────────────────────────────────────────────────
zsh scripts/setup-cron.sh                          # install Monday 08:00 cron
zsh scripts/setup-cron.sh --remove                 # remove cron job
```

---

## Conventions for Adding New Workflows

1. **Add agents first** — create `engine/<loop>/agents/<role>_agent.txt`
2. **Create a workflow folder** — `engine/<loop>/workflows/<name>/`
3. **Write a manifest** — `workflow.md` listing agents, pipeline steps, defaults
4. **Add a template** — `templates/` for the output structure
5. **Register the trigger** in `CLAUDE.md`
6. **Add a CLI command** in `scripts/` if it needs a terminal entry point
7. **Update this file** — add a row to Agent Roster and Workflow Map
8. **Register the path** in `scripts/config.py`

**Naming rules:**
- Folders: `kebab-case`
- Agent files: `<role>_agent.txt`
- Raw input: `YYYY-MM-DD_<topic>_raw.md`
- Processed output: `YYYY-MM-DD_<topic>_processed.md`
- Archive: `engine/<loop>/workflows/<name>/archive/<year>/`
