# Decision Record

## D001: Use `Mingdao007/reproduce-tase` As Authoritative Repo

- Date: 2026-05-24
- Status: accepted
- Decision:
  Use `https://github.com/Mingdao007/reproduce-tase` as the authoritative home
  for reproduction code, configs, plans, reports, and lightweight metadata.
- Reason:
  The old UR10e workspace contains many unrelated and untracked experiment
  folders. A dedicated repo is needed for rollback and review.
- Consequence:
  Existing local artifacts are migrated selectively. Heavy raw artifacts are
  represented by manifests unless Git LFS is explicitly configured.

## D002: Keep MuJoCo As Baseline Simulator

- Date: 2026-05-24
- Status: accepted for v0/v1
- Decision:
  Keep MuJoCo as the first reproducible simulation baseline.
- Reason:
  Existing scripts and plans already target MuJoCo, and the user requested it
  as the default while allowing alternatives.
- Consequence:
  Other simulators can be proposed later, but not before the MuJoCo baseline is
  audited.

## D003: No Real Robot Motion Or Writes In Current Phase

- Date: 2026-05-24
- Status: accepted
- Decision:
  Current work is documentation, migration, audit, and simulation only.
- Reason:
  TCP, payload, force source, OnRobot force reference, and contact setup are
  unresolved.
- Consequence:
  Hardware work remains read-only until a separate user-approved SOP exists.

## D004: Treat Existing E1-E4 Results As Synthetic

- Date: 2026-05-24
- Status: accepted
- Decision:
  Existing article-level E1-E4 results are useful migration evidence, but not
  final paper-truth reproduction.
- Reason:
  PDF extraction is still pending and the current configs include provisional
  values.
- Consequence:
  Reports must state "UR10e adapted reproduction" or "synthetic simulation"
  where appropriate.

## D005: Keep Orientation Signal Ambiguity Open

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record the Section V signal `u = [cos(0.1t), sin(0.1t)]` as PDF-extracted,
  but keep its implementation interpretation unresolved.
- Reason:
  Earlier in the paper, orientation compliance is described using a force
  direction vector and rotation matrix. The Section V notation appears
  lower-dimensional and cannot be transferred to UR10e without an explicit
  convention.
- Consequence:
  `configs/paper_truth.yaml` keeps orientation dimension resolution in
  `pending_pdf_verify`.

## D006: Use Repo Test Wrapper With Pytest Plugin Autoload Disabled

- Date: 2026-05-24
- Status: accepted
- Decision:
  Use `scripts/run_tests.sh` as the test entry point.
- Reason:
  The bench has system pytest `6.2.5` and a user-site `anyio` pytest plugin
  that expects newer pytest internals. Direct `python3 -m pytest` failed during
  plugin loading before collecting repo tests.
