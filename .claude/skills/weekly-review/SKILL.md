---
name: weekly-review
description: Monday cockpit across pipeline, contacts, and 1-on-1 commitments. Use when asked to run weekly-review, do the weekly review, or ask "what needs my attention this week".
---

# Weekly Review — Monday Cockpit

Aggregates what last week's events wrote into the knowledge base. This skill intentionally scans folders, but extracts only the sections listed below to stay token-lean. Never load full contact or person files here.

## Steps

1. **Pipeline scan:** from every file in `knowledge/contacts/`, extract only the `## Pipeline Status` block (grep, not full read). Collect: CRL, target, momentum, bottleneck, next action, last reviewed date.
2. **People scan:** from every file in `knowledge/people/` (exclude `_template.md`), extract only the header block and the `## Open commitments` section.
3. **Compose the cockpit**, in this order:

   ### 1 · Needs action this week
   - Accounts with momentum ↓
   - Accounts not reviewed in 14+ days
   - My commitments to people that are due or overdue
   - 1-on-1s overdue against their cadence

   ### 2 · Waiting on others
   - Buyer next actions pending per account (from Pipeline Status)
   - What colleagues owe me (from people files)

   ### 3 · Pipeline snapshot
   - One line per account: name · CRL→target · momentum · bottleneck (short)

   ### 4 · Top 3 for the week
   - Propose the three highest-leverage actions, each justified by one observable fact from the scan

4. Keep the whole cockpit under 40 lines. No filler, no restating what is fine.

## Rules

- Read-only: this skill never modifies any file
- Every flagged item must cite its source (account or person)
- If a section is empty, write one line saying so and move on
