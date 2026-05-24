# Base-Z Plus1mm Split Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v108-base-z-plus1mm-split`

Implementation commit: `987e360d9244bf8c98ce549c21c7787ab163868a`

## Objective

Split the v100 `base_z_plus1mm` unresolved result into its start-contact,
terminal-orientation, path, and stitched-handoff components without rerunning
MuJoCo. The audit reads the existing v100 exact failed-cell metrics plus the
v68 start-contact, v69 terminal-orientation, and v70 relaxed-orientation
recovery metrics.

## Artifacts

- New audit script:
  `scripts/audit_base_z_plus1mm_split.py`
- New run:
  `runs/base_z_plus1mm_split/20260525T071440`
- New test:
  `tests/test_base_z_plus1mm_split.py`

## Result

The v108 split reports:

```text
base_z_offset_delta_mm = 1.0
exact_planned_cell_status = executed_unresolved
exact_closure_passed = false
exact_start_passed = false
broader_start_search_passed = true
terminal_force_xy_contact_passed = true
terminal_diagnostic_passed = false
terminal_orientation_error_rad = 0.11948560786548146
exact_orientation_gate_rad = 0.08
orientation_excess_over_exact_gate_rad = 0.039485607865481456
relaxed_gate_rad = 0.12
relaxed_gate_margin_rad = 0.0005143921345185376
relaxed_terminal_passed = true
relaxed_path_passed = true
relaxed_path_min_duration_s = 10.018584837157274
relaxed_stitched_recovered = false
relaxed_stage_b_handoff_pass_counts = 3/4, 3/4
failed_cell_closed = false
```

Key slices:

| evidence slice | pass | key value | interpretation |
| --- | --- | ---: | --- |
| exact start | `false` | `force_error_N,target_contact_count` | planned seed misses contact |
| broader start | `true` | `0.14209391841232932 N` force error | start contact is local seed-limited |
| terminal force/x-y/contact | `true` | `2.3037127760972e-15 rad` yaw gap | not a force/x-y/contact failure |
| terminal orientation gate | `false` | `0.039485607865481456 rad` excess | `0.08 rad` gate blocks terminal/path |
| relaxed Stage A/path | `true` | `10.018584837157274 s` path minimum duration | run-local `0.12 rad` gate recovers endpoint/path |
| relaxed stitched | `false` | `3/4, 3/4` | Stage B handoff remains blocked |

The exact v99 `base_z_plus1mm` command remains executed-unresolved. V108
narrows why: the planned start miss is seed-limited, terminal/path recovery is
orientation-gate limited under the current contact-point model, and the
run-local `0.12 rad` evidence still does not recover stitched Stage B.

## Claim Boundary

V108 is a post-hoc offline audit over existing metrics. It does not close the
original v99 `base_z_plus1mm` failed cell. It does not accept `0.12 rad` as a
canonical orientation gate, change canonical configs, calibrate contact
geometry, prove robustness, prove strict paper-equivalent feasibility,
establish hardware readiness, or authorize hardware motion/configuration.

## Validation

- `python3 -m py_compile scripts/audit_base_z_plus1mm_split.py`
  passed.
- `scripts/run_tests.sh tests/test_base_z_plus1mm_split.py`
  passed with `3 passed in 0.09s`.
- `python3 scripts/audit_base_z_plus1mm_split.py --output-dir runs/base_z_plus1mm_split/20260525T071440`
  created the v108 run.
- `rg -n "&id|\*id" runs/base_z_plus1mm_split/20260525T071440/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/base_z_plus1mm_split/20260525T071440 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `153 passed in 7.22s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `987e360d9244bf8c98ce549c21c7787ab163868a`.

## Next Step

Without explicit live bench approval, continue only non-final offline work. A
next branch can audit the acceptance boundary for promoting weighted priority
into a named diagnostic controller profile, or target the remaining relaxed
`base_z_plus1mm` Stage B handoff timing/qdot blocker without accepting the
relaxed orientation gate as canonical.
