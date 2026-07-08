# Loan Agreements Workflow

## What it does
Fills a Word loan agreement template, creates an internal Confluence tracking page, and drafts the cover email. All document handling is local Python — nothing leaves the laptop except the Confluence API call and the email draft.

## Agreement types
| Type | §7 | Use when |
|:---|:---|:---|
| `standard` | None — borrower handles all shipping | Customer arranges transport |
| `ds` | Your company arranges transport + insurance both ways | You handle shipping |

---

## Setup (one-time)

### Word templates
Place your loan agreement templates here:
```
work/loan-agreements/templates/
  loan_agreement_standard.docx
  loan_agreement_ds.docx
```
These are gitignored and never pushed to any repo.

The templates must have no `{{placeholder}}` tokens. Fill points are located by paragraph anchor text — see `scripts/fill_loan_agreement.py` for details. If your template structure differs, update the `fill_document()` function.

### Confluence
Edit `scripts/create_loan_page.py` and set:
```python
TEMPLATE_PAGE_ID = 'YOUR_TEMPLATE_PAGE_ID'   # page ID of your Confluence template
PARENT_PAGE_ID   = 'YOUR_PARENT_PAGE_ID'     # parent page for new loan tracking pages
SPACE_KEY        = 'YOUR_SPACE_KEY'          # your Confluence space key
```

### Shell alias
Add to `~/.zshrc`:
```zsh
alias fill-loan='python3 /path/to/scripts/run_loan_workflow.py'
```

---

## Running from the terminal

### Step 1 — Prepare the fields file
```zsh
cd ~/path/to/agentic-workspace
cp work/loan-agreements/active/fields_example.json \
   work/loan-agreements/active/fields_COMPANY.json
```

Edit `fields_COMPANY.json`. Required fields:

| Field | Example |
|:---|:---|
| BORROWER_NAME | Institute of Photonics |
| BORROWER_ADDRESS | Main Street 1, 12345 City, Country |
| BORROWER_DELIVERY_ADDRESS | (delivery address: ...) — optional |
| COMPANY_CONTACT | Jane Smith, jane@yourcompany.com, Market Development Manager |
| BORROWER_CONTACT | Dr. Lee, lee@institute.org, Application Scientist |
| ARTICLE_DESIGNATION | Product Model Name |
| SERIAL_NUMBER | SN-XXXX-XX |
| VALUE_CHF | 100'000 |
| REMARKS | — |
| TOTAL_VALUE_CHF | 100'000 |
| START_DATE | 2026-07-01 |
| END_DATE | 2026-12-31 |
| AGREEMENT_DATE | 1 July 2026 |
| BORROWER_PLACE_DATE | City, 1 July 2026 |
| COMPANY_SIGNING_CITY | Your City |
| COMPANY_SIGNER_NAME | Jane Smith |
| COMPANY_SIGNER_TITLE | Market Development Manager |
| BORROWER_SIGNER_NAME | Dr. Lee |
| BORROWER_SIGNER_TITLE | Director |
| CUSTOMER_EMAIL | lee@institute.org — for Confluence page |
| CUSTOMER_COUNTRY | Country — for Confluence page |
| CUSTOMER_ORGANIZATION | Department — for Confluence page |
| LOAN_REASON | One sentence — for Confluence page |

---

### Single command (recommended)
Runs all three steps: Word fill → Confluence page → email draft via Ollama.
```zsh
fill-loan \
  --company "InstituteName" \
  --type standard \
  --fields work/loan-agreements/active/fields_COMPANY.json \
  --recipient "First Last" \
  --recipient-email contact@institute.org
```

Flags:
| Flag | Purpose |
|:---|:---|
| `--skip-confluence` | Skip page creation (renewals where page exists) |
| `--skip-email` | Skip email draft |
| `--dry-run` | Preview Confluence page without creating it |
| `--model phi4:latest` | Override Ollama model for email |

After running: open the Word file, review. Edit custom clauses manually in Word if needed. Save company-specific variants to `templates/loan_agreement_COMPANY.docx` for future renewals.

---

## File locations
```
work/
├── agents/
│   └── loan_agent.txt          ← field collection rules + email guidelines
└── workflows/loan-agreements/
    ├── workflow.md              ← this file
    ├── templates/               ← Word templates (gitignored — never pushed)
    ├── active/                  ← in-progress agreements + fields JSON (gitignored)
    └── archive/                 ← signed/completed agreements (gitignored)

scripts/
├── fill_loan_agreement.py      ← fills the Word template
├── create_loan_page.py         ← creates the Confluence tracking page
└── run_loan_workflow.py        ← orchestrator: runs all three steps
```

## Confidentiality
Templates, filled agreements, and fields files are gitignored. They never leave the laptop.
AI (Ollama) only touches email drafting — never the agreement text.
For customers with an NDA in place, use `--local` flag on email scripts.
