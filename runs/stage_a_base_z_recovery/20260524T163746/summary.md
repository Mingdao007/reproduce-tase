# Stage A Base-Z Recovery Summary

Run root: `/home/andy/reproduce-tase/runs/stage_a_base_z_recovery/20260524T163746`

- Recovered cases: `1 / 3`
- Start pass cases: `base_z_minus_1mm, base_z_minus_1mm_stage_a_16s_recovery`
- Terminal pass cases: `base_z_minus_1mm, base_z_minus_1mm_stage_a_16s_recovery`
- Path pass cases: `base_z_minus_1mm_stage_a_16s_recovery`
- Stitched pass cases: `base_z_minus_1mm_stage_a_16s_recovery`
- Unresolved cases: `base_z_minus_1mm, base_z_plus_1mm`

| case | status | Stage A duration s | start pass | terminal pass count | path pass | stitched pass | terminal orientation err rad | path min duration s | Stage B pass |
| --- | --- | ---: | --- | ---: | --- | --- | ---: | ---: | ---: |
| `base_z_minus_1mm` | `path_gate_failed` | `15.0` | `True` | `25` | `False` | `False` | `0.047179212704768526` | `15.652271522331025` | `0/4` |
| `base_z_minus_1mm_stage_a_16s_recovery` | `recovered` | `16.0` | `True` | `25` | `True` | `True` | `0.047179212704768526` | `15.652271522331025` | `4/4` |
| `base_z_plus_1mm` | `start_and_terminal_not_found` | `15.0` | `False` | `0` | `None` | `None` | `0.11948560786548146` | `None` | `None` |

Interpretation:

- This audit tests perturbation-aware terminal target search and path reoptimization for the v64 1 mm base-z failures.
- A recovered case requires a passing rebalanced start contact, passing terminal target, passing qdot-limited path gate at the listed Stage A duration, and passing stitched Stage A plus Stage B handoff.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility, a robustness proof, or hardware readiness.
