---
name: adr
description: Records an architecture decision as docs/adr/NNNN-title.md. Use when a decision touches bounded contexts, service extraction, data stores, cloud services, dependencies or security controls, or when the user says "record this decision" or runs /adr.
---
1. Read docs/adr/ to find the highest number; the new ADR is that number + 1, zero-padded to four digits. Create docs/adr/ if missing and start at 0001.
2. Derive a kebab-case title of at most 6 words from the decision.
3. Fill [template.md](template.md). Write Context and Decision from what was actually discussed; never invent alternatives that were not considered — write "None recorded" instead.
4. Status is `Proposed` unless the user said it is decided, then `Accepted`. If it replaces an older ADR, set the old one's status to `Superseded by NNNN` and link both ways.
5. Keep it under one page. Return the path and a one-line summary.
