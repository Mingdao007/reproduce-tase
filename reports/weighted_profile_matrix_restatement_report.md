# Weighted Profile Matrix Restatement Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v111-weighted-profile-matrix-restatement`

Implementation commit: `7900d441e3d072026bdf0f874da98b322cf9628d`

## Objective

Audit whether the v98/v99 diagnostic robustness matrix can be restated with
the v110 named weighted diagnostic profile while preserving the current claim
boundary: no canonical controller or gate changes, no failed-cell closure, and
no robustness claim.

## Artifacts

- New audit script:
  `scripts/audit_weighted_profile_matrix_restatement.py`
- New run:
  `runs/weighted_profile_matrix_restatement/20260525T075040`
- New test:
  `tests/test_weighted_profile_matrix_restatement.py`

## Result

The v111 restatement reports:

```text
profile_name = weighted_zero_angular_stage_b_diagnostic
restatement_supported = true
source_cell_count = 12
source_failed_cell_count = 4
profile_overlay_supported_count = 2
profile_overlay_supported_cell_ids = base_z_plus1mm, positive_fast_timing_0p0075
gate_acceptance_blocked_cell_ids = positive_orientation_gate_0p119, weighted_plus1mm_0p119_gate
closed_cell_count = 0
candidate_matrix_complete = false
accepted_as_robustness_proof = false
all_failed_cells_closed = false
do_not_mark_goal_complete = true
```

Failed-cell restatement:

| failed cell | profile overlay | supported | restated status | closed |
| --- | --- | --- | --- | --- |
| `base_z_plus1mm` | `relaxed_base_z_plus1mm_handoff` | `true` | `failed_with_noncanonical_profile_overlay` | `false` |
| `positive_fast_timing_0p0075` | `positive_fast_timing_full_e1e4` | `true` | `failed_with_noncanonical_profile_overlay` | `false` |
| `positive_orientation_gate_0p119` | `none` | `false` | `failed_without_profile_overlay` | `false` |
| `weighted_plus1mm_0p119_gate` | `none` | `false` | `failed_without_profile_overlay` | `false` |

The v98/v99 matrix can be restated with the named weighted profile as a
non-canonical overlay. It still cannot be upgraded into a complete diagnostic
matrix or robustness proof because original failed cells remain open and the
orientation-gate rows remain gate-acceptance blocked.

## Claim Boundary

V111 is post-hoc offline bookkeeping over existing metrics. It does not rerun
MuJoCo, make weighted priority canonical, accept `0.12 rad` as a canonical
orientation gate, close original v99 failed cells, prove robustness, prove
strict paper-equivalent feasibility, calibrate contact geometry, establish
hardware readiness, or authorize hardware motion/configuration.

## Validation

- `python3 -m py_compile scripts/audit_weighted_profile_matrix_restatement.py`
  passed.
- `scripts/run_tests.sh tests/test_weighted_profile_matrix_restatement.py`
  passed with `3 passed in 0.04s`.
- `python3 scripts/audit_weighted_profile_matrix_restatement.py --output-dir runs/weighted_profile_matrix_restatement/20260525T075040`
  created the v111 run.
- `rg -n "&id|\*id" runs/weighted_profile_matrix_restatement/20260525T075040/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/weighted_profile_matrix_restatement/20260525T075040 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `162 passed in 7.00s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `7900d441e3d072026bdf0f874da98b322cf9628d`.

## Next Step

Without explicit live bench approval, continue only non-final offline work. The
next clean offline step is a blocker-prioritization audit over the remaining
non-profile-covered rows: orientation gate acceptance, contact calibration,
strict feasibility, and hardware-readiness evidence.
