# Contact Intelligence Workflow

## Purpose
Maintain a living relationship brief for each prospect, customer, and partner.
Generate passive weekly follow-up email drafts — review and send, no drafting effort required.

## Architecture

```
Company page in Confluence (e.g. "Acme Corp")
├── Acme Corp - Contact Intelligence   ← living brief (this workflow's output)
└── Acme Corp - Meeting Notes          ← immutable history (meeting-intelligence workflow)
    ├── 🗒️ 2026-06-18 ...
    └── ...

Space root (YOUR_SPACE_KEY)
└── 📊 Contact Intelligence Dashboard   ← company-visible status table (auto-updated)

~/Desktop/followups_YYYY-MM-DD.md   ← personal drafts (never in Confluence)
```

## Information Separation Principle

| Content | Destination | Audience |
| :--- | :--- | :--- |
| Meeting notes | Confluence (under company page) | Whole team |
| CI page (relationship brief) | Confluence (under company page) | Whole team — marked CONFIDENTIAL |
| Dashboard (status table) | Confluence (space root) | Whole team |
| Email drafts | Local file on Desktop | Personal only — never published |
| Pricing / deal terms | CRM only | Never in this workspace |

**Rule:** Confluence = company knowledge. Local = personal operations.

## Agents Used
| Agent | File | Role |
| :--- | :--- | :--- |
| Contact Agent | `agents/contact_agent.txt` | Reads CI page, drafts follow-up emails |

## Pipeline Steps

### new-contact (one-time setup per company)
1. Load `contact_page_template.md`
2. Prepend routing slip with company's Confluence parent page
3. Publish via `publish_page.py` → creates "Contact Intelligence" sub-page

### follow-up (on-demand)
1. `contact_pipeline.py` fetches CI page from Confluence
2. Cloud: prompt passed to Claude Code with `contact_agent.txt` rules
3. Local: CI content passed to Ollama with `contact_agent.txt` as system prompt
4. Output: email draft printed to terminal

### review-contacts / weekly_review.py (automated, every Monday 08:00)
1. Fetch all "Contact Intelligence" pages in configured space
2. For each: evaluate last contact date and next action vs. priority thresholds
   - High: 14 days | Medium: 28 days | Low: 45 days
3. **Publish Confluence Dashboard** — status table only (Company, Priority, Last Contact, Next Action, Deal Stage)
4. **Save local draft file** — email drafts for overdue contacts → `~/Desktop/followups_YYYY-MM-DD.md`
5. macOS notification → opens local draft file automatically

## Priority Thresholds
| Priority | Follow-up interval |
| :--- | :--- |
| High | 14 days |
| Medium | 28 days |
| Low | 45 days |

## Privacy Rules
- NDA status → never on the Confluence CI page; track personally
- If a company has an NDA → always use `--local` flag when running AI on their data
- Company names and general relationship context → cloud fine
- Email drafts → local file only, never Confluence
- Pricing, deal terms → CRM only, never here

## Commands
```zsh
new-contact "Acme Corp" "Acme Corp (Parent Page)"   # create CI page (once per company)
follow-up "Acme Corp"                                # draft email now (cloud)
follow-up "Acme Corp" --local                        # draft email now (local)
review-contacts                                      # weekly review: dashboard + local drafts
review-contacts --dry-run                            # preview without publishing or saving
zsh scripts/setup-cron.sh                            # install Monday 08:00 cron
```
