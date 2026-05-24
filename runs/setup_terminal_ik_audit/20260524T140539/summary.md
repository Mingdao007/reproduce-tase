# Setup Terminal IK Audit Summary

Run root: `/home/andy/reproduce-tase/runs/setup_terminal_ik_audit/20260524T140539`

## Result

- Candidate count: `65`
- Terminal setup pass count: `0`
- Initial orientation error: `0.17453292523412012`
- Initial x/y error: `0.0`
- Initial force error: `3.2605029787191597e-12`
- Best seed: `random_006`
- Best pass: `False`
- Best failed criteria: `tangential_error_m;orientation_error_rad`
- Best max gate ratio: `2.413534417888994`
- Best force error N: `0.0050975519688662985`
- Best x/y error m: `0.0030075788240061675`
- Best orientation error rad: `0.07240603253666981`

## Limits

This probe optimizes only terminal state. It does not prove that a path
exists under the Stage A velocity law, and it is not a global infeasibility
proof.
