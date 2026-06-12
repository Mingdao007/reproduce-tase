# IK/RNN Offline Frontier Summary

Run root: `runs/ik_rnn_offline_frontier/20260612T000000`

- Audit passed: `True`
- Position error: `2.291288` mm -> `0.000003` mm
- Orientation error: `1.718873` deg -> `1.224466` deg
- Solver success fraction: `1.0`
- Max |qdot|: `0.15` rad/s under `0.15` rad/s
- Completion claim allowed: `False`

Figures:

- Position error: `runs/ik_rnn_offline_frontier/20260612T000000/ik-rnn-position-error_20260612T000000.png`
- Orientation error: `runs/ik_rnn_offline_frontier/20260612T000000/ik-rnn-orientation-error_20260612T000000.png`
- qdot utilization: `runs/ik_rnn_offline_frontier/20260612T000000/ik-rnn-qdot-utilization_20260612T000000.png`

Interpretation:

- This is an offline constrained IK/RNN inner-loop frontier, not a live robot run.
- The run verifies the simple finite-time velocity law can reduce a small TCP pose error while respecting the selected qdot envelope.
- It does not resolve contact-force modeling, strict paper-equivalent feasibility, robustness, or hardware readiness.
