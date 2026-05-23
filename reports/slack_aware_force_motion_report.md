# Slack-Aware Force-Motion Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v11-slack-aware-solve`

Run root:

`runs/slack_aware_force_motion/20260524T020245`

## Scope

This iteration adds an opt-in bounded slack-aware velocity solve. The task
model is:

```text
Jp qdot + slack = v_cmd
```

Joint velocity and one-step joint-position bounds remain hard on `qdot`.
Task mismatch is represented explicitly by `slack`, with separate planar and
normal slack penalties.

This is still simulation-only. The goal is not to tune another final answer,
but to expose the E2/E3 full-speed tradeoff as solver slack rather than only as
post-run residuals.

## Tests

Verification command:

```bash
scripts/run_tests.sh
```

Result:

`29 passed`

## Representative Slack Probes

Common settings:

- E2/E3 only.
- `--paper-time-scale 1.0`
- `--qdot-limit-rad-s 0.15`
- `--force-gain 5e-4`
- `--use-slack-solve`
- `--planar-slack-weight 1`
- `--slack-constraint-weight 1000`

| run | normal slack weight | tail force error N | contact present | max position error m | max planar slack m/s | tail planar slack m/s | max normal slack m/s | tail normal slack m/s | max qdot rad/s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E2 | `100` | `5.0` | `0.568` | `0.0057693956482014275` | `0.0036232839672081176` | `0.003397431194447601` | `0.0011754316818573876` | `0.001170428865234319` | `0.14999999999999997` |
| E2 | `400` | `4.227246781153561` | `1.0` | `0.014038002179956672` | `0.009094427143951382` | `0.008370142844679428` | `0.00108717196930919` | `0.0010293814110897664` | `0.14999999999999997` |
| E2 | `10000` | `0.047984` | `1.0` | `0.021143` | `0.013217` | `0.012361` | `0.00010718` | `0.00010013` | `0.15` |
| E3 | `100` | `5.0` | `0.656` | `0.008504621058720654` | `0.005359207304529535` | `0.005007184180132771` | `0.0011612165102032775` | `0.001155710416432828` | `0.14999999999999997` |
| E3 | `400` | `2.101515579413298` | `1.0` | `0.013586438069119399` | `0.008734690038218052` | `0.008064471592543686` | `0.0007776548320813294` | `0.0007231527084777461` | `0.14999999999999997` |
| E3 | `10000` | `0.01441` | `1.0` | `0.016176` | `0.010693` | `0.00961` | `0.00005457` | `0.00004759` | `0.15` |

## Interpretation

The slack-aware solve makes the allocation explicit:

- Low normal slack penalty preserves more planar tracking but leaves large
  normal slack and loses force.
- High normal slack penalty recovers force/contact but allocates large planar
  slack and saturates qdot.

This is the same physical limitation observed in v8-v10, now represented
inside the optimization variables. The next improvement cannot come from
renaming residuals or changing scalar weights alone. It needs either:

- a trajectory-speed or posture change that keeps the task feasible under the
  hard qdot cap, or
- a more complete controller model with explicit priority, timing, and
  acceptable planar slack thresholds.

## Limitations

- This is simulation-only; no real UR10e motion or hardware writes were
  performed.
- The slack-aware solve is velocity-level and does not model torque dynamics,
  impedance, or orientation compliance.
- Full-speed E2/E3 are still not reproduced: reducing normal slack creates
  centimeter-scale planar tracking error.
- The qdot cap remains saturated in the high-normal-slack cases.

## Next Step

Use the explicit slack metrics to define pass/fail thresholds for the
simulation matrix, then test whether slower paper-time scaling, different
initial posture, or a planned approach phase can keep E2/E3 feasible before
adding orientation compliance.
