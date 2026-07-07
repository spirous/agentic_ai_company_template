---
name: irl-new
description: Create a new KTH IRL initiative profile via guided interview. Use when asked to run irl-new "Initiative Name" or to set up a new initiative assessment.
---

# IRL New Initiative — Guided Interview → Initiative Profile

## Steps

1. Read `./engine/decide/agents/irl_orchestrator.txt`
2. Read `./engine/decide/methodologies/kth-irl/agents/irl_interview_agent.txt`
3. Check if `./engine/decide/methodologies/kth-irl/initiatives/[slugified-name].md` exists — if so, offer to update
4. Run the guided interview — ask one question at a time, fill template incrementally
5. Save to `./engine/decide/methodologies/kth-irl/initiatives/[slugified-name].md`
