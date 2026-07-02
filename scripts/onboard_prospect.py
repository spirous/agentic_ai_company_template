#!/usr/bin/env python3
"""
Onboard a new prospect into the Confluence structure.

Follows the established pattern:
  YOUR Industry Top-Level Page
  └── YOUR Companies Container
      └── [Geography]          (Europe / Americas / Asia)
          └── [Country]
              └── [Company (Country)]
                  └── [Company] - Meeting Notes

Usage:
  python3 scripts/onboard_prospect.py "Acme Corp" --country Germany --sector YOUR_SECTOR
  python3 scripts/onboard_prospect.py "Beta Inc" --country Japan --sector NEW_SECTOR --new-sector

Setup:
  1. In SECTORS below, replace YOUR_* IDs with your actual Confluence page IDs.
  2. Add more sectors as your portfolio grows.
  3. Alias: add to ~/.zshrc:
       alias onboard-prospect='python3 ~/projects/YOUR_REPO/scripts/onboard_prospect.py'

Environment variables (in .env):
  CONFLUENCE_URL         https://yourcompany.atlassian.net
  CONFLUENCE_EMAIL       you@yourcompany.com
  CONFLUENCE_API_TOKEN   your_token
"""

import os
import sys
import argparse
import requests
from requests.auth import HTTPBasicAuth

SPACE_KEY  = 'YOUR_SPACE_KEY'   # e.g. 'PROJ1'
ROOT_PAGE  = 'YOUR_ROOT_PAGE_ID' # Confluence ID of your top-level page

CONF_URL   = None
AUTH       = None

# ── Optional guardrails ───────────────────────────────────────────────────────
# Add any terms that should never appear in company/country/sector names.
# Remove or leave empty if not needed.
BANNED_TERMS = []

def check_guardrails(text):
    low = text.lower()
    for term in BANNED_TERMS:
        if term in low:
            print(f'❌  Guardrail: "{term}" is not permitted.')
            sys.exit(1)


# ── Known sectors ─────────────────────────────────────────────────────────────
# Replace YOUR_* with real Confluence page IDs.
# 'sections' controls the heading structure of company pages.
SECTORS = {
    'your_sector': {
        'industry_id':    'YOUR_INDUSTRY_PAGE_ID',
        'industry_title': 'YOUR Industry Title',
        'companies_id':   'YOUR_COMPANIES_PAGE_ID',
        'companies_title': 'YOUR Companies Title',
        'sections': [
            ('🏢', 'Size'),
            ('🔬', 'Activity / Products'),
            ('👤', 'Key Contacts'),
            ('🏆', 'Champion'),
        ],
    },
    # Add more sectors here:
    # 'second_sector': { ... },
}

COUNTRY_TO_GEOGRAPHY = {
    'france': 'Europe', 'germany': 'Europe', 'sweden': 'Europe',
    'switzerland': 'Europe', 'netherlands': 'Europe', 'uk': 'Europe',
    'united kingdom': 'Europe', 'italy': 'Europe', 'spain': 'Europe',
    'belgium': 'Europe', 'austria': 'Europe', 'denmark': 'Europe',
    'finland': 'Europe', 'norway': 'Europe', 'poland': 'Europe',
    'usa': 'Americas', 'united states': 'Americas', 'canada': 'Americas',
    'brazil': 'Americas', 'mexico': 'Americas',
    'japan': 'Asia', 'china': 'Asia', 'south korea': 'Asia',
    'korea': 'Asia', 'taiwan': 'Asia', 'singapore': 'Asia', 'india': 'Asia',
}


# ── Confluence helpers ────────────────────────────────────────────────────────

def init_confluence():
    global CONF_URL, AUTH
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k] = v.strip().strip('"').strip("'")
    url   = os.getenv('CONFLUENCE_URL', '').rstrip('/')
    email = os.getenv('CONFLUENCE_EMAIL', '')
    token = os.getenv('CONFLUENCE_API_TOKEN', '')
    if not url or not email or not token:
        print('❌  Confluence credentials not configured in .env')
        sys.exit(1)
    CONF_URL = url
    AUTH     = HTTPBasicAuth(email, token)


def get_children(parent_id):
    r = requests.get(
        f'{CONF_URL}/wiki/rest/api/content/{parent_id}/child/page',
        params={'limit': 100}, auth=AUTH, timeout=20,
    )
    r.raise_for_status()
    return {p['title']: p['id'] for p in r.json().get('results', [])}


def find_child(parent_id, title):
    return get_children(parent_id).get(title)


def create_page(title, parent_id, body='<p></p>'):
    payload = {
        'type':      'page',
        'title':     title,
        'space':     {'key': SPACE_KEY},
        'ancestors': [{'id': parent_id}],
        'body':      {'storage': {'value': body, 'representation': 'storage'}},
    }
    r = requests.post(
        f'{CONF_URL}/wiki/rest/api/content',
        auth=AUTH,
        headers={'Content-Type': 'application/json'},
        json=payload, timeout=30,
    )
    if r.status_code not in (200, 201):
        print(f'❌  Failed to create "{title}": {r.status_code} {r.text[:300]}')
        sys.exit(1)
    data = r.json()
    page_url = f'{CONF_URL}/wiki{data["_links"]["webui"]}'
    print(f'  ✅  Created: {title}')
    return data['id'], page_url


