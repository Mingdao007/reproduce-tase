# Run Artifacts Manifest

This repo tracks lightweight migrated run metadata and plots. Large raw arrays
and large nested worktrees remain in the legacy source unless Git LFS is later
configured.

Legacy source root:

`/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/`

## Migrated Lightweight Runs

### Fig.5 scalar sweep

- Run: `runs/fig5_r_sweep/20260523T113301`
- Migrated: `metrics.yaml`, `metrics.json`, `fig5_r-sweep_20260523T113301.png`
- Omitted raw: `fig5_r-sweep_raw.npz`
- Status: legacy run, not yet re-run from this repo.

### Article-level synthetic E1-E4

- Run: `runs/full_article_experiments/20260523T114332`
- Migrated: metrics, CSV, summary Markdown, and PNG plots.
- Omitted raw: `article_experiments_raw.npz`
- Status: synthetic simulation reference, not PDF-verified paper truth.

### UR10e smoke

- Runs:
  - `runs/ur10e_smoke/20260523T113313`
  - `runs/ur10e_smoke/20260523T113341`
  - `runs/ur10e_smoke/20260523T113420`
- Migrated: metrics and PNG plots.
- Omitted raw: `ur10e-smoke_raw-state.npz`
- Status: legacy smoke runs, not yet re-run from this repo.

## New Repo Verification Runs

### Fig.5 scalar sweep

- Run: `runs/fig5_r_sweep/20260524T011145`
- Command:
  `python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml`
- Git state at run time:
  branch `exp/tase-ur10e-v0-paper-audit`, no initial commit yet, dirty tree
  with untracked migrated files.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `fig5_r-sweep_20260524T011145.png`
- Ignored raw artifact:
  `fig5_r-sweep_raw.npz`
- Result:
  completed with expected `pending_pdf_verify` warning.

### Fig.5 scalar sweep after initial PDF extraction

- Run: `runs/fig5_r_sweep/20260524T011603`
- Command:
  `python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml`
- Git state at run time:
  branch `exp/tase-ur10e-v0-paper-audit`, starting commit
  `fe8681582e5e28243c62042f41d91c9c16f107b6`, dirty tree with PDF extraction
  edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `fig5_r-sweep_20260524T011603.png`
- Ignored raw artifact:
  `fig5_r-sweep_raw.npz`
- Result:
  completed with remaining warnings for orientation signal dimension and `z0`
  source.

### UR10e MuJoCo smoke

- Run: `runs/ur10e_smoke/20260524T011145`
- Command:
  `python3 scripts/run_ur10e_mujoco_adaptation.py --config configs/mujoco_ur10e.yaml --smoke`
- Git state at run time:
  branch `exp/tase-ur10e-v0-paper-audit`, no initial commit yet, dirty tree
  with untracked migrated files.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `ur10e-smoke_contact-force_20260524T011145.png`,
  `ur10e-smoke_tcp-z_20260524T011145.png`
- Ignored raw artifact:
  `ur10e-smoke_raw-state.npz`
- Result:
  completed as approximate MJCF smoke only, not controller validation.

## V1 Math-Contract Branch Verification Runs

### Fig.5 smoke

- Run: `runs/fig5_r_sweep/20260524T012004`
- Command:
  `python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml --smoke`
- Git state at run time:
  branch `exp/tase-ur10e-v1-math-contracts`, starting commit
  `3ca7fe22ca70dab22368523cf5066b2dd30f9e84`, dirty tree with v1
  math-contract edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `fig5_r-sweep_20260524T012004.png`
- Ignored raw artifact:
  `fig5_r-sweep_raw.npz`
- Result:
  completed with expected remaining warnings for orientation signal dimension
  and `z0` source.

### UR10e MuJoCo smoke

- Run: `runs/ur10e_smoke/20260524T012004`
- Command:
  `python3 scripts/run_ur10e_mujoco_adaptation.py --config configs/mujoco_ur10e.yaml --smoke`
- Git state at run time:
  branch `exp/tase-ur10e-v1-math-contracts`, starting commit
  `3ca7fe22ca70dab22368523cf5066b2dd30f9e84`, dirty tree with v1
  math-contract edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `ur10e-smoke_contact-force_20260524T012004.png`,
  `ur10e-smoke_tcp-z_20260524T012004.png`
- Ignored raw artifact:
  `ur10e-smoke_raw-state.npz`
- Result:
  completed as approximate MJCF smoke only, not controller validation.

## V2 Controller Smoke Runs

### Simulation-only velocity controller smoke

- Run: `runs/controller_smoke/20260524T012218`
- Command:
  `python3 scripts/run_controller_smoke.py --config configs/mujoco_ur10e.yaml --duration-s 1.0`
