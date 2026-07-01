# Agentic Company — Command Reference

---

## Meeting Prep
Generate a pre-meeting brief from past notes and contact context.

| Command | What it does |
| :--- | :--- |
| `meet-prep "Company"` | Brief from past notes and contact file → saved to Apple Notes |
| `meet-prep "Company" "focus note"` | Same, with a specific focus for this meeting |
| `meet-prep "Company" --local` | Same, via local Ollama |

```zsh
meet-prep "Acme Corp"
meet-prep "Acme Corp" "focus on the renewal agreement and next steps"
meet-prep "Acme Corp" --local
```

---

## Export Note
Export an Apple Note to a raw `.md` file, then optionally push to Confluence.

| Command | What it does |
| :--- | :--- |
| `export-note "Company"` | Finds most recent Apple Note → saves as raw `.md` → optionally runs `push-notes` |
| `export-note "Company" --to SPACE/'Parent'` | Same, with custom Confluence destination |

```zsh
export-note "Acme Corp"
export-note "Acme Corp" --to YOUR_SPACE/'Acme Corp - Meeting Notes'
```

---

## Meeting Intelligence
Push raw meeting notes through AI and publish to Confluence.

| Command | What it does |
| :--- | :--- |
| `push-notes <file>` | Notes to Confluence (default destination) |
| `push-notes <file> --to SPACE/'Parent'` | Notes to Confluence (custom destination) |
| `push-notes <file> --local` | Same, via local Ollama |

```zsh
push-notes engine/deliver/workflows/meeting-intelligence/archive/2026/2026-06-18_acme_raw.md
push-notes ~/Desktop/my_meeting.md --to YOUR_SPACE/'Acme Corp - Meeting Notes'
push-notes ~/Desktop/my_meeting.md --local
```

---

## Contact Intelligence
Manage relationship briefs and draft follow-up emails.

| Command | What it does |
| :--- | :--- |
| `new-contact "Co" "Parent Page"` | Create CI page in Confluence (once per company) |
| `follow-up "Company"` | Fetch CI page and draft follow-up email |
| `follow-up "Company" --local` | Same, via local Ollama |
| `follow-up "Company" --context "note"` | Same, with extra context |
| `review-contacts` | Weekly review: draft emails for all overdue contacts |
| `review-contacts --dry-run` | Preview without publishing to Confluence |

```zsh
new-contact "Acme Corp" "Acme Corp (Parent Page)"
follow-up "Acme Corp"
follow-up "Acme Corp" --context "sent renewal agreement on June 19"
review-contacts --dry-run
```

---

## Contact Notes
Add quick notes to local contact context files — improves every future email draft for that company.

| Command | What it does |
| :--- | :--- |
| `add-contact-note "Co" "note"` | Append a dated note to a contact file |
| `add-contact-note "Co"` | Open contact file in editor |
| `add-contact-note --list` | Show all contact files |

```zsh
add-contact-note "Acme Corp" "confirmed they are reviewing the proposal this week"
add-contact-note "Acme Corp"
add-contact-note --list
```

---

## Email Intelligence
Draft replies or new outbound emails from the terminal.

| Command | What it does |
| :--- | :--- |
| `draft-email` | Reply to email currently in clipboard |
| `draft-email --local` | Same, via local Ollama |
| `draft-email --new "description"` | Draft a new outbound email |
| `draft-email --file email.txt` | Read email from file |

```zsh
draft-email
draft-email --new "follow up on the proposal we sent last week"
draft-email --file ~/Desktop/incoming.txt
```

Review loop after draft:
```
[a] approve   copy to clipboard + save to knowledge base
[i] iterate   give a revision instruction, regenerate
[e] edit      open in VS Code
[d] discard
```

---

## Cron / Automation

```zsh
zsh scripts/setup-cron.sh           # install Monday 08:00 auto-review
zsh scripts/setup-cron.sh --remove  # uninstall
```
