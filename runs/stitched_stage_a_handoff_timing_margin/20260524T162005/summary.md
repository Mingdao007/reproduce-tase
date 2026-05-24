# Stitched Stage A Handoff Timing Margin Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_timing_margin/20260524T162005`

- Stitched pass count: `4 / 7`
- Failing cases: `stage_a_14s_reference_fail, qdot012_stage_a_17p5_reference_fail, paper_time_scale_0p0125_reference_fail`
- Claim scope: diagnostic-label timing-margin audit only; not robustness proof or hardware evidence.

| case | pass | Stage A pass | Stage B pass | Stage A max qdot | terminal force err N | Stage B worst force err N | parameters |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `nominal` | `True` | `True` | `4/4` | `0.14332635022814824` | `0.005097546556703136` | `0.003461025015189971` | `nominal` |
| `stage_a_14s_reference_fail` | `False` | `False` | `0/4` | `0.15` | `2.03704061425341` | `0.005164775788000147` | `stage_a_duration_s=14.0` |
| `stage_a_14p5_recovery` | `True` | `True` | `4/4` | `0.14826863816707989` | `0.005097546556703136` | `0.003461025015189971` | `stage_a_duration_s=14.5` |
| `qdot012_stage_a_17p5_reference_fail` | `False` | `False` | `0/4` | `0.12` | `2.0144060251115015` | `0.0051716759259824` | `qdot_limit_rad_s=0.12, stage_a_duration_s=17.5` |
| `qdot012_stage_a_18p0_recovery` | `True` | `True` | `4/4` | `0.1194386251900526` | `0.005097546556703136` | `0.003460893452988381` | `qdot_limit_rad_s=0.12, stage_a_duration_s=18.0` |
| `paper_time_scale_0p012_recovery` | `True` | `True` | `4/4` | `0.14332635022814824` | `0.005097546556703136` | `0.004977812422968393` | `paper_time_scale=0.012` |
| `paper_time_scale_0p0125_reference_fail` | `False` | `True` | `3/4` | `0.14332635022814824` | `0.005097546556703136` | `0.009659333060181977` | `paper_time_scale=0.0125` |

Interpretation:

- Passing recovery cases show timing or qdot-budget margins for the nominal diagnostic stitched policy.
- Reference-fail cases preserve the nearby failing boundaries from v64.
- This audit does not recover 1 mm base-z/contact perturbations and does not change paper-equivalent or hardware claims.
