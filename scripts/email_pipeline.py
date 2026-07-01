#!/usr/bin/env python3
"""
Email Intelligence pipeline — frictionless email drafting from the terminal.

Flow:
  1. Read input: clipboard (default), file, or --new description
  2. Load knowledge base: style guide + pattern + contact context
  3. Draft email via Claude (cloud) or Ollama (local)
  4. Interactive review loop: [a]pprove / [i]terate / [e]dit / [d]iscard
  5. On approve: copy to clipboard + save to knowledge base

Usage:
  python3 scripts/email_pipeline.py                       # reply to clipboard email
  python3 scripts/email_pipeline.py --local               # same, Ollama
  python3 scripts/email_pipeline.py --new "follow up on proposal"
  python3 scripts/email_pipeline.py --file email.txt
"""

import os
import re
import sys
import argparse
import subprocess
import tempfile
import requests
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PROJECT_DIR, KNOWLEDGE_DIR, CONTACTS_DIR, STYLE_FILE, PATTERNS_DIR, APPROVED_DIR, MARKET_DEV_AGENTS

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
KNOWLEDGE  = KNOWLEDGE_DIR


# ── Knowledge base ────────────────────────────────────────────────────────────

def load_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def load_style():
    return load_file(STYLE_FILE)


def detect_pattern(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["follow up", "no response", "following up", "reminder"]):
        return "follow_up"
    if any(w in text_lower for w in ["introduce", "introduction", "reaching out", "first time"]):
        return "introduction"
    if any(w in text_lower for w in ["thank", "thanks", "great meeting", "great call"]):
        return "thank_you"
    if any(w in text_lower for w in ["update", "status", "progress", "wanted to share"]):
        return "update"
    return None


def load_pattern(name):
    if not name:
        return ""
    path = os.path.join(PATTERNS_DIR, f"{name}.md")
    content = load_file(path)
    return f"\n## Email pattern to follow:\n{content}" if content else ""


def load_contact_context(text):
    contacts_dir = CONTACTS_DIR
    if not os.path.isdir(contacts_dir):
        return ""
    text_lower = text.lower()
    for fname in os.listdir(contacts_dir):
        if not fname.endswith(".md"):
            continue
        keyword = fname.replace(".md", "").replace("_", " ").lower()
        if keyword in text_lower:
            content = load_file(os.path.join(contacts_dir, fname))
            if content:
                return f"\n## Contact context:\n{content}"
    return ""


def detect_company(text):
    contacts_dir = CONTACTS_DIR
    if not os.path.isdir(contacts_dir):
        return None
    text_lower = text.lower()
    for fname in os.listdir(contacts_dir):
        if not fname.endswith(".md"):
            continue
        keyword = fname.replace(".md", "").replace("_", " ").lower()
        if keyword in text_lower:
            return fname.replace(".md", "").replace("_", " ")
    return None


def build_prompt(input_text, is_new, style, pattern, contact):
    agent_rules = load_file(os.path.join(MARKET_DEV_AGENTS, "email_agent.txt"))
    system = f"{agent_rules}\n\n## Your style guide:\n{style}{pattern}{contact}"

    if is_new:
        user = f"Draft a new outbound email for this situation:\n{input_text}"
    else:
        user = f"Draft a reply to this incoming email:\n\n{input_text}"

    return system, user


# ── AI backends ───────────────────────────────────────────────────────────────

def call_ollama(model, system, user_content):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
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


def call_cloud(system, user_content):
    """Use Claude Code CLI — reuses your existing subscription, no API key needed."""
    full_prompt = (
        f"{system}\n\n"
        f"---\n\n"
        f"{user_content}\n\n"
        f"Output ONLY the email draft. Start with 'SUBJECT:' on the first line."
    )
    env = {**os.environ}
    env.pop("ANTHROPIC_AUTH_TOKEN", None)
    env.pop("ANTHROPIC_BASE_URL", None)

    try:
        result = subprocess.run(
            ["claude", "--dangerously-skip-permissions", "-p", full_prompt],
            capture_output=True, text=True, env=env, timeout=120,
        )
    except FileNotFoundError:
        print("❌ Claude Code not found. Install it or use: draft-email --local")
        sys.exit(1)

    if result.returncode != 0:
        print(f"❌ Claude Code error: {result.stderr[:300]}")
        sys.exit(1)

    clean = re.sub(r"\x1b\[[0-9;]*[mGKHF]", "", result.stdout)
    match = re.search(r"SUBJECT:.*", clean, re.DOTALL)
    return match.group(0).strip() if match else clean.strip()


