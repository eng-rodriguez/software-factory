---
name: change-scope
description: Keeps implementation, verification and review findings within the current approved feature or fix. Use when building, testing or reviewing a factory change, especially when checks uncover existing bugs.
---
Use the approved story and brief, or the approved plan for /factory-lite, as the scope. For a standalone task, use the user's request. A finding's severity does not expand that scope.

Classify each bug, failed check or review finding before requesting or making a fix:
- **In scope:** a defect in the requested behavior or a regression introduced by the current change, including regressions outside the edited files. Cite the acceptance criterion, plan item or causal link to the diff.
- **Unrelated:** an existing defect, cleanup or improvement that the current task neither requires fixing nor introduces or worsens. Being in a touched file, appearing in a full-suite run or having Critical severity is not enough to make it in scope.
- **Uncertain:** the relationship to the current change is not established. Inspect the diff and existing evidence; where practical, compare the same failing check against the pre-change baseline without disturbing the working tree. Do not label a failure pre-existing without evidence, or repeatedly retry it to infer causality. If still uncertain, report the limitation and pause affected work for a scope decision.

Fix only in-scope defects. Keep unrelated findings in a separate deferred list with location, evidence and impact; do not fix them, create tickets or start a new workstream without an explicit request. A pre-existing defect explicitly targeted by the task is in scope. If another existing defect prevents implementing or verifying the task, report the dependency and request a scope decision instead of silently expanding the work.

Run the required checks and report their actual results, including unrelated failures. Never skip or weaken tests, scanners or quality controls to get green results. Deferred findings do not trigger the factory's fix loop; unresolved verification blockers must remain visible in the handoff.

Review output: separate in-scope findings (Critical / Important / Minor), deferred unrelated findings, and uncertain findings. Include evidence for the scope classification. Base the change verdict on in-scope findings and unresolved verification blockers, while preserving the severity of deferred findings.

Apply [risk, evidence and completion](completion.md) throughout planning, implementation, review and resumption.
