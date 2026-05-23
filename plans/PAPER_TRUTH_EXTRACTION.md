# Paper Truth Extraction Plan

## Scope

Extract the equations, parameters, assumptions, trajectories, metrics, and
experiment matrix from the TASE finite-time force-motion paper.

## Assumptions

- The PDF path is:
  `/home/andy/Zotero/storage/UZRF97KG/Xu 等 - 2026 - Finite-Time Convergence Neural Network-Based Force-Motion Control for Unknown Surface With Orientati.pdf`
- Existing YAML values marked `pending_pdf_verify` are provisional.
- Local MATLAB/RNN scripts are references only, not truth.

## Exact Files Touched

- `configs/paper_truth.yaml`
- `plans/PAPER_TRUTH_EXTRACTION.md`
- `reports/DECISION_RECORD.md`
- `reports/paper_truth_extraction.md`
- `reports/ITERATION_LOG.md`
- `reports/math_derivation_ur10e_transfer.md`

## Commands To Run

```bash
pdfinfo "<paper-pdf>"
pdftotext -layout "<paper-pdf>" /tmp/tase_paper_layout.txt
wc -l /tmp/tase_paper_layout.txt
rg -n "finite|force|constraint|MIAE|Experiment|Fig|Md|Bd|epsilon|kp|ko|kf" /tmp/tase_paper_layout.txt
```

## Expected Outputs

- A table mapping every controller equation to PDF section/equation number.
- Section V parameters with PDF evidence.
- Section VI experiment trajectories, surfaces, target forces, duration, and
  metrics with PDF evidence.
- All `pending_pdf_verify` fields either resolved or explicitly retained.
- `configs/paper_truth.yaml` records `reports/paper_truth_extraction.md` as
  the tracked source-of-truth report.

## Pass/Fail Criteria

Pass:

- No parameter is treated as paper truth without a PDF citation.
- Ambiguous orientation signal dimensions are documented.

Fail:

- Existing synthetic configs are used as paper truth.

## Rollback Point Or Recovery Command

Keep edits to `configs/paper_truth.yaml` in one commit. Revert that commit if
PDF extraction is later found wrong.

## Unresolved Risks

- PDF text extraction may mangle equations.
- Eq. (10) appears to apply scalar trigonometric functions to a vector `u`.
- Section V gives a 2D orientation signal, while the orientation law defines a
  3D normalized force vector.
- Section V `z0` remains undefined in extracted text.

## Next Executable Step

Resolve the Section V orientation signal ambiguity before implementing a
paper-faithful desired-orientation generator. The current UR10e
`linear-primary` orientation result must remain labeled as adapted
orientation-hold, not paper orientation compliance.
