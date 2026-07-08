"""
Central path configuration for the agentic workspace.
All scripts import from here — change a path once, it updates everywhere.
"""
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Agents (flat — all capability prompt files) ───────────────────────────────
AGENTS_DIR = os.path.join(PROJECT_DIR, "agents")

# Backwards-compat aliases — all agent files now live in one flat folder
SHARED_AGENTS  = AGENTS_DIR
DELIVER_AGENTS = AGENTS_DIR
DECIDE_AGENTS  = AGENTS_DIR
LEARN_AGENTS   = AGENTS_DIR

# Backwards-compat alias
MARKET_DEV_AGENTS = DELIVER_AGENTS

# ── Shared style ───────────────────────────────────────────────────────────────
STYLE_DIR    = os.path.join(PROJECT_DIR, "company", "style")
STYLE_FILE   = os.path.join(STYLE_DIR, "style.md")
PATTERNS_DIR = os.path.join(STYLE_DIR, "patterns")
APPROVED_DIR = os.path.join(STYLE_DIR, "approved")

# ── Knowledge (company-wide) ──────────────────────────────────────────────────
KNOWLEDGE_DIR = os.path.join(PROJECT_DIR, "knowledge")
CONTACTS_DIR  = os.path.join(KNOWLEDGE_DIR, "contacts")

# ── Workflow archives ──────────────────────────────────────────────────────────
MEETING_ARCHIVE = os.path.join(
    PROJECT_DIR, "work", "meeting-intelligence", "archive"
)

# ── Decide loop ───────────────────────────────────────────────────────────────
KTH_IRL_DIR = os.path.join(PROJECT_DIR, "engine", "decide", "methodologies", "kth-irl")
