---
name: push-notes
description: Meeting intelligence pipeline. Use when asked to run the complete workflow/pipeline on a raw notes file, process meeting notes, or push notes to Confluence.
---

# Push Notes — Raw Meeting Notes → Confluence

## Steps

1. Read `agents/document_agent.txt`
2. Parse notes into the layout of `./work/meeting-intelligence/templates/meeting_protocol_template.md`
3. Prepend routing slip. Use Space/Parent from the command if given; else use `CONFLUENCE_SPACE` / `CONFLUENCE_DEFAULT_PARENT` from `.env`. Generate a headline title from the content: date + company + 2 to 3 key outcomes in plain language, drawn strictly from what is in the notes. Format: `YYYY-MM-DD Company Name — outcome one, outcome two`. Save as `_processed.md`.
4. Run: `python3 scripts/publish_page.py <path_to_processed_file>`

## After publish

Propose contact file updates per the Knowledge Base Update Guardrail (user confirms before saving). If the meeting is for an initiative account, check whether the content warrants a CRL level change and add a one-sentence CRL check note at the end of the output.
