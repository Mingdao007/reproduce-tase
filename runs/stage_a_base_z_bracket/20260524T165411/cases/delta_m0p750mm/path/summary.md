# Stage A Contact Path Audit Summary

Run root: `/home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411/cases/delta_m0p750mm/path`

- Initial label: `delta_m0p750mm_perturbed_start_contact`
- Selected label: `delta_m0p750mm_perturbed_terminal_target`
- Initial source: `cli_initial_q`
- Target source: `cli_target_q`
- Base-z offset delta m: `-0.00075`
- Knot count: `128`
- Path gate pass: `False`
- Terminal diagnostic gate pass: `True`
- Min duration for qdot limit: `138.0288650739265`
- Max qdot at recorded duration: `0.15`
- Target contact present fraction: `1.0`
- Max force error: `0.001872753597179866`
- Max scheduled x/y error: `0.0028504630410804335`
- Max scheduled orientation error: `0.09627510687282123`
- Max force-normal orientation error along path: `0.15263167414728848`
- Terminal force-normal orientation error: `0.055561410650865485`

Interpretation:

- This is an offline quasi-static path through optimized contact-manifold knots.
- It does not prove an online Stage A controller can track the path.
- The terminal target still uses the diagnostic setup label, not the strict paper-equivalent setup label.
