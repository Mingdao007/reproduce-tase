# Setup Terminal IK Audit Summary

Run root: `/home/andy/reproduce-tase/runs/setup_terminal_ik_audit/20260524T135619`

## Result

- Candidate count: `65`
- Terminal setup pass count: `0`
- Initial orientation error: `0.17453292523412012`
- Initial x/y error: `0.0`
- Initial force error: `3.3218849893046354e-09`
- Best seed: `initial`
- Best pass: `False`
- Best failed criteria: `tangential_error_m;orientation_error_rad`
- Best max gate ratio: `1.733278048340598`
- Best force error N: `0.004835673570861232`
- Best x/y error m: `0.002178947478445584`
- Best orientation error rad: `0.05199834145021794`

## Limits

This probe optimizes only terminal state. It does not prove that a path
exists under the Stage A velocity law, and it is not a global infeasibility
proof.
