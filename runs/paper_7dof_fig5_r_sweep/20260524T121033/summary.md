# Paper 7DOF Fig.5 r Sweep

Run id: `20260524T121033`

Scope: Python 7DOF Section V diagnostic coverage for Fig.5 r-sweep windows.
This is not paper-equivalent Fig.5 numerical parity by itself.

| r | execution | tail force pass | task residual RMS | metrics |
| ---: | ---: | ---: | ---: | --- |
| `0.2` | `True` | `False` | `0.13487857241557796` | `runs/paper_7dof_fig5_r_sweep/20260524T121033/r_0p2/metrics.yaml` |
| `0.4` | `True` | `False` | `0.1212787876329949` | `runs/paper_7dof_fig5_r_sweep/20260524T121033/r_0p4/metrics.yaml` |
| `0.6` | `True` | `False` | `0.12141523603923539` | `runs/paper_7dof_fig5_r_sweep/20260524T121033/r_0p6/metrics.yaml` |
| `0.8` | `True` | `False` | `0.1243757377448289` | `runs/paper_7dof_fig5_r_sweep/20260524T121033/r_0p8/metrics.yaml` |
| `1.0` | `True` | `False` | `0.12967020697293458` | `runs/paper_7dof_fig5_r_sweep/20260524T121033/r_1p0/metrics.yaml` |

Config snapshot:

```yaml
duration_s: 2.0
dt_s: 0.002
q0_rad:
- 0.0
- -0.7853981633974483
- 0.0
- -2.356194490192345
- 0.0
- 1.5707963267948966
- 0.7853981633974483
radius_m: 0.2
omega_rad_s: 0.2
desired_force_N: 5.0
epsilon: 0.022
kp: 4.0
ko: 5.0
kf: 1.0
md_kg: 12.0
bd_N_s_m: 550.0
finite_time_power: 0.6666666666666666
q_min_rad: -2.5
q_max_rad: 2.5
qdot_min_rad_s: -1.5
qdot_max_rad_s: 1.5
escape_velocity_alpha: 2.0
communication_delay_s: 0.032
max_angular_speed_rad_s: 1.0
contact_stiffness_N_m: 40000.0
contact_damping_N_s_m: 220.0
max_contact_force_N: 50.0
force_integral_limit: 0.1
force_integral_leak: 0.0
force_min_norm_N: 1.0e-06
orientation_mode: force_shortest_arc
solver_mode: kkt_projection
force_loop_mode: paper_literal
z0_convention: q0_forward_kinematics_height
```
