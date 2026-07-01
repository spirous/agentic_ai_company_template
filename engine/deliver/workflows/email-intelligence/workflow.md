# Email Intelligence Workflow

## Purpose
Draft replies and outbound emails from the terminal with minimal friction.
Review, iterate, approve — nothing goes out without you confirming it.
Build a personal knowledge base that improves over time.

## Flow
```
1. Copy incoming email in Gmail  (Cmd+A, Cmd+C)
2. Terminal: draft-email
3. AI reads clipboard + style guide + contact context → draft
4. Review loop:
     [a] approve  → clipboard + saved to knowledge base
     [i] iterate  → give a revision instruction, regenerate
     [e] edit     → open in VS Code, edit manually
     [d] discard
5. Cmd+Tab → Gmail → Cmd+V → review → send
```

## Agents Used
| Agent | File | Role |
| :--- | :--- | :--- |
| Email Agent | `agents/email_agent.txt` | Drafts emails using style guide + knowledge base |

## Knowledge Base — Two Tiers

```
shared/style/
  style.md               ← tone, structure, do/don't rules
  patterns/              ← common email types
    follow_up.md
    introduction.md
    thank_you.md
    update.md
  approved/              ← approved drafts (gitignored — may contain names)

knowledge/contacts/      ← local only, gitignored
  [company].md           ← one file per contact/company
```

**Public tier** (`shared/style/`): style guide + patterns — safe for GitHub, no names.
**Private tier** (`knowledge/contacts/`): per-contact context — local only.
**Approved drafts** (`shared/style/approved/`): gitignored — may contain real names.

## How the knowledge base grows
- Every `[a]pprove` saves the draft to `shared/style/approved/YYYY-MM-DD_NN.md`
- The email agent loads `style.md` on every run
- Periodically review approved drafts → distill patterns → update `style.md` manually

## Contact context files (`knowledge/contacts/`)
One markdown file per contact/company. Free-form. Include what helps the agent:
- Who they are and their role
- What you are doing together
- What they care about
- Past interactions summary
- Any tone notes (formal/informal, their communication style)

## Commands
```zsh
draft-email                          # reply to clipboard (cloud)
draft-email --local                  # reply to clipboard (Ollama)
draft-email --new "description"      # new outbound (cloud)
draft-email --new "description" --local   # new outbound (Ollama)
draft-email --file email.txt         # read from file
```

## Cloud vs local
- Cloud (`draft-email`): uses Claude Code CLI — same subscription as push-notes, no extra key needed
- Local (`draft-email --local`): uses Ollama — works offline, fully private
