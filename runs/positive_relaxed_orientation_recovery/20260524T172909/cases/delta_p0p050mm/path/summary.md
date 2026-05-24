# Stage A Contact Path Audit Summary

Run root: `/home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p050mm/path`

- Initial label: `delta_p0p050mm_perturbed_start_contact`
- Selected label: `delta_p0p050mm_perturbed_terminal_target`
- Initial source: `cli_initial_q`
- Target source: `cli_target_q`
- Base-z offset delta m: `5e-05`
- Knot count: `128`
- Path gate pass: `True`
- Terminal diagnostic gate pass: `True`
- Min duration for qdot limit: `14.198707940657611`
- Max qdot at recorded duration: `0.15000000000000002`
- Target contact present fraction: `1.0`
- Max force error: `0.0043113621525501244`
- Max scheduled x/y error: `8.616136842634396e-09`
- Max scheduled orientation error: `7.904355137414299e-07`
- Max force-normal orientation error along path: `0.1805329252341198`
- Terminal force-normal orientation error: `0.08381755908962295`

Interpretation:

- This is an offline quasi-static path through optimized contact-manifold knots.
- It does not prove an online Stage A controller can track the path.
- The terminal target still uses the diagnostic setup label, not the strict paper-equivalent setup label.
