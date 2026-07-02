#!/usr/bin/env python3
"""
Confluence loan wiki page creator — Agentic Company Workspace

Creates a new internal loan tracking page by fetching your Confluence
template, substituting ac:placeholder elements with field values, and posting
a new page under your configured parent page.

Usage:
  python3 scripts/create_loan_page.py --fields fields.json
  python3 scripts/create_loan_page.py --fields fields.json --dry-run

Setup (one-time):
  1. Create a template page in Confluence with ac:placeholder elements
     (use the Confluence template editor, not a regular page).
  2. Find its page ID in the URL (/pages/XXXXXXXXX/) and set TEMPLATE_PAGE_ID below.
  3. Set PARENT_PAGE_ID to the page under which new loan pages should be created.
  4. Set SPACE_KEY to your Confluence space key.

Required fields:
  BORROWER_NAME          Company/institute name  (page title prefix)
  SERIAL_NUMBER          Serial number           (page title suffix)
  ARTICLE_DESIGNATION    Product name / model
  START_DATE             Loan start date (YYYY-MM-DD)
  END_DATE               Loan end date (YYYY-MM-DD)
  COMPANY_CONTACT        Your contact person name + role

Optional fields:
  PI_NAME                Principal Investigator
  COMPANY_ADMIN          Admin managing logistics
  CUSTOMER_EMAIL         Customer contact email
  CUSTOMER_COUNTRY       Country where system will be used
  CUSTOMER_ORGANIZATION  Institute / department name
  SHIPMENT_BY            Who handles shipping
  LOAN_REASON            Background / aim (free text)
  COMMENTS               Additional notes
"""

import os
import sys
import json
import re
import argparse
import requests
from requests.auth import HTTPBasicAuth

# ── Configure these for your Confluence instance ─────────────────────────────
# Find page IDs in the URL: /wiki/spaces/SPACE/pages/XXXXXXXXX/Page+Title
TEMPLATE_PAGE_ID = 'YOUR_TEMPLATE_PAGE_ID'   # Template page with ac:placeholder elements
PARENT_PAGE_ID   = 'YOUR_PARENT_PAGE_ID'     # Parent page for new loan tracking pages
SPACE_KEY        = 'YOUR_SPACE_KEY'          # Confluence space key (e.g. 'MS', 'BD', 'ENG')
# ─────────────────────────────────────────────────────────────────────────────

if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key] = val.strip().strip('"').strip("'")


def get_credentials():
    url   = os.getenv('CONFLUENCE_URL', '').rstrip('/')
    email = os.getenv('CONFLUENCE_EMAIL', '')
    token = os.getenv('CONFLUENCE_API_TOKEN', '')
    if not url or not email or not token:
        print('❌  Confluence credentials not configured in .env')
        print('    Required: CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN')
        sys.exit(1)
    return url, HTTPBasicAuth(email, token)


def fetch_template(url, auth):
    resp = requests.get(
        f'{url}/wiki/rest/api/content/{TEMPLATE_PAGE_ID}',
        params={'expand': 'body.storage'},
        auth=auth, timeout=30,
    )
    resp.raise_for_status()
    return resp.json()['body']['storage']['value']


def _replace_placeholder(body, partial_match, value):
    """Replace an ac:placeholder whose text contains partial_match with value."""
    if not value:
        return body
    pattern = r'<ac:placeholder[^>]*>[^<]*' + re.escape(partial_match) + r'.*?</ac:placeholder>'
    replaced, n = re.subn(pattern, value, body, flags=re.DOTALL | re.IGNORECASE)
    if n == 0:
        print(f'  ⚠  Placeholder not found: "{partial_match}"')
    return replaced