def generate(system, user_content, use_local, model):
    if use_local:
        print(f"🤖 Drafting with {model}...")
        return call_ollama(model, system, user_content)
    else:
        print("🤖 Drafting with Claude...")
        return call_cloud(system, user_content)


def regenerate(system, user_content, previous_draft, instruction, use_local, model):
    refine_user = (
        f"{user_content}\n\n"
        f"Previous draft:\n{previous_draft}\n\n"
        f"Revision instruction: {instruction}\n"
        f"Output the improved email in the same SUBJECT / body format."
    )
    return generate(system, refine_user, use_local, model)


# ── Input ─────────────────────────────────────────────────────────────────────

def read_clipboard():
    result = subprocess.run(["pbpaste"], capture_output=True, text=True)
    text = result.stdout.strip()
    if not text:
        print("❌ Clipboard is empty. Copy an email first, or use --new or --file.")
        sys.exit(1)
    return text


def read_file(path):
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


# ── Review loop ───────────────────────────────────────────────────────────────

def print_draft(draft):
    print("\n" + "─" * 60)
    print(draft)
    print("─" * 60)


def open_in_editor(draft):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, prefix="email_draft_") as f:
        f.write(draft)
        tmp = f.name
    editor = os.environ.get("EDITOR", "code")
    flags = ["-w"] if "code" in editor else []
    subprocess.run([editor] + flags + [tmp])
    with open(tmp, "r", encoding="utf-8") as f:
        edited = f.read().strip()
    os.unlink(tmp)
    return edited


def copy_to_clipboard(text):
    subprocess.run(["pbcopy"], input=text, text=True)


def save_approved(draft):
    approved_dir = APPROVED_DIR
    os.makedirs(approved_dir, exist_ok=True)
    today = date.today().isoformat()
    existing = [f for f in os.listdir(approved_dir) if f.startswith(today)]
    idx = len(existing) + 1
    path = os.path.join(approved_dir, f"{today}_{idx:02d}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(draft)
    return path


def review_loop(draft, system, user_content, use_local, model, company=None):
    while True:
        print_draft(draft)
        print("\n  [a] approve — copy to clipboard + save")
        print("  [i] iterate — give a revision instruction")
        print("  [e] edit    — open in editor")
        print("  [d] discard\n")

        choice = input("  > ").strip().lower()

        if choice == "a":
            copy_to_clipboard(draft)
            saved = save_approved(draft)
            print(f"\n✅ Copied to clipboard. Paste into your email client.")
            print(f"   Saved to knowledge base: {os.path.relpath(saved, PROJECT_DIR)}")
            if company:
                import sys as _sys
                _sys.path.insert(0, PROJECT_DIR + "/scripts")
                from knowledge_utils import update_from_email
                update_from_email(user_content, company)
            break

        elif choice == "i":
            instruction = input("  Instruction: ").strip()
            if instruction:
                print()
                draft = regenerate(system, user_content, draft, instruction, use_local, model)

        elif choice == "e":
            draft = open_in_editor(draft)
            print("  Draft updated from editor.")

        elif choice == "d":
            print("  Discarded.")
            break

        else:
            print("  Type a, i, e, or d.")


# ── Main ──────────────────────────────────────────────────────────────────────

def run(use_local, model, new_description, file_path):
    if file_path:
        input_text = read_file(file_path)
        is_new = False
    elif new_description:
        input_text = new_description
        is_new = True
    else:
        print("📋 Reading from clipboard...")
        input_text = read_clipboard()
        is_new = False

    style   = load_style()
    pattern = load_pattern(detect_pattern(input_text))
    contact = load_contact_context(input_text)
    company = detect_company(input_text)

    system, user_content = build_prompt(input_text, is_new, style, pattern, contact)
    draft = generate(system, user_content, use_local, model)
    review_loop(draft, system, user_content, use_local, model, company)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email drafting pipeline")
    parser.add_argument("--local",  action="store_true",   help="Use local Ollama model")
    parser.add_argument("--model",  default="phi4:latest", help="Ollama model (with --local)")
    parser.add_argument("--new",    default="",            help="Description for new outbound email")
    parser.add_argument("--file",   default="",            help="Read email from file instead of clipboard")
    args = parser.parse_args()

    run(args.local, args.model, args.new, args.file)
