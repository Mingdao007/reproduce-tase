# Paper 7DOF Section V Diagnostic

Run id: `20260524T114736`

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
| `duration_s` | `5.0` |
| `sample_count` | `2501` |
| `max_abs_q_rad` | `2.49936692429611` |
| `max_abs_qdot_rad_s` | `0.6331334903981037` |
| `q_bound_violation_count` | `0` |
| `qdot_bound_violation_count` | `0` |
| `velocity_clamp_fraction` | `0.5181927229108356` |
| `contact_fraction` | `0.6173530587764894` |
| `tail_contact_fraction` | `1.0` |
| `task_residual_rms` | `0.07857329192890224` |
| `tail_position_error_mean_m` | `0.00044122814610554124` |
| `tail_orientation_error_mean_rad` | `2.7345108152399078e-05` |
| `tail_force_error_mean_N` | `0.06720487008205062` |

Config snapshot:

```yaml
duration_s: 5.0
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