def get_or_create(title, parent_id, body='<p></p>'):
    existing = find_child(parent_id, title)
    if existing:
        page_url = f'{CONF_URL}/wiki/spaces/{SPACE_KEY}/pages/{existing}'
        print(f'  ↩️  Exists:  {title}')
        return existing, page_url
    return create_page(title, parent_id, body)


# ── Page body templates ───────────────────────────────────────────────────────

def company_page_body(sections):
    html = ''
    for emoji, label in sections:
        html += f'<h2>{emoji} {label}</h2><ul><li><p></p></li></ul>\n'
    return html


PAGETREE_BODY = (
    '<p><ac:structured-macro ac:name="pagetree" ac:schema-version="1">'
    '<ac:parameter ac:name="root"><ac:link>'
    '<ri:page ri:content-title="@self" /></ac:link></ac:parameter>'
    '<ac:parameter ac:name="startDepth">5</ac:parameter>'
    '</ac:structured-macro></p>'
)


def build_new_sector(sector_name):
    """Create [Sector] Industry + [Sector] Companies pages under root."""
    industry_title  = f'{sector_name.title()} Industry'
    companies_title = f'{sector_name.title()} Companies'

    industry_id, _  = get_or_create(industry_title,  ROOT_PAGE,   PAGETREE_BODY)
    companies_id, _ = get_or_create(companies_title, industry_id, PAGETREE_BODY)

    return {
        'industry_id':    industry_id,
        'industry_title': industry_title,
        'companies_id':   companies_id,
        'companies_title': companies_title,
        'sections': [
            ('🏢', 'Size'),
            ('🔬', 'Activity / Products'),
            ('👤', 'Key Contacts'),
            ('🏆', 'Champion'),
        ],
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Onboard a new prospect into Confluence')
    parser.add_argument('company',      help='Company name, e.g. "Acme Corp"')
    parser.add_argument('--country',    required=True, help='Country, e.g. "Germany"')
    parser.add_argument('--sector',     default=None,  help='Sector key from SECTORS dict')
    parser.add_argument('--new-sector', action='store_true',
                        help='Create a new sector hierarchy (requires --sector for the name)')
    parser.add_argument('--geography',  default=None,
                        help='Override geography (Europe/Americas/Asia). Auto-detected if omitted.')
    args = parser.parse_args()

    check_guardrails(args.company)
    check_guardrails(args.country)
    if args.sector:
        check_guardrails(args.sector)

    if not args.sector:
        print('❌  --sector is required. Known sectors: ' + ', '.join(SECTORS.keys()))
        print('    For a new sector, pass --sector "Name" --new-sector')
        sys.exit(1)

    init_confluence()

    print(f'\n{"═"*60}')
    print(f'  Onboarding: {args.company} ({args.country})')
    print(f'{"═"*60}\n')

    sector_key = args.sector.lower()
    if args.new_sector:
        print(f'▶  Building new sector: {args.sector}')
        sector = build_new_sector(args.sector)
        SECTORS[sector_key] = sector
    elif sector_key in SECTORS:
        sector = SECTORS[sector_key]
        print(f'▶  Sector: {sector["industry_title"]}')
    else:
        print(f'❌  Unknown sector "{args.sector}". Known: {", ".join(SECTORS.keys())}')
        print('    Add --new-sector to create it.')
        sys.exit(1)

    geography = args.geography
    if not geography:
        geography = COUNTRY_TO_GEOGRAPHY.get(args.country.lower())
    if not geography:
        print(f'⚠️   Could not auto-detect geography for "{args.country}".')
        print('    Pass --geography Europe|Americas|Asia')
        sys.exit(1)

    print(f'▶  Geography: {geography} → {args.country}\n')

    geo_id,     _        = get_or_create(geography,   sector['companies_id'], PAGETREE_BODY)
    country_id, _        = get_or_create(args.country, geo_id,                PAGETREE_BODY)
    company_title        = f'{args.company} ({args.country})'
    company_id, comp_url = create_page(company_title, country_id,
                                       company_page_body(sector['sections']) + PAGETREE_BODY)
    notes_title          = f'{args.company} - Meeting Notes'
    notes_id,  notes_url = create_page(notes_title, company_id, PAGETREE_BODY)

    print(f'\n{"─"*60}')
    print('  Done. Next steps:\n')
    print(f'  1. Fill in the company page:')
    print(f'     {comp_url}\n')
    print(f'  2. Export your Apple Note and push meeting notes:')
    print(f'     export-note')
    print(f"     push-notes <file>.md --to {SPACE_KEY}/'{notes_title}'\n")
    print(f'  3. Create the Contact Intelligence page:')
    print(f'     new-contact "{args.company}" "{company_title}"\n')
    print(f'  4. Draft your follow-up email:')
    print(f'     follow-up "{args.company}"')
    print(f'{"─"*60}\n')


if __name__ == '__main__':
    main()
