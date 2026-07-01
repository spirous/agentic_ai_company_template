#!/usr/bin/env python3
"""
meet-prep — Generate a pre-meeting brief from past notes and contact context.
Saves the brief to Apple Notes and prints it to the terminal.

Usage:
  meet-prep "Acme Corp"
  meet-prep "Acme Corp" "focus on the renewal agreement"
  meet-prep "Acme Corp" --local
"""

import os
import re
import sys
import subprocess
import requests
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PROJECT_DIR, CONTACTS_DIR, MEETING_ARCHIVE, MARKET_DEV_AGENTS

ARCHIVE_DIR = MEETING_ARCHIVE
OLLAMA_URL  = "http://localhost:11434/v1/chat/completions"


def load_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def find_past_notes(company, max_files=2):
    keyword = company.strip().lower().replace(" ", "_")
    matches = []
    for root, _, files in os.walk(ARCHIVE_DIR):
        for fname in files:
            if keyword in fname.lower() and fname.endswith("_processed.md"):
                matches.append(os.path.join(root, fname))
    matches.sort(reverse=True)
    return matches[:max_files]


def load_contact_context(company):
    filename = company.strip().lower().replace(" ", "_") + ".md"
    path = os.path.join(CONTACTS_DIR, filename)
    return load_file(path)


def build_prompt(company, meeting_context, contact_context, past_notes_content):
    agent = load_file(os.path.join(MARKET_DEV_AGENTS, "meeting_prep_agent.txt"))
    sections = [agent]
    sections.append(f"\n## Contact context:\n{contact_context}" if contact_context else "\n## Contact context:\nNone on file.")
    sections.append(f"\n## Past meeting notes:\n{past_notes_content}" if past_notes_content else "\n## Past meeting notes:\nNone found.")
    if meeting_context:
        sections.append(f"\n## Focus for this meeting:\n{meeting_context}")
    system = "\n".join(sections)
    user = f"Generate the pre-meeting brief for my upcoming call with {company.strip().title()}."
    return system, user


def call_cloud(system, user_content):
    full_prompt = f"{system}\n\n---\n\n{user_content}\n\nOutput ONLY the brief in the exact format specified."
    env = {**os.environ}
    env.pop("ANTHROPIC_AUTH_TOKEN", None)
    env.pop("ANTHROPIC_BASE_URL", None)
    try:
        result = subprocess.run(
            ["claude", "--dangerously-skip-permissions", "-p", full_prompt],
            capture_output=True, text=True, env=env, timeout=120,
        )
    except FileNotFoundError:
        print("Claude Code not found.")
        sys.exit(1)
    if result.returncode != 0:
        print(f"Claude error: {result.stderr[:300]}")
        sys.exit(1)
    clean = re.sub(r"\x1b\[[0-9;]*[mGKHF]", "", result.stdout)
    return clean.strip()


def call_ollama(model, system, user_content):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        "stream": False,
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=180)
    except requests.exceptions.ConnectionError:
        print("Ollama is not running. Start it with: ollama serve")
        sys.exit(1)
    if resp.status_code != 200:
        print(f"Ollama error {resp.status_code}: {resp.text}")
        sys.exit(1)
    return resp.json()["choices"][0]["message"]["content"].strip()


def save_to_apple_notes(title, body):
    safe_body = body.replace('"', '\\"').replace('\n', '\\n')
    script = f'''
    tell application "Notes"
        make new note with properties {{name:"{title}", body:"{safe_body}"}}
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Could not save to Apple Notes: {result.stderr.strip()}")
    else:
        print(f'Saved to Apple Notes: "{title}"')


def run(company, meeting_context, use_local, model):
    contact_context = load_contact_context(company)
    if not contact_context:
        print(f"No contact file found for {company}. Run: add-contact-note \"{company}\"")

    note_files = find_past_notes(company)
    if note_files:
        print(f"Found {len(note_files)} past meeting note(s) for {company.title()}.")
        past_notes_content = ""
        for path in note_files:
            date_label = os.path.basename(path)[:10]
            content = load_file(path)
            past_notes_content += f"\n### Meeting {date_label}\n{content}\n"
    else:
        print(f"No past meeting notes found for {company.title()}.")
        past_notes_content = ""

    system, user = build_prompt(company, meeting_context, contact_context, past_notes_content)

    if use_local:
        print(f"Generating brief with {model}...")
        brief = call_ollama(model, system, user)
    else:
        print("Generating brief...")
        brief = call_cloud(system, user)

    print("\n" + "=" * 60)
    print(brief)
    print("=" * 60 + "\n")

    today = date.today().isoformat()
    note_title = f"Meeting Prep — {company.strip().title()} — {today}"
    save_to_apple_notes(note_title, brief)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Pre-meeting brief generator")
    parser.add_argument("company", help="Company or contact name")
    parser.add_argument("context", nargs="?", default="", help="Optional focus for this meeting")
    parser.add_argument("--local", action="store_true", help="Use local Ollama model")
    parser.add_argument("--model", default="phi4:latest", help="Ollama model (with --local)")
    args = parser.parse_args()

    run(args.company, args.context, args.local, args.model)
