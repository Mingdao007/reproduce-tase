# Phase1 Row-Quality Guard Audit

Run id: `20260525T120000`

Audit passed: `True`
Guard complete: `True`
Case count: `5`
Rejected cases: `5`
Scaffold-preserved cases: `5`
Approved evidence created in dry runs: `0`
Repository evidence run created: `False`
Guard authorizes execution: `False`
Completion claim allowed: `False`
Do not mark goal complete: `True`

Rejection cases:

| Case | Rejected | Scaffold preserved | Expected stderr |
| --- | ---: | ---: | --- |
| `placeholder_datum` | `True` | `True` | `datum must be non-empty and not a placeholder` |
| `invalid_tool_axis_sign` | `True` | `True` | `tool_axis_sign must be one of` |
| `nonnumeric_distance` | `True` | `True` | `distance_mm is not numeric` |
| `nonpositive_resolution` | `True` | `True` | `resolution_mm must be finite and positive` |
| `placeholder_row_operator` | `True` | `True` | `operator must be non-empty and not a placeholder` |

Violations:

- None

Interpretation:

The phase1 finalizer rejects malformed TCP/contact measurement rows before approved evidence can be written. No repository evidence run is created, and this audit authorizes no live access or execution.
