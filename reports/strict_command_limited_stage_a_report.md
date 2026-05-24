# Strict Command-Limited Stage A Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v114-strict-command-limited-stage-a`

Implementation commit: `aaa42097f6778cc0b2c8617c9ffc21f57b5fbfb4`

## Objective

Probe a Stage A formulation change beyond the v113 instantaneous priority
matrix by limiting command generation before the velocity allocation solve:
lower finite-time normal-force gains, cap force-normal angular commands, and
extend setup durations while preserving the strict setup-chain gate.

No hardware command, live read, TCP/payload/configuration write, force-control
step, gate acceptance, contact calibration, or robustness claim is performed.

## Artifacts

- New audit script:
  `scripts/audit_strict_command_limited_stage_a.py`
- New run:
  `runs/strict_command_limited_stage_a/20260525T074557`
- New test:
  `tests/test_strict_command_limited_stage_a.py`

## Result

The v114 probe reports:

```text
case_count = 4
strict_setup_chain_pass_count = 0 / 4
trajectory_feasibility_pass_count = 2 / 4
planned_setup_then_trajectory_pass_count = 0 / 4
strict_command_limited_stage_a_complete = false
strict_paper_equivalent_feasibility = false
do_not_mark_goal_complete = true
```

Failure counts across the four command-limited cases:

```text
final_tangential_position_error_m = 4
setup_max_qdot_saturation_fraction = 4
setup_max_tail_qdot_utilization = 4
setup_min_contact_present_fraction = 3
terminal_tail_mean_abs_force_error_N = 1
```

Best observed rows:

| metric | best case | value |
| --- | --- | ---: |
| setup violation score | `v113_reference_uncapped` | `102.11334382627673` |
| setup qdot saturation | `v113_reference_uncapped` | `1.0` |
| setup x/y error | `v113_reference_uncapped` | `0.008185871326022855 m` |
| setup orientation error | `angular_cap_0p01_low_planar_slow` | `0.0003898438945537693 rad` |

Interpretation:

- Command limiting changes Stage A command generation before allocation, but
  no tested row satisfies the strict setup chain.
- Lower force gain and angular caps reduce some terminal force/orientation
  pressure but do not recover x/y recentering.
- The best qdot-saturation row still saturates at `1.0`, far above the strict
  `0.01` fraction threshold.
- Command limiting alone is not a strict Stage A recovery path.

## Claim Boundary

V114 is offline simulation only. It does not prove strict paper-equivalent
feasibility, make a canonical controller change, accept a replacement
orientation gate, close failed cells, prove robustness, calibrate contact
geometry, establish hardware readiness, or authorize hardware
motion/configuration.

## Validation

- `python3 -m py_compile scripts/audit_strict_command_limited_stage_a.py`
  passed.
- `scripts/run_tests.sh tests/test_strict_command_limited_stage_a.py`
  passed with `3 passed in 0.12s`.
- `python3 scripts/audit_strict_command_limited_stage_a.py --output-dir runs/strict_command_limited_stage_a/20260525T074557`
  created the v114 run.
- `rg -n "&id|\*id" runs/strict_command_limited_stage_a/20260525T074557/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/strict_command_limited_stage_a/20260525T074557 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `171 passed in 7.16s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `aaa42097f6778cc0b2c8617c9ffc21f57b5fbfb4`.

## Next Step

Without explicit live bench approval, continue only non-final offline work. The
next strict-feasibility step should stop treating Stage A as a command-limited
instantaneous velocity problem and instead test an explicit path or terminal
constraint formulation that can hold x/y while restoring force-normal
orientation without setup qdot saturation.
