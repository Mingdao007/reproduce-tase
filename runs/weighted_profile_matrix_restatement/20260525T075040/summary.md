# Weighted Profile Matrix Restatement Summary

Run root: `runs/weighted_profile_matrix_restatement/20260525T075040`

- Profile name: `weighted_zero_angular_stage_b_diagnostic`
- Restatement supported: `True`
- Source cells: `12`
- Source failed cells: `4`
- Profile overlay supported cells: `base_z_plus1mm, positive_fast_timing_0p0075`
- Gate-acceptance blocked cells: `positive_orientation_gate_0p119, weighted_plus1mm_0p119_gate`
- Closed cells: `0`
- Accepted as robustness proof: `False`
- Do not mark goal complete: `True`

| failed cell | profile overlay | supported | restated status | closed |
| --- | --- | --- | --- | --- |
| `base_z_plus1mm` | `relaxed_base_z_plus1mm_handoff` | `True` | `failed_with_noncanonical_profile_overlay` | `False` |
| `positive_fast_timing_0p0075` | `positive_fast_timing_full_e1e4` | `True` | `failed_with_noncanonical_profile_overlay` | `False` |
| `positive_orientation_gate_0p119` | `none` | `False` | `failed_without_profile_overlay` | `False` |
| `weighted_plus1mm_0p119_gate` | `none` | `False` | `failed_without_profile_overlay` | `False` |

Interpretation:

- The v98/v99 matrix can be restated with the named weighted diagnostic profile as a non-canonical overlay.
- The overlay touches `base_z_plus1mm` and `positive_fast_timing_0p0075`; orientation-gate rows remain gate-acceptance blocked.
- The restatement does not close failed cells, prove robustness, accept a controller or gate, or authorize hardware work.
