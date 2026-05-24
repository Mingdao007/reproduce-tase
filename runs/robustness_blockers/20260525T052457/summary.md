# Robustness Blockers Audit

Run root: `/home/andy/reproduce-tase/runs/robustness_blockers/20260525T052457`

- Robustness complete: `False`
- Completion claim allowed: `False`
- Offline-actionable from v95: `True`
- Baseline stitched pass count: `4 / 9`
- Positive matrix pass count: `37 / 40`
- Primary blocker: `accepted_model_robustness_not_closed`
- Unresolved blockers: `['base_z_plus_1mm_contact_or_terminal_orientation', 'base_z_minus_path_duration_or_geometry_margin', 'faster_timing_qdot_tail_utilization', 'tightened_orientation_gate_plus1mm', 'contact_model_calibration_missing']`

## Claim Boundary

- This audit is offline simulation bookkeeping only.
- It does not prove robustness, strict paper-equivalent feasibility,
  contact calibration, gate acceptance, or hardware readiness.
