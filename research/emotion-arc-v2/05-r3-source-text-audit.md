# R3 targeted source-text audit gate

R3 keeps the existing research architecture and adds an optional trust layer for cases where a QA-PASS canonical row conflicts with the frozen source text.

When `source_text_audit_path` is present, each audit row must identify the research claim, canonical record and field, frozen source repository/commit/path/line range, observed source fact, consistency result, affected research records, required correction, and review status. The validator confirms that these references exist and that any binding to a `CONTRADICTED` canonical field acknowledges the matching audit row.

This gate has intentionally narrow authority:

- It can reject an ambiguous checksum label, a malformed audit row, an unknown canonical field, or an unacknowledged contradicted field.
- It cannot infer whether two co-occurring events are causal, whether a new line has macro-scale organization, or whether narrative dominance transferred.
- It never changes canonical data, grants semantic PASS, or promotes research to production.

The BOOK_001 pilot adds separate data-level regressions for the observed R3 counterexamples: chapter-31 notice versus chapter-32 execution, chapter-34 access denial, partial payoff versus macro closure, and MA2 start versus MA1 contract cancellation.
