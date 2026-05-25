# Calibrated MJCF Replay Summary

Run root: `/home/andy/reproduce-tase/runs/calibrated_mjcf_replay_after_v147/20260525T212000`

- Audit passed: `True`
- MuJoCo model loads: `True`
- Calibrated MJCF replay matches RTDE TCP: `True`
- Position error: `2.016003536429377e-06` m
- Orientation error: `6.278799181396437e-06` rad
- Simulation can use calibrated MJCF seed: `True`
- Completion claim allowed: `False`

Interpretation:

- The simplified calibrated MJCF loads in MuJoCo and reproduces the backed-up RTDE TCP pose.
- The model is kinematic seed infrastructure only; it intentionally does not define contact plane, contact patch, or force-source truth.
