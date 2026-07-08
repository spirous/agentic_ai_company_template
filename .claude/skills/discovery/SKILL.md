---
name: discovery
description: Mom Test customer discovery. Use for discovery-prep "Account/topic" (question set before a conversation), discovery-debrief (classify notes after), discovery-verdict "Initiative" (aggregate evidence — is there a real business here?).
---

# Discovery — Mom Test Customer Discovery / Jobs-to-be-Done

## Steps

1. Read `./agents/discovery_agent.txt`
2. Read `./methodologies/mom-test/principles.md` (the distilled methodology — never read the full book PDF)
3. Route by invocation:
   - `discovery-prep "Account"` → read that account's contact file (`## Demand Signal` block), run PREP mode
   - `discovery-prep "topic"` → run PREP mode on the described topic, no file needed
   - `discovery-debrief` → take the user's rough notes, run DEBRIEF mode; save the Demand Signal update only after user confirmation; archive the debrief
   - `discovery-verdict "Initiative"` → read all debriefs in `./work/customer-discovery/debriefs/` plus the initiative's end-user Demand Signal blocks, run VERDICT mode

## Rules

- Evidence rubric is binding: only FACTS and COMMITMENTS count; compliments, fluff, and hypotheticals never move a signal or verdict
- Debriefs are archived per conversation; verdicts read the archive, never re-interview memory
- Verdict answers demand ("real business?"); defensibility is handed off to `irl-assess`
- End-user conversations feed Demand Signal blocks and initiative-level CRL/BRL evidence, never account CRL rows (channel-vs-demand rule)
