#!/usr/bin/env python3
"""
Loan Workflow Orchestrator — Agentic Company Workspace

Runs the complete loan agreement workflow in one command:
  1. Fill Word agreement    (fill_loan_agreement.py)
  2. Create Confluence page (create_loan_page.py)
  3. Draft cover email      (via Ollama — fully local)

Usage:
  python3 scripts/run_loan_workflow.py \\
    --company "Institute Name" \\
    --type standard \\
    --fields engine/legal/workflows/loan-agreements/active/fields_institute.json \\
    --recipient "First Last" \\
    --recipient-email contact@institute.org

Flags:
  --skip-confluence   Skip page creation (renewals where page already exists)
  --skip-email        Skip email draft
  --dry-run           Confluence dry run — preview, no page created
  --model             Ollama model for email draft (default: phi4:latest)

Add to ~/.zshrc for one-command access:
  alias fill-loan='python3 /path/to/scripts/run_loan_workflow.py'
"""

import os
import sys
import json
import argparse
import subprocess
import requests

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
OLLAMA_URL  = 'http://localhost:11434/v1/chat/completions'


def run_step(label, cmd):
    print(f'\n{"─"*60}')
    print(f'▶  {label}')
    print(f'{"─"*60}')
    sys.stdout.flush()
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f'\n❌  {label} failed (exit {result.returncode})')
        sys.exit(result.returncode)


def draft_email(fields, recipient_name, model):
    first_name = recipient_name.split()[0]
    product    = fields.get('ARTICLE_DESIGNATION', '')
    serial     = fields.get('SERIAL_NUMBER', '')
    start      = fields.get('START_DATE', '')
    end        = fields.get('END_DATE', '')
    borrower   = fields.get('BORROWER_NAME', '')

    prompt = (
        f"Draft a short cover email to {recipient_name} at {borrower}, "
        f"attaching a loan agreement for {product} (SN {serial}), "
        f"period {start} to {end}.\n\n"
        f"FORMAT — exactly this structure:\n"
        f"Dear {first_name},\n\n"
        f"[One sentence: attached is the loan agreement. Ask them to review and sign.]\n\n"
        f"[One sentence: once we receive the signed agreement, we will countersign "
        f"and return a copy for their records.]\n\n"
        f"Best,\n\n"
        f"BANNED phrases — never write:\n"
        f"- 'at your earliest convenience'\n"
        f"- 'Thank you for your prompt attention'\n"
        f"- 'I hope this finds you well'\n"
        f"- 'Please do not hesitate' / 'Feel free to'\n"
        f"- 'Additionally,' / 'Furthermore,'\n"
        f"- em dashes (—)\n"
        f"- any name or company after 'Best,'\n\n"
        f"Use 'we will' not 'I will'. Output ONLY the email text."
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
    parser = argparse.ArgumentParser(description='Loan workflow orchestrator')
    parser.add_argument('--company',         required=True,
                        help='Company name (used in output filename)')
    parser.add_argument('--type',            required=True, choices=['standard', 'ds'],
                        help='standard = borrower ships; ds = your company ships both ways')
    parser.add_argument('--fields',          required=True,
                        help='Path to the fields JSON file')
    parser.add_argument('--recipient',       default=None,
                        help='Recipient full name for the cover email')
    parser.add_argument('--recipient-email', default=None,
                        help='Recipient email address (shown at bottom of draft)')
    parser.add_argument('--skip-confluence', action='store_true',
                        help='Skip Confluence page creation')
    parser.add_argument('--skip-email',      action='store_true',
                        help='Skip email draft')
    parser.add_argument('--dry-run',         action='store_true',
                        help='Confluence dry run — preview without creating page')
    parser.add_argument('--model',           default='phi4:latest',
                        help='Ollama model for email draft (default: phi4:latest)')
    args = parser.parse_args()

    if not os.path.exists(args.fields):
        print(f'❌  Fields file not found: {args.fields}')
        sys.exit(1)

    with open(args.fields, 'r', encoding='utf-8') as fh:
        fields = json.load(fh)

    print(f'\n{"═"*60}')
    print(f'  Loan Workflow — {args.company} ({args.type})')
    print(f'{"═"*60}')

    # ── Step 1: Fill Word agreement ─────────────────────────────────────────
    run_step('Filling Word agreement', [
        sys.executable,
        os.path.join(SCRIPTS_DIR, 'fill_loan_agreement.py'),
        '--company', args.company,
        '--type',    args.type,
        '--fields',  args.fields,
    ])

    # ── Step 2: Confluence tracking page ────────────────────────────────────
    if not args.skip_confluence:
        conf_cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, 'create_loan_page.py'),
            '--fields', args.fields,
        ]
        if args.dry_run:
            conf_cmd.append('--dry-run')
        run_step('Creating Confluence tracking page', conf_cmd)
    else:
        print('\n[skip] Confluence page — --skip-confluence set')

    # ── Step 3: Cover email via Ollama ───────────────────────────────────────
    if not args.skip_email:
        recipient = args.recipient
        if not recipient:
            bc = fields.get('BORROWER_CONTACT', '')
            recipient = bc.split(',')[0].strip() if bc else None

        if not recipient:
            print('\n⚠  No recipient — pass --recipient "First Last" to draft the email')
        else:
            print(f'\n{"─"*60}')
            print(f'▶  Drafting cover email via Ollama ({args.model})')
            print(f'{"─"*60}')

            draft = draft_email(fields, recipient, args.model)
            if draft:
                subject = (
                    f'Loan Agreement — {fields.get("ARTICLE_DESIGNATION","")} '
                    f'(SN {fields.get("SERIAL_NUMBER","")}) '
                    f'{fields.get("START_DATE","")} – {fields.get("END_DATE","")}'
                )
                print(f'\nSubject: {subject}\n')
                if args.recipient_email:
                    print(f'To: {args.recipient_email}\n')
                print(draft)
                print('\n⚠  Review draft before sending.')
                print('   Add personal context and your sign-off.')
            else:
                print('⚠  Ollama not responding — start it with: ollama serve')
                print('   Then re-run with --skip-confluence --skip-email=false')
    else:
        print('\n[skip] Email draft — --skip-email set')

    print(f'\n{"═"*60}')
    print('  Workflow complete')
    print(f'{"═"*60}\n')


if __name__ == '__main__':
    main()
