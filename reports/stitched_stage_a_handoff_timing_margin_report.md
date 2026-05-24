# Stitched Stage A Handoff Timing Margin Report

## Summary

v65 narrows the timing and qdot failures exposed by v64. It reuses the v63
stitched diagnostic Stage A tracker plus Stage B handoff evaluator and runs a
targeted `timing-margin` case set.

The formal run is:

- `runs/stitched_stage_a_handoff_timing_margin/20260524T162005`
- command:
  `scripts/audit_stitched_stage_a_handoff_sensitivity.py --case-set timing-margin`
- code commit: `c071469132a2d39336f9e8727f51fed88d5334a1`

The stitched gate passes `4 / 7` cases. This recovers the qdot/timing side of
the v64 failures under explicit margins, but it does not address the 1 mm
base-z/contact perturbation failures.

## Metrics

From
`runs/stitched_stage_a_handoff_timing_margin/20260524T162005/metrics.yaml`:

- stitched pass count: `4 / 7`
- passing cases: `nominal`, `stage_a_14p5_recovery`,
  `qdot012_stage_a_18p0_recovery`, `paper_time_scale_0p012_recovery`
- failing cases: `stage_a_14s_reference_fail`,
  `qdot012_stage_a_17p5_reference_fail`,
  `paper_time_scale_0p0125_reference_fail`
- stitched pass fraction: `0.5714285714285714`
- all cases passed: `false`

| case | pass | Stage A pass | Stage B pass | key result |
| --- | --- | --- | ---: | --- |
| `nominal` | `true` | `true` | `4 / 4` | Reproduces the v63/v64 nominal stitched pass. |
| `stage_a_14s_reference_fail` | `false` | `false` | `0 / 4` | Stage A clips at `0.15 rad/s`; terminal force error is `2.03704061425341 N`. |
| `stage_a_14p5_recovery` | `true` | `true` | `4 / 4` | Stage A passes at `14.5 s` with max qdot `0.14826863816707989 rad/s`. |
| `qdot012_stage_a_17p5_reference_fail` | `false` | `false` | `0 / 4` | `0.12 rad/s` with `17.5 s` still misses the terminal force gate. |
| `qdot012_stage_a_18p0_recovery` | `true` | `true` | `4 / 4` | `0.12 rad/s` recovers at `18.0 s`; max qdot is `0.1194386251900526 rad/s`. |
| `paper_time_scale_0p012_recovery` | `true` | `true` | `4 / 4` | Stage B passes at `paper_time_scale = 0.012`. |
| `paper_time_scale_0p0125_reference_fail` | `false` | `true` | `3 / 4` | Stage B fails one row; worst qdot saturation fraction is `0.114`. |

## Claim Boundary

This is diagnostic-label simulation timing-margin evidence only. It is not:

- strict paper-equivalent feasibility
- a full robustness claim
- recovery of the v64 1 mm base-z/contact failures
- evidence that the MuJoCo contact model is hardware-calibrated
- authorization to move, configure, or write settings on the real UR10e

The result says the current stitched diagnostic policy has limited timing
margin: Stage A needs at least about `14.5 s` under the `0.15 rad/s` qdot
limit, about `18.0 s` under a `0.12 rad/s` limit, and Stage B remains passing
up to `paper_time_scale = 0.012` but not `0.0125` in this case set.

## Next Step

The remaining v64 failure class is base-z/contact perturbation. The next
branch should test perturbation-aware Stage A path reoptimization for
`base_z_minus_1mm` and `base_z_plus_1mm`, while keeping strict
paper-equivalent setup, v38 relaxed trajectory-after-setup, and v63-v65
diagnostic labels separate.
