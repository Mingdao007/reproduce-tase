# Normal Guard Force-Motion Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v9-normal-guard-force-motion`

Run root:

`runs/normal_guard_force_motion/20260524T015341`

## Scope

This iteration adds a normal-force guard to the simulation-only force-motion
controller. When measured normal force drops below a threshold, the guard
scales the commanded planar x/y velocity:

```text
scale = clamp(force / (force_target * guard_fraction), min_scale, 1)
v_xy_guarded = scale * v_xy_command
```

The intent was to see whether reducing planar motion during low-force periods
could recover full-speed E2/E3 contact with less planar tracking error than the
v8 high normal-axis weighting.

## Tests

Verification command:

```bash
scripts/run_tests.sh
```

Result:

`28 passed`

## E2/E3 Guard Probes

Common settings:

- `--paper-time-scale 1.0`
- `--qdot-limit-rad-s 0.15`
- `--force-gain 5e-4`
- `--normal-guard-force-fraction 0.9`
- `--normal-guard-min-planar-scale 0.0`

| run | tail force error N | final force N | contact present | max position error m | mean position error m | min planar scale | tail mean scale |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E2 guard, equal axes | `4.907864338977237` | `0.0` | `0.89775` | `0.013725477778366387` | `0.004350430058271426` | `0.0` | `0.02047459133839171` |
| E3 guard, equal axes | `4.892864056573585` | `0.36041026524685116` | `0.75125` | `0.01318649928311497` | `0.004034573083892085` | `0.0` | `0.023807987428092193` |
| E2 guard, normal weight 20 | `2.4967580284410574` | `2.3863678498474674` | `1.0` | `0.0167935207502178` | `0.0062509539062278645` | `0.5301560217794372` | `0.556275993679765` |
| E3 guard, normal weight 20 | `1.5423792188330292` | `3.3152350513403873` | `1.0` | `0.014275596924317675` | `0.005522222053855301` | `0.7367189002978639` | `0.7683912847037715` |
| E2 guard, normal weight 50 | `0.5085483615637729` | `4.439603842736771` | `1.0` | `0.020166709027307318` | `0.00816042767750598` | `0.9864334747591575` | `0.9957724594183881` |
| E3 guard, normal weight 50 | `0.14769228903285758` | `4.822471085318497` | `1.0` | `0.015963081975681002` | `0.0063193933682347695` | `1.0` | `1.0` |

## Guarded E1-E4 Matrix

The complete guarded matrix used `normal_axis_weight = 50`:

| trajectory | tail force error N | final force N | contact present | max position error m | mean position error m | min planar scale | max qdot rad/s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 cycloid | `0.00033856499675277707` | `5.000215125388599` | `1.0` | `1.9594057514147845e-06` | `9.432197376772552e-07` | `1.0` | `0.149999999999919` |
| E2 figure-eight | `0.5085483615637729` | `4.439603842736771` | `1.0` | `0.020166709027307318` | `0.00816042767750598` | `0.9864334747591575` | `0.14999999999999997` |
| E3 circle | `0.14769228903285758` | `4.822471085318497` | `1.0` | `0.015963081975681002` | `0.0063193933682347695` | `1.0` | `0.14999999999999997` |
| E4 cardioid | `0.008334236881239064` | `4.980330996105661` | `1.0` | `0.0016131684506960832` | `0.00010380657698883623` | `1.0` | `0.14999999999999997` |

## Interpretation

The guard by itself does not solve the full-speed E2/E3 problem. With equal
axis weights it suppresses planar motion aggressively but still loses force.
With moderate normal-axis weighting it preserves contact, but force regulation
and planar tracking still trade off. At `normal_axis_weight = 50`, the guard is
mostly inactive on E2/E3, so the result behaves like another weighted blend
rather than a real task-priority controller.

The v9 conclusion is negative but useful: scalar planar speed guarding is not
enough. The next controller needs a solver-level task hierarchy or explicit
slack variables so the system can quantify and allocate normal-force and
planar-tracking residuals rather than tuning a single blend.

## Limitations

- This is simulation-only; no real UR10e motion or hardware writes were
  performed.
- The guard is heuristic and does not represent the paper's impedance or
  orientation-compliance controller.
- Full-speed E2/E3 remain unreproduced because planar tracking error is still
  centimeter-scale.
- qdot saturation remains active in guarded weighted runs.

## Next Step

Implement and test a slack-aware velocity solve that reports normal residual
and planar residual separately. A practical next branch should add explicit
task residual metrics before attempting more tuning.
