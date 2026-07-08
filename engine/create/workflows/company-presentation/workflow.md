# Company Presentation Workflow

## Purpose

Generate a presenter-ready slide brief for a company-wide or team meeting. Recurring: once or twice per year per active initiative.

## Command

```
prep-presentation --period "H1 2026" --initiative "YOUR_INITIATIVE_NAME"
```

Optional flags:
- `--last-brief engine/create/workflows/company-presentation/brief_[PRIOR_PERIOD].md` — provide prior brief for continuity
- `--slot 10min` — adjust slide count (default: 12 slides)

## Inputs

| Input | Source | Required |
|:---|:---|:---:|
| IRL initiative profile | `engine/decide/methodologies/kth-irl/initiatives/[name].md` | Yes |
| Contact files | `knowledge/contacts/[relevant].md` | Yes |
| Prior presentation summary | Provided by user or in initiative notes | Recommended |
| Company identity | `company/identity.md` | Yes |

## Steps

1. Read `engine/create/agents/company_presentation_agent.txt`
2. Read the initiative profile
3. Read relevant contact files (all accounts mentioned in the initiative profile)
4. Read prior presentation summary if available
5. Generate 12-slide presenter script following the agent's story arc
6. Save brief as `engine/create/workflows/company-presentation/brief_[PERIOD].md`
7. Render IRL chart: open `dashboards/irl-readiness.html` — update dimension values in the JS `DEFAULTS` array to match current profile scores

## Outputs

| Output | Path |
|:---|:---|
| Presenter script | `engine/create/workflows/company-presentation/brief_[PERIOD].md` |
| IRL readiness chart | `dashboards/irl-readiness.html` |

## IRL chart update

Before each presentation, update the `DEFAULTS` array in `dashboards/irl-readiness.html`:

```js
var DEFAULTS = [
  { code:'CRL', name:'Customer Readiness Level', cur:X, tgt:Y, next:'...' },
  { code:'TRL', name:'Technology Readiness Level', cur:X, tgt:Y, next:'...' },
  ...
];
```

Screenshot the rendered chart and insert into Slide 5 of the deck.

## Archive

Save previous briefs in this folder with the period in the filename:
- `brief_H2_2025.md`
- `brief_H1_2026.md`
- etc.
