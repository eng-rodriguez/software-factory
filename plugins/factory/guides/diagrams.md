# Diagrams in briefs and closing notes

Include a Mermaid diagram when it makes a process, interaction, relationship or lifecycle easier to understand than prose alone. Choose the smallest useful view; never include every type by default. A simple fix or wording change may need no diagram. Omit an empty diagram section rather than filling a quota.

Use the official [Mermaid introduction and Diagram Syntax](https://mermaid.js.org/intro/) as the reference. Select by the question the reader needs answered:

| Question | Diagram |
| --- | --- |
| What happens, and where does the path branch? | Flowchart (`flowchart`) |
| Who owns each step or handoff? | Swimlane; use flowchart subgraphs for broad renderer compatibility |
| Which participants exchange messages, and in what order? | Sequence (`sequenceDiagram`) |
| Which domain types collaborate or inherit behavior? | Class (`classDiagram`), only relevant relationships |
| Which states and transitions are allowed? | State (`stateDiagram-v2`) |
| How are persisted entities related, including cardinality? | Entity relationship (`erDiagram`) |
| What does the person experience across the task? | User journey (`journey`); do not invent satisfaction scores |

Native [swimlane syntax](https://mermaid.js.org/syntax/swimlanes.html) uses `swimlane-beta` and requires Mermaid 11.16.0 or later. Use it only when the destination renderer supports it; otherwise use a flowchart with labeled subgraphs. Renderer support, not the latest Mermaid website version, determines usable syntax.

For a **technical brief**, place each diagram beside the section it explains (domain model, API, data, frontend, or infrastructure). Show the proposed behavior and meaningful boundaries/error paths. Distinguish current behavior from proposed behavior, and mark unresolved design assumptions. Avoid duplicating the same view in multiple diagram types.

For **closing notes**, prefer one small flowchart, swimlane or user journey showing the delivered user/business outcome, with plain-language labels. Use a technical diagram only if it helps the intended audience. Derive it from the actual implementation and evidence, not an outdated proposal; distinguish deferred or unshipped behavior. The 250-word prose limit excludes Mermaid source syntax; keep labels and captions concise.

Write fenced `mermaid` blocks, preceded by a descriptive sentence or caption that also explains the takeaway when the renderer cannot display the diagram. Keep identifiers simple, labels readable, arrows meaningful and colors optional. Do not include secrets, personal data or internal endpoints, or upload private diagrams to public rendering services. For journey diagrams without grounded scores, use a flowchart instead.

Check the diagram against the brief/diff and preview with the project's existing renderer when available. Report when rendering was not verified; do not add a rendering dependency solely for a small documentation change. If the destination lacks Mermaid support, preserve the source in the Markdown artifact and provide a short text explanation for copied notes. Keep diagrams synchronized when an approved design changes.
