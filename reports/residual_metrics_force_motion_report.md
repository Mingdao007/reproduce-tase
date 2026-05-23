# Residual Metrics Force-Motion Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v10-residual-metrics`

Run root:

`runs/residual_metrics_force_motion/20260524T015831`

## Scope

This iteration adds explicit unweighted Cartesian velocity residual metrics to
the simulation-only force-motion controller:

```text
residual = actual_tcp_linear_velocity - commanded_tcp_linear_velocity
planar residual = ||residual_xy||
normal residual = residual_z
```

The purpose is to stop treating solver success as enough evidence. The v10
metrics separate normal task failure from planar tracking failure, which is
required before implementing a real slack-aware or task-priority controller.

## Tests

Verification command:

```bash
scripts/run_tests.sh
```

Result:

`28 passed`

## Representative Full-Speed Residual Matrix

Common settings:

- E2/E3 only.
- `--paper-time-scale 1.0`
- `--qdot-limit-rad-s 0.15`
- `--force-gain 5e-4`
- equal rows for the baseline cases.
- `--normal-axis-weight 100 --planar-axis-weight 1` for the weighted cases.

| run | tail force error N | contact present | max position error m | max planar velocity residual m/s | tail planar residual m/s | max normal velocity residual m/s | tail normal residual m/s | max qdot rad/s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E2 equal | `5.0` | `0.46725` | `6.701093192370075e-05` | `4.616584808830004e-05` | `4.2944922298345356e-05` | `0.0012211832551020988` | `0.0012199977697645642` | `0.14988843113129563` |
| E2 weighted | `0.04680027821015285` | `1.0` | `0.02114519099848796` | `0.013308364152647561` | `0.012362863961667026` | `0.00010776051130989523` | `0.00010021894847826024` | `0.14999999999999997` |
| E3 equal | `5.0` | `0.42725` | `0.00011339128879628036` | `6.865700971642382e-05` | `6.568121577264033e-05` | `0.0012373628185900344` | `0.0011462334341136979` | `0.1499997999931814` |
| E3 weighted | `0.013411903132922096` | `1.0` | `0.016169767707432416` | `0.0105921848161393` | `0.009606765082707578` | `5.415531503391008e-05` | `4.762494056458478e-05` | `0.14999999999999997` |

## Interpretation

The residual metrics confirm the controller tradeoff:

- Equal weighting tracks planar velocity almost exactly, but leaves a large
  normal velocity residual. Contact is lost and tail force error remains `5 N`.
- High normal weighting reduces normal residual enough to keep contact and
  regulate force, but it creates large planar velocity residual and
  centimeter-scale path error.

The hard qdot cap is saturated in weighted cases. That means full-speed E2/E3
cannot be validated by the current blended least-squares controller. The next
solver must expose slack or hierarchy in the optimization itself, not only in
post-run summaries.

## Limitations

- This is simulation-only; no real UR10e motion or hardware writes were
  performed.
- Residual instrumentation does not solve the control problem by itself.
- Orientation compliance, impedance dynamics, calibrated TCP, `z0`, and real
  force-source reconciliation remain unresolved.

## Next Step

Implement a solver that treats normal and planar tasks as separate terms with
reported slack. The minimum useful next design is a bounded least-squares
problem with explicit task residual outputs and pass/fail thresholds for
normal force, planar tracking, qdot saturation, and contact presence.
