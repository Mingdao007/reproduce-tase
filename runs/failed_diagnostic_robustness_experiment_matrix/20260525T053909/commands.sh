#!/usr/bin/env bash
set -euo pipefail

# Offline diagnostic robustness experiments planned by v99.
# These commands do not use live hardware, but they may be compute-heavy.

# base_z_plus1mm: Focused +1.0 mm base-z start/terminal/path bracket
/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_stage_a_base_z_bracket.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm --base-z-deltas-mm 1.0 --stage-a-durations-s 15.0,16.0,18.0

# positive_fast_timing_0p0075: Focused +1.0 mm positive fast-timing stitched sensitivity
/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_positive_stitched_sensitivity.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075 --base-z-deltas-mm 1.0 --scenarios paper_time_scale_0p0075

# positive_orientation_gate_0p119: Focused +1.0 mm positive orientation-gate boundary
/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_positive_orientation_gate_boundary.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119 --base-z-delta-mm 1.0 --orientation-gates 0.119,0.11925,0.1195,0.11975,0.1199,0.11995,0.11997,0.11998,0.12

# weighted_plus1mm_0p119_gate: Focused weighted +1.0 mm gate/time boundary
/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_weighted_gate_time_matrix.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate --base-z-deltas-mm 1.0 --boundary-base-z-delta-mm 1.0 --orientation-gates 0.119,0.11925,0.1195,0.11955,0.1196,0.1197,0.11995
