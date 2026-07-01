#!/usr/bin/env python3
"""
Shared knowledge base update utility.
Called after push-notes, draft-email, and meet-prep to organically update contact files.

Standalone usage (after push-notes cloud run):
  python3 scripts/knowledge_utils.py <notes_file>
"""

import os
import re
import sys
import subprocess
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PROJECT_DIR, CONTACTS_DIR, SHARED_AGENTS


def load_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def company_from_filename(filepath):
    filename = os.path.basename(filepath)
    m = re.match(r"\d{4}-\d{2}-\d{2}_(.+?)_(?:raw|processed)\.md", filename)
    if m:
        return m.group(1).replace("_", " ").replace("-", " ")
    return None


def detect_company_from_text(text):
    if not os.path.isdir(CONTACTS_DIR):
        return None
    text_lower = text.lower()
    for fname in os.listdir(CONTACTS_DIR):
        if not fname.endswith(".md"):
            continue
        keyword = fname.replace(".md", "").replace("_", " ").lower()
        if keyword in text_lower:
            return fname.replace(".md", "").replace("_", " ")
    return None


def extract_intel(content, company, source_type):
    agent = load_file(os.path.join(SHARED_AGENTS, "knowledge_update_agent.txt"))
    prompt = (
        f"{agent}\n\n"
        f"## Source type: {source_type}\n"
        f"## Company / Contact: {company}\n\n"
        f"## Content to analyse:\n{content}\n\n"
        f"Output ONLY the bullet list or NOTHING_TO_UPDATE."
    )
    env = {**os.environ}
    env.pop("ANTHROPIC_AUTH_TOKEN", None)
    env.pop("ANTHROPIC_BASE_URL", None)
    try:
        result = subprocess.run(
            ["claude", "--dangerously-skip-permissions", "-p", prompt],
            capture_output=True, text=True, env=env, timeout=60,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    clean = re.sub(r"\x1b\[[0-9;]*[mGKHF]", "", result.stdout).strip()
    return clean if clean != "NOTHING_TO_UPDATE" else None


def propose_and_apply(company, proposed_update):
    filename = company.strip().lower().replace(" ", "_") + ".md"
    filepath = os.path.join(CONTACTS_DIR, filename)

    print("\nProposed contact update for " + company.title() + ":")
    print("-" * 40)
    print(proposed_update)
    print("-" * 40)

    choice = input("Save to contact file? [y/n] ").strip().lower()
    if choice != "y":
        print("Skipped.")
        return

    os.makedirs(CONTACTS_DIR, exist_ok=True)
    today = date.today().isoformat()

    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {company.strip().title()}\n\n")

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"\n## {today} (auto-extracted)\n{proposed_update}\n")

    print("Contact file updated.")


def update_from_notes(notes_filepath):
    company = company_from_filename(notes_filepath)
    if not company:
        return
    content = load_file(notes_filepath)
    if not content:
        return
    print(f"\nChecking for contact intel to save for {company.title()}...")
    intel = extract_intel(content, company, "meeting notes")
    if intel:
        propose_and_apply(company, intel)
    else:
        print("Nothing new to add to the contact file.")


def update_from_email(email_content, company):
    if not company:
        return
    print(f"\nChecking for contact intel to save for {company.title()}...")
    intel = extract_intel(email_content, company, "email thread")
    if intel:
        propose_and_apply(company, intel)
    else:
        print("Nothing new to add to the contact file.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 knowledge_utils.py <notes_file>")
        sys.exit(1)
    update_from_notes(sys.argv[1])
