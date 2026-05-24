# Tilted Orientation Gain/Timing Sweep Summary

Run root: `runs/tilted_orientation_gain_timing_sweep/20260524T091826`

## Scope

E1 cycloid checks on the 10 degree tilted MuJoCo plane using `orientation_mode = force-normal`, `orientation_priority_mode = linear-primary`, and `normal_velocity_mode = contact-normal`.

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

## Result

- Cases: `18`
- Passing cases: `0`
- Best max orientation error: `0.17416151436895033` at kp `2.0`, paper time scale `0.05`.
- Best non-saturating max orientation error: `0.1744456588511598` at kp `0.25`, paper time scale `0.05`.

No gain/time-scale pair passes the existing gates. Low gains avoid qdot saturation but fail the max-orientation-error gate because the run starts with about `0.174 rad` misalignment to the tilted normal. Gains at or above `0.5` also fail qdot saturation and angular-slack gates.

## Cases

| kp | time scale | pass | failed criteria | force tail MAE N | max orient err rad | max angular slack rad/s | qdot sat frac | tail qdot util |
| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 0.1 | `0.05` | `False` | `max_orientation_error_rad` | `0.00017021009960104026` | `0.1744980186604636` | `3.112113010491921e-06` | `0.0` | `0.10864164340958926` |
| 0.1 | `0.075` | `False` | `max_orientation_error_rad` | `0.00017028171203874897` | `0.1744980186604636` | `7.001930470953769e-06` | `0.0` | `0.10864180071848975` |
| 0.1 | `0.1` | `False` | `max_orientation_error_rad` | `0.00017042122824620254` | `0.1744980186604636` | `1.2447475324324366e-05` | `0.0` | `0.10864210734330415` |
| 0.25 | `0.05` | `False` | `max_orientation_error_rad` | `0.0021338787423030637` | `0.1744456588511598` | `3.551370008415211e-06` | `0.0` | `0.24531098707176816` |
| 0.25 | `0.075` | `False` | `max_orientation_error_rad` | `0.002134130648298882` | `0.1744456588511598` | `7.987443653810365e-06` | `0.0` | `0.24531120157979486` |
| 0.25 | `0.1` | `False` | `max_orientation_error_rad` | `0.002134621303736162` | `0.1744456588511598` | `1.4178358880774764e-05` | `0.0` | `0.24531161979307198` |
| 0.5 | `0.05` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.001581200683072752` | `0.17435839250232021` | `0.03769354013880992` | `0.229` | `1.0` |
| 0.5 | `0.075` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0015813218217458935` | `0.17435839250232021` | `0.0376959415297048` | `0.229` | `1.0` |
| 0.5 | `0.1` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0015815317012663054` | `0.17435839250232021` | `0.03769512024508997` | `0.229` | `1.0` |
| 1.0 | `0.05` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005552897717242855` | `0.17418386008451897` | `0.07466032247827491` | `1.0` | `1.0` |
| 1.0 | `0.075` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005552990351419318` | `0.17418386008451897` | `0.07466040890291388` | `1.0` | `1.0` |
| 1.0 | `0.1` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005553170726111966` | `0.17418386008451897` | `0.07466057862274032` | `1.0` | `1.0` |
| 2.0 | `0.05` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005500972858954655` | `0.17416151436895033` | `0.1633604348751847` | `1.0` | `1.0` |
| 2.0 | `0.075` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005501050363900939` | `0.17416151436895033` | `0.1633604348751847` | `1.0` | `1.0` |
| 2.0 | `0.1` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005501200306344068` | `0.17416151436895033` | `0.1633604348751847` | `1.0` | `1.0` |
| 5.0 | `0.05` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005500972850374586` | `0.17416151436895033` | `0.6869592104751856` | `1.0` | `1.0` |
| 5.0 | `0.075` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005501050439880206` | `0.17416151436895033` | `0.6869592104751856` | `1.0` | `1.0` |
| 5.0 | `0.1` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005501200319756405` | `0.17416151436895033` | `0.6869592104751856` | `1.0` | `1.0` |
