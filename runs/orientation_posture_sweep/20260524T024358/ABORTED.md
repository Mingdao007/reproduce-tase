# Aborted Orientation Posture Sweep

Date: 2026-05-24

Branch: `exp/tase-ur10e-v17-orientation-posture-sweep`

This was the first focused full-speed E2/E3 orientation-gated posture sweep.
It completed `bend_0p10` and `bend_0p125` cases, then aborted while
calibrating the next posture because the sweep driver treated calibration
failure as fatal.

The failing condition was:

```text
ValueError: could not calibrate initial posture to target force: best force 0 N, target 5 N, tolerance 0.01 N
```

This root is retained as negative process evidence. The corrected rerun is:

`runs/orientation_posture_sweep/20260524T041329_calibration_safe`

Raw `.npz` files remain ignored by repository policy.
