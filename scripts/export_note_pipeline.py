#!/usr/bin/env python3
"""
export-note — Export an Apple Note to a raw .md file ready for push-notes.

Finds the most recently modified Apple Note matching the company name,
strips HTML, saves as YYYY-MM-DD_<company>_raw.md in the archive.

Usage:
  export-note "Acme Corp"
  export-note "Acme Corp" --to SPACE/'Parent Page'
"""

import os
import re
import sys
import subprocess
from datetime import date
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PROJECT_DIR, MEETING_ARCHIVE
ARCHIVE_DIR = MEETING_ARCHIVE


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lines = []
        self.current = []

    def handle_data(self, data):
        self.current.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in ("div", "p", "br"):
            if self.current:
                self.lines.append("".join(self.current).strip())
                self.current = []

    def handle_endtag(self, tag):
        if tag in ("div", "p"):
            if self.current:
                self.lines.append("".join(self.current).strip())
                self.current = []

    def get_text(self):
        if self.current:
            self.lines.append("".join(self.current).strip())
        return "\n".join(line for line in self.lines if line)


def strip_html(html):
    parser = HTMLStripper()
    parser.feed(html)
    return parser.get_text()


def find_note_in_apple_notes(keyword):
    script = f'''
    tell application "Notes"
        set matchingNotes to (every note whose name contains "{keyword}")
        if (count of matchingNotes) is 0 then
            return "NOT_FOUND"
        end if
        set latestNote to item 1 of matchingNotes
        set latestDate to modification date of item 1 of matchingNotes
        repeat with n in matchingNotes
            if modification date of n > latestDate then
                set latestDate to modification date of n
                set latestNote to n
            end if
        end repeat
        return name of latestNote & "|||" & body of latestNote
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Apple Notes error: {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()


def save_raw_note(company, content, topic=""):
    today = date.today().isoformat()
    year = today[:4]
    year_dir = os.path.join(ARCHIVE_DIR, year)
    os.makedirs(year_dir, exist_ok=True)

    slug = company.strip().lower().replace(" ", "_")
    if topic:
        slug += "_" + topic.strip().lower().replace(" ", "_")
    filename = f"{today}_{slug}_raw.md"
    filepath = os.path.join(year_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def run(company, destination, topic=""):
    print(f"Searching Apple Notes for \"{company}\"...")
    raw = find_note_in_apple_notes(company)

    if raw == "NOT_FOUND":
        print(f"No Apple Note found containing \"{company}\".")
        sys.exit(1)

    parts = raw.split("|||", 1)
    note_title = parts[0].strip()
    note_body_html = parts[1].strip() if len(parts) > 1 else ""

    print(f"Found: {note_title}")

    content = strip_html(note_body_html)
    if not content:
        print("Note appears to be empty.")
        sys.exit(1)

    filepath = save_raw_note(company, content, topic)
    print(f"Saved: {os.path.relpath(filepath, PROJECT_DIR)}\n")

    dest_hint = f" --to {destination}" if destination else ""
    choice = input("Run push-notes on this file now? [y/n] ").strip().lower()
    if choice == "y":
        push = os.path.join(PROJECT_DIR, "scripts", "push-notes")
        cmd = [push, filepath]
        if destination:
            cmd += ["--to", destination]
        subprocess.run(cmd)
    else:
        print(f"\nWhen ready:\n  push-notes {filepath}{dest_hint}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Export Apple Note to raw .md")
    parser.add_argument("company", help="Keyword to search for in Apple Notes")
    parser.add_argument("--to", default="", dest="destination", help="Confluence destination: SPACE/'Parent Page'")
    parser.add_argument("--topic", default="", help="Short topic label added to the filename and page title")
    args = parser.parse_args()

    run(args.company, args.destination, args.topic)
