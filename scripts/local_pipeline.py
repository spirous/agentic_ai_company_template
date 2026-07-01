#!/usr/bin/env python3
"""
Local pipeline for the meeting intelligence workflow.
Calls Ollama API directly — no Claude Code or tool calling required.

Two-phase approach:
  Phase 1 — Model extracts facts in plain text (no XML needed from the model).
  Phase 2 — Python assembles the full Confluence XHTML from those facts.

Saves a draft _processed.md but does NOT auto-publish.
Review the draft, then publish manually with:
  python3 scripts/publish_page.py <path_to_processed_file>
"""

import os
import sys
import re
import argparse
import requests

OLLAMA_URL  = "http://localhost:11434/v1/chat/completions"
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Extraction prompt ────────────────────────────────────────────────────────

EXTRACTION_PROMPT = """\
Extract the key information from the raw meeting notes below.
Output ONLY in this exact format. No extra text, no XML, no HTML, no markdown.

DATE: YYYY-MM-DD
PARTICIPANTS: name (org), name (org)
CC: name, name
GOALS: one-line meeting objective
PREP: one-line background context

NOTES:
- key fact or decision (one per line, max 10)

TAKEAWAYS:
Category | Detail (one per line; use categories: Technical Specifications, Engineering Constraints, Business Alignment)

ACTIONS:
Task description | YYYY-MM-DD
(use 'none' for deadline if unknown)

Raw notes:
{raw_notes}"""


# ── Ollama call ──────────────────────────────────────────────────────────────

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def call_ollama(model, prompt):
    print(f"🤖 Extracting facts with {model}...")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    if response.status_code != 200:
        print(f"❌ Ollama error {response.status_code}: {response.text}")
        sys.exit(1)

    return response.json()["choices"][0]["message"]["content"].strip()


# ── Parser ───────────────────────────────────────────────────────────────────

def parse_extraction(text):
    data = {
        "date": "", "participants": "", "cc": "",
        "goals": "", "prep": "",
        "notes": [], "takeaways": [], "actions": [],
    }

    for field, key in [("DATE", "date"), ("PARTICIPANTS", "participants"),
                        ("CC", "cc"), ("GOALS", "goals"), ("PREP", "prep")]:
        m = re.search(rf"^{field}:\s*(.+)$", text, re.MULTILINE)
        if m:
            data[key] = m.group(1).strip()

    def extract_section(label):
        m = re.search(rf"^{label}:\n(.*?)(?=\n[A-Z]+:|\Z)", text, re.DOTALL | re.MULTILINE)
        return m.group(1).strip().splitlines() if m else []

    for line in extract_section("NOTES"):
        line = line.lstrip("-• ").strip()
        if line:
            data["notes"].append(line)

    for line in extract_section("TAKEAWAYS"):
        if "|" in line:
            cat, detail = line.split("|", 1)
            data["takeaways"].append((cat.strip(), detail.strip()))

    for line in extract_section("ACTIONS"):
        line = line.lstrip("-• ").strip()
        if not line:
            continue
        if "|" in line:
            task, deadline = line.split("|", 1)
            data["actions"].append((task.strip(), deadline.strip()))
        else:
            data["actions"].append((line, "none"))

    return data


# ── Confluence HTML builder ──────────────────────────────────────────────────

