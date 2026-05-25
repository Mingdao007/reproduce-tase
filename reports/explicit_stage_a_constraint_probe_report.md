# Explicit Stage A Constraint Probe Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v115-explicit-stage-a-constraint-probe`

Implementation commit: `315052286c42300dc9cf1665aec8a7b9279587bf`

## Objective

Probe the next offline strict-feasibility step after v113 and v114: stop
treating Stage A as an instantaneous controller schedule, and test explicit
terminal/path constraints with qdot-timed paths.

The probe uses the v56 contact-manifold terminal constraint cases and the v62
diagnostic contact path reference. It asks whether qdot saturation can be
removed while holding strict x/y, target force/contact, and force-normal
orientation.

No hardware command, live read, TCP/payload/configuration write, force-control
step, gate acceptance, contact calibration, or robustness claim is performed.

## Artifacts

- New audit script:
  `scripts/audit_explicit_stage_a_constraint_probe.py`
- New run:
  `runs/explicit_stage_a_constraint_probe/20260525T082500`
- New test:
  `tests/test_explicit_stage_a_constraint_probe.py`

## Result

The v115 probe reports:

```text
case_count = 5
strict_setup_path_pass_count = 0 / 5
terminal_strict_criteria_pass_count = 0 / 5
qdot_criteria_pass_count = 5 / 5
planned_setup_then_trajectory_pass_count = 0 / 5
explicit_stage_a_constraint_probe_complete = false
strict_paper_equivalent_feasibility = false
do_not_mark_goal_complete = true
```

Failure counts across the five rows:

```text
path_target_contact_present_fraction = 1
terminal_force_error_N = 1
terminal_orientation_error_rad = 3
terminal_tangential_error_m = 3
```

Key rows:

| case | qdot sat | tail qdot util | terminal x/y m | terminal orientation rad | terminal force error N | contact fraction | failed criteria |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `diagnostic_contact_path_tracking_reference` | `0.0` | `0.9555090015209883` | `0.0030075762251302427` | `0.07240605683117463` | `0.005097546556703136` | `1.0` | `terminal_tangential_error_m;terminal_orientation_error_rad` |
| `terminal_xy_force_hold` | `0.0` | `0.9500000000000501` | `1.2984463881799684e-15` | `0.14697007178233126` | `2.4868995751603507e-14` | `1.0` | `terminal_orientation_error_rad` |
| `terminal_xy_orientation_hold` | `0.0` | `0.9500000000000741` | `5.204170427930421e-18` | `5.551115123125783e-17` | `5.0` | `0.011382113821138212` | `terminal_force_error_N;path_target_contact_present_fraction` |
| `terminal_force_orientation_hold` | `0.0` | `0.9500000000000963` | `0.014127706733724453` | `3.608594916770049e-14` | `1.6253665080512292e-13` | `1.0` | `terminal_tangential_error_m` |
| `terminal_xy_force_orientation_soft_best` | `0.0` | `0.9500000000000547` | `0.0030075787462736734` | `0.07240603326354965` | `0.005097551486581864` | `1.0` | `terminal_tangential_error_m;terminal_orientation_error_rad` |

Interpretation:

- Qdot-timed paths remove the v113/v114 setup qdot-saturation failure in all
  tested rows.
- Removing qdot saturation does not solve the strict terminal compatibility
  problem.
- Holding x/y plus force leaves orientation outside the strict gate.
- Holding x/y plus orientation loses target contact and force.
- Holding force plus orientation causes centimeter-scale x/y drift.
- The best soft strict terminal compromise still fails strict x/y and
  orientation.

## Claim Boundary

V115 is offline simulation only. It does not prove strict paper-equivalent
feasibility, run a Stage B trajectory, make a canonical controller change,
accept a replacement orientation gate, close failed cells, prove robustness,
calibrate contact geometry, establish hardware readiness, or authorize
hardware motion/configuration.

## Validation

- `python3 -m py_compile scripts/audit_explicit_stage_a_constraint_probe.py`
  passed.
- `scripts/run_tests.sh tests/test_explicit_stage_a_constraint_probe.py`
  passed with `3 passed in 0.12s`.
- `python3 scripts/audit_explicit_stage_a_constraint_probe.py --output-dir runs/explicit_stage_a_constraint_probe/20260525T082500`
  created the v115 run.
- `rg -n "&id|\*id" runs/explicit_stage_a_constraint_probe/20260525T082500/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/explicit_stage_a_constraint_probe/20260525T082500 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `174 passed in 7.12s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `315052286c42300dc9cf1665aec8a7b9279587bf`.

## Next Step

Without explicit live bench approval, continue only non-final offline work. The
strict terminal compatibility blocker now remains even when qdot saturation is
removed by explicit timing. The next strict-feasibility step should either test
a stronger constrained optimization over the accepted contact model or wait for
approved read-only calibration evidence that can justify changing the setup
target/contact model. Do not promote any v115 row to a strict setup claim.
