"""
Central path configuration for the agentic workspace.
All scripts import from here — change a path once, it updates everywhere.
"""
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Engine loop agent directories ─────────────────────────────────────────────
SHARED_AGENTS  = os.path.join(PROJECT_DIR, "shared", "agents")
DELIVER_AGENTS = os.path.join(PROJECT_DIR, "engine", "deliver", "agents")
DECIDE_AGENTS  = os.path.join(PROJECT_DIR, "engine", "decide", "agents")
LEARN_AGENTS   = os.path.join(PROJECT_DIR, "engine", "learn", "agents")

# Backwards-compat alias
MARKET_DEV_AGENTS = DELIVER_AGENTS

# ── Shared style ───────────────────────────────────────────────────────────────
STYLE_DIR    = os.path.join(PROJECT_DIR, "shared", "style")
STYLE_FILE   = os.path.join(STYLE_DIR, "style.md")
PATTERNS_DIR = os.path.join(STYLE_DIR, "patterns")
APPROVED_DIR = os.path.join(STYLE_DIR, "approved")

# ── Knowledge (company-wide) ──────────────────────────────────────────────────
KNOWLEDGE_DIR = os.path.join(PROJECT_DIR, "knowledge")
CONTACTS_DIR  = os.path.join(KNOWLEDGE_DIR, "contacts")

# ── Workflow archives ──────────────────────────────────────────────────────────
MEETING_ARCHIVE = os.path.join(
    PROJECT_DIR, "engine", "deliver", "workflows", "meeting-intelligence", "archive"
)

# ── Decide loop ───────────────────────────────────────────────────────────────
KTH_IRL_DIR = os.path.join(PROJECT_DIR, "engine", "decide", "methodologies", "kth-irl")