def build_confluence_html(data):
    lines = []

    lines += [
        f'<p><b>Date:</b> {data["date"]}</p>',
        f'<p><b>Participants:</b> {data["participants"]}</p>',
        f'<p><b>To Be Informed (CC):</b> {data["cc"]}</p>',
        '<hr />',
    ]

    lines += [
        '## 1. The Launchpad (Before)',
        '### Meeting Goals',
        f'* {data["goals"]}',
        '### Prep Notes & Context',
        f'* {data["prep"]}',
        '---',
    ]

    lines += ['## 2. The Intelligence (During)', '### Discussion Notes']
    for note in data["notes"]:
        lines.append(f'* {note}')
    lines.append('---')

    lines += [
        '## 3. The Momentum (After)',
        '### Key Technical & Business Takeaways',
        '<table>',
        '<tr><th>Category</th><th>Detail / Constraint</th></tr>',
    ]
    for cat, detail in data["takeaways"]:
        lines.append(f'<tr><td><b>{cat}</b></td><td>{detail}</td></tr>')
    lines.append('</table>')

    # Action items — set CONFLUENCE_ACCOUNT_ID in .env for clickable task assignments
    account_id = os.getenv("CONFLUENCE_ACCOUNT_ID", "YOUR_ACCOUNT_ID")
    lines.append('### Next Steps & Action Items')
    lines.append('<ac:task-list>')
    for i, (task, deadline) in enumerate(data["actions"], 1):
        d = deadline.strip().lower()
        deadline_text = f" — {deadline.strip()}" if d and d != "none" else ""
        lines += [
            '<ac:task>',
            f'<ac:task-id>{i}</ac:task-id>',
            '<ac:task-status>incomplete</ac:task-status>',
            f'<ac:task-body>'
            f'<ac:link><ri:user ri:account-id="{account_id}" /></ac:link> '
            f'{task}{deadline_text}'
            f'</ac:task-body>',
            '</ac:task>',
        ]
    lines.append('</ac:task-list>')

    return '\n'.join(lines)


# ── Helpers ──────────────────────────────────────────────────────────────────

def derive_title(raw_path, data=None):
    filename = os.path.basename(raw_path)
    m = re.match(r"(\d{4}-\d{2}-\d{2})_(.+?)_raw\.md", filename)
    date = m.group(1) if m else ""
    company = m.group(2).replace("_", " ").replace("-", " ").title() if m else "Meeting"

    if data and data.get("notes"):
        points = "; ".join(n for n in data["notes"][:2] if n)
        return f"🗒️ {date} {company} — {points}"
    return f"🗒️ {date} {company} Meeting"


def build_routing_slip(space, parent, title):
    return (
        f'---\n'
        f'confluence_space: "{space}"\n'
        f'confluence_parent_page: "{parent}"\n'
        f'confluence_title: "{title}"\n'
        f'---\n'
    )


# ── Main ─────────────────────────────────────────────────────────────────────

def run(raw_path, space, parent, model):
    processed_path = raw_path.replace("_raw.md", "_processed.md")

    print("📖 Reading raw notes...")
    raw_notes = read_file(raw_path)

    extraction = call_ollama(model, EXTRACTION_PROMPT.format(raw_notes=raw_notes))

    print("🔧 Assembling Confluence HTML...")
    data = parse_extraction(extraction)
    title = derive_title(raw_path, data)
    body = build_confluence_html(data)

    routing_slip      = build_routing_slip(space, parent, title)
    processed_content = routing_slip + body

    print(f"💾 Saving: {processed_path}")
    with open(processed_path, "w", encoding="utf-8") as f:
        f.write(processed_content)

    print("🚀 Publishing to Confluence...")
    publish_script = os.path.join(PROJECT_DIR, "scripts", "publish_page.py")
    exit_code = os.system(f'python3 "{publish_script}" "{processed_path}"')

    if exit_code == 0:
        sys.path.insert(0, os.path.join(PROJECT_DIR, "scripts"))
        from knowledge_utils import update_from_notes
        update_from_notes(raw_path)

    sys.exit(0 if exit_code == 0 else 1)


if __name__ == "__main__":
    # Load env for defaults
    env_path = os.path.join(PROJECT_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k, v.strip("\"'"))

    default_space  = os.getenv("CONFLUENCE_SPACE", "YOUR_SPACE_KEY")
    default_parent = os.getenv("CONFLUENCE_DEFAULT_PARENT", "Meeting Notes")

    parser = argparse.ArgumentParser(description="Local Ollama meeting intelligence pipeline")
    parser.add_argument("file",            help="Path to raw notes file (*_raw.md)")
    parser.add_argument("--space",  default=default_space,  help="Confluence space key")
    parser.add_argument("--parent", default=default_parent, help="Confluence parent page title")
    parser.add_argument("--model",  default="phi4:latest",  help="Ollama model name")
    args = parser.parse_args()

    raw_path = os.path.realpath(args.file)
    if not os.path.exists(raw_path):
        print(f"❌ File not found: {raw_path}")
        sys.exit(1)

    run(raw_path, args.space, args.parent, args.model)
