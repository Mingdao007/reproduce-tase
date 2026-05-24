# Stage A Contact Path Audit Summary

Run root: `/home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p750mm/path`

- Initial label: `delta_p0p750mm_perturbed_start_contact`
- Selected label: `delta_p0p750mm_perturbed_terminal_target`
- Initial source: `cli_initial_q`
- Target source: `cli_target_q`
- Base-z offset delta m: `0.00075`
- Knot count: `128`
- Path gate pass: `True`
- Terminal diagnostic gate pass: `True`
- Min duration for qdot limit: `10.367805178961204`
- Max qdot at recorded duration: `0.14999999999999997`
- Target contact present fraction: `1.0`
- Max force error: `0.07998720741366228`
- Max scheduled x/y error: `8.559649885854467e-09`
- Max scheduled orientation error: `6.669912255442434e-07`
- Max force-normal orientation error along path: `0.1805329252341198`
- Terminal force-normal orientation error: `0.11002164736335086`

Interpretation:

- This is an offline quasi-static path through optimized contact-manifold knots.
- It does not prove an online Stage A controller can track the path.
- The terminal target still uses the diagnostic setup label, not the strict paper-equivalent setup label.
