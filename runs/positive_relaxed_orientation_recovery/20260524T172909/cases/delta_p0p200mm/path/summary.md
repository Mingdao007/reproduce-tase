# Stage A Contact Path Audit Summary

Run root: `/home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p200mm/path`

- Initial label: `delta_p0p200mm_perturbed_start_contact`
- Selected label: `delta_p0p200mm_perturbed_terminal_target`
- Initial source: `cli_initial_q`
- Target source: `cli_target_q`
- Base-z offset delta m: `0.0002`
- Knot count: `128`
- Path gate pass: `True`
- Terminal diagnostic gate pass: `True`
- Min duration for qdot limit: `14.424277184724716`
- Max qdot at recorded duration: `0.15`
- Target contact present fraction: `1.0`
- Max force error: `0.04426348783838385`
- Max scheduled x/y error: `8.453936625406201e-09`
- Max scheduled orientation error: `7.534150528050841e-07`
- Max force-normal orientation error along path: `0.1890329252341192`
- Terminal force-normal orientation error: `0.08934348318237903`

Interpretation:

- This is an offline quasi-static path through optimized contact-manifold knots.
- It does not prove an online Stage A controller can track the path.
- The terminal target still uses the diagnostic setup label, not the strict paper-equivalent setup label.
