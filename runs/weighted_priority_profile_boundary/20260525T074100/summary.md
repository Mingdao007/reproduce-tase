# Weighted Priority Profile Boundary Summary

Run root: `runs/weighted_priority_profile_boundary/20260525T074100`

- Profile name: `weighted_zero_angular_stage_b_diagnostic`
- Diagnostic profile naming supported: `True`
- Evidence faces: `positive_fast_timing_full_e1e4, relaxed_base_z_plus1mm_handoff`
- Weighted all faces recovered: `True`
- Baseline failure reproduced all faces: `True`
- Canonical controller change: `False`
- Canonical orientation gate change: `False`
- Failed cell closed: `False`
- Robustness claim: `False`

| face | baseline failures | weighted passes | max weighted orientation | max weighted qdot sat | max weighted tail qdot |
| --- | ---: | ---: | ---: | ---: | ---: |
| `positive_fast_timing_full_e1e4` | `1` | `2` | `0.11954627160547111` | `0.0` | `0.5177926211135458` |
| `relaxed_base_z_plus1mm_handoff` | `2` | `4` | `0.11956645203696047` | `0.0` | `0.520987929048311` |

Supported diagnostic profile scope:

- Orientation priority mode: `weighted`
- Orientation kp: `0.0`
- Normal-axis weights: `[1.0, 30.0]`
- Orientation gate status: `run_local_diagnostic_noncanonical`

Interpretation:

- The existing evidence supports naming `weighted_zero_angular_stage_b_diagnostic` as a diagnostic profile for the covered faces.
- This audit does not make the profile canonical, accept the `0.12 rad` gate, close any original v99 failed cell, prove robustness, or authorize hardware work.
