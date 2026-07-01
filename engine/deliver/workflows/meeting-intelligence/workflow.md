# Workflow: Meeting Intelligence

**Input:** Raw `.md` file with unstructured meeting notes
**Output:** Formatted protocol page published to Confluence
**Command:** `push-notes <file> [--to SPACE/'Parent Page'] [--local]`

## Agent Pipeline

| Step | Agent | Role | Input | Output |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `document_agent` | Transforms raw notes into structured Confluence XHTML | `*_raw.md` | `*_processed.md` with routing slip |
| 2 | `publish_page.py` | Reads routing slip, POSTs page to Confluence API | `*_processed.md` | Live Confluence page |

## Agents Used
- [`../../../../shared/agents/document_agent.txt`](../../../../shared/agents/document_agent.txt) — extraction rules, style guide, Confluence macro formats
- [`../../../../shared/agents/qa_agent.txt`](../../../../shared/agents/qa_agent.txt) — output quality review

## Confluence Defaults
- Space: set in `.env` → `CONFLUENCE_SPACE`
- Parent page: set in `.env` → `CONFLUENCE_DEFAULT_PARENT`

## File Conventions
- Raw input: `archive/YYYY/YYYY-MM-DD_<topic>_raw.md`
- Processed output: `archive/YYYY/YYYY-MM-DD_<topic>_processed.md`
