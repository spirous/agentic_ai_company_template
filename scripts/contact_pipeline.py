#!/usr/bin/env python3
"""
Local pipeline for the Contact Intelligence workflow.
Fetches a Contact Intelligence page from Confluence and drafts a follow-up email via Ollama.

Usage:
  # Draft email and print to terminal
  python3 contact_pipeline.py "Acme Corp" [--model phi4:latest] [--context "3 months no contact"]

  # Fetch CI page and print a ready prompt (used by follow-up --cloud path)
  python3 contact_pipeline.py "Acme Corp" --fetch-only
"""

import os
import sys
import argparse
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PROJECT_DIR, MARKET_DEV_AGENTS
from confluence_utils import get_credentials, search_pages_by_title_contains, html_to_text

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"


def load_agent_rules():
    path = os.path.join(MARKET_DEV_AGENTS, "contact_agent.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def fetch_ci_page(company_keyword):
    url, _, _, auth = get_credentials()

    # Load CONFLUENCE_SPACE from env
    env_path = os.path.join(PROJECT_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k, v.strip("\"'"))
    space = os.getenv("CONFLUENCE_SPACE", "YOUR_SPACE_KEY")

    pages = search_pages_by_title_contains(url, auth, space, "Contact Intelligence")
    if not pages:
        return None, None

    keyword_lower = company_keyword.lower()
    for page in pages:
        if keyword_lower in page.get("title", "").lower():
            body_html = page.get("body", {}).get("storage", {}).get("value", "")
            body_text = html_to_text(body_html)
            page_url  = f"{url}/wiki/spaces/{space}/pages/{page['id']}"
            return body_text, page_url

    return None, None


def call_ollama(model, system_prompt, user_content):
    print(f"🤖 Drafting email with {model}...")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_content},
        ],
        "stream": False,
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=180)
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is not running. Start it with: ollama serve")
        sys.exit(1)
    if resp.status_code != 200:
        print(f"❌ Ollama error {resp.status_code}: {resp.text}")
        sys.exit(1)
    return resp.json()["choices"][0]["message"]["content"].strip()


def run(company, model, context, fetch_only):
    print(f"📋 Fetching Contact Intelligence page for '{company}'...")
    ci_text, ci_url = fetch_ci_page(company)

    if not ci_text:
        print(f"❌ No Contact Intelligence page found for '{company}'.")
        print(f"   Create one first with: new-contact \"{company}\" \"<Parent Page Title>\"")
        sys.exit(1)

    agent_rules = load_agent_rules()

    user_content = f"Contact Intelligence Page for {company}:\n{ci_url}\n\n{ci_text}"
    if context:
        user_content += f"\n\nAdditional context: {context}"

    if fetch_only:
        print(f"Read the agent rules in engine/deliver/agents/contact_agent.txt, then draft a follow-up email "
              f"for the following Contact Intelligence page.\n\n"
              f"Source: {ci_url}\n\n{ci_text}")
        if context:
            print(f"\nAdditional context: {context}")
        return

    draft = call_ollama(model, agent_rules, user_content)
    print("\n" + "─" * 60)
    print(f"📧 Follow-up draft for {company}")
    print("─" * 60)
    print(draft)
    print("─" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("company",       help="Company name keyword (e.g. 'Acme Corp')")
    parser.add_argument("--model",       default="phi4:latest", help="Ollama model")
    parser.add_argument("--context",     default="",            help="Optional extra context")
    parser.add_argument("--fetch-only",  action="store_true",   help="Print prompt for Claude Code cloud path")
    args = parser.parse_args()

    run(args.company, args.model, args.context, args.fetch_only)
