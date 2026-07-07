---
name: log-meeting
description: One-command meeting logging from Apple Notes to Confluence. Use when asked to run log-meeting "Company" --space SPACE --parent 'Parent Page'.
---

# Log Meeting — Apple Note → Confluence → CI Page → Email Draft

## Steps

1. Run `python3 scripts/log_meeting.py "Company" --space SPACE --parent 'Parent Page'`
2. Script: exports Apple Note → pushes to Confluence → optionally creates CI page → drafts follow-up email via Ollama
3. Interactive prompts guide through each step; any step can be skipped
4. Email draft uses local Ollama — nothing leaves the laptop
