# Plus1mm Unresolved Diagnostic Probe Summary

Run root: `/home/andy/reproduce-tase/runs/plus1mm_unresolved_diagnostic_probe/20260525T062237`

- Planned failed cells: `4`
- Executed cells: `4`
- Closed cells: `0`
- Not-executed cells: `0`
- Unresolved cells: `4`
- Qdot-limited cells: `positive_fast_timing_0p0075`
- Orientation-limited cells: `base_z_plus1mm, positive_fast_timing_0p0075, positive_orientation_gate_0p119, weighted_plus1mm_0p119_gate`

## Cell Signatures

| cell | class | closure | key margin | qdot sat | blockers |
| --- | --- | --- | ---: | ---: | --- |
| `base_z_plus1mm` | `start_terminal_path_unrecovered` | `False` | `0.0004856078654814633` | `n/a` | `start_contact_not_recovered, terminal_orientation_over_gate, path_geometry_not_recovered, duration_not_recovered` |
| `positive_fast_timing_0p0075` | `fast_timing_e2_qdot_and_orientation` | `False` | `0.0002030587287190494` | `0.999` | `e2_qdot_saturation, e2_tail_qdot_utilization, e2_orientation_over_gate` |
| `positive_orientation_gate_0p119` | `unweighted_orientation_margin` | `False` | `0.0009788204275829049` | `0.006` | `current_gate_stage_a_terminal_orientation, current_gate_stage_b_orientation, replacement_gate_not_accepted` |
| `weighted_plus1mm_0p119_gate` | `weighted_orientation_margin_without_qdot_saturation` | `False` | `0.0005664520369604714` | `0.0` | `current_gate_stage_a_terminal_orientation, current_gate_stage_b_orientation, replacement_gate_not_accepted` |

## Ranked Orientation Excess Over Current Gate

| cell | quantity | excess rad | excess deg |
| --- | --- | ---: | ---: |
| `positive_fast_timing_0p0075` | `stage_b_max_orientation` | `0.0012030587287190503` | `0.06893018766197583` |
| `positive_orientation_gate_0p119` | `stage_b_max_orientation` | `0.0009788204275829049` | `0.05608227940169108` |
| `weighted_plus1mm_0p119_gate` | `stage_b_max_orientation` | `0.0005664520369604714` | `0.03245531101442353` |
| `base_z_plus1mm` | `terminal_orientation` | `0.0004856078654814633` | `0.02782328119044446` |

Interpretation:

- The four v99 failed cells are all executed and all remain unresolved.
- The only `+1.0 mm` row with a qdot-saturation blocker is the unweighted fast-timing `paper_time_scale = 0.0075` case.
- The orientation-gate rows remain above the current `0.119 rad` gate, and the diagnostic replacement gates are not accepted.
- This is post-hoc offline bookkeeping over existing metrics. It does not close a cell, calibrate contact geometry, or authorize hardware work.
