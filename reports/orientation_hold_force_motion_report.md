# Orientation-Hold Force-Motion Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v15-orientation-hold`

## Scope

This iteration adds an opt-in TCP orientation-hold task to the simulation-only
UR10e force-motion controller. The task keeps the initial TCP orientation as a
desired orientation while E1-E4 run at full paper time scale from the v14
calibrated `bend_0p10` MuJoCo posture.

The implementation uses the MuJoCo site angular Jacobian and explicit angular
slack. This is not the paper's full orientation-compliance law; it is the
first UR10e-adapted orientation task with measured orientation error and
angular slack.

## Controller Form

When `--orientation-mode hold` is enabled, the bounded solve uses stacked
linear and angular rows:

```text
[Jp] qdot + s_linear  = v_cmd
[Jr] qdot + s_angular = omega_cmd

omega_cmd = k_R log(R_desired R_current^T)
```

Hard joint-position and joint-velocity bounds remain enforced inside the
solver. Normal-force, planar, and angular task allocation is controlled by
separate slack weights.

## Runs

Common settings:

- trajectories: E1 cycloid, E2 figure-eight, E3 circle, E4 cardioid
- `--time-scales 1.0`
- `--initial-q 0,-0.1,0.15,-0.05,0,0`
- `--base-z-offset-m=-0.0009710693359375`
- `--qdot-limit-rad-s 0.15`
- `--force-gain 5e-4`
- `--orientation-mode hold`
- `--orientation-kp 1.0`
- planar slack weight `1`
- normal slack weight `10000`
- slack constraint weight `1000`

| run root | angular slack weight | E1-E4 force-motion gate pass | max pos err m | max planar slack m/s | max orientation err rad | max angular slack rad/s | note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `runs/orientation_hold_matrix/20260524T030000` | `0.1` | `0/4` | `0.015476725649078916` | `0.009324376968676102` | `0.022792200960046364` | `0.024703715417836912` | stronger orientation priority breaks planar tracking |
| `runs/orientation_hold_matrix/20260524T023404` | `0.001` | `3/4` | `0.0005297974306642689` | `0.00032966241701242236` | `0.0792791337407633` | `0.0869211753487964` | E2 fails only sustained tail qdot utilization |
| `runs/orientation_hold_matrix/20260524T023429` | `0.0001` | `4/4` | `5.097698265515408e-05` | `3.483121447610465e-05` | `0.08108796381776726` | `0.08895566203803207` | preserves v14 force-motion gates with weak orientation hold |

The accepted low-priority orientation run has these per-trajectory results:

| trajectory | pass | force error N | max pos err m | max orient err rad | max angular slack rad/s | tail qdot util |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| E1 cycloid | `True` | `0.00027029934127870245` | `8.681961433797088e-06` | `0.017123697812485454` | `0.02116478539299565` | `0.026984383521778604` |
| E2 figure-eight | `True` | `0.0004916689518725792` | `2.797143784170073e-05` | `0.03763453579359901` | `0.04250367598436786` | `0.6171247964473606` |
| E3 circle | `True` | `0.0008205269114679869` | `5.097698265515408e-05` | `0.08108796381776726` | `0.08895566203803207` | `0.28127974679800305` |
| E4 cardioid | `True` | `0.00017134573277962305` | `1.0950950750024289e-05` | `0.024563131472431995` | `0.03274048254777163` | `0.054561711669854386` |

## Interpretation

Orientation hold competes directly with planar tracking on the 6DOF UR10e
transfer. Giving the angular task moderate priority reduces orientation error
but makes the full-speed E1-E4 matrix fail the existing position and planar
slack gates. Making orientation a very low-priority soft task preserves the
v14 force-motion baseline, but the orientation error reaches about `0.081 rad`
and the angular slack reaches about `0.089 rad/s`.

This is useful progress because orientation is no longer an unmeasured missing
term. It is now an explicit task with residuals, slack, and plots. It should
not be described as paper-faithful orientation compliance.

## Limitations

- Simulation only. No real UR10e motion, TCP write, payload write, force
  zeroing, URCap setting, or OnRobot configuration change was performed.
- The desired orientation is an initial-orientation hold, not the ambiguous
  paper orientation signal.
- The angular task is a velocity-level MuJoCo Jacobian task, not a torque,
  impedance, or finite-time orientation controller.
- Current feasibility gates still cover force, contact, planar tracking,
  slack, and joint limits. Orientation error is reported but not yet a hard
  pass/fail gate.

## Next Step

Define an orientation-specific acceptance gate and test whether time scaling,
posture changes, or a stricter task-priority solve can reduce orientation error
without losing the v14 force-motion gates.