def apply_substitutions(body, f):
    """Map field values to Confluence template placeholders.

    The strings below are partial matches against the placeholder text in your
    Confluence template. Update them to match your own template's placeholder text.
    """
    subs = [
        ('Name of Product',               f.get('ARTICLE_DESIGNATION', '')),
        ('Serial Number of Product',       f.get('SERIAL_NUMBER', '')),
        ('@Your Name',                     f.get('COMPANY_CONTACT', '')),
        ('@PI',                            f.get('PI_NAME', '')),
        ('@Admin',                         f.get('COMPANY_ADMIN', '')),
        ('Start Date',                     f.get('START_DATE', '')),
        ('End Date',                       f.get('END_DATE', '')),
        ('Name and contact information',
            f'{f.get("BORROWER_NAME","")} ({f.get("CUSTOMER_EMAIL","")})'),
        ('In which country',               f.get('CUSTOMER_COUNTRY', '')),
        ('All other necessary information', f.get('COMMENTS', '')),
        ('Why do you want to ship',        f.get('LOAN_REASON', '')),
    ]
    for partial, value in subs:
        body = _replace_placeholder(body, partial, value)
    return body


def create_page(url, auth, title, body, dry_run=False):
    payload = {
        'type':      'page',
        'title':     title,
        'space':     {'key': SPACE_KEY},
        'ancestors': [{'id': PARENT_PAGE_ID}],
        'body': {
            'storage': {
                'value':          body,
                'representation': 'storage',
            }
        },
    }

    if dry_run:
        print(f'[dry-run] Would create: "{title}" under parent {PARENT_PAGE_ID}')
        print(f'[dry-run] Body length: {len(body)} chars')
        return None, None

    resp = requests.post(
        f'{url}/wiki/rest/api/content',
        auth=auth,
        headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
        json=payload,
        timeout=30,
    )
    if resp.status_code not in (200, 201):
        print(f'❌  Confluence API error {resp.status_code}: {resp.text[:400]}')
        sys.exit(1)

    data = resp.json()
    return data['id'], f'{url}/wiki{data["_links"]["webui"]}'


def main():
    parser = argparse.ArgumentParser(description='Create a loan tracking page in Confluence')
    parser.add_argument('--fields',  required=True, help='Path to JSON file with field values')
    parser.add_argument('--dry-run', action='store_true', help='Preview without creating the page')
    args = parser.parse_args()

    if TEMPLATE_PAGE_ID == 'YOUR_TEMPLATE_PAGE_ID':
        print('❌  TEMPLATE_PAGE_ID not configured. Edit create_loan_page.py and set your page IDs.')
        sys.exit(1)

    if not os.path.exists(args.fields):
        print(f'❌  Fields file not found: {args.fields}')
        sys.exit(1)

    with open(args.fields, 'r', encoding='utf-8') as fh:
        fields = json.load(fh)

    required = ['BORROWER_NAME', 'SERIAL_NUMBER', 'ARTICLE_DESIGNATION',
                'START_DATE', 'END_DATE', 'COMPANY_CONTACT']
    missing = [k for k in required if not fields.get(k)]
    if missing:
        print(f'⚠️   Missing required fields: {", ".join(missing)}')
        sys.exit(1)

    conf_url, auth = get_credentials()

    print('📥  Fetching Confluence template…')
    body = fetch_template(conf_url, auth)

    print('🔧  Substituting fields…')
    body = apply_substitutions(body, fields)

    title = f'{fields["BORROWER_NAME"]} - {fields["SERIAL_NUMBER"]}'
    print(f'📄  Page title: "{title}"')

    page_id, page_url = create_page(conf_url, auth, title, body, dry_run=args.dry_run)

    if page_url:
        print(f'✅  Page created (ID {page_id}): {page_url}')
        print()
        print('Manual steps still needed in Confluence:')
        print('  - Add @ mentions for Contact, PI, Admin')
        print('  - Attach signed agreement once received')
        print('  - Update status macros as the process progresses')
    elif args.dry_run:
        print('✅  Dry run complete — no page was created')


if __name__ == '__main__':
    main()
