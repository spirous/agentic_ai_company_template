#!/usr/bin/env python3
"""
Log a meeting end-to-end: Apple Note → Confluence → CI page → email draft.

Usage:
  log-meeting "Acme Corp" --space PROJ1 --parent 'Acme Corp - Meeting Notes'
  log-meeting "Acme Corp" --space PROJ1 --parent 'Acme Corp - Meeting Notes' --topic "Q3 review"

Steps:
  1. Find Apple Note matching company name, export to .md, push to Confluence
  2. Optionally create a Contact Intelligence page
  3. Prompt for email description, draft via Ollama

Alias (add to ~/.zshrc):
  alias log-meeting='python3 ~/projects/YOUR_REPO/scripts/log_meeting.py'
"""

import os
import sys
import subprocess
import argparse
import requests

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
sys.path.insert(0, SCRIPTS_DIR)

from export_note_pipeline import run as export_run

OLLAMA_URL = 'http://localhost:11434/v1/chat/completions'


def draft_email_ollama(description, company, model):
    prompt = (
        f"Draft a short professional email based on this description: {description}\n\n"
        f"Context: this is a follow-up email after a meeting with {company}.\n\n"
        f"Rules:\n"
        f"- Start with 'Dear [Name],' or appropriate greeting\n"
        f"- Be concise — 3 sentences max in the body\n"
        f"- Use 'we will' not 'I will' for company actions\n"
        f"- No em dashes. No 'Additionally,', 'Furthermore,', or filler phrases.\n"
        f"- No 'Please do not hesitate', 'Feel free to', 'I hope this finds you well'\n"
        f"- End with 'Best,' — no name after it\n"
        f"- Output ONLY the email text. No subject line, no explanations."
    )
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                'model':    model,
                'messages': [{'role': 'user', 'content': prompt}],
                'stream':   False,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content'].strip()
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description='Log a meeting end-to-end')
    parser.add_argument('company',   help='Company name — used to search Apple Notes')
    parser.add_argument('--space',   required=True, help='Confluence space key, e.g. PROJ1')
    parser.add_argument('--parent',  required=True, help='Confluence parent page title')
    parser.add_argument('--topic',   default='',    help='Short topic label added to filename')
    parser.add_argument('--model',   default='phi4:latest', help='Ollama model for email draft')
    args = parser.parse_args()

    destination = f"{args.space}/'{args.parent}'"

    print(f'\n{"═"*60}')
    print(f'  Log Meeting — {args.company}')
    print(f'{"═"*60}')

    # ── Step 1: Export note + push to Confluence ─────────────────────────────
    print('\n▶  Step 1/3 — Export Apple Note and push to Confluence\n')
    export_run(args.company, destination, args.topic)

    # ── Step 2: Contact Intelligence page ────────────────────────────────────
    print('\n▶  Step 2/3 — Contact Intelligence page')
    create_ci = input('   Create CI page for this company? [y/n] ').strip().lower()
    if create_ci == 'y':
        ci_parent = input(f'   CI page parent title: ').strip()
        new_contact_script = os.path.join(PROJECT_DIR, 'scripts', 'new-contact')
        subprocess.run([new_contact_script, args.company, ci_parent])
    else:
        print('   Skipped.')

    # ── Step 3: Follow-up email ───────────────────────────────────────────────
    print('\n▶  Step 3/3 — Follow-up email draft')
    description = input('   Describe the email (or press Enter to skip): ').strip()
    if description:
        print(f'\n   Drafting via Ollama ({args.model})…\n')
        draft = draft_email_ollama(description, args.company, args.model)
        if draft:
            print('─' * 60)
            print(draft)
            print('─' * 60)
            print('\n   Review before sending. Add personal context and sign-off.')
        else:
            print('   Ollama not responding. Start it with: ollama serve')
            print(f'   Then run: draft-email --new "{description}"')
    else:
        print('   Skipped.')

    print(f'\n{"═"*60}')
    print('  Done')
    print(f'{"═"*60}\n')


if __name__ == '__main__':
    main()
