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

### Three-Tier Loading (how Claude reads this project)

Token consumption is progressive: each tier loads only when a task actually needs it.

```
Tier 1 · Always loaded (~1k tokens)
  CLAUDE.md                    ← Guardrails, style, command→skill routing table. Nothing else.

Tier 2 · Loaded when a command is invoked (~500 tokens per skill)
  .claude/skills/<command>/SKILL.md
                               ← The process: steps, inputs, outputs, and which
                                 Tier-3 files to read at which step.

Tier 3 · Loaded only at the step that needs it
  engine/<loop>/agents/*.txt   ← Agent capabilities (reused across skills)
  shared/agents/*.txt          ← Cross-loop agents (document, QA)
  shared/templates/            ← Output structures
  knowledge/contacts/<one>.md  ← One entity per read, never the whole folder
  engine/decide/methodologies/kth-irl/initiatives/<one>.md
  company/identity.md          ← Only for externally published output
```

### Folder Map

```
├── CLAUDE.md          Tier 1 router
├── PLAYBOOK.md        Human reference, never auto-loaded
├── dashboards/        ← YOU: all interactive HTML boards, one place
├── knowledge/         ← YOU: contacts, people, opportunities (your data)
├── shared/references/ ← YOU: drop PDFs and books here
├── .claude/skills/    Tier 2 — one skill per command (machinery)
├── engine/            Business loops: sense, decide, create, deliver, learn, legal (machinery)
│   └── <loop>/
│       ├── agents/    Capability prompt files
│       └── workflows/ Working files + outputs per workflow (archives gitignored)
├── shared/            Cross-cutting agents, templates, style (machinery)
├── company/           Identity and market facts (machinery)
└── scripts/           CLI entry points — reached via shell aliases, not by browsing
```

**Human navigation rule:** you only ever touch the folders marked YOU. Everything else is machinery that skills and scripts navigate for you.

**Key principles:**
- **Agents are capabilities** (what someone knows how to do). **Skills are processes** (which steps, in what order, loading what). Kept separate so agents are reused across skills.
- **Knowledge is entity-sharded.** One file per contact, per initiative. A task loads one file, never scans a folder.
- **Outputs are terminal.** Archives and `_processed` files never re-enter context unless explicitly requested.
- **Growth is flat-cost.** A new workflow adds one skill folder and one routing-table row. Tier 1 size stays constant.

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
| Person files (`knowledge/people/`) | Local only — never Confluence, never emails | Personal only | 1-on-1 notes about colleagues are more sensitive than customer notes |

**The rule in one sentence:** Confluence = company knowledge; local = personal operations.

---

## AI Ecosystem Concepts

| Term | Definition |
| :--- | :--- |
| **Agent** | A capability — a prompted role that knows HOW to do one thing |
| **Skill** | An invocable process manifest (Claude Code native, lazy-loaded from `.claude/skills/`) |
| **Tool** | A function interface (API call, file I/O, shell command) |
| **Workflow** | Working directory for a process: inputs, outputs, templates |
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
| CRL Pipeline Agent | `engine/deliver/agents/crl_pipeline_agent.txt` | KTH CRL assessment, bottleneck analysis, next action writing for prospect accounts | `crl-pipeline` |

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
| `crl-pipeline` | ✅ Active | Contact files + meeting notes | Structured CRL assessment per account + dashboard update + contact file Pipeline Status | `crl-pipeline`, `crl-update` |

---

## Commands

```zsh
# ── Meeting Intelligence ────────────────────────────────────────────────────
push-notes <file>                                  # cloud, default destination
push-notes <file> --to SPACE/'Parent Page'         # cloud, custom destination
push-notes <file> --local                          # local Ollama model

# ── Prospect Onboarding ─────────────────────────────────────────────────────
onboard-prospect "Company" --country Germany --sector your_sector   # full Confluence hierarchy
onboard-prospect "Company" --country Japan --sector new_sector --new-sector  # create new sector

# ── Meeting Log (end-to-end) ─────────────────────────────────────────────────
log-meeting "Company" --space PROJ1 --parent 'Company - Meeting Notes'
log-meeting "Company" --space PROJ1 --parent 'Company - Meeting Notes' --topic "Q3 review"

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

# ── CRL Pipeline ─────────────────────────────────────────────────────────────
# In Claude Code:
crl-pipeline "YOUR_INITIATIVE"                     # full review: read contact files, assess all accounts, propose updates
crl-update "account-codename" --crl 5             # advance a single account with evidence
crl-update "account-codename" --bottleneck "text" # update bottleneck only
# Dashboard (open in browser):
open dashboards/crl-pipeline.html

# ── Cron ────────────────────────────────────────────────────────────────────
zsh scripts/setup-cron.sh                          # install Monday 08:00 cron
zsh scripts/setup-cron.sh --remove                 # remove cron job
```

---

## Conventions for Adding New Workflows

1. **Pick the engine loop** — sense, decide, create, deliver, learn, or legal
2. **Add agents first** — create `engine/<loop>/agents/<role>_agent.txt`; reuse existing agents where possible
3. **Create a workflow folder** — `engine/<loop>/workflows/<name>/`
4. **Write a manifest** — `workflow.md` listing agents, pipeline steps, defaults
5. **Add a template** — `templates/` for the output structure
6. **Create the skill** — `.claude/skills/<command>/SKILL.md` with frontmatter (name, description with trigger phrases) and numbered steps that say exactly which file to read at which step
7. **Add one row** to the Commands → Skills table in `CLAUDE.md`
8. **Add a CLI command** in `scripts/` if it needs a terminal entry point
9. **Update this file** — add a row to Agent Roster and Workflow Map
10. **Register the path** in `scripts/config.py`

**Naming rules:**
- Folders: `kebab-case`
- Agent files: `<role>_agent.txt`
- Raw input: `YYYY-MM-DD_<topic>_raw.md`
- Processed output: `YYYY-MM-DD_<topic>_processed.md`
- Archive: `engine/<loop>/workflows/<name>/archive/<year>/`
