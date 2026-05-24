# Stage A Base-Z Recovery Report

## Summary

v66 tests perturbation-aware Stage A endpoint and path recovery for the v64
1 mm base-z/contact failures. The audit rebalances the Stage A start contact,
searches for a perturbed diagnostic terminal target, reoptimizes the contact
path, and then runs the stitched Stage A plus Stage B handoff when a path is
available.

The formal run is:

- `runs/stage_a_base_z_recovery/20260524T163746`
- command: `scripts/audit_stage_a_base_z_recovery.py`
- run-time base commit: `a50628bb7351b12d59320e69ec85bce0acca1e96`

The recovery audit passes `1 / 3` cases. It recovers the `-1 mm` perturbation
only when Stage A is extended to `16.0 s`; the exact `15.0 s` reference still
misses the qdot budget, and the `+1 mm` side still has no passing start plus
terminal target pair under this diagnostic search.

## Metrics

From `runs/stage_a_base_z_recovery/20260524T163746/metrics.yaml`:

- recovered cases: `1 / 3`
- recovered case: `base_z_minus_1mm_stage_a_16s_recovery`
- unresolved cases: `base_z_minus_1mm`, `base_z_plus_1mm`
- start pass cases: `base_z_minus_1mm`,
  `base_z_minus_1mm_stage_a_16s_recovery`
- terminal pass cases: `base_z_minus_1mm`,
  `base_z_minus_1mm_stage_a_16s_recovery`
- path pass cases: `base_z_minus_1mm_stage_a_16s_recovery`
- stitched pass cases: `base_z_minus_1mm_stage_a_16s_recovery`

| case | status | Stage A duration | path pass | stitched pass | key result |
| --- | --- | ---: | --- | --- | --- |
| `base_z_minus_1mm` | `path_gate_failed` | `15.0 s` | `false` | `false` | Rebalanced start and terminal target pass, but the reoptimized path needs `15.652271522331025 s` at `0.15 rad/s`; the 15 s replay clips. |
| `base_z_minus_1mm_stage_a_16s_recovery` | `recovered` | `16.0 s` | `true` | `true` | The same reoptimized path passes with max Stage A qdot `0.14674004552188208 rad/s` and Stage B `4 / 4`. |
| `base_z_plus_1mm` | `start_and_terminal_not_found` | `15.0 s` | `none` | `none` | The start rebalance does not find target contact from the nominal start, and terminal search finds `0` passes; best terminal orientation error is `0.11948560786548146 rad` versus the `0.08 rad` gate. |

## Claim Boundary

This is diagnostic-label simulation evidence only. It is not:

- strict paper-equivalent feasibility
- a full robustness claim
- evidence that the contact model is hardware-calibrated
- hardware readiness or authorization to move/configure the real UR10e

The useful claim is narrow: a perturbation-aware rebalanced endpoint plus
reoptimized path can recover the `-1 mm` base-z case if Stage A has `16.0 s`.
The original `15.0 s` `base_z_minus_1mm` sensitivity case remains failing, and
the `+1 mm` perturbation remains unresolved under this diagnostic search.

## Next Step

Focus the next branch on the unresolved `+1 mm` base-z/contact side and the
remaining exact `15.0 s` `-1 mm` boundary. Useful next audits are a broader
or contact-aware `+1 mm` terminal/start search, a smaller base-z perturbation
bracket, or a contact-model calibration check before treating this as
robustness evidence.
