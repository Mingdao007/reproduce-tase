# Stage A Contact Path Audit Summary

Run root: `/home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p100mm/path`

- Initial label: `delta_p0p100mm_perturbed_start_contact`
- Selected label: `delta_p0p100mm_perturbed_terminal_target`
- Initial source: `cli_initial_q`
- Target source: `cli_target_q`
- Base-z offset delta m: `0.0001`
- Knot count: `128`
- Path gate pass: `True`
- Terminal diagnostic gate pass: `True`
- Min duration for qdot limit: `14.206784149197896`
- Max qdot at recorded duration: `0.15`
- Target contact present fraction: `1.0`
- Max force error: `0.020717782163206522`
- Max scheduled x/y error: `8.578111377044505e-09`
- Max scheduled orientation error: `7.793344015033563e-07`
- Max force-normal orientation error along path: `0.18203292523411982`
- Terminal force-normal orientation error: `0.08565245135289722`

Interpretation:

- This is an offline quasi-static path through optimized contact-manifold knots.
- It does not prove an online Stage A controller can track the path.
- The terminal target still uses the diagnostic setup label, not the strict paper-equivalent setup label.
