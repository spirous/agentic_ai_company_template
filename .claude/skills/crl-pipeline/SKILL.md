---
name: crl-pipeline
description: KTH CRL pipeline assessment and account updates. Use for crl-pipeline "Initiative" (full review), crl-update "Company" --crl [n] (single account), or crl-update "Company" --bottleneck "text".
---

# CRL Pipeline — Contact Files → Account CRL Assessment

## Steps

1. Read `./agents/crl_pipeline_agent.txt`
2. Read relevant contact files in `./knowledge/contacts/` — look for `## Pipeline Status` sections
3. For `crl-pipeline "Initiative"`: assess all accounts linked to the initiative against CRL 3–7 criteria, output structured account review, propose updated Pipeline Status blocks and HTML dashboard DATA/HOLDING arrays
4. For `crl-update "Company" --crl [n]`: assess the single account, output updated CRL block, propose contact file Pipeline Status update
5. For `crl-update "Company" --bottleneck "text"`: update bottleneck text only in the contact file

## Rules

- **Channel vs demand:** CRL levels are assessed for channel accounts (the companies that can issue you a purchase order — files with a `## Pipeline Status` block) only. End users (files with a `## Demand Signal` block) are never given CRL rows; read them as evidence for initiative-level CRL and for the linked channel account's assessment
- Never assign a CRL level without citing a specific observable fact from notes or the contact file
- Propose contact file updates after every review — user confirms before saving
- After `push-notes` completes for any initiative account: check if the meeting content warrants a CRL level change and add a one-sentence CRL check note at the end of the output
