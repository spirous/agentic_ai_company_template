#!/usr/bin/env python3
"""
Weekly Contact Intelligence review.

Two outputs — separated by audience:

  1. Confluence Dashboard (company-visible)
     "📊 Contact Intelligence Dashboard" — status table only.
     Shows: Company | Type | Priority | Last Contact | Next Action | Deal Stage
     No email drafts. No operational detail. Safe for the whole team to see.

  2. Local drafts file (personal, never published)
     ~/Desktop/followups_YYYY-MM-DD.md
     Full email drafts for overdue contacts only. Open → review → copy into email client.
     macOS notification opens the file automatically.

Architecture principle: Confluence = company knowledge. Local = personal operations.

Run manually:   python3 scripts/weekly_review.py
Dry run:        python3 scripts/weekly_review.py --dry-run
Cron (Monday 08:00 installed by scripts/setup-cron.sh)
"""

import os
import re
import sys
import argparse
import subprocess
import requests
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PROJECT_DIR, MARKET_DEV_AGENTS
from confluence_utils import (
    get_credentials, search_pages_by_title_contains,
    find_page_by_title, html_to_text, create_or_update_page,
    get_space_homepage,
)


# ── Configuration ─────────────────────────────────────────────────────────────

# Load env for CONFLUENCE_SPACE default
_env_path = os.path.join(PROJECT_DIR, ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k, _v.strip("\"'"))

SPACE               = os.getenv("CONFLUENCE_SPACE", "YOUR_SPACE_KEY")
DASHBOARD_TITLE     = "📊 Contact Intelligence Dashboard"
LOCAL_DRAFTS_DIR    = os.path.expanduser("~/Desktop")
FOLLOW_UP_DAYS      = {"High": 14, "Medium": 28, "Low": 45}
DEFAULT_INTERVAL    = 30


# ── Agent rules ───────────────────────────────────────────────────────────────

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"


def load_agent_rules():
    path = os.path.join(MARKET_DEV_AGENTS, "contact_agent.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ── Parse CI page fields ──────────────────────────────────────────────────────

def parse_date(val):
    val = val.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(val, fmt).date()
        except ValueError:
            continue
    return None


def extract_field(text, label):
    m = re.search(rf"{label}[:\s]+([^\n<|]+)", text, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def parse_ci_page(ci_text):
    return {
        "type":         extract_field(ci_text, "Type"),
        "priority":     extract_field(ci_text, "Priority"),
        "contact":      extract_field(ci_text, "Primary Contact"),
        "last_contact": extract_field(ci_text, "Last Contact"),
        "next_action":  extract_field(ci_text, "Next Action"),
        "deal_stage":   extract_field(ci_text, "Deal Stage"),
    }


def assess_status(fields, today):
    priority     = fields.get("priority", "")
    last_contact = parse_date(fields.get("last_contact", ""))
    next_action  = fields.get("next_action", "")

    if not last_contact:
        return "🔴", True, "No last contact date recorded"

    days_since = (today - last_contact).days
    interval   = FOLLOW_UP_DAYS.get(priority, DEFAULT_INTERVAL)

    if next_action:
        m = re.search(r"by\s+(\d{4}-\d{2}-\d{2})", next_action, re.IGNORECASE)
        if m:
            action_date = parse_date(m.group(1))
            if action_date and action_date < today:
                return "🔴", True, f"Action overdue since {m.group(1)}"
            if action_date and (action_date - today).days <= 7:
                return "🟡", True, f"Action due {m.group(1)}"

    if days_since >= interval:
        return "🔴", True, f"{days_since}d since last contact (threshold: {interval}d)"
    if days_since >= int(interval * 0.75):
        return "🟡", False, f"{days_since}d since last contact — approaching threshold"

    return "🟢", False, f"On track ({days_since}d since last contact)"


# ── Email drafting ────────────────────────────────────────────────────────────

def draft_email_ollama(ci_text, company, reason, model):
    agent_rules  = load_agent_rules()
    user_content = f"Contact Intelligence Page for {company}:\n\n{ci_text}\n\nContext: {reason}"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": agent_rules},
            {"role": "user",   "content": user_content},
        ],
        "stream": False,
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=180)
    except requests.exceptions.ConnectionError:
        return "⚠️  Ollama not running — start with: ollama serve"
    if resp.status_code != 200:
        return f"⚠️  Ollama error {resp.status_code}"
    return resp.json()["choices"][0]["message"]["content"].strip()


def draft_email_cloud(ci_text, company, reason, api_key):
    agent_rules  = load_agent_rules()
    user_content = f"Contact Intelligence Page for {company}:\n\n{ci_text}\n\nContext: {reason}"
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 1024,
            "system": agent_rules,
            "messages": [{"role": "user", "content": user_content}],
        },
        timeout=60,
    )
    if resp.status_code != 200:
        return f"⚠️  Anthropic API error {resp.status_code}"
    return resp.json()["content"][0]["text"].strip()


# ── Confluence Dashboard builder ──────────────────────────────────────────────

