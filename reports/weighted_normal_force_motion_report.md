# Weighted Normal Force-Motion Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v8-normal-weighted-force-motion`

Run root:

`runs/weighted_normal_force_motion/20260524T014811`

## Scope

This iteration investigates the v7 full-speed E2/E3 contact-loss blocker by
adding axis weights to the Cartesian velocity solve. The controller remains
simulation-only and velocity-level, but the z/normal velocity row can now be
weighted above planar x/y tracking:

```text
minimize ||W_axis (Jp qdot - v_cmd)||^2 + damping ||qdot||^2
subject to qdot and one-step joint bounds
```

The objective is diagnostic: determine whether prioritizing normal motion can
recover full-speed contact in the approximate MuJoCo UR10e setup, and quantify
the resulting planar tracking tradeoff.

## Baseline Failure From V7

The v7 full-speed matrix with `--qdot-limit-rad-s 0.15` and equal axis weights
lost contact on E2 and E3:

| trajectory | tail mean abs force error N | contact present | max position error m | max qdot rad/s |
| --- | ---: | ---: | ---: | ---: |
| E2 figure-eight | `5.0` | `0.424` | `8.944233779332086e-06` | `0.06257171191905564` |
| E3 circle | `5.0` | `0.426` | `2.2364375253766477e-05` | `0.11746291997870727` |

Trace inspection showed that after contact loss the force command asked for
negative z velocity, but the equal-weight solve still produced positive actual
z velocity because the coupled Jacobian favored planar tracking.

## Weighted Probes

Intermediate probes with `axis_weights = [1, 1, 20]` improved contact duration
but still lost contact:

| trajectory | tail mean abs force error N | contact present | max position error m | max qdot rad/s |
| --- | ---: | ---: | ---: | ---: |
| E2 figure-eight, w20 | `5.0` | `0.53075` | `0.003673424956038479` | `0.14999999999999997` |
| E3 circle, w20 | `5.0` | `0.5295` | `0.0058611930422428` | `0.14999999999999997` |

The accepted v8 diagnostic matrix uses:

- `--qdot-limit-rad-s 0.15`
- `--normal-axis-weight 100`
- `--planar-axis-weight 1`
- `--force-gain 5e-4`
- `--paper-time-scale 1.0`

| trajectory | tail mean abs force error N | final force N | contact present | max position error m | mean position error m | max qdot rad/s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 cycloid | `0.00033862693701109726` | `5.000215380160267` | `1.0` | `1.9594095253937445e-06` | `9.432204451630211e-07` | `0.14999999924398735` |
| E2 figure-eight | `0.04680027821015285` | `4.946972301289366` | `1.0` | `0.02114519099848796` | `0.008577241949811257` | `0.14999999999999997` |
| E3 circle | `0.013411903132922096` | `4.984705437530245` | `1.0` | `0.016169767707432416` | `0.006388867383313256` | `0.14999999999999997` |
| E4 cardioid | `0.0015612634092028888` | `4.996629228907928` | `1.0` | `0.0016367063021719241` | `0.00010570007247865235` | `0.14999999999999997` |

## Interpretation

Normal-axis weighting plus a larger finite-time force gain is sufficient to
recover full-speed contact and force regulation in this approximate MuJoCo
setup. It is not sufficient for full paper trajectory reproduction because
E2/E3 pay for contact recovery with centimeter-scale planar tracking error and
qdot saturation.

This confirms the v7 diagnosis: the issue is controller task allocation, not a
missing trajectory formula. The next controller should explicitly model normal
force as a higher-priority task with planar tracking slack rather than relying
on a single weighted least-squares blend.

## Limitations

- This is simulation-only; no real UR10e motion or hardware writes were
  performed.
- Axis weights are diagnostic tuning, not a final controller design.
- E2/E3 full-speed planar tracking is not acceptable yet.
- Orientation compliance, impedance dynamics, `z0`, calibrated TCP, and real
  force-source reconciliation remain unresolved.
- The qdot cap is saturated in the weighted full-speed runs.

## Next Step

Implement a two-stage or prioritized velocity solve:

1. solve the normal force row first under hard joint and velocity bounds;
2. solve planar tracking in the remaining feasible velocity space or with an
   explicit slack metric;
3. report force error, contact fraction, planar error, qdot saturation, and
   task residuals separately.
