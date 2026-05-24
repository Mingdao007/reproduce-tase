# Paper 7DOF Section V Diagnostic

Run id: `20260524T134441`

Scope: separate paper-platform 7DOF executable diagnostic for the paper Section V setup.
This is not a UR10e adapted run and not a hardware gate.

Implemented coverage:

- 7 joint Panda/Franka DH kinematics ported from the legacy MATLAB `forward_panda.m` and `getJacobian_panda.m` files.
- Paper Section V q0, circle trajectory, 5 N normal force target, joint limits, velocity limits, and finite-time inner-loop projection.
- Explicit `z0` convention: q0 forward-kinematics height, because Section V uses `z0` without defining it.

Known limits:

- The Panda DH parameters remain inherited from the legacy MATLAB audit and still need vendor/manual verification.
- The paper's force-derived desired-rotation equation is dimensionally ambiguous; this line uses the documented shortest-arc force-normal interpretation.
- The run is a diagnostic executable line, not a claim of Fig. 5/Fig. 6 numerical parity.

Key metrics:

| Metric | Value |
| --- | ---: |
| `execution_success` | `True` |
| `contact_force_tail_success` | `True` |
| `duration_s` | `30.0` |
| `sample_count` | `30001` |
| `max_abs_q_rad` | `2.4999999999358065` |
| `max_abs_qdot_rad_s` | `1.5` |
| `q_bound_violation_count` | `0` |
| `qdot_bound_violation_count` | `0` |
| `velocity_clamp_fraction` | `0.9844671844271857` |
| `contact_fraction` | `0.5523482550581648` |
| `tail_contact_fraction` | `1.0` |
| `task_residual_rms` | `0.24201586774000083` |
| `tail_position_error_mean_m` | `0.0012460142796336512` |
| `tail_orientation_error_mean_rad` | `2.7169713442019066e-06` |
| `tail_force_error_mean_N` | `0.0004629648106931554` |
| `fig6_q7_sample_time_s` | `22.0` |
| `fig6_q7_at_22s_rad` | `2.4999999999331863` |
| `fig6_q7_abs_error_to_2p5_rad` | `6.681366571115177e-11` |

Config snapshot:

```yaml
duration_s: 30.0
dt_s: 0.001
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
kp: 25.0
ko: 5.0
kf: 1.0
md_kg: 12.0
bd_N_s_m: 550.0
finite_time_power: 0.6666666666666666
q_min_rad: -2.5
q_max_rad: 2.5
qdot_min_rad_s: -1.5
qdot_max_rad_s: 1.5
escape_velocity_alpha: 20.0
communication_delay_s: 0.032
max_angular_speed_rad_s: 1.5
contact_stiffness_N_m: 40000.0
contact_damping_N_s_m: 220.0
max_contact_force_N: 50.0
force_integral_limit: 5.0
force_integral_leak: 1.5
normal_track_gain: 20.0
max_normal_command_velocity_m_s: 0.12
max_normal_state_velocity_m_s: 0.12
max_normal_target_offset_m: 0.05
normal_target_restore_rate: 6.0
q7_nullspace_speed_rad_s: 0.35
force_min_norm_N: 1.0e-06
orientation_mode: normal_only
solver_mode: pinv_bounded
force_loop_mode: admittance_proxy
z0_convention: q0_forward_kinematics_height
```
