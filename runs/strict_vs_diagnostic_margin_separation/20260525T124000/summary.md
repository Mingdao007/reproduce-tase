# Strict vs Diagnostic Margin Separation Audit

Run root: `/home/andy/reproduce-tase/runs/strict_vs_diagnostic_margin_separation/20260525T124000`

- Audit passed: `True`
- Separation complete: `True`
- Diagnostic required normal rotation rad: `0.0005664520369604714`
- Strict orientation increase rad: `0.0335984782867086`
- Strict/diagnostic orientation ratio: `59.31389790209757`
- Minimum uniform multiplier: `2.11994927622362`
- Minimum uniform requires all three scalar gates: `True`
- V85 margin can close strict orientation: `False`
- V85 margin can close strict paper-equivalent goal: `False`
- Completion claim allowed: `False`
- Do not mark goal complete: `True`

## Violations

- None

## Interpretation

The v85 diagnostic margin is a small orientation/contact definition margin for the weighted diagnostic row. It is not large enough to close the v126 strict-terminal orientation gap, and the strict best uniform row also needs force and tangential relaxation. This audit therefore keeps the diagnostic calibration path separate from any strict paper-equivalent feasibility claim.
