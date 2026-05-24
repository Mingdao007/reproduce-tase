# Stitched Stage A Handoff Sensitivity Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_sensitivity/20260524T161111`

- Stitched pass count: `4 / 9`
- Failing cases: `base_z_minus_1mm, base_z_plus_1mm, stage_a_14s, qdot_limit_0p12, paper_time_scale_0p02`
- Claim scope: diagnostic-label simulation sensitivity only; not robustness proof or hardware evidence.

| case | pass | Stage A pass | Stage B pass | Stage A max qdot | terminal force err N | Stage B worst force err N | parameters |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `nominal` | `True` | `True` | `4/4` | `0.14332635022814824` | `0.005097546556703136` | `0.003461025015189971` | `nominal` |
| `base_z_minus_1mm` | `False` | `False` | `0/4` | `0.14332635022814824` | `92.55645811468109` | `4.80843116250581` | `base_z_offset_delta_m=-0.001` |
| `base_z_plus_1mm` | `False` | `False` | `0/4` | `0.14332635022814824` | `5.0` | `5.0` | `base_z_offset_delta_m=0.001` |
| `stage_a_14s` | `False` | `False` | `0/4` | `0.15` | `2.03704061425341` | `0.005164775788000147` | `stage_a_duration_s=14.0` |
| `stage_a_16s` | `True` | `True` | `4/4` | `0.1343684533387775` | `0.005097546556703136` | `0.003461025015189971` | `stage_a_duration_s=16.0` |
| `qdot_limit_0p12` | `False` | `False` | `0/4` | `0.12` | `17.084553106115138` | `0.0035858309824553956` | `qdot_limit_rad_s=0.12` |
| `force_gain_5e-5` | `True` | `True` | `4/4` | `0.14332635022814824` | `0.005097546556703136` | `0.013843278429059795` | `force_gain=5e-05` |
| `force_gain_2e-4` | `True` | `True` | `4/4` | `0.14332635022814824` | `0.005097546556703136` | `0.000865457999273005` | `force_gain=0.0002` |
| `paper_time_scale_0p02` | `False` | `True` | `3/4` | `0.14332635022814824` | `0.005097546556703136` | `0.037200872609881336` | `paper_time_scale=0.02` |

Interpretation:

- Passing cases preserve the v63 diagnostic stitched gate under the listed perturbation only.
- Failing cases bound the nominal result and prevent a broad robustness claim.
- This audit does not change the strict paper-equivalent, v38 relaxed, or v63 diagnostic claim labels.
