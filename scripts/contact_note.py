#!/usr/bin/env python3
"""
add-contact-note — Append a dated note to a local contact context file.

Usage:
  add-contact-note "Acme Corp" "agreed to pilot in Q3"
  add-contact-note "Acme Corp"       # open file in editor
  add-contact-note --list            # show all contact files
"""

import os
import sys
import subprocess
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PROJECT_DIR, CONTACTS_DIR


def company_to_filename(name):
    return name.strip().lower().replace(" ", "_") + ".md"


def list_contacts():
    if not os.path.isdir(CONTACTS_DIR):
        print("No contact files yet.")
        return
    files = [f for f in os.listdir(CONTACTS_DIR) if f.endswith(".md")]
    if not files:
        print("No contact files yet.")
        return
    print("Contacts:")
    for f in sorted(files):
        print(f"  {f.replace('.md', '').replace('_', ' ').title()}")


def open_in_editor(path):
    editor = os.environ.get("EDITOR", "code")
    flags = ["-w"] if "code" in editor else []
    subprocess.run([editor] + flags + [path])


def add_note(company, note):
    os.makedirs(CONTACTS_DIR, exist_ok=True)
    filename = company_to_filename(company)
    filepath = os.path.join(CONTACTS_DIR, filename)

    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {company.strip().title()}\n\n")
        print(f"Created {filename}")

    today = date.today().isoformat()
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"\n## {today}\n{note.strip()}\n")

    print(f"Note added to {filename}")


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return

    if args[0] == "--list":
        list_contacts()
        return

    company = args[0]
    filename = company_to_filename(company)
    filepath = os.path.join(CONTACTS_DIR, filename)

    if len(args) == 1:
        os.makedirs(CONTACTS_DIR, exist_ok=True)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {company.strip().title()}\n\n")
            print(f"Created {filename}")
        open_in_editor(filepath)
        return

    note = " ".join(args[1:])
    add_note(company, note)


if __name__ == "__main__":
    main()
