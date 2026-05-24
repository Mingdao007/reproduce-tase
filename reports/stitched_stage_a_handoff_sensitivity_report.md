# Stitched Stage A Handoff Sensitivity Report

## Summary

v64 runs a sensitivity audit around the v63 stitched diagnostic Stage A tracker
plus Stage B handoff. It reuses the v63 evaluator and varies small contact,
timing, qdot, and handoff-policy parameters.

The formal run is:

- `runs/stitched_stage_a_handoff_sensitivity/20260524T161111`
- command: `scripts/audit_stitched_stage_a_handoff_sensitivity.py`
- code commit: `1e15d9828145cc30b93c274d77eb99d2206a670f`

The stitched gate passes `4 / 9` cases. This bounds the v63 nominal result:
the policy has some parameter margin, but it is not robust to the audited
contact/model and timing perturbations.

## Metrics

From
`runs/stitched_stage_a_handoff_sensitivity/20260524T161111/metrics.yaml`:

- stitched pass count: `4 / 9`
- passing cases: `nominal`, `stage_a_16s`, `force_gain_5e-5`,
  `force_gain_2e-4`
- failing cases: `base_z_minus_1mm`, `base_z_plus_1mm`, `stage_a_14s`,
  `qdot_limit_0p12`, `paper_time_scale_0p02`
- stitched pass fraction: `0.4444444444444444`
- all cases passed: `false`

| case | pass | Stage A pass | Stage B pass | key result |
| --- | --- | --- | ---: | --- |
| `nominal` | `true` | `true` | `4 / 4` | Reproduces v63. |
| `base_z_minus_1mm` | `false` | `false` | `0 / 4` | Terminal force error rises to `92.55645811468109 N`. |
| `base_z_plus_1mm` | `false` | `false` | `0 / 4` | Target contact is lost in Stage B; force error is `5.0 N`. |
| `stage_a_14s` | `false` | `false` | `0 / 4` | Stage A clips at qdot limit and terminal force error rises to `2.03704061425341 N`. |
| `stage_a_16s` | `true` | `true` | `4 / 4` | Slower Stage A reduces max qdot to `0.1343684533387775 rad/s`. |
| `qdot_limit_0p12` | `false` | `false` | `0 / 4` | Stage A cannot reach the terminal target; terminal force error is `17.084553106115138 N`. |
| `force_gain_5e-5` | `true` | `true` | `4 / 4` | Lower force gain still passes; worst Stage B tail force error is `0.013843278429059795 N`. |
| `force_gain_2e-4` | `true` | `true` | `4 / 4` | Higher force gain still passes; worst Stage B tail force error is `0.000865457999273005 N`. |
| `paper_time_scale_0p02` | `false` | `true` | `3 / 4` | Stage B qdot saturation fails one row; worst qdot saturation is `0.833`. |

## Claim Boundary

This is diagnostic-label simulation sensitivity evidence only. It is not:

- strict paper-equivalent feasibility
- a formal robustness proof
- evidence that the model is calibrated for hardware
- authorization to move, configure, or write settings on the real UR10e

The result strengthens the audit boundary rather than the controller claim:
the nominal v63 stitched pass is fragile to 1 mm contact/base-z perturbations
and to tighter qdot/timing budgets.

## Next Step

Before treating the stitched result as robust, run a perturbation-aware
controller/path audit. The most direct follow-up is to test whether reoptimized
Stage A contact paths or margin-aware timing can recover the base-z/contact and
qdot failures while preserving the strict paper-equivalent, v38 relaxed, and
v63/v64 diagnostic labels as separate claims.