def build_dashboard_html(contacts, today_str):
    rows = []
    for c in contacts:
        f   = c["fields"]
        ind = c["indicator"]
        rows.append(
            f'<tr>'
            f'<td><a href="{c["page_url"]}">{c["company"]}</a></td>'
            f'<td>{f["type"]}</td>'
            f'<td>{f["priority"]}</td>'
            f'<td>{f["last_contact"]}</td>'
            f'<td>{ind} {f["next_action"] or "—"}</td>'
            f'<td>{f["deal_stage"]}</td>'
            f'</tr>'
        )

    return (
        f'<p><i>Last updated: {today_str} · Auto-generated · '
        f'🔴 overdue / action due · 🟡 approaching · 🟢 on track</i></p>'
        f'<table>'
        f'<tr><th>Company</th><th>Type</th><th>Priority</th>'
        f'<th>Last Contact</th><th>Next Action</th><th>Deal Stage</th></tr>'
        + "".join(rows) +
        f'</table>'
    )


# ── Local drafts file ─────────────────────────────────────────────────────────

def save_drafts_locally(entries, today_str):
    if not entries:
        return None

    filename  = f"followups_{today_str}.md"
    filepath  = os.path.join(LOCAL_DRAFTS_DIR, filename)
    lines     = [
        f"# Follow-up Drafts — {today_str}",
        "_Personal — do not share. Review, copy into your email client, then send._",
        "",
    ]
    for i, e in enumerate(entries, 1):
        lines += [
            "---",
            f"## {i}. {e['company']} — {e['fields']['priority']} Priority",
            f"**Trigger:** {e['reason']}",
            f"**CI page:** {e['page_url']}",
            "",
            e["draft"],
            "",
        ]
    lines.append("---\n_End of drafts_")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath


# ── Notification ──────────────────────────────────────────────────────────────

def notify(message, open_path=None):
    script = f'display notification "{message}" with title "Contact Intelligence" sound name "Glass"'
    subprocess.run(["osascript", "-e", script], capture_output=True)
    if open_path:
        subprocess.run(["open", open_path], capture_output=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def run(use_cloud, model, api_key, dry_run):
    today     = date.today()
    today_str = today.isoformat()

    print(f"🔍 Fetching Contact Intelligence pages ({SPACE})...")
    url, _, _, auth = get_credentials()
    ci_pages = search_pages_by_title_contains(url, auth, SPACE, "Contact Intelligence")

    if not ci_pages:
        print("ℹ️  No Contact Intelligence pages found yet.")
        print("   Create one with: new-contact \"Company\" \"Parent Page Title\"")
        return

    print(f"📋 Found {len(ci_pages)} CI page(s). Evaluating status...")

    all_contacts = []
    draft_entries = []

    for page in ci_pages:
        body_html = page.get("body", {}).get("storage", {}).get("value", "")
        ci_text   = html_to_text(body_html)
        page_url  = f"{url}/wiki/spaces/{SPACE}/pages/{page['id']}"
        raw_title = page.get("title", "")
        company   = raw_title.replace(" - Contact Intelligence", "").strip() or raw_title
        fields    = parse_ci_page(ci_text)

        indicator, needs_action, reason = assess_status(fields, today)
        print(f"  {indicator} {company} — {reason}")

        all_contacts.append({
            "company":   company,
            "fields":    fields,
            "indicator": indicator,
            "reason":    reason,
            "page_url":  page_url,
        })

        if needs_action:
            print(f"     → Drafting email...")
            if use_cloud and api_key:
                draft = draft_email_cloud(ci_text, company, reason, api_key)
            else:
                draft = draft_email_ollama(ci_text, company, reason, model)
            draft_entries.append({**all_contacts[-1], "draft": draft})

    dashboard_html = build_dashboard_html(all_contacts, today_str)

    if dry_run:
        print("\n" + "─" * 60)
        print("DRY RUN — Dashboard HTML (not published):")
        print("─" * 60)
        print(dashboard_html[:800], "...")
        print("\n─ Local draft emails ─")
        for e in draft_entries:
            print(f"\n### {e['company']}\n{e['draft'][:300]}...")
        return

    print(f"\n🚀 Publishing Contact Intelligence Dashboard to Confluence...")
    homepage = get_space_homepage(url, auth, SPACE)
    if not homepage:
        print(f"❌ Could not find space homepage for {SPACE}. Check credentials.")
        sys.exit(1)

    dashboard_url = create_or_update_page(
        url, auth, SPACE, homepage["id"], DASHBOARD_TITLE, dashboard_html
    )

    if dashboard_url:
        print(f"✅ Dashboard: {dashboard_url}")
    else:
        print("❌ Dashboard publish failed.")

    if draft_entries:
        print(f"\n💾 Saving {len(draft_entries)} email draft(s) locally...")
        drafts_path = save_drafts_locally(draft_entries, today_str)
        if drafts_path:
            print(f"✅ Drafts: {drafts_path}")
            notify(
                f"{len(draft_entries)} follow-up draft(s) ready on your Desktop",
                drafts_path,
            )
    else:
        print("\n✅ No follow-ups needed this week.")
        notify("No follow-ups needed this week ✅")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weekly Contact Intelligence review")
    parser.add_argument("--cloud",   action="store_true", help="Use Anthropic API (requires ANTHROPIC_API_KEY in .env)")
    parser.add_argument("--model",   default="phi4:latest", help="Ollama model (default when not using --cloud)")
    parser.add_argument("--dry-run", action="store_true", help="Preview output without publishing or saving")
    args = parser.parse_args()

    api_key = None
    if args.cloud:
        from confluence_utils import load_env
        load_env()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("❌ --cloud requires ANTHROPIC_API_KEY in .env")
            sys.exit(1)

    run(args.cloud, args.model, api_key, args.dry_run)
