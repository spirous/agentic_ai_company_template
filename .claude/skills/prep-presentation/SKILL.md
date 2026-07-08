---
name: prep-presentation
description: Prepare the company presentation for an initiative. Use when asked to run prep-presentation --period "H1 2026" --initiative "Name" or to prepare a leadership/company presentation.
---

# Prep Presentation — Initiative Profile → 12-Slide Presenter Script

## Steps

1. Read `./engine/create/agents/company_presentation_agent.txt`
2. Read the initiative profile in `./engine/decide/methodologies/kth-irl/initiatives/`
3. Read relevant contact files in `./knowledge/contacts/` (all accounts mentioned in the initiative profile)
4. Read `./company/identity.md`
5. Read the prior brief if provided (`--last-brief` flag) or the most recent `brief_*.md` in `./engine/create/workflows/company-presentation/`
6. Ask only for: presentation slot length (if not in the command), thank-you names
7. Generate 12-slide presenter script following the agent's story arc
8. Save brief as `./engine/create/workflows/company-presentation/brief_[PERIOD].md`
9. Remind user to update the `DEFAULTS` array in `dashboards/irl-readiness.html` and screenshot the chart for Slide 5