- Git state at run time:
  branch `exp/tase-ur10e-v2-controller-smoke`, starting commit
  `17093c62c255b27e981b7244477e8c0d7057031e`, dirty tree with v2 controller
  smoke source edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `controller-smoke_qdot_20260524T012218.png`,
  `controller-smoke_tracking-error_20260524T012218.png`
- Ignored raw artifact:
  `controller-smoke_raw.npz`
- Result:
  completed. Solver success fraction `1.0`; maximum velocity-bound violation
  `0.0`; maximum joint-limit violation `0.0`.

## V3 Contact Force Ladder Runs

### Static contact-model force ladder

- Run: `runs/contact_force_ladder/20260524T012524`
- Command:
  `python3 scripts/run_contact_force_ladder.py --config configs/mujoco_ur10e.yaml --steps 500 --tail-steps 100 --tolerance-N 0.01`
- Git state at run time:
  branch `exp/tase-ur10e-v3-contact-force-ladder`, starting commit
  `ab94671f472a6043955dfdea5d605edc55c6dc33`, dirty tree with v3 contact
  ladder source edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `contact-force-ladder_offsets_20260524T012524.png`,
  `contact-force-ladder_target-vs-measured_20260524T012524.png`
- Result:
  completed. Targets `[0.5, 1.0, 2.0, 5.0] N` were matched with maximum
  absolute force error `0.0088706346160502 N`.
- Limit:
  This is a static model-offset calibration, not closed-loop force control.

## V4 Stationary Force Feedback Runs

### Stationary 5 N normal-force feedback

- Run: `runs/stationary_force_feedback/20260524T013040`
- Command:
  `python3 scripts/run_stationary_force_feedback.py --config configs/mujoco_ur10e.yaml --duration-s 4.0 --target-force-N 5.0 --gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5`
- Git state at run time:
  branch `exp/tase-ur10e-v4-stationary-force-feedback`, starting commit
  `082ab4e063b57bdd1cc23a4f436967a63d8497a0`, dirty tree with v4 stationary
  force-feedback source edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `stationary-force-feedback_force_20260524T013040.png`,
  `stationary-force-feedback_vz_20260524T013040.png`
- Ignored raw artifact:
  `stationary-force-feedback_raw.npz`
- Result:
  completed. Initial force `5.886648180968636 N`, final force
  `5.000002800044511 N`, tail mean absolute force error
  `2.8000475610912012e-06 N`, solver success fraction `1.0`, no qdot or
  joint-limit violation.
- Limit:
  This is stationary simulation-only normal-force feedback, not tangential
  force-motion trajectory tracking and not hardware validation.

## V5 Tangential Force-Motion Runs

### Low-speed x tangential motion with 5 N normal force

- Run: `runs/tangential_force_motion/20260524T013342`
- Command:
  `python3 scripts/run_tangential_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 4.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --tangential-velocity 0.0005,0.0 --tangential-kp 0.5`
- Git state at run time:
  branch `exp/tase-ur10e-v5-tangential-force-motion`, starting commit
  `387ad1dce8b83c0ba5e897a9683e6883661aaca6`, dirty tree with v5 tangential
  force-motion source edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `tangential-force-motion_force_20260524T013342.png`,
  `tangential-force-motion_xy_20260524T013342.png`
- Ignored raw artifact:
  `tangential-force-motion_raw.npz`
- Result:
  completed. Final x displacement `0.0019989989469737 m`, desired x
  displacement `0.0019990000000000008 m`, tail mean absolute force error
  `1.775978411200585e-05 N`, solver success fraction `1.0`, contact present
  fraction `1.0`, no qdot or joint-limit violation.
- Limit:
  This is low-speed simulation-only force-motion smoke. It still lacks
  orientation compliance and does not validate hardware.

## V6 Paper Trajectory Force-Motion Runs

### Paper E1 cycloid path with 5 N normal force

- Run: `runs/paper_trajectory_force_motion/20260524T013829`
- Command:
  `python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 8.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --trajectory e1-cycloid --amplitude-m 0.015 --omega-rad-s 0.1 --paper-time-scale 1.0 --planar-kp 0.5`
- Git state at run time:
  branch `exp/tase-ur10e-v6-paper-trajectory-force-motion`, starting commit
  `e47c2fe6d3ec1b17904623dcab1d787441d0183b`, dirty tree with v6 paper
  trajectory force-motion source edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `paper-trajectory-force-motion_force_20260524T013829.png`,
  `paper-trajectory-force-motion_xy_20260524T013829.png`
- Ignored raw artifact:
  `paper-trajectory-force-motion_raw.npz`
- Result:
  completed. Final tangential displacement
  `[0.0012394851720925958, 0.004549066283786667] m`, desired displacement
  `[0.0012387489718280922, 0.00454724750054618] m`, tail mean absolute force
  error `0.00898488092600231 N`, solver success fraction `1.0`, contact
  present fraction `1.0`, and no qdot or joint-limit violation.
