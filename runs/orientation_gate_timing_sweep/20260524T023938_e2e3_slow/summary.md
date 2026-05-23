# Timing Feasibility Sweep Summary

Run root: `runs/orientation_gate_timing_sweep/20260524T023938_e2e3_slow`

## Gates

- `solver_success_fraction_min`: `1.0`
- `contact_present_fraction_min`: `1.0`
- `tail_mean_abs_force_error_N_max`: `0.25`
- `max_tangential_position_error_m_max`: `0.002`
- `max_planar_velocity_slack_m_s_max`: `0.001`
- `max_abs_normal_velocity_slack_m_s_max`: `0.0002`
- `max_qdot_violation_rad_s_max`: `1e-09`
- `max_joint_limit_violation_rad_max`: `1e-09`
- `qdot_saturation_fraction_max`: `0.01`
- `tail_max_qdot_utilization_max`: `0.98`
- `max_orientation_error_rad_max`: `0.03`
- `max_angular_velocity_slack_rad_s_max`: `0.03`

## Fastest Passing Scale

- `e2-figure-eight`: `0.1`
- `e3-circle`: none

## Cases

| trajectory | scale | pass | failed criteria | force error N | contact | max pos err m | max planar slack m/s | max normal slack m/s | qdot sat frac | tail qdot util | max orient err rad | max angular slack rad/s |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e2-figure-eight | `0.15` | `False` | `max_planar_velocity_slack_m_s` | `0.00027674337343401746` | `1.0` | `0.0017015874023387015` | `0.001066535242222138` | `6.270271252773789e-11` | `0.0` | `0.06462799581944233` | `0.002544398187252183` | `0.0028287875735388238` |
| e2-figure-eight | `0.1` | `True` | `none` | `0.00027780426626062394` | `1.0` | `0.0011404321848763198` | `0.0007163702055920432` | `2.505107995604455e-11` | `0.0` | `0.02530129669100761` | `0.0017061767936499997` | `0.0018992953192046853` |
| e3-circle | `0.15` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s` | `0.00027414347501199753` | `1.0` | `0.0025704763941887788` | `0.0016157482314288392` | `9.853467507740747e-11` | `0.0` | `0.09038849430072055` | `0.003846797474136364` | `0.0042841960159030945` |
| e3-circle | `0.1` | `False` | `max_planar_velocity_slack_m_s` | `0.0002771165536991338` | `1.0` | `0.0017160357723471772` | `0.0010792940395144709` | `3.184774176915602e-11` | `0.0` | `0.03869465036395444` | `0.002568205077479452` | `0.0028610958265000387` |
