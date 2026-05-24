# Stitched Stage A Handoff Report

## Summary

v63 runs the first single-script diagnostic staged evaluation that executes the
v62 Stage A qdot-limited tracker and then the v60 slowed low-gain Stage B
handoff policy under one explicit timing and acceptance policy.

The formal run is:

- `runs/stitched_stage_a_handoff_eval/20260524T152807`
- command: `scripts/evaluate_stitched_stage_a_handoff.py`
- code commit: `748c4d46730d6f7044c8056fb6babc6c0804f1d2`

The stitched gate passes: Stage A tracking passes, and Stage B handoff reports
`4 / 4` E1-E4 passes.

## Metrics

From `runs/stitched_stage_a_handoff_eval/20260524T152807/metrics.yaml`:

- stitched gate pass: `true`
- Stage A gate pass: `true`
- Stage B handoff pass count: `4 / 4`
- Stage A duration: `15.0 s`
- Stage B duration per trajectory: `2.0 s`
- Stage A max qdot: `0.14332635022814824 rad/s`
- Stage A qdot saturation fraction: `0.0`
- Stage A final tracking error norm: `0.0 rad`
- Stage A target contact present fraction: `1.0`
- Stage A max force error: `0.13962429878283 N`

Stage B target-pair gate summary:

| trajectory | pass | force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `true` | `2.9518820398761747e-05` | `1.861383876553019e-08` | `0.07241130795799401` | `0.0` | `1.0` |
| `e2-figure-eight` | `true` | `0.003461025015189971` | `1.2123675244811085e-06` | `0.07314538284753326` | `0.0` | `1.0` |
| `e3-circle` | `true` | `2.950975921846677e-05` | `6.28103669350004e-08` | `0.07241138231384438` | `0.0` | `1.0` |
| `e4-cardioid` | `true` | `2.9512246949807698e-05` | `1.8613358680752423e-08` | `0.07241185573280741` | `0.0` | `1.0` |

## Claim Boundary

This is the first connected diagnostic-label staged simulation evidence line
for the selected UR10e target.

It is still not:

- strict paper-equivalent feasibility
- a proof that the strict setup label is achievable
- a robustness claim under contact/model perturbations
- hardware readiness

The Stage A policy is a qdot-limited joint replay of the v61 optimized path.
The Stage B policy uses the v60 slowed low-gain handoff settings:
`paper_time_scale = 0.01`, `force_gain = 1e-4`, and `orientation_kp = 0.0`.

## Next Step

Run a sensitivity audit around the v63 stitched policy before treating it as
more than a nominal diagnostic simulation pass. Keep strict paper-equivalent
setup, the v38 relaxed trajectory-after-setup label, and this v63 diagnostic
staged label separate.
