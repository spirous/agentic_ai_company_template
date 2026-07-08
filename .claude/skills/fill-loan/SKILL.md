---
name: fill-loan
description: Prepare an equipment loan agreement. Use when asked to run fill-loan "Company" --type [standard|ds] or to prepare/draft a loan agreement.
---

# Fill Loan — Field Collection → Loan Agreement Package

## Steps

1. Read `./agents/loan_agent.txt`
2. Collect fields in groups (agreement + Confluence page, signatories, internal tracking) — one group at a time
3. Once confirmed, output a ready-to-use `fields_COMPANY.json` and the terminal command to run
4. If customer has comments: assess change type (field / clause / clarification) — never modify legal clauses directly
5. Once agreed: draft DocuSign notification email, remind user to trigger DocuSign manually

## Terminal command

Runs entirely locally (Word fill + Confluence page + email draft via Ollama):

```
fill-loan --company "Company" --type standard --fields work/loan-agreements/active/fields_COMPANY.json --recipient "First Last" --recipient-email contact@company.com
```

Flags: `--skip-confluence` (renewal, page exists), `--skip-email`, `--dry-run` (Confluence preview)

Type `ds` = your company handles shipping both ways.
