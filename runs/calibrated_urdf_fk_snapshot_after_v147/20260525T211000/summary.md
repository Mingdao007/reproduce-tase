# Calibrated URDF FK Snapshot Summary

Run root: `/home/andy/reproduce-tase/runs/calibrated_urdf_fk_snapshot_after_v147/20260525T211000`

- Audit passed: `True`
- Calibrated URDF FK matches RTDE TCP: `True`
- Best frame: `tool0_plus_live_tcp_offset_z`
- Best position error: `2.0160035361820057e-06` m
- Best orientation error: `6.278799181278485e-06` rad
- Nominal MuJoCo position error before this: `1.1351349451303372` m
- Nominal MuJoCo orientation error before this: `2.840514162594206` rad
- Completion claim allowed: `False`

| frame | position error m | orientation error rad |
| --- | ---: | ---: |
| `flange` | `0.12253914007924249` | `2.0944001199563695` |
| `tool0` | `0.12253914007924249` | `6.278799181278485e-06` |
| `tool0_plus_live_tcp_offset_z` | `2.0160035361820057e-06` | `6.278799181278485e-06` |
| `tool0_minus_live_tcp_offset_z` | `0.24507914007245934` | `6.278799181278485e-06` |

Interpretation:

- The generated calibrated URDF plus the live TCP offset reproduces the RTDE TCP pose at the backed-up joint state.
- The older nominal MuJoCo primitive remains too approximate for real-state replay.
- This is a kinematic alignment result only, not contact/setup-target acceptance or a hardware-readiness claim.
