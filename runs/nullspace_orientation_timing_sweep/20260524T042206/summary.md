# Timing Feasibility Sweep Summary

Run root: `runs/nullspace_orientation_timing_sweep/20260524T042206`

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

- `e2-figure-eight`: `0.075`
- `e3-circle`: `0.075`

## Cases

| trajectory | scale | pass | failed criteria | force error N | contact | max pos err m | max planar slack m/s | max normal slack m/s | qdot sat frac | tail qdot util | max orient err rad | max angular slack rad/s |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e2-figure-eight | `1.0` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005011031206470318` | `1.0` | `8.944242741889184e-06` | `1.9575401563049538e-07` | `3.679725364000232e-10` | `0.1845` | `1.0` | `0.03774766436372975` | `0.04492437394720665` |
| e2-figure-eight | `0.75` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.00014946633455506953` | `1.0` | `6.708182251390124e-06` | `3.50791120518532e-08` | `6.474718219713404e-11` | `0.154` | `1.0` | `0.03501762847534395` | `0.03706468836695612` |
| e2-figure-eight | `0.5` | `False` | `qdot_saturation_fraction` | `0.00025851911019694307` | `1.0` | `4.472121797206802e-06` | `1.780018691679371e-08` | `2.6841570266900212e-11` | `0.148` | `0.03978237755261255` | `0.026953431667816132` | `0.029563397178398124` |
| e2-figure-eight | `0.35` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.00029143729700152333` | `1.0` | `3.130485542133294e-06` | `1.148721742763999e-08` | `2.2682845680140496e-11` | `0.147` | `1.0` | `0.019968191633749657` | `0.02218943027778598` |
| e2-figure-eight | `0.25` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0002999272401727515` | `1.0` | `2.236086177915552e-06` | `7.987660349065045e-09` | `2.3383716749763358e-11` | `0.1435` | `1.0` | `0.014645834298341194` | `0.01637189293486165` |
| e2-figure-eight | `0.2` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0003147806851398849` | `1.0` | `1.7913001248655088e-06` | `6.557875702911612e-09` | `2.373415239977127e-11` | `0.1405` | `1.0` | `0.011833962492106373` | `0.013258124542901822` |
| e2-figure-eight | `0.15` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0005209100715186343` | `1.0` | `1.346754747464866e-06` | `5.129709132856242e-09` | `2.40845879345827e-11` | `0.127` | `1.0` | `0.008945503859163125` | `0.010038867601499916` |
| e2-figure-eight | `0.1` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.00028017224329198175` | `1.0` | `8.944251461459207e-07` | `3.367061605502975e-09` | `2.4435023455841604e-11` | `0.01775` | `1.0` | `0.006008040747789106` | `0.006736682020150603` |
| e2-figure-eight | `0.075` | `True` | `none` | `0.0002771005815372496` | `1.0` | `6.708191085550114e-07` | `2.4433712474975925e-09` | `2.461024130117435e-11` | `0.0` | `0.005903898478793365` | `0.004516128236962064` | `0.005076738194606452` |
| e3-circle | `1.0` | `False` | `qdot_saturation_fraction;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0003924016561831989` | `1.0` | `5.999914591096698e-06` | `6.312024736453601e-07` | `7.417388251306308e-10` | `0.15675` | `0.20538347700437862` | `0.08131187102533075` | `0.08921566880313665` |
| e3-circle | `0.75` | `False` | `qdot_saturation_fraction;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.00016573913038812394` | `1.0` | `4.4999359434905595e-06` | `9.59622161232346e-08` | `1.0874905722605603e-10` | `0.157` | `0.06539207961925256` | `0.06394216962697459` | `0.07096559851478133` |
| e3-circle | `0.5` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0002591187431432473` | `1.0` | `2.9999572957404333e-06` | `3.559111767286287e-08` | `3.60879524336367e-11` | `0.1565` | `1.0` | `0.044050697770772494` | `0.04926061501821568` |
| e3-circle | `0.35` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0002897324272924806` | `1.0` | `2.0999701070412428e-06` | `1.9891295820297455e-08` | `2.513589464743721e-11` | `0.155` | `1.0` | `0.031244339876937404` | `0.035044255531701485` |
| e3-circle | `0.25` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0002958396272706876` | `1.0` | `1.4999786478944267e-06` | `1.2757890637781255e-08` | `2.5135894620332156e-11` | `0.15225` | `1.0` | `0.02245521556692771` | `0.02522092436355364` |
| e3-circle | `0.2` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0002986401956237339` | `1.0` | `1.1999829183179938e-06` | `9.952295583122495e-09` | `2.513589462710842e-11` | `0.14925` | `1.0` | `0.01800562418991458` | `0.02023367181336409` |
| e3-circle | `0.15` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0003070437304159301` | `1.0` | `8.999871887400896e-07` | `7.770310299262654e-09` | `2.5135894633884683e-11` | `0.143` | `1.0` | `0.013528548324401937` | `0.015208347476837535` |
| e3-circle | `0.1` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.001573486797399346` | `1.0` | `5.999914591612067e-07` | `5.599487870530898e-09` | `2.5135894620332156e-11` | `0.1155` | `1.0` | `0.009031791252937182` | `0.01015630822843078` |
| e3-circle | `0.075` | `True` | `none` | `0.00027633354479075225` | `1.0` | `4.49993594371628e-07` | `3.695694551120664e-09` | `2.5135894633884683e-11` | `0.0` | `0.005652094795331068` | `0.006787233568225033` | `0.007632937570076151` |
