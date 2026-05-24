# E2 Posture Regularization Summary

Run root: `runs/staged_orientation_e2_posture_regularization/20260524T102224`

## Counts

- Cases: `10`
- Approach terminal-orientation passes: `10 / 10`
- Approach ordinary-feasibility passes: `0 / 10`
- Trajectory feasibility passes: `4 / 10`
- Trajectory-after-approach passes: `4 / 10`
- Full staged-feasibility passes: `0 / 10`

## Rows

| case | phase | weight | failed criteria | orient err | qdot sat | tail util | force err N |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `baseline` | none | 0.0 | qdot_saturation_fraction;tail_max_qdot_utilization | `0.020294558071100602` | `0.9935` | `1.0` | `0.015543559546856045` |
| `trajectory_w0p001` | trajectory | 0.001 | none | `0.0203545748607252` | `0.0` | `0.015816929731774558` | `0.011842144259021303` |
| `trajectory_w0p01` | trajectory | 0.01 | none | `0.02257965740356133` | `0.0` | `0.012156427259521778` | `0.01199958307572846` |
| `trajectory_w0p1` | trajectory | 0.1 | max_orientation_error_rad | `0.0470714526557534` | `0.0` | `0.03872667331311572` | `0.012019995583968601` |
| `approach_w0p001` | approach | 0.001 | qdot_saturation_fraction;tail_max_qdot_utilization | `0.020262454514735267` | `0.99875` | `1.0` | `0.01554842357981645` |
| `approach_w0p01` | approach | 0.01 | qdot_saturation_fraction;tail_max_qdot_utilization | `0.018046083032793606` | `0.873` | `1.0` | `0.015541878599242054` |
| `approach_w0p1` | approach | 0.1 | contact_present_fraction;tail_mean_abs_force_error_N | `0.004585181966021033` | `0.0` | `0.19286920174859198` | `5.0` |
| `both_w0p001` | both | 0.001 | none | `0.02032274607472726` | `0.0` | `0.015813124322961183` | `0.01164567391060789` |
| `both_w0p01` | both | 0.01 | none | `0.020634679203137215` | `0.0` | `0.013426156756298442` | `0.011815380010165022` |
| `both_w0p1` | both | 0.1 | contact_present_fraction;tail_mean_abs_force_error_N | `0.014264369164437523` | `0.0` | `0.16691630259259307` | `5.0` |
