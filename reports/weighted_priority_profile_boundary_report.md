# Weighted Priority Profile Boundary Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v110-weighted-priority-profile-boundary`

Implementation commit: `V110_IMPLEMENTATION_COMMIT_PENDING`

## Objective

Use the verified v107 and v109 evidence to decide whether weighted Stage B
priority can be named as a diagnostic controller profile without becoming
canonical, accepting a replacement gate, or closing original v99 failed cells.

## Artifacts

- New audit script:
  `scripts/audit_weighted_priority_profile_boundary.py`
- New run:
  `runs/weighted_priority_profile_boundary/20260525T074100`
- New test:
  `tests/test_weighted_priority_profile_boundary.py`

## Result

The v110 boundary audit reports:

```text
profile_name = weighted_zero_angular_stage_b_diagnostic
diagnostic_profile_naming_supported = true
evidence_face_count = 2
covered_faces = positive_fast_timing_full_e1e4, relaxed_base_z_plus1mm_handoff
weighted_all_faces_recovered = true
baseline_failure_reproduced_all_faces = true
can_name_diagnostic_profile = true
canonical_controller_change = false
canonical_orientation_gate_change = false
failed_cell_closed = false
robustness_claim = false
hardware_readiness = false
```

Evidence faces:

| face | baseline failures | weighted passes | max weighted orientation | max weighted qdot sat | max weighted tail qdot |
| --- | ---: | ---: | ---: | ---: | ---: |
| `positive_fast_timing_full_e1e4` | `1` | `2` | `0.11954627160547111` | `0.0` | `0.5177926211135458` |
| `relaxed_base_z_plus1mm_handoff` | `2` | `4` | `0.11956645203696047` | `0.0` | `0.520987929048311` |

Supported diagnostic profile scope:

- profile name: `weighted_zero_angular_stage_b_diagnostic`
- orientation priority mode: `weighted`
- orientation kp: `0.0`
- normal-axis weights: `[1.0, 30.0]`
- base-z offset delta: `+1.0 mm`
- qdot limit: `0.15 rad/s`
- orientation gate: run-local diagnostic `0.12 rad`, non-canonical
- covered trajectories: E1-E4 Stage B rows in the v107 and v109 faces

## Claim Boundary

V110 supports naming a diagnostic profile for the covered faces only. It does
not make weighted priority a canonical controller default, accept `0.12 rad` as
a canonical orientation gate, close any original v99 failed cell, prove
robustness, prove strict paper-equivalent feasibility, calibrate contact
geometry, establish hardware readiness, or authorize hardware
motion/configuration.

## Validation

- `python3 -m py_compile scripts/audit_weighted_priority_profile_boundary.py`
  passed.
- `scripts/run_tests.sh tests/test_weighted_priority_profile_boundary.py`
  passed with `3 passed in 0.04s`.
- `python3 scripts/audit_weighted_priority_profile_boundary.py --output-dir runs/weighted_priority_profile_boundary/20260525T074100`
  created the v110 run.
- `rg -n "&id|\*id" runs/weighted_priority_profile_boundary/20260525T074100/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/weighted_priority_profile_boundary/20260525T074100 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `159 passed in 6.93s`.
- `git diff --check`
  passed.
- Branch push verification is pending the implementation commit.

## Next Step

Without explicit live bench approval, continue only non-final offline work. The
next clean offline step is to audit whether the v98/v99 diagnostic robustness
matrix can be restated with the named weighted diagnostic profile while keeping
canonical controller/gate changes, failed-cell closure, and robustness claims
false.
