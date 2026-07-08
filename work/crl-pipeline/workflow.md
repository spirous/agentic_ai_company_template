# CRL Pipeline Workflow

## Purpose
Track individual prospect accounts on the KTH CRL 3–7 continuum from first contact to first commercial sale. One pipeline per market initiative. Keeps the team focused on the right accounts and the right actions.

## Agent
`agents/crl_pipeline_agent.txt`

## Information sources (auto-loaded)

| Source | Location | What it provides |
| :--- | :--- | :--- |
| Contact files | `knowledge/contacts/*.md` | Relationship history, org chart, prior meetings, Pipeline Status sections |
| Meeting notes archive | `workflows/meeting-intelligence/archive/` | Recent processed notes — loaded on demand |
| Initiative profile | `knowledge/initiatives/[initiative].md` | Overall CRL score and dimension context |
| HTML dashboard | `dashboards/crl-pipeline.html` | Interactive pipeline view (open in browser) |

## Commands

| Command | What it does |
| :--- | :--- |
| `crl-pipeline "Initiative"` | Full review — read all contact files, assess CRL levels, output structured review, propose HTML and contact file updates |
| `crl-update "Company" --crl [n]` | Assess a single account, output updated CRL block, propose contact file Pipeline Status update |
| `crl-update "Company" --bottleneck "text"` | Update bottleneck text only |

## Pipeline stages

| CRL | Stage | Gate — all criteria must be met |
| :--- | :--- | :--- |
| 3 | Holding | Direct conversations with possible customers, users, or market experts — feedback received. Problem/need hypothesis clearer after that direct contact. No confirmed problem statement or stakeholder map. |
| 4 | Qualify | Problem/need and its importance confirmed by this account. User, paying customer, and decision maker identified by name. Product/service hypothesis defined with positioning against their current alternatives. |
| 5 | Engage | Account has expressed interest and confirmed problem-solution fit. Established working relationship. Value proposition adapted to their specific context. |
| 6 | Validate | Customer/user testing has confirmed the value and benefits. Sales pitch and VP updated based on their feedback. Structured commercial activities initiated. |
| 7 | Close | Customer agreement in place — first sale or test sale of an early version, OR account actively engaged in qualification or extended testing. |

## Integration hooks

**After `push-notes`:** If the processed meeting involves a company with a Pipeline Status section in its contact file, the agent checks whether the meeting content warrants a CRL level change and proposes an update. User confirms before saving.

**Before `prep-presentation`:** CRL pipeline summary for the relevant initiative is auto-loaded as context — one line per account, CRL level, momentum, bottleneck in under 10 words.

**After `crl-pipeline` review:** Agent proposes updated Pipeline Status sections for all affected contact files. User reviews and confirms each one before saving.

## Contact file convention

Each contact file relevant to a tracked initiative should end with a `## Pipeline Status` section:

```markdown
## Pipeline Status

**Initiative:** [YOUR_INITIATIVE]
**Current CRL:** [n] — [stage name]
**Target CRL:** [n]
**Momentum:** [↑ / → / ↓]
**Bottleneck:** [one sentence — specific buyer-side blocker]
**Next Action (buyer):** [one sentence — verifiable buyer action]
**Last reviewed:** [YYYY-MM-DD]
```

## File conventions

- Dashboard: `dashboards/crl-pipeline.html`
- Archive snapshots: `work/crl-pipeline/archive/YYYY-MM-DD_[initiative-slug].md`
- Contact file updates: append or update `## Pipeline Status` at the end of the relevant contact file
