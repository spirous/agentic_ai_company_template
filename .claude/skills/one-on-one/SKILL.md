---
name: one-on-one
description: Internal stakeholder 1-on-1 system. Use for one-on-one "Name" (prep brief before a meeting), one-on-one "Name" --log (capture notes after), one-on-one --new "Name" (create person file), one-on-one --list (overview with overdue flags).
---

# One-on-One — Internal Stakeholder Intelligence

Person files live in `knowledge/people/`, one per colleague/stakeholder. **Local only: content never goes to Confluence, emails, or any published output.**

## Steps

1. Read `agents/one_on_one_agent.txt`
2. Route by invocation:
   - `one-on-one "Name"` → read `knowledge/people/[slugified-name].md`, run PREP mode
   - `one-on-one "Name" --log` → read the person file, take the user's rough notes, run LOG mode, propose the updated file, save only after confirmation
   - `one-on-one --new "Name"` → run NEW mode from `knowledge/people/_template.md`
   - `one-on-one --list` → run LIST mode (header blocks only, never full files)
3. If the person file does not exist for PREP or LOG, offer to create it first (NEW mode)

## Rules

- Load one person file per task; never scan the whole folder except in LIST mode
- All commitments must carry dates
- User confirms before any file is saved
