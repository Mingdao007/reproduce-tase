# Git State

- Run root: `runs/nullspace_orientation_timing_sweep/20260524T042206`
- Branch: `exp/tase-ur10e-v18-nullspace-orientation`
- Starting commit: `3ab4c4ef8b832230682d89668cc3621e6c493ea4`
- Dirty state: `M scripts/run_paper_trajectory_force_motion.py
 M scripts/run_posture_feasibility_sweep.py
 M scripts/run_timing_feasibility_sweep.py
 M src/tase_repro/constraints.py
 M src/tase_repro/controller.py
 M src/tase_repro/force_feedback.py
 M tests/test_constraints.py
 M tests/test_controller.py
?? runs/nullspace_orientation_timing_sweep/`
- Scope:
  Force-motion feasibility sweep for `e2-figure-eight, e3-circle` with time scales `1.0,0.75,0.5,0.35,0.25,0.2,0.15,0.1,0.075`.
- Orientation task:
  mode `hold`, priority `linear-primary`, kp `1.0`, angular axis weight `1.0`, angular slack weight `1.0`.
- Orientation gates:
  max orientation error `0.03`, max angular slack `0.03`.
- Note:
  Raw `.npz` files are ignored by repo policy. Metrics, plots, and aggregate summaries are tracked.
