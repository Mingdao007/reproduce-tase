# Stage A Contact Path Audit Summary

Run root: `/home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p500mm/path`

- Initial label: `delta_p0p500mm_perturbed_start_contact`
- Selected label: `delta_p0p500mm_perturbed_terminal_target`
- Initial source: `cli_initial_q`
- Target source: `cli_target_q`
- Base-z offset delta m: `0.0005`
- Knot count: `128`
- Path gate pass: `True`
- Terminal diagnostic gate pass: `True`
- Min duration for qdot limit: `11.224745619891337`
- Max qdot at recorded duration: `0.14999999999999997`
- Target contact present fraction: `1.0`
- Max force error: `0.07328844161217152`
- Max scheduled x/y error: `8.597486673110686e-09`
- Max scheduled orientation error: `7.136877402532296e-07`
- Max force-normal orientation error along path: `0.1805329252341198`
- Terminal force-normal orientation error: `0.10056247728509893`

Interpretation:

- This is an offline quasi-static path through optimized contact-manifold knots.
- It does not prove an online Stage A controller can track the path.
- The terminal target still uses the diagnostic setup label, not the strict paper-equivalent setup label.
