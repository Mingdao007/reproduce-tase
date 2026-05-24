# Stage A Contact Path Audit Summary

Run root: `/home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411/cases/delta_m0p500mm/path`

- Initial label: `delta_m0p500mm_perturbed_start_contact`
- Selected label: `delta_m0p500mm_perturbed_terminal_target`
- Initial source: `cli_initial_q`
- Target source: `cli_target_q`
- Base-z offset delta m: `-0.0005`
- Knot count: `128`
- Path gate pass: `True`
- Terminal diagnostic gate pass: `True`
- Min duration for qdot limit: `14.625580232388335`
- Max qdot at recorded duration: `0.15`
- Target contact present fraction: `1.0`
- Max force error: `0.0006070100497499453`
- Max scheduled x/y error: `0.00021607905641326118`
- Max scheduled orientation error: `0.011580746036452625`
- Max force-normal orientation error along path: `0.15053331358836075`
- Terminal force-normal orientation error: `0.06415852510723169`

Interpretation:

- This is an offline quasi-static path through optimized contact-manifold knots.
- It does not prove an online Stage A controller can track the path.
- The terminal target still uses the diagnostic setup label, not the strict paper-equivalent setup label.