- Consequence:
  The wrapper sets `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and then runs
  `python3 -m pytest -q`.

## D007: Start Controller With No-Contact Velocity-Level Smoke

- Date: 2026-05-24
- Status: accepted
- Decision:
  Implement the first controller path as a simulation-only velocity-level TCP
  smoke test, not as force/contact control.
- Reason:
  The MuJoCo model is approximate, the force source is unresolved, and
  OnRobot/RTDE force-frame issues are still open. A bounded velocity task is
  the smallest useful step that validates the UR10e 6DOF hard-limit contract.
- Consequence:
  Contact-force ladder work must come next before any claim about force-motion
  control.

## D008: Use Static Model Offset For First Contact Force Ladder

- Date: 2026-05-24
- Status: accepted
- Decision:
  Use tiny `base_link` z offsets to create calibrated static contact forces in
  the v1 approximate MuJoCo model.
- Reason:
  The current objective is to verify contact force sign and target-force
  measurement behavior before implementing closed-loop force control. Direct
  model offsets are deterministic and avoid pretending a controller exists.
- Consequence:
  The ladder results are valid only as MuJoCo contact-model evidence. They are
  not robot motion, not closed-loop control, and not hardware validation.

## D009: Use Lightly Bent Posture For Stationary Force Feedback

- Date: 2026-05-24
- Status: accepted
- Decision:
  Use `q = [0, -0.02, 0.03, -0.01, 0, 0]` and a small `base_link` z offset for
  the first stationary force-feedback simulation.
- Reason:
  At the zero pose, the approximate MJCF has a TCP z Jacobian row of zero, so
  joint velocity commands cannot regulate normal contact force. The lightly
  bent posture gives a nonzero z Jacobian while keeping the motion small.
- Consequence:
  The stationary force-feedback result is a simulation scaffolding result. It
  must not be translated to real UR10e posture or motion without a separate
  hardware gate.

## D010: Start Force-Motion With Straight Low-Speed Tangential Smoke

- Date: 2026-05-24
- Status: accepted
- Decision:
  Validate force-motion coupling first with a straight, low-speed x-direction
  tangential TCP command while holding 5 N normal force.
- Reason:
  This isolates force-motion coupling before adding paper trajectory geometry
  and orientation compliance.
- Consequence:
  The result is the first UR10e adapted force-motion smoke, but it is not yet a
  paper trajectory reproduction.

## D011: Use Paper E1 Cycloid As First Paper-Shaped Contact Path

- Date: 2026-05-24
- Status: accepted
- Decision:
  Add the Section VI Experiment 1 cycloid as the first paper-shaped
  force-motion path in MuJoCo, using the PDF-extracted planar formula with
  no time scaling.
- Reason:
  The straight v5 smoke already isolated force-motion coupling. E1 is the
  smallest next step because it adds real paper geometry while avoiding the
  larger E2-E4 trajectory matrix and still keeping orientation compliance out
  of scope.
- Consequence:
  The v6 result can be described as a paper-trajectory-shaped simulation smoke,
  not a full paper reproduction. Orientation compliance, force-source
  reconciliation, and hardware validation remain blocked.

## D012: Record Full-Speed E2/E3 Contact Loss And Use Low-Speed Matrix

- Date: 2026-05-24
- Status: accepted
- Decision:
  Keep the full-speed E1-E4 matrix attempts as negative evidence and use a
  `paper_time_scale = 0.25` E1-E4 matrix as the v7 baseline.
- Reason:
  E2 and E3 lost contact at full paper time scale under both the initial
  `0.05 rad/s` qdot cap and a `0.15 rad/s` simulation cap. Increasing the
  force gain saturated qdot and still did not restore contact. The low-speed
  matrix isolates trajectory-shape support without hiding the full-speed
  controller limitation.
- Consequence:
  v7 demonstrates simulation-only E1-E4 shape tracking in contact at low
  speed. Full-speed E2/E3 remain open controller issues.

## D013: Treat Axis Weighting As Diagnostic, Not Final Controller

- Date: 2026-05-24
- Status: accepted
- Decision:
  Add row-wise Cartesian axis weights to the velocity solve and use high
  normal-axis weights to diagnose the full-speed E2/E3 contact-loss blocker.
- Reason:
  Trace inspection showed the equal-weight solve could command negative z after
  contact loss but still realize positive z because planar tracking dominated
  the coupled Jacobian. Axis weighting is the smallest change that can test
  whether prioritizing normal motion recovers contact.
- Consequence:
  The weighted v8 matrix recovers contact and force regulation but creates
  unacceptable planar error on E2/E3. The next controller needs explicit
  priority or slack accounting, not just larger weights.

## D014: Reject Scalar Planar Guard As Full-Speed Fix

- Date: 2026-05-24
- Status: accepted
- Decision:
  Keep the normal-force planar-speed guard as diagnostic instrumentation, but
  do not treat it as the full-speed E2/E3 fix.
- Reason:
  Equal-axis guarding suppresses planar motion but still loses force. Moderate
  normal-axis weighting with guarding keeps contact but retains centimeter-scale
  E2/E3 planar error and qdot saturation.
- Consequence:
  The next controller step must expose normal and planar residuals explicitly,
  likely with slack variables or a true task-priority solve.

## D015: Treat Solver Success As Insufficient Without Task Residuals

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record unweighted normal and planar TCP velocity residuals for force-motion
  runs.
- Reason:
  Prior full-speed E2/E3 runs had solver success `1.0` even when contact was
  lost or planar tracking was unacceptable. The bounded solver can satisfy its
  numerical objective while failing the reproduction task.
- Consequence:
  Future pass/fail criteria must include task residuals, contact fraction,
  force error, qdot saturation, and joint-limit violation.

## D016: Use Slack Metrics To Define Feasibility, Not To Claim Success

- Date: 2026-05-24
- Status: accepted
- Decision:
  Add an opt-in slack-aware velocity solve, but treat its E2/E3 outputs as
  feasibility diagnostics rather than successful full-speed reproduction.
- Reason:
  Explicit slack variables show the same hard tradeoff as weighted residuals:
  force/contact can be recovered by assigning large planar slack, but that
  violates trajectory tracking expectations.
- Consequence:
  The next experiment should define pass/fail thresholds and search for
  feasible timing/posture changes before adding more controller features.

## D017: Gate Timing Feasibility With Sustained Qdot Saturation Metrics

- Date: 2026-05-24
- Status: accepted
- Decision:
  Treat qdot cap contact as a pass/fail issue only when it is sustained, using
  qdot saturation fraction and tail max qdot utilization rather than a single
  max qdot sample.
- Reason:
  The slack-aware controller can briefly touch the velocity cap during startup
  even when the later trajectory is well within limits. A single max sample
  would reject otherwise useful slowed-timing baselines, while sustained tail
  saturation still indicates the trajectory/controller combination is not
  feasible.
- Consequence:
  For E2/E3 under the current posture and slack-aware controller,
  `paper_time_scale = 0.2` is the fastest tested timing that passes the current
  force, contact, slack, position, limit, and sustained qdot saturation gates.

## D018: Treat Initial Posture As A Simulation Feasibility Variable

- Date: 2026-05-24
- Status: accepted
- Decision:
  Sweep small simulation-only initial postures with per-posture static contact
  calibration before adding more controller features.
- Reason:
  v12 showed a timing limitation at the near-straight posture, but the UR10e
  6DOF Jacobian coupling can change substantially with even small bends. A
  posture sweep tests whether the blocker is controller formulation alone or a
  posture/conditioning issue.
- Consequence:
  The `bend_0p10` simulation posture passes current full-speed E2/E3 gates and
  becomes the next MuJoCo baseline. It is not approved for real robot motion;
  hardware use still requires measured TCP/payload/force source and an
  explicit SOP.

## D019: Use Bend 0p10 As The Full-Speed MuJoCo Matrix Baseline

- Date: 2026-05-24
- Status: accepted
- Decision:
  Use the calibrated `bend_0p10` posture as the current full-speed MuJoCo
  baseline for the complete E1-E4 force-motion trajectory matrix.
- Reason:
  v14 shows E1, E2, E3, and E4 all pass the v12 feasibility gates at
  `paper_time_scale = 1.0` with the same slack-aware controller settings,
  qdot cap, force gain, and calibrated initial contact setup.
- Consequence:
  The next simulation work can build orientation compliance or a planned
  approach phase from this baseline. The posture is still not a real robot
  command and does not relax the hardware safety gate.

## D020: Treat Orientation Hold As A Soft Measured Task

- Date: 2026-05-24
- Status: accepted
- Decision:
  Add an opt-in TCP orientation-hold task with angular residual and slack
  metrics, but keep it soft and lower priority than normal-force and planar
  force-motion gates.
- Reason:
  Stronger angular priority reduces orientation error but breaks full-speed
  E1-E4 planar tracking on the 6DOF UR10e transfer. A very low angular slack
  weight preserves the v14 force-motion gates while exposing residual
  orientation error instead of hiding the missing orientation term.
- Consequence:
  Orientation is now measurable in the MuJoCo controller, but it is not yet a
  paper-faithful orientation compliance result. The next step is an explicit
  orientation gate or task-priority formulation.

## D021: Gate Orientation Separately From Force-Motion

- Date: 2026-05-24
- Status: accepted
- Decision:
  Add optional orientation feasibility thresholds and use provisional gates of
  `0.03 rad` max orientation error and `0.03 rad/s` max angular slack for the
  first orientation-hold timing sweep.
- Reason:
  v15 showed that a full-speed force-motion pass can still carry large
  orientation error when the angular task is very low priority. The gate makes
  that tradeoff explicit and prevents force/contact success from hiding
  orientation failure.
- Consequence:
  The current common E1-E4 matrix that passes force-motion plus orientation
  gates is slowed to `paper_time_scale = 0.075`. Full-speed orientation-gated
  reproduction remains open.

## D022: Do Not Claim Full-Speed Orientation-Gated Success From Posture Tuning

- Date: 2026-05-24
- Status: accepted
- Decision:
  Treat the v17 small-posture and angular-priority bracket as negative
  evidence for full-speed E2/E3 orientation-gated feasibility under the
  current velocity-level controller.
- Reason:
  `bend_0p10` and `bend_0p125` both calibrate to the `5 N` initial-contact
  target, but at angular slack weight `0.1` they satisfy the orientation gates
  only while failing planar position and planar slack gates. Reducing angular
  priority restores planar tracking only by failing the orientation gates,
  especially on E3.
- Consequence:
  The current accepted orientation-gated fallback remains the v16 common
  `paper_time_scale = 0.075` E1-E4 matrix. The next full-speed attempt should
  be a true task-priority/null-space-aware solve or a paper-specific
  orientation signal extraction, not a claim based on small posture tuning.

## D023: Prefer Linear-Primary Orientation Over Weighted Angular Priority

- Date: 2026-05-24
- Status: accepted
- Decision:
  Use the v18 linear-primary orientation option as the cleaner controller
  baseline for the current `paper_time_scale = 0.075` orientation-gated
  fallback.
- Reason:
  The two-stage solve preserves the first-stage TCP linear velocity and then
  optimizes orientation hold inside the remaining feasible velocity space. It
  removes the v17 planar-slack failure mode and passes the E1-E4 combined gate
  matrix at `0.075` with smaller planar errors than the weighted angular solve.
- Consequence:
  This is still not full-speed reproduction. Full-speed E2/E3 remain rejected
  because qdot saturation and orientation residuals bind at higher paper-time
  scales. Further full-speed attempts need paper-specific orientation
  extraction, planned orientation/timing scheduling, or a separate qdot-budget
  decision.

## D024: Keep Paper Orientation Compliance Separate From UR10e Orientation Hold

- Date: 2026-05-24
- Status: accepted
- Decision:
  Treat the paper's orientation law as force-normal-derived orientation
  compliance, with `u = F / ||F||`, `R_d` from the paper's Rodrigues-like
  expression, quaternion error, and `xdot_o = k_o e_o` under the unknown-surface
  slow-variation assumption. Keep the current UR10e `linear-primary`
  orientation result labeled as adapted initial-orientation hold.
- Reason:
  PDF extraction resolves the Section VI gains and force-sensor filtering
  note, but it also confirms a real ambiguity: Section III defines `u` as a
  3D normalized force vector, while Section V writes a 2D signal
  `[cos(0.1t), sin(0.1t)]`. The extracted Eq. (10) also applies scalar
  trigonometric functions to `u`.
- Consequence:
  Future full-speed orientation claims must either resolve the paper's
  orientation-signal ambiguity or explicitly document an adapted UR10e
  orientation schedule. The v18 slowed `0.075` matrix remains the current
  orientation-gated simulation fallback, not a paper-faithful orientation
  compliance reproduction.

## D025: Treat Section V Orientation Signal As A Verified Paper Ambiguity

- Date: 2026-05-24
- Status: accepted
- Decision:
  Remove `orientation_signal_dimension_resolution` from
  `pending_pdf_verify` and record it as a known paper ambiguity. Future
  paper-orientation implementation must use the Section III 3D force-normal
  contract, `u = F / ||F||`, or explicitly label any 2D Section V orientation
  schedule as adapted.
- Reason:
  Multiple PDF extraction modes agree that Section V contains only
  `u = [cos(0.1t), sin(0.1t)]`, with no hidden third component. Section III
  still defines `u` as a three-component normalized force vector and Eq. (9)
  uses `u1`, `u2`, and `u3`.
- Consequence:
  The repo should not infer a missing third component and call it paper truth.
  The only remaining Section V PDF-verification field is `z0_source`.

## D026: Implement Force-Normal Orientation As Explicit UR10e Convention

- Date: 2026-05-24
- Status: accepted
- Decision:
  Add `orientation_mode="force_normal"` as a simulation-only mode that aligns
  the TCP local z-axis to the measured 3D MuJoCo contact-normal force vector
  and preserves the initial TCP local x-axis projected into the tangent plane.
- Reason:
  The paper's Section III contract requires a 3D force-normal orientation
  input, but it does not specify yaw about the normal and Section V's 2D signal
  is a verified ambiguity. The repo needs an explicit, testable convention
  rather than an implied hidden paper value.
- Consequence:
  Force-normal orientation can now be tested independently from the old
  initial-orientation hold mode. Results must still be labeled UR10e adapted
  simulation because the yaw convention, MuJoCo force source, and kinematic
  velocity-level controller are not the paper's full torque/RNN system.

## D027: Add Tilted Plane And Contact-Normal Force Correction

- Date: 2026-05-24
- Status: accepted
- Decision:
  Add a 10 degree tilted MuJoCo plane and a `normal_velocity_mode =
  "contact_normal"` controller option. Keep the previous `world_z` normal
  correction as the default for backward-compatible flat-plane runs.
- Reason:
  The v21 force-normal orientation smoke used a flat plane, so the measured
  force normal was `[0, 0, 1]` and did not test nontrivial surface-normal
  alignment. On a tilted plane, applying the scalar force correction only in
  world z is geometrically inconsistent with the measured contact-normal
  direction.
- Consequence:
  The tilted-plane smoke exposes a controller tradeoff: high orientation gain
  pulls the TCP toward the tilted normal but saturates the `0.15 rad/s` qdot
  budget, while low gain avoids saturation but leaves large orientation error.
  Further progress needs a small gain/timing sweep and then an explicit
  orientation approach-phase or qdot-budget decision if scalar gain tuning does
  not pass the existing gates.

## D028: Stop Scalar Gain Tuning For Tilted Orientation Gates

- Date: 2026-05-24
- Status: accepted
- Decision:
  Do not claim tilted force-normal orientation feasibility from scalar
  orientation-gain/time-scale tuning alone. The next controller step should be
  a staged orientation approach phase before paper-trajectory tracking, or an
  explicitly documented qdot-budget relaxation.
- Reason:
  The v23 tilted gain/timing sweep tested 18 E1 cases across orientation gains
  `0.1`, `0.25`, `0.5`, `1.0`, `2.0`, and `5.0` and paper time scales
  `0.05`, `0.075`, and `0.1`. No case passed the existing gates. Low gains
  avoided qdot saturation but failed the `0.03 rad` max-orientation-error gate
  because the run starts about `0.174 rad` away from the tilted normal. Gains
  at or above `0.5` also failed qdot saturation and angular-slack gates.
- Consequence:
  Further tilted-surface work should move the initial orientation mismatch out
  of the paper-trajectory run through an explicit approach/pre-alignment phase,
  or make a transparent decision to spend more joint-velocity budget. More
  unlabeled scalar gain sweeps are not enough evidence.

## D029: Separate Approach-Phase Feasibility From Trajectory-Phase Feasibility

- Date: 2026-05-24
- Status: accepted
- Decision:
  Report staged tilted orientation runs with separate approach and trajectory
  gates. A paper trajectory may be allowed to start after prealignment, but the
  approach phase must not be hidden inside the trajectory pass/fail result.
- Reason:
  The v24 staged run shows that weighted prealignment can reduce tilted-normal
  orientation error to `0.0020237968932491765 rad`, after which the E1
  trajectory phase passes all current gates. The same approach phase fails the
  ordinary feasibility gate because it has qdot saturation fraction `0.961`,
  max planar drift `0.009738544642078033 m`, and max angular slack
  `0.06085033484246333 rad/s`.
- Consequence:
  The repo can now distinguish "trajectory after approach passes" from "full
  staged maneuver passes." The next controller work should reduce approach
  drift and saturation, or explicitly document a separate relaxed approach
  budget before trajectory tracking.

## D030: Stop Simple Slack Bracketing For Tilted Stage A

- Date: 2026-05-24
- Status: accepted
- Decision:
  Do not claim a full staged tilted-plane maneuver pass from simple Stage A
  scalar gain, slack-weight, or priority-mode bracketing.
- Reason:
  The v25 bracket tested seven E1 Stage A cases. Five reached the terminal
  orientation threshold, and three allowed the following trajectory phase to
  pass, but no approach phase passed the ordinary feasibility gate. Weighted
  cases that align the tilted normal still spend sustained qdot saturation and
  millimeter-scale planar drift. Higher planar slack weights trade drift for
  larger angular slack and failed terminal alignment. The linear-primary
  approach preserves planar position but stalls at about `0.074 rad`, above
  the `0.03 rad` threshold.
- Consequence:
  Further tilted Stage A work should be a controller redesign, an explicitly
  scheduled longer approach with approach-specific gates, or a transparent
  decision to treat prealignment as a separate relaxed-budget maneuver. More
  unlabeled scalar slack bracketing is not enough evidence.

## D031: Stop Longer Low-Gain Stage A Probes Under Same Controller

- Date: 2026-05-24
- Status: accepted
- Decision:
  Do not continue longer low-gain Stage A probes under the same weighted or
  linear-primary controller formulation.
- Reason:
  The v26 probe tested six longer approaches from 4 to 18 seconds. Three
  weighted cases reached the terminal orientation threshold, but no case
  passed the terminal approach budget, ordinary approach feasibility, the
  trajectory-after-approach gate, or full staged feasibility. Low-gain
  weighted cases still had qdot saturation fractions above `0.526` and planar
  drift above `0.0039 m`. The long linear-primary reference preserved planar
  position but stalled at about `0.074 rad`.
- Consequence:
  Further Stage A progress requires a controller change, such as an
  orientation-rate-limited approach schedule, or an explicit relaxed-budget
  prealignment decision. More duration/gain probes with the same objective are
  unlikely to produce useful evidence.

## D032: Keep Angular-Command Cap As Instrumentation, Not Stage A Fix

- Date: 2026-05-24
- Status: accepted
- Decision:
  Keep the v27 angular-command cap API and CLI surface, but do not claim that
  angular-command capping solves the tilted Stage A approach.
- Reason:
  The v27 rate-cap probe shows that the cap is respected in all six cases.
  Weighted capped cases reduce qdot saturation compared with the uncapped
  baseline, but still fail the terminal approach budget. The best capped
  weighted qdot saturation fraction is `0.46366666666666667`, and planar drift
  remains above `0.0075 m`. The capped `linear-primary` reference preserves
  planar position but stalls at about `0.074 rad`, above the `0.03 rad`
  terminal threshold.
- Consequence:
  Further Stage A work should change task structure or explicitly define a
  relaxed approach budget. Candidate next steps are position-hold constraints,
  a documented relaxed-budget prealignment state, or a task-priority approach
  that gives contact/position first claim on the velocity budget.

## D033: Relaxed Stage A Qdot Alone Is Not An Approach Budget

- Date: 2026-05-24
- Status: accepted
- Decision:
  Keep separate Stage A and Stage B qdot-limit support, but do not accept
  relaxed Stage A qdot alone as the tilted prealignment solution.
- Reason:
  The v28 probe tested weighted and `linear-primary` approaches with Stage A
  caps up to `0.50 rad/s` while keeping Stage B at `0.15 rad/s`. No case passed
  the terminal approach budget or full staged feasibility. Weighted cases
  aligned the tilted normal but still saturated the relaxed cap and drifted
  about `8 mm`. `linear-primary` cases preserved planar position but stalled
  near `0.074 rad`, above the terminal orientation threshold.
- Consequence:
  Future work should either change the task structure or explicitly accept a
  relaxed-drift prealignment phase separate from paper-trajectory feasibility.
  Qdot relaxation by itself is not enough evidence.

## D034: Do Not Accept Partial E1-E4 After Prealignment As Full Staged Reproduction

- Date: 2026-05-24
- Status: accepted
- Decision:
  Do not claim a complete staged tilted-plane E1-E4 reproduction from the v29
  trajectory-after-prealignment matrix.
- Reason:
  The v29 matrix repeats the weighted tilted-normal prealignment and then runs
  the slowed Section VI E1-E4 trajectories for `8 s` at
  `paper_time_scale = 0.075`. E1, E3, and E4 pass the Stage B trajectory gate,
  but E2 fails due qdot saturation fraction `0.9935` and tail qdot utilization
  `1.0`. The approach phase also fails ordinary feasibility in all four cases
  because the repeated weighted approach saturates qdot for the full approach
  and drifts `0.008347977658392892 m` tangentially.
- Consequence:
  Keep the v29 run as partial trajectory-after-prealignment evidence. The next
  isolated blocker is E2 after prealignment, or a genuinely different Stage A
  task structure that avoids both planar drift and sustained qdot saturation.

## D035: Stop Scalar E2 Timing/Gain Brackets Under Same Posture

- Date: 2026-05-24
- Status: accepted
- Decision:
  Do not keep expanding scalar E2 post-prealignment timing or trajectory
  orientation-gain brackets under the same posture and task structure.
- Reason:
  The v30 E2 bracket tested 12 cases crossing `paper_time_scale` values
  `0.075`, `0.05`, and `0.025` with trajectory orientation gains `0.10`,
  `0.05`, `0.02`, and `0.00`. No case passed the trajectory-after-approach
  or full staged gate. Every case failed only qdot saturation and tail qdot
  utilization. Even the slowest zero-gain case had qdot saturation fraction
  `0.906` and tail qdot utilization `1.0`.
- Consequence:
  Treat E2 after prealignment as a kinematic velocity-budget blocker. The next
  useful experiments should change posture, the prealignment terminal
  configuration, tangent task allocation, or add an explicit posture/nullspace
  objective before E2.

## D036: Threshold-Duration Stage A Does Not Fix E2

- Date: 2026-05-24
- Status: accepted
- Decision:
  Do not treat stopping the weighted Stage A near its first terminal
  orientation threshold crossing as the E2 fix.
- Reason:
  The v31 bracket tested Stage A durations `0.94`, `1.00`, `1.20`, `2.00`,
  and `4.00 s` before the same E2 Stage B trajectory. No case passed the
  trajectory-after-approach or full staged gate. Short approaches reduce Stage
  A drift to about `5.5-6.4 mm`, but E2 then fails orientation and angular
  gates. Longer approaches recover E2 orientation but still fail qdot
  saturation and tail qdot utilization, with qdot saturation near `0.99`.
- Consequence:
  The next useful change should alter the terminal configuration through a
  posture objective, explicit nullspace/posture step, or different tangent
  allocation, rather than changing only Stage A duration.

## D037: Use Moderate Trajectory Posture Regularization As The E2 Stage B Fix Candidate

- Date: 2026-05-24
- Status: accepted
- Decision:
  Keep the joint-velocity posture regularization hook and treat moderate
  trajectory-phase posture regularization as the current E2 Stage B fix
  candidate after weighted prealignment. Do not claim full staged feasibility
  from this result.
- Reason:
  The v32 matrix added a posture velocity target toward
  `q = [0, -0.1, 0.15, -0.05, 0, 0]` with `kp = 1.0` and max posture velocity
  `0.05 rad/s`. Four cases passed the trajectory-after-approach gate:
  `trajectory_w0p001`, `trajectory_w0p01`, `both_w0p001`, and `both_w0p01`.
  These rows reduced E2 qdot saturation fraction from the baseline `0.9935`
  to `0.0` while keeping orientation, force, position, and slack within the
  existing gates. However, all ten rows still failed ordinary Stage A
  feasibility, and strong approach posture weighting (`0.1`) broke
  contact/force tracking.
- Consequence:
  Preserve the trajectory-stage posture objective for subsequent E2/E1-E4
  staged tests. The next unresolved problem is Stage A task structure or an
  explicitly documented approach budget; approach posture weighting alone is
  not enough.
