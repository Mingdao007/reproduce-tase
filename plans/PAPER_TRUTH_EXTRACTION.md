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
- Future: `reports/paper_truth_extraction.md`

## Commands To Run

```bash
pdftotext "<paper-pdf>" /tmp/tase_paper.txt
rg -n "finite|force|constraint|MIAE|Experiment|Fig" /tmp/tase_paper.txt
```

## Expected Outputs

- A table mapping every controller equation to PDF section/equation number.
- Section V parameters with PDF evidence.
- Section VI experiment trajectories, surfaces, target forces, duration, and
  metrics with PDF evidence.
- All `pending_pdf_verify` fields either resolved or explicitly retained.

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
- Some values may only appear in figures and require manual inspection.

## Next Executable Step

Extract text from the PDF and write `reports/paper_truth_extraction.md`.

