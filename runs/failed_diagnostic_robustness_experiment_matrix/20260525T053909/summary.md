# Failed Diagnostic Robustness Experiment Matrix

Run root: `/home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909`

- Status: `planned_not_executed`
- Experiment count: `4`
- Planned-not-executed count: `4`
- Source failed cells: `['base_z_plus1mm', 'positive_fast_timing_0p0075', 'positive_orientation_gate_0p119', 'weighted_plus1mm_0p119_gate']`
- Commands file: `/home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/commands.sh`

## Experiments

### base_z_plus1mm

- Title: Focused +1.0 mm base-z start/terminal/path bracket
- Status: `planned_not_executed`
- Output dir: `/home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm`
- Command: `/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_stage_a_base_z_bracket.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm --base-z-deltas-mm 1.0 --stage-a-durations-s 15.0,16.0,18.0`

### positive_fast_timing_0p0075

- Title: Focused +1.0 mm positive fast-timing stitched sensitivity
- Status: `planned_not_executed`
- Output dir: `/home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075`
- Command: `/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_positive_stitched_sensitivity.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075 --base-z-deltas-mm 1.0 --scenarios paper_time_scale_0p0075`

### positive_orientation_gate_0p119

- Title: Focused +1.0 mm positive orientation-gate boundary
- Status: `planned_not_executed`
- Output dir: `/home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119`
- Command: `/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_positive_orientation_gate_boundary.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119 --base-z-delta-mm 1.0 --orientation-gates 0.119,0.11925,0.1195,0.11975,0.1199,0.11995,0.11997,0.11998,0.12`

### weighted_plus1mm_0p119_gate

- Title: Focused weighted +1.0 mm gate/time boundary
- Status: `planned_not_executed`
- Output dir: `/home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate`
- Command: `/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_weighted_gate_time_matrix.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate --base-z-deltas-mm 1.0 --boundary-base-z-delta-mm 1.0 --orientation-gates 0.119,0.11925,0.1195,0.11955,0.1196,0.1197,0.11995`

## Claim Boundary

- This matrix only plans offline diagnostic simulation commands.
- It does not execute experiments, prove robustness, calibrate contact geometry,
  accept a gate, authorize hardware, or mark the goal complete.
