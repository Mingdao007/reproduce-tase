# Stage A Contact Path Audit Summary

Run root: `/home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411/cases/delta_m0p250mm/path`

- Initial label: `delta_m0p250mm_perturbed_start_contact`
- Selected label: `delta_m0p250mm_perturbed_terminal_target`
- Initial source: `cli_initial_q`
- Target source: `cli_target_q`
- Base-z offset delta m: `-0.00025`
- Knot count: `128`
- Path gate pass: `True`
- Terminal diagnostic gate pass: `True`
- Min duration for qdot limit: `14.37320363810477`
- Max qdot at recorded duration: `0.15`
- Target contact present fraction: `1.0`
- Max force error: `0.0007178839857182595`
- Max scheduled x/y error: `8.799284589709732e-09`
- Max scheduled orientation error: `3.7905935059018363e-07`
- Max force-normal orientation error along path: `0.16184318334122877`
- Terminal force-normal orientation error: `0.07297047742214499`

Interpretation:

- This is an offline quasi-static path through optimized contact-manifold knots.
- It does not prove an online Stage A controller can track the path.
- The terminal target still uses the diagnostic setup label, not the strict paper-equivalent setup label.
