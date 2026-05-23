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
- `reports/orientation_signal_ambiguity_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/math_derivation_ur10e_transfer.md`

## Commands To Run

```bash
pdfinfo "<paper-pdf>"
pdftotext -layout "<paper-pdf>" /tmp/tase_paper_layout.txt
wc -l /tmp/tase_paper_layout.txt
rg -n "finite|force|constraint|MIAE|Experiment|Fig|Md|Bd|epsilon|kp|ko|kf" /tmp/tase_paper_layout.txt
pdftotext -raw "<paper-pdf>" /tmp/tase_paper_raw.txt
pdftotext -fixed 3 "<paper-pdf>" /tmp/tase_paper_fixed3.txt
pdftohtml -xml -f 3 -l 4 -stdout "<paper-pdf>" > /tmp/tase_paper_p3_4.xml
pdftohtml -xml -f 5 -l 8 -stdout "<paper-pdf>" > /tmp/tase_paper_p5_8.xml
```

## Expected Outputs

- A table mapping every controller equation to PDF section/equation number.
- Section V parameters with PDF evidence.
- Section VI experiment trajectories, surfaces, target forces, duration, and
  metrics with PDF evidence.
- All `pending_pdf_verify` fields either resolved or explicitly retained.
- `configs/paper_truth.yaml` records `reports/paper_truth_extraction.md` as
  the tracked source-of-truth report.
- Section V orientation mismatch is either resolved from the PDF or recorded
  as a known paper ambiguity with evidence from multiple extraction modes.

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
  3D normalized force vector. V20 confirms this as a paper ambiguity rather
  than a hidden extraction omission.
- Section V `z0` remains undefined in extracted text.

## Next Executable Step

Implement paper-orientation work from the Section III 3D force-normal contract,
`u = F / ||F||`, not from an inferred Section V third component. Keep any
Section V 2D orientation schedule as an explicitly adapted option with its own
decision record and gates. The remaining PDF-truth extraction item is the
Section V `z0` source.