- Limit:
  This is the paper E1 planar trajectory shape only. It is still
  simulation-only and lacks orientation compliance, torque dynamics, calibrated
  TCP, and hardware force source validation.

## V7 Paper Trajectory Matrix Runs

### Full-speed matrix under conservative qdot cap

- Run root: `runs/paper_trajectory_matrix/20260524T014139`
- Scope:
  E1-E4 paper trajectory shapes, `paper_time_scale = 1.0`, config default
  `0.05 rad/s` qdot cap.
- Tracked lightweight artifacts:
  per-trajectory `metrics.yaml`, `metrics.json`, force plot, xy plot, and root
  `git_state.md`.
- Ignored raw artifacts:
  per-trajectory `paper-trajectory-force-motion_raw.npz`.
- Result:
  E2 and E3 lost contact; retained as negative evidence.

### Full-speed matrix under 0.15 rad/s qdot cap

- Run root: `runs/paper_trajectory_matrix/20260524T014244`
- Scope:
  E1-E4 paper trajectory shapes, `paper_time_scale = 1.0`,
  `--qdot-limit-rad-s 0.15`, plus E2/E3 high-force-gain probes.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, and root
  `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  E2 and E3 still lost contact; high-force-gain probes saturated near the qdot
  cap and did not recover contact.

### Low-speed matrix accepted as v7 baseline

- Run root: `runs/paper_trajectory_matrix/20260524T014344`
- Scope:
  E1-E4 paper trajectory shapes, `paper_time_scale = 0.25`, config default
  `0.05 rad/s` qdot cap.
- Tracked lightweight artifacts:
  per-trajectory `metrics.yaml`, `metrics.json`, force plot, xy plot, and root
  `git_state.md`.
- Ignored raw artifacts:
  per-trajectory `paper-trajectory-force-motion_raw.npz`.
- Result:
  all four trajectories maintained contact, solver success, and hard-limit
  compliance. Tail mean absolute force errors were `2.7377314706467093e-06 N`
  for E1, `0.22110301894575918 N` for E2, `0.07713928700031802 N` for E3, and
  `2.7477968988542934e-06 N` for E4.
- Limit:
  This is a low-speed trajectory-shape baseline, not full-speed Section VI
  reproduction.

## V8 Weighted Normal Force-Motion Runs

### Full-speed weighted normal-force diagnostic

- Run root: `runs/weighted_normal_force_motion/20260524T014811`
- Scope:
  Full-speed E2/E3 probes and complete E1-E4 weighted matrix using
  `--normal-axis-weight 100`, `--planar-axis-weight 1`,
  `--force-gain 5e-4`, and `--qdot-limit-rad-s 0.15`.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, and root
  `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  Contact and force regulation were recovered for E1-E4 at full paper time
  scale. E2 and E3 still showed large planar tracking errors:
  `0.02114519099848796 m` and `0.016169767707432416 m` max error.
- Limit:
  This is diagnostic evidence for task-priority design. It is not a final
  full-speed paper trajectory reproduction.

## V9 Normal Guard Force-Motion Runs

### Full-speed scalar normal guard diagnostic

- Run root: `runs/normal_guard_force_motion/20260524T015341`
- Scope:
  Full-speed E2/E3 scalar guard probes plus a guarded E1-E4 matrix using
  `normal_axis_weight = 50`, `force_gain = 5e-4`,
  `--qdot-limit-rad-s 0.15`, and `normal_guard_force_fraction = 0.9`.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, and root
  `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  Equal-axis guarding did not preserve E2/E3 force. Guarded
  `normal_axis_weight = 50` maintained contact, but E2/E3 retained max planar
  errors `0.020166709027307318 m` and `0.015963081975681002 m`.
- Limit:
  The scalar guard is diagnostic only. It does not solve the full-speed E2/E3
  controller tradeoff.

## Full Paper MATLAB/RNN Run

### Selected migrated evidence

- Legacy run: `runs/full_paper_matlab/20260523T114034`
- Migrated:
  selected Markdown reports and PNG verification figures under
  `runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/`, plus the
  artifact README.
- Reason:
  These files are lightweight enough for the initial ordinary Git commit and
  preserve the report links for Fig.5/Fig.6 evidence.
- Omitted:
  MATLAB source worktree files, `.mat` raw data, tarball snapshots, logs, and
  archive payloads.
- Current documentation:
  `reports/full_article_reproduction_report.md` summarizes the result and
  legacy paths.
- Future action:
  Decide whether to migrate selected MATLAB source, use Git LFS for raw
  artifacts, or preserve the legacy path as external provenance.
