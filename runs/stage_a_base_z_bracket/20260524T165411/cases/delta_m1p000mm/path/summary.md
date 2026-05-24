# Stage A Contact Path Audit Summary

Run root: `/home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411/cases/delta_m1p000mm/path`

- Initial label: `delta_m1p000mm_perturbed_start_contact`
- Selected label: `delta_m1p000mm_perturbed_terminal_target`
- Initial source: `cli_initial_q`
- Target source: `cli_target_q`
- Base-z offset delta m: `-0.001`
- Knot count: `128`
- Path gate pass: `True`
- Terminal diagnostic gate pass: `True`
- Min duration for qdot limit: `15.652271522331025`
- Max qdot at recorded duration: `0.15`
- Target contact present fraction: `1.0`
- Max force error: `0.0019615624793152264`
- Max scheduled x/y error: `3.4664923105732207e-07`
- Max scheduled orientation error: `3.6688328675344596e-05`
- Max force-normal orientation error along path: `0.15994043789349663`
- Terminal force-normal orientation error: `0.04717921270476678`

Interpretation:

- This is an offline quasi-static path through optimized contact-manifold knots.
- It does not prove an online Stage A controller can track the path.
- The terminal target still uses the diagnostic setup label, not the strict paper-equivalent setup label.
