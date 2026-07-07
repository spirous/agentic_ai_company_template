---
name: onboard-prospect
description: Create the full Confluence hierarchy for a new prospect company. Use when asked to onboard a new company or run onboard-prospect "Company" --country Country --sector sector.
---

# Onboard Prospect — New Company → Confluence Hierarchy

## Steps

1. Run `python3 scripts/onboard_prospect.py "Company" --country Country --sector sector`
2. Script creates the full Confluence hierarchy: Industry → Companies → Geography → Country → Company → Meeting Notes
3. For a new sector not yet in SECTORS dict, add `--new-sector` flag
4. Output: confirmation of created/reused pages + next steps (fill company page, push notes, create CI page)

Note: Configure SECTORS dict in `onboard_prospect.py` with your actual Confluence page IDs before first use.
