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

## D038: Treat Slowed E1-E4 Stage B After Prealignment As Solved With Posture Regularization

- Date: 2026-05-24
- Status: accepted
- Decision:
  Treat the slowed E1-E4 trajectory-after-prealignment matrix as passing under
  the v32 moderate trajectory posture objective. Do not claim full staged
  feasibility.
- Reason:
  The v33 matrix ran E1-E4 with the same weighted Stage A prealignment as v29
  and added trajectory-phase posture regularization with target
  `q = [0, -0.1, 0.15, -0.05, 0, 0]`, `kp = 1.0`, weight `0.001`, and max
  posture velocity `0.05 rad/s`. All four Stage B trajectories passed:
  `trajectory_after_approach_pass_count = 4 / 4`, qdot saturation fraction
  `0.0` in every trajectory, and no failed trajectory criteria. The full
  staged pass count remains `0 / 4` because Stage A ordinary feasibility still
  fails in every row.
- Consequence:
  Further Stage B E2 tuning is no longer the immediate blocker for the slowed
  tilted-plane matrix. The next useful work should focus on Stage A approach
  feasibility or on explicitly defining and justifying a relaxed approach
  budget.

## D039: Planar-Primary Priority Is Diagnostic, Not The Stage A Fix

- Date: 2026-05-24
- Status: accepted
- Decision:
  Keep `planar-primary` orientation priority as a diagnostic controller mode,
  but do not use it as the accepted Stage A approach solution.
- Reason:
  The v34 planar-primary bracket preserves x/y position very well: the
  planar-primary rows reduce Stage A drift from the weighted reference
  `0.008347977658392892 m` to below `3e-5 m`, with planar velocity slack near
  zero. However, default normal secondary weighting loses contact and force
  tracking. Raising normal secondary weight restores force quality only by
  stalling terminal orientation near `0.07 rad`, matching the earlier
  linear-primary failure mode. No tested row passes the terminal approach
  budget, and sustained qdot saturation remains above the gate in the
  normal-weight follow-up.
- Consequence:
  Stage A is no longer just an x/y drift problem. The remaining task is to
  define either an explicit relaxed approach budget or a planned prealignment
  path/task formulation with separate contact-maintenance and terminal-state
  gates.

## D040: Two-Phase Recenter Does Not Produce An Accepted Setup

- Date: 2026-05-24
- Status: accepted
- Decision:
  Keep the optional recenter phase and explicit setup terminal-state gate as
  diagnostic infrastructure, but do not accept the tested two-phase recenter
  path as the Stage A solution.
- Reason:
  The v35 E2 matrix tested weighted prealignment followed by optional
  weighted, linear-primary, or planar-primary recentering to the original x/y
  reference, then the v32 trajectory posture-regularized E2 Stage B. The
  setup terminal-state gate requires final orientation `<= 0.03 rad`, final
  x/y error `<= 0.002 m`, contact fraction `1.0`, tail force error
  `<= 0.25 N`, and no hard qdot or joint-limit violations. No case passed
  this setup gate. Short linear-primary recenter windows (`0.2-0.3 s`) kept
  the following trajectory passing but left `7.21-7.57 mm` x/y error and
  `1.40-1.55 N` recenter tail force error. The `4 s` linear-primary recenter
  reduced x/y error to `0.001202027969075075 m` and tail force error to
  `0.07268453631886647 N`, but lost terminal orientation
  (`0.06144921366675186 rad`) and made E2 fail. Weighted recentering preserved
  the old Stage B pass but left about `8.36 mm` x/y error. Planar-primary
  recentering lost contact/force.
- Consequence:
  Do not continue scalar recenter-duration tuning as the primary path. The
  next Stage A option should either introduce a genuinely force-maintaining
  recenter formulation with phase-specific normal/force authority, or make an
  explicit relaxed setup-budget decision that remains separate from
  paper-equivalent full staged feasibility.

## D041: Three-Phase Settle Still Does Not Produce An Accepted Setup

- Date: 2026-05-24
- Status: accepted
- Decision:
  Do not accept the tested align -> recenter -> settle path as the Stage A
  solution. Keep the optional settle phase as diagnostic infrastructure only.
- Reason:
  The v36 matrix added a post-recenter settle phase that targets the original
  x/y setup reference while restoring force-normal orientation before the
  posture-regularized E2 trajectory. The matrix produced `0 / 10` setup
  terminal-state passes, `8 / 10` trajectory feasibility passes, `8 / 10`
  legacy trajectory-after-approach passes, and `0 / 10` planned
  setup-then-trajectory passes. Weighted settling restored orientation and
  force enough for Stage B, but final x/y error returned to about
  `7.2-8.3 mm`. Linear-primary settling kept x/y error as low as
  `0.00017396214319096055 m`, but terminal orientation rose to
  `0.07228244179626259 rad` and the following E2 trajectory failed
  orientation.
- Consequence:
  Stop scalar phase-duration bracketing for Stage A under the current
  instantaneous velocity task formulation. The next decision should either
  define a relaxed setup budget that explicitly accepts weighted-prealignment
  drift, or move to a mathematically different Stage A formulation rather than
  another align/recenter/settle schedule.

## D042: Terminal IK Audit Does Not Find An Accepted Setup State

- Date: 2026-05-24
- Status: accepted
- Decision:
  Keep the setup terminal IK probe as configuration-feasibility evidence, but
  do not accept it as a Stage A solution and do not treat it as a global
  infeasibility proof.
- Reason:
  The v37 probe removed path and instantaneous velocity-controller constraints
  and directly optimized terminal joint states against the setup gate. Across
  65 deterministic candidates, no candidate passed the terminal setup gate.
  The best local candidate kept contact and force error small
  (`0.004835673570861232 N`) but still failed x/y error
  (`0.002178947478445584 m` against a `0.002 m` gate) and force-normal
  orientation error (`0.05199834145021794 rad` against a `0.03 rad` gate).
- Consequence:
  More align/recenter/settle scheduling is not justified by the current
  evidence. The next useful decision is to either define an explicit relaxed
  setup budget for the UR10e adapted reproduction, or revisit model/TCP/contact
  geometry and run a broader terminal feasibility audit before adding another
  Stage A controller.

## D043: Define A Separate UR10e Adapted Relaxed Setup Budget

- Date: 2026-05-24
- Status: accepted
- Decision:
  Define `ur10e_adapted_trajectory_after_relaxed_setup` as a separate
  simulation-only acceptance label. It accepts setup drift up to `0.010 m`,
  requires final setup orientation `<= 0.03 rad`, setup tail force error
  `<= 0.25 N`, contact fraction `1.0`, and no qdot or joint-limit violation.
  Setup qdot saturation is recorded but not gated by this relaxed label.
- Reason:
  v35-v37 show that the strict setup terminal-state gate is not met, while
  v33 shows all four slowed tilted-plane Stage B trajectories pass after the
  current weighted prealignment with moderate trajectory posture
  regularization. The v38 evaluator gives `4 / 4`
  `ur10e_adapted_trajectory_after_relaxed_setup` passes for the v33 E1-E4
  matrix, while strict full staged feasibility remains `0 / 4`.
- Consequence:
  Reports may use the relaxed label only when they also state that it is not
  paper-equivalent full staged feasibility and not hardware-ready. The strict
  full staged gate remains the criterion for any future paper-equivalent
  reproduction claim.

## D044: Completion Audit Does Not Close The Overall Goal

- Date: 2026-05-24
- Status: accepted
- Decision:
  Do not mark the overall reproduction goal complete from the current
  repository state.
- Reason:
  The audit confirms that the Git-backed UR10e adapted simulation line has an
  accepted relaxed-label result, but strict paper-equivalent full staged
  feasibility remains `0 / 4`, the terminal setup audit remains `0 / 65`, the
  paper-faithful 7DOF executable line is not separate and complete, and the
  hardware gate is not passed.
- Consequence:
  Continue to report the current result as UR10e adapted simulation evidence
  only. Future completion requires closing the paper-truth/model gaps or
  producing a separate paper-faithful reproduction line; real hardware remains
  blocked by the hardware gate.

## D045: Section V z0 Is Verified Undefined In Simulation Text

- Date: 2026-05-24
- Status: accepted
- Decision:
  Remove `z0_source` from `pending_pdf_verify` and record Section V `z0` as
  verified undefined in the simulation text.
- Reason:
  V40 layout and raw PDF extraction both show Section V states
  `xpd = [0.2 cos(0.2t); 0.2 sin(0.2t); z0]` but does not define `z0` in the
  simulation section. Section VI later defines experiment `z0` as the
  anticipated z position equal to the initial manipulator position, but that
  statement appears in the experimental verification section.
- Consequence:
  No `pending_pdf_verify` fields remain in `configs/paper_truth.yaml`. Future
  Section V simulation code must choose an explicit adapted `z0` convention
  instead of silently importing the Section VI experimental definition.

## D046: Keep The Paper 7DOF Line Separate And Diagnostic

- Date: 2026-05-24
- Status: accepted
- Decision:
  Add a separate paper-platform 7DOF executable diagnostic line, but do not
  treat it as paper-faithful numerical parity or as a UR10e adapted result.
- Reason:
  The v41 executable uses 7 joint Panda/Franka-style kinematics, a 6x7
  Jacobian, Section V q0, circle trajectory, 5 N normal-force target, joint
  limits, velocity limits, and the finite-time KKT-projection update. The
  recorded run at `runs/paper_7dof_section_v/20260524T113608` executes with
  no joint or qdot bound violations, but contact is not maintained in the tail:
  `tail_contact_fraction = 0.0` and `tail_force_error_mean_N = 5.0`.
- Consequence:
  The repo now has an executable paper-platform line to iterate on separately
  from UR10e. Any paper-equivalent claim remains blocked until the 7DOF line
  maintains the force/contact behavior and the inherited Panda DH model and
  force-normal orientation interpretation are verified.

## D047: Stabilize The Paper 7DOF Contact Tail As A Diagnostic Variant

- Date: 2026-05-24
- Status: accepted
- Decision:
  Keep the v42 contact-stabilized 7DOF run as a diagnostic paper-platform
  variant, not as the paper-faithful KKT result.
- Reason:
  The run at `runs/paper_7dof_section_v/20260524T114244` uses the same
  Section V trajectory, q0, 5 N target, joint limits, velocity limits, and
  force-normal orientation interpretation as v41, but switches the projection
  target to `pinv_bounded` and caps the force integral at `0.1`. It passes the
  contact tail gate with `tail_contact_fraction = 1.0`,
  `tail_force_error_mean_N = 0.013764149103712913`, and no q or qdot bound
  violations.
- Consequence:
  The v41 contact-tail failure is closed for the diagnostic 7DOF line, but the
  paper-equivalent claim remains blocked because the KKT-projection line still
  loses contact and the Panda DH/orientation assumptions remain unverified.

## D048: Treat Capped-Integral KKT Contact Recovery As Diagnostic Evidence

- Date: 2026-05-24
- Status: accepted
- Decision:
  Accept the capped-integral `kkt_projection` run as contact-recovery evidence
  for the paper-platform diagnostic line, but not as paper-equivalent
  numerical parity.
- Reason:
  The v43 run at `runs/paper_7dof_section_v/20260524T114736` uses
  `kkt_projection`, paper epsilon `0.022`, Section V hard joint and velocity
  bounds, and a force-integral limit of `0.1`. It passes tail contact-force
  metrics with `tail_contact_fraction = 1.0`,
  `tail_force_error_mean_N = 0.06720487008205062`, and no q or qdot bound
  violations. The improvement shows v41 contact loss was tied to unbounded
  force integral behavior, not an unavoidable KKT projection failure.
- Consequence:
  Future paper-platform work should move from contact recovery to parity
  definition and model provenance: compare against legacy MATLAB/RNN outputs,
  verify Panda/Franka DH parameters, and keep the force-integral cap labeled as
  an explicit diagnostic anti-windup decision unless the paper source supports
  it.

## D049: Define Strict Paper-Platform Parity Gate Before Upgrading 7DOF Claims

- Date: 2026-05-24
- Status: accepted
- Decision:
  Define `paper_platform_7dof_strict_parity` as a separate gate against the
  legacy MATLAB/RNN Section V outputs. The gate is configured in
  `configs/paper_platform_parity.yaml` and evaluated by
  `scripts/evaluate_paper_platform_parity.py`.
- Reason:
  The v44 evaluation at `runs/paper_platform_parity_eval/20260524T115641`
  shows the v43 Python capped-integral KKT candidate matches the
  formula-faithful tail convergence metrics within configured tolerances, but
  strict parity still fails. The candidate is only `5.0 s` long, lacks the
  Fig.6 q7-at-22 s landmark, lacks Python Fig.5 r-sweep coverage, and uses
  `force_integral_limit = 0.1`.
- Consequence:
  Reports may say the Python 7DOF line has a formal parity gate and partial
  tail-convergence agreement with the legacy formula-faithful output. They
  must not call it paper-equivalent numerical parity until the strict gate
  passes, including duration, Fig.5/Fig.6 landmarks, and assumption
  compatibility.

## D050: Treat The 30 s Python 7DOF Candidate As Partial Parity Evidence

- Date: 2026-05-24
- Status: accepted
- Decision:
  Use the v45 30 s capped-integral KKT run as the current Python candidate for
  `paper_platform_7dof_strict_parity`, while keeping the strict parity result
  failed.
- Reason:
  The run at `runs/paper_7dof_section_v/20260524T120439` is generated from a
  clean code commit, covers `30.0 s`, passes execution/contact/bounds, and
  records `fig6_q7_at_22s_rad = 1.6755097668200787`. The gate evaluation at
  `runs/paper_platform_parity_eval/20260524T120503` now passes duration and
  formula-faithful tail convergence checks, but fails the Fig.6 q7 landmark
  by `0.8244902331799213 rad`, still lacks Python Fig.5 r-sweep coverage, and
  still uses `force_integral_limit = 0.1`.
- Consequence:
  Future parity work should focus on the q7 landmark mismatch, Fig.5 r-sweep
  coverage, and paper justification or removal of the integral cap. The v45
  run is not paper-equivalent numerical parity and not hardware readiness.

## D051: Treat Python 7DOF Fig.5 r-Sweep Coverage As Present But Not Parity

- Date: 2026-05-24
- Status: accepted
- Decision:
  Add Python 7DOF Fig.5 r-sweep metrics for `r = 0.2, 0.4, 0.6, 0.8, 1.0` and
  allow the strict parity gate to pass the Fig.5 coverage check when each
  metrics file has the expected r value, `execution_success = true`, and a
  `2.0 s` window.
- Reason:
  The v46 sweep at `runs/paper_7dof_fig5_r_sweep/20260524T121033` records a
  clean 0-2 s Python 7DOF diagnostic for every paper r value. The parity
  evaluation at `runs/paper_platform_parity_eval/20260524T121116` now passes
  `fig5_r_sweep_coverage`, while strict parity remains failed on
  `fig6_q7_22s_landmark` and `paper_assumption_compatibility`.
- Consequence:
  Future paper-platform claims can say Python Fig.5 r-sweep coverage exists,
  but not that Fig.5 numerical parity is achieved. The remaining
  paper-platform blockers are the q7 landmark mismatch and the finite
  force-integral cap.

## D052: Use The Uncapped KKT Candidate For Strict Paper-Platform Parity

- Date: 2026-05-24
- Status: accepted
- Decision:
  Replace the capped v45 candidate in `configs/paper_platform_parity.yaml`
  with the uncapped 30 s KKT candidate at
  `runs/paper_7dof_section_v/20260524T121503`.
- Reason:
  The uncapped run passes execution, contact tail, hard q/qdot bounds,
  duration coverage, formula-faithful tail convergence, and Fig.5 coverage.
  The v47 parity evaluation at
  `runs/paper_platform_parity_eval/20260524T121542` passes
  `paper_assumption_compatibility`; strict parity now fails only on
  `fig6_q7_22s_landmark`.
- Consequence:
  The finite force-integral cap is no longer a strict-gate blocker for the
  current Python 7DOF line. Future paper-platform work should focus on the
  q7-at-22 s mismatch and model/provenance or redundancy differences.

## D053: Treat q7 Mismatch As Variant-Insensitive Across Current Python Modes

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record the v48 q7 variant probe as evidence that the Fig.6 q7-at-22 s
  mismatch is not explained by the current supported Python solver,
  orientation, or force-integral-cap variants.
- Reason:
  The probe at `runs/paper_7dof_q7_variant_probe/20260524T122345` covers all
  eight combinations of `kkt_projection`/`pinv_bounded`,
  `force_shortest_arc`/`normal_only`, and uncapped/`0.1` force integral over
  the full 30 s Fig.6 window. All rows execute successfully and expose q7 at
  22 s. The q7 range is only `0.02232563934802667 rad`, the closest variant is
  still `0.8164105207854273 rad` away from the `2.5 rad` figure-match
  reference, and `figure_match_pass_count = 0`.
- Consequence:
  Do not keep cycling through these local Python knobs as the primary q7
  parity strategy. The next paper-platform branch should compare Python
  Panda kinematics and q trajectories against the legacy MATLAB/RNN raw Fig.6
  data or audit the provenance of the figure-match q7 landmark.

## D054: Treat Fig.6 q7 Landmark As Figure-Match Provenance, Not FK Error

- Date: 2026-05-24
- Status: accepted
- Decision:
  Treat the remaining Fig.6 q7-at-22 s mismatch as a legacy figure-match
  provenance issue, not as evidence of a Python Panda DH/FK/Jacobian porting
  error.
- Reason:
  The v49 raw provenance comparison at
  `runs/paper_7dof_fig6_raw_provenance/20260524T123130` evaluates the current
  Python uncapped KKT candidate against the ignored local legacy Fig.6 `.mat`
  files. Python Panda FK and Jacobian conditioning match sampled legacy raw
  states to numerical precision. The legacy formula-faithful line uses
  `kkt_projection`, `force_shortest_arc`, and `paper_literal`, while the
  legacy figure-match line uses `pinv_bounded`, `normal_only`, and
  `admittance_proxy` with `landmark` acceptance. The figure-match q7
  trajectory is exactly at the upper limit for `17829` samples and first nears
  the upper limit at `11.872999999998859 s`.
- Consequence:
  Future strict parity work should not treat the `2.5 rad` q7 landmark as a
  validated formula-faithful target without preserving this provenance
  boundary. The next choice is either to implement the legacy
  `admittance_proxy` figure-match line in Python as a separate tuned landmark
  candidate, or revise the parity gate so formula-faithful behavior is primary
  and q7 figure-match remains labeled landmark evidence.

## D055: Separate Figure-Match Landmark Tuning From Formula-Faithful Parity

- Date: 2026-05-24
- Status: accepted
- Decision:
  Treat the legacy `figure_match` q7-at-22 s result as tuned landmark
  evidence, not as a formula-faithful parity requirement.
- Reason:
  The v50 source audit at
  `runs/legacy_figure_match_source_audit/20260524T123651` parses the legacy
  MATLAB/RNN configuration and implementation. It finds eight non-paper-
  faithful tuning knobs in `figure_match`: `normal_only`, `pinv_bounded`,
  `admittance_proxy`, `landmark`, `alpha = 20.0`,
  `maxAngularSpeed = 1.5`, `kp = 25.0`, and `q7NullspaceSpeed = 0.35`.
  The q7 speed is explicitly wired into the pseudoinverse nullspace branch,
  and the raw figure-match trajectory pins q7 at the upper limit for `17829`
  samples.
- Consequence:
  The strict paper-platform gate should be split or relabeled before stronger
  claims are made: formula-faithful parity should not fail solely because it
  does not reproduce a tuned q7-nullspace landmark. A separate Python
  `figure_match` candidate may still be useful, but it must be labeled as a
  tuned landmark reproduction rather than paper-equivalent numerical parity.

## D056: Split Paper-Platform Gate Into Formula Convergence And Landmark Claims

- Date: 2026-05-24
- Status: accepted
- Decision:
  Split the paper-platform evaluator into three claim levels:
  `formula_convergence`, `figure_match_landmark`, and the backward-compatible
  `legacy_strict_all_checks` aggregate.
- Reason:
  The v51 evaluation at `runs/paper_platform_parity_eval/20260524T124200`
  reports `paper_platform_formula_convergence_pass = true`,
  `paper_platform_figure_match_landmark_pass = false`, and
  `paper_platform_parity_pass = false`. This keeps the v49-v50 provenance
  boundary visible: formula-convergence evidence should not be blocked by the
  tuned figure-match q7 landmark, but the old aggregate still records that
  full strict paper-platform parity is not achieved.
- Consequence:
  Future reports may claim formula-convergence evidence for the Python
  7DOF paper-platform line. They must not call it full paper-equivalent
  numerical parity, Fig.6 q-trajectory parity, or figure-match landmark
  reproduction unless the corresponding claim level passes.

## D057: Keep Tuned Figure-Match Candidate Separate From Formula Parity

- Date: 2026-05-24
- Status: accepted
- Decision:
  Implement and report the Python v52 tuned figure-match candidate as a
  separate landmark-reproduction line, not as a replacement for the
  formula-faithful paper-platform candidate.
- Reason:
  The v52 run `runs/paper_7dof_section_v/20260524T134441` reproduces the
  Fig.6 q7 landmark with `fig6_q7_at_22s_rad = 2.4999999999331863`. The raw
  provenance comparison at
  `runs/paper_7dof_fig6_raw_provenance/20260524T134549` shows
  legacy-vs-Python figure-match joint RMSE of `6.081574510252252e-09 rad`.
  The matching line uses `admittance_proxy`, `normal_only`, `pinv_bounded`,
  `alpha = 20.0`, `kp = 25.0`, and `q7_nullspace_speed_rad_s = 0.35`.
- Consequence:
  The project can now claim tuned figure-match landmark reproduction in
  Python. It still must not claim that the formula-faithful paper-platform
  line reproduces Fig.6 q-trajectory parity or that full paper-equivalent
  numerical parity is achieved.

## D058: Treat Current UR10e TCP/Contact Geometry As Unresolved

- Date: 2026-05-24
- Status: accepted
- Decision:
  Do not treat the current tilted-plane UR10e MJCF TCP/contact convention as
  hardware-ready. The model must be replaced with an explicit contact-point
  convention or updated from measured mounted-stack geometry before any
  hardware gate can use it.
- Reason:
  The v53 audit at `runs/tcp_contact_model_audit/20260524T135607` verifies
  that the config TCP guess `[0, 0, -0.085]` matches both the MJCF body offset
  and the EOAT note distance, but the TCP site is coincident with the center of
  the colliding `contact_tip` sphere. MuJoCo plane contact therefore occurs
  about one sphere radius away from the site: the site-to-sphere-surface
  projection is `0.04500000000000001 m`, and the simulated parent-to-surface
  distance in the audited posture is `0.12955222618906498 m`.
- Consequence:
  The v53 terminal setup rerun at
  `runs/setup_terminal_ik_audit/20260524T135619` preserves the strict setup
  failure (`0 / 65` passes). That failure should remain a simulation-model
  result, not hardware evidence. Future UR10e adapted branches should first
  decide whether the EOAT 85 mm note denotes a physical contact point or a
  sphere-center/tool-frame point, then rerun the setup audit with that explicit
  model.

## D059: Use A Separate Contact-Point Variant For The 85 mm TCP Convention

- Date: 2026-05-24
- Status: accepted
- Decision:
  Keep the v53 center-site MJCF as historical evidence and add a separate v54
  TCP contact-point MJCF/config variant instead of silently rewriting the old
  model.
- Reason:
  The v54 variant
  `assets/mjcf/ur10e_tilted_plane_10deg_tcp_contact_point.xml` keeps the EOAT
  candidate TCP site at `85 mm` but moves the colliding `contact_tip` sphere
  center to local `[0, 0, 0.045]`. The audit run
  `runs/tcp_contact_model_audit/20260524T140535` reports
  `site_coincident_with_contact_geom_center = false`,
  `contact_surface_offset_requires_model_decision = false`, and
  `surface_extension_beyond_declared_tcp_m = -0.00068365111445505`.
- Consequence:
  The named contact-point convention is now available for simulation, but it
  is still not hardware-ready. The terminal setup rerun at
  `runs/setup_terminal_ik_audit/20260524T140539` remains `0 / 65`, so the next
  useful simulation step is broader terminal feasibility or gate-definition
  analysis, not another scalar phase schedule.

## D060: Gate Terminal Setup Force On The Intended Tool-Plane Contact Pair

- Date: 2026-05-24
- Status: accepted
- Decision:
  The terminal setup audit must use target-pair contact force from
  `contact_plane` / `contact_tip`, not total MuJoCo contact force from all
  contacts.
- Reason:
  A broad v55 exploratory run exposed a false-positive path: robot
  self-collision could create `5 N` of total positive normal force while the
  TCP site was far from the plane. The fixed v55 run
  `runs/setup_terminal_ik_audit/20260524T141321` records
  `target_contact_count` and `total_normal_force_N` separately and uses only
  target-pair force for the gate.
- Consequence:
  The broad v55 terminal audit reports `0 / 513` passing candidates. Future
  setup claims must preserve target-contact-pair accounting, especially when
  using wide random seeds that may introduce non-tool contacts.

## D061: Treat Strict UR10e Setup As A Gate-Definition Conflict

- Date: 2026-05-24
- Status: accepted
- Decision:
  Stop treating the strict adapted UR10e setup failure as a phase-scheduling
  problem. Under the current v54 TCP contact-point model, it is a gate-
  definition conflict between original x/y, intended tool-plane force, and
  force-normal TCP orientation.
- Reason:
  The v56 contact-manifold audit at
  `runs/contact_manifold_gate_audit/20260524T142404` seeds from known
  target-contact neighborhoods and solves relaxed gate combinations. It finds
  `0 / 161` strict passes. The `xy_force` case can satisfy x/y and force but
  leaves `0.14697007178233126 rad` orientation error; the `xy_orientation`
  case satisfies x/y and orientation but loses target contact and has `5.0 N`
  force error; the best optimized `force_orientation` case has
  `0.014127706733724453 m` x/y error.
- Consequence:
  Future UR10e adapted setup work should explicitly relax or redefine the
  setup gate, or change the setup target definition, before another Stage A
  controller is designed. Full strict staged feasibility remains unachieved.

## D062: Add A Diagnostic-Only Adapted Terminal Setup Gate

- Date: 2026-05-24
- Status: accepted
- Decision:
  Add `ur10e_adapted_terminal_setup_diagnostic_gate` as a separate diagnostic
  label. This gate is not paper-equivalent, not path-feasible, not trajectory-
  feasible, and not hardware-ready.
- Reason:
  v56 showed the strict setup gate is a gate-definition conflict. The v57
  diagnostic gate rounds the best terminal candidate into explicit thresholds:
  `max_terminal_tangential_error_m = 0.004`,
  `max_terminal_orientation_error_rad = 0.08`,
  `max_terminal_force_error_N = 0.25`, and
  `min_target_contact_count = 1`. The evaluation run
  `runs/terminal_setup_gate_eval/20260524T143019` reports `1 / 513` passing
  candidates.
- Consequence:
  Future UR10e adapted controller work must name which setup label it targets:
  strict paper-equivalent setup, v38 relaxed trajectory-after-setup budget, or
  v57 diagnostic terminal setup. These labels must not be merged into a single
  paper-equivalent claim.

## D063: Target V57 Diagnostic Terminal Setup For The Next Stage A Prototype

- Date: 2026-05-24
- Status: accepted
- Decision:
  Use `ur10e_adapted_terminal_setup_diagnostic` as the target label for the
  next Stage A simulation prototype.
- Reason:
  Strict paper-equivalent setup remains blocked, and v38 relaxed
  trajectory-after-setup is an existing trajectory-label claim rather than a
  terminal target. The v57 diagnostic gate supplies one explicit terminal
  target candidate, recorded in `configs/ur10e_adapted_stage_a_target.yaml`.
- Consequence:
  Any next Stage A controller work must evaluate against the selected
  diagnostic terminal target unless a later decision changes the target label.
  This target remains simulation-only and must not be relabeled as path
  feasibility, trajectory feasibility, paper-equivalent feasibility, or
  hardware readiness.

## D064: Treat Diagnostic Target Handoff As Qdot-Blocked

- Date: 2026-05-24
- Status: accepted
- Decision:
  Do not treat the v58 selected diagnostic terminal target as trajectory
  feasible by itself.
- Reason:
  The v59 handoff evaluation at
  `runs/stage_a_target_handoff_eval/20260524T144654` starts directly from the
  selected q and evaluates E1-E4 using target-pair force/contact accounting.
  All rows keep target contact and satisfy force, x/y, and diagnostic
  orientation thresholds, but the pass count is `0 / 4` because every row
  fails `qdot_saturation_fraction` and `tail_max_qdot_utilization`.
- Consequence:
  The next controller branch must be qdot-budget aware, or it must explicitly
  change timing/gates before making any trajectory-feasibility claim. The v59
  result is a handoff audit only, not a Stage A path, trajectory, paper-
  equivalent, or hardware-readiness claim.

## D065: Keep Qdot-Aware Diagnostic Handoff Separate From Stage A Path Feasibility

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record the v60 qdot-aware handoff as direct-target evidence only.
- Reason:
  The v60 run at `runs/stage_a_target_handoff_eval/20260524T145433` starts
  directly from the v58 selected q and changes the handoff policy to
  `paper_time_scale = 0.01`, `force_gain = 1e-4`, and `orientation_kp = 0.0`.
  It reports `4 / 4` E1-E4 handoff passes with target-pair contact accounting
  and zero qdot saturation.
- Consequence:
  The project can claim a qdot-aware slowed diagnostic handoff from the
  selected target. It still must not claim Stage A path feasibility, strict
  trajectory feasibility, paper-equivalent feasibility, or hardware readiness
  until a controller reaches that target from an ordinary initial state under
  the same claim boundary.

## D066: Treat The Contact Path As Offline Evidence Until An Online Tracker Exists

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record the v61 contact path audit as offline quasi-static path evidence only.
- Reason:
  The v61 run at `runs/stage_a_contact_path_audit/20260524T151201` optimizes a
  128-knot contact-manifold path from the ordinary setup initial q to the v58
  selected diagnostic terminal target. The path gate and terminal diagnostic
  gate pass, target contact is present throughout, and the minimum duration for
  the `0.15 rad/s` qdot budget is `14.332635022800167 s`.
- Consequence:
  The project can claim that an offline qdot-limited contact path exists for
  the diagnostic target. It still must not claim an online Stage A controller,
  strict trajectory feasibility, paper-equivalent feasibility, hardware
  readiness, or all-knot force-normal diagnostic orientation compliance from
  this result alone.

## D067: Keep Qdot-Limited Contact Path Tracking Separate From Staged Trajectory Feasibility

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v62 as a qdot-limited Stage A joint-path tracking prototype, not as a
  connected staged trajectory claim.
- Reason:
  The v62 run at `runs/stage_a_contact_path_tracking/20260524T152346` tracks
  the v61 path over `15.0 s`. The tracking gate and terminal diagnostic gate
  pass, max qdot is `0.14332635022814824 rad/s`, qdot saturation is `0.0`, and
  target contact remains present throughout.
- Consequence:
  The project can claim that the selected diagnostic target is reachable by a
  qdot-limited joint-path replay in simulation. It still must not claim a
  connected Stage A plus Stage B trajectory, force-feedback robustness,
  paper-equivalent feasibility, or hardware readiness until the tracked path and
  handoff are evaluated in one explicit stitched run.

## D068: Treat The Stitched Diagnostic Run As Nominal Simulation Evidence

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v63 as a connected diagnostic Stage A plus Stage B simulation pass,
  while keeping it separate from strict paper-equivalent and hardware claims.
- Reason:
  The v63 run at `runs/stitched_stage_a_handoff_eval/20260524T152807` executes
  the v62 Stage A tracker and v60 slowed handoff in one script. The stitched
  gate passes, Stage A passes, and Stage B reports `4 / 4` E1-E4 handoff
  passes with target-pair force/contact accounting and zero qdot saturation.
- Consequence:
  The project can claim a nominal diagnostic staged simulation pass for the
  selected UR10e target. It still must not claim strict paper-equivalent
  feasibility, robustness to contact/model perturbations, or hardware readiness
  until those gates are explicitly evaluated.

## D069: Treat The Stitched Sensitivity Audit As A Robustness Boundary

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v64 as a sensitivity boundary around the v63 stitched diagnostic
  policy, not as a robustness pass.
- Reason:
  The v64 run at
  `runs/stitched_stage_a_handoff_sensitivity/20260524T161111` evaluates nine
  cases around the v63 Stage A tracker plus Stage B handoff. The stitched gate
  passes `4 / 9` cases: nominal, `stage_a_16s`, `force_gain_5e-5`, and
  `force_gain_2e-4`. It fails 1 mm base-z/contact perturbations, `stage_a_14s`,
  `qdot_limit_0p12`, and `paper_time_scale_0p02`.
- Consequence:
  The project can claim only that the nominal diagnostic stitched policy has
  limited audited margin. It must not claim robustness, strict
  paper-equivalent feasibility, or hardware readiness. The next controller
  branch should test perturbation-aware path reoptimization or margin-aware
  timing against these failure cases.

## D070: Keep Timing-Margin Recovery Separate From Contact-Model Robustness

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v65 as timing-margin recovery evidence for the diagnostic stitched
  policy, while keeping 1 mm base-z/contact perturbation recovery unresolved.
- Reason:
  The v65 run at
  `runs/stitched_stage_a_handoff_timing_margin/20260524T162005` evaluates
  seven timing-margin cases. It recovers the nearby Stage A and qdot failures:
  `stage_a_14p5_recovery`, `qdot012_stage_a_18p0_recovery`, and
  `paper_time_scale_0p012_recovery` pass, while their nearby reference-fail
  boundaries remain failing.
- Consequence:
  The project can claim limited qdot/timing margins for the diagnostic
  stitched policy. It still must not claim robustness, strict paper-equivalent
  feasibility, or hardware readiness. The next branch should focus on
  perturbation-aware Stage A path reoptimization for `base_z_minus_1mm` and
  `base_z_plus_1mm`.

## D071: Treat Base-Z Recovery As One-Sided And Margin-Bounded

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v66 as one-sided diagnostic recovery evidence for `-1 mm` base-z only
  under an explicit Stage A timing margin, not as base-z/contact robustness.
- Reason:
  The v66 run at `runs/stage_a_base_z_recovery/20260524T163746` evaluates
  perturbation-aware start rebalance, terminal search, contact path
  reoptimization, and stitched handoff for three base-z cases. It recovers
  `base_z_minus_1mm_stage_a_16s_recovery` with `16.0 s` Stage A and Stage B
  `4 / 4`, while the exact `15.0 s` `base_z_minus_1mm` reference remains
  qdot-limited and `base_z_plus_1mm` has no passing start plus terminal target
  pair under this diagnostic search.
- Consequence:
  The project can claim a narrow diagnostic simulation recovery for the `-1 mm`
  base-z side only with an explicit `16.0 s` Stage A margin. It still must not
  claim robustness, strict paper-equivalent feasibility, contact-model
  calibration, hardware readiness, or recovery of the `+1 mm` perturbation.

## D072: Treat Positive Base-Z Failure As A Contact-Model/Start-Contact Gap

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v67 as a compact base-z bracket that rules out treating the positive
  base-z side as only a Stage A timing problem under the current diagnostic
  model.
- Reason:
  The v67 run at `runs/stage_a_base_z_bracket/20260524T165411` evaluates 13
  base-z deltas from `-1.0 mm` to `+1.0 mm`. Nominal, `-0.25 mm`, and
  `-0.5 mm` recover at `15.0 s`, and `-1.0 mm` recovers at `16.0 s`; however,
  no tested positive delta from `+0.05 mm` through `+1.0 mm` has both a
  passing start contact and terminal target. The `+0.05 mm` row already loses
  start contact and exceeds the terminal orientation gate.
- Consequence:
  The next branch should investigate the positive-side contact-model or
  start-contact definition instead of adding only more Stage A timing margin.
  The project still must not claim robustness, strict paper-equivalent
  feasibility, contact-model calibration, or hardware readiness.

## D073: Treat Positive Base-Z Failure As Terminal-Orientation Limited

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v68 as evidence that the positive base-z side is no longer a
  start-contact recovery problem under the broader diagnostic seed search; the
  remaining audited blocker is terminal orientation.
- Reason:
  The v68 run at `runs/positive_base_z_start_contact/20260524T170350`
  evaluates eight positive deltas from `+0.05 mm` through `+1.0 mm`. The
  broader deterministic single-joint, paired-joint, and random start-contact
  seeds recover start contact for `8 / 8` cases. The compact terminal probe
  still passes `0 / 8`, and the best terminal orientation error increases from
  `0.0838175590896232 rad` at `+0.05 mm` to
  `0.11948560786548146 rad` at `+1.0 mm`.
- Consequence:
  The next branch should investigate the positive-side terminal orientation
  gate, desired force-normal convention, or contact-point model instead of
  spending another iteration only on start-contact recovery. The project still
  must not claim robustness, strict paper-equivalent feasibility,
  contact-model calibration, or hardware readiness.

## D074: Treat Positive Terminal Failure As Current-Model Orientation Margin

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v69 as evidence that the positive terminal blocker in the current
  contact-point model is the diagnostic orientation margin, not yaw handling or
  force/x-y/contact terminal feasibility.
- Reason:
  The v69 run at `runs/positive_terminal_orientation/20260524T171705`
  evaluates eight positive deltas for the current contact-point model and the
  older sphere-center model as a known flawed comparison. In the current model,
  force/x-y/contact passes `8 / 8` positive terminal cases, while the
  `0.08 rad` diagnostic orientation gate passes `0 / 8`. Full-rotation and
  force-normal-only errors differ by at most `4.884981308350689e-15 rad`, so
  yaw preservation is not the cause. Covering all positive force/x-y/contact
  cases through `+1.0 mm` requires about `0.11948560786548146 rad`.
- Consequence:
  The next branch should test positive-side path and stitched recovery only if
  an explicit diagnostic `0.12 rad` terminal orientation envelope is accepted.
  If that envelope is not acceptable, the project should revisit the physical
  contact-point model or terminal target definition before further path work.
  The legacy sphere-center model must remain a comparison only, not a
  hardware-ready fix.

## D075: Treat Positive Relaxed-Orientation Recovery As Stage-B Limited

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v70 as evidence that a run-local `0.12 rad` diagnostic terminal
  orientation envelope recovers positive-side start, terminal, and offline path
  feasibility through `+1.0 mm`, but does not recover stitched Stage A plus
  Stage B feasibility.
- Reason:
  The v70 run at
  `runs/positive_relaxed_orientation_recovery/20260524T172909` evaluates eight
  positive deltas in the current contact-point model. Start, terminal, and
  path geometry pass `8 / 8`; all terminal orientation errors are within
  `0.12 rad`, with `+1.0 mm` at `0.11948560786548146 rad`. However, stitched
  recovery count is `0`; every tested `15.0 s` and `16.0 s` row has Stage A
  passing and Stage B handoff `3 / 4`, with E2 failing on qdot saturation and
  tail max qdot utilization.
- Consequence:
  The next branch should combine the v70 relaxed terminal/path setup with a
  Stage B E2 timing or qdot margin audit. The project still must not claim
  robustness, strict paper-equivalent feasibility, contact-model calibration,
  or hardware readiness.

## D076: Treat Positive E2 Handoff As Timing-Recoverable

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v71 as evidence that the remaining positive-side E2 Stage B handoff
  blocker under the v70 run-local relaxed terminal/path setup is recoverable by
  slowing E2 timing to `paper_time_scale = 0.005`.
- Reason:
  The v71 run at `runs/positive_stage_b_e2_margin/20260524T192129` evaluates
  E2 only for eight positive deltas from `+0.05 mm` through `+1.0 mm`.
  Original `paper_time_scale = 0.01` passes `0 / 8`; `0.0075` passes `7 / 8`
  through `+0.75 mm`; and `0.005` passes `8 / 8` through `+1.0 mm`. A
  qdot-limit-only probe on the hardest `+1.0 mm` case at original `0.01`
  timing still fails even at `0.25 rad/s`, because max orientation error stays
  just above the run-local `0.12 rad` diagnostic gate.
- Consequence:
  The next branch should run the full positive E1-E4 stitched matrix with the
  v70 relaxed terminal/path setup and `paper_time_scale = 0.005`. The project
  still must not claim robustness, strict paper-equivalent feasibility,
  contact-model calibration, or hardware readiness.

## D077: Treat Positive Full Stitched Recovery As Diagnostic-Only

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v72 as evidence that the v70 run-local relaxed terminal/path setup
  plus v71 E2-safe timing recovers the full positive E1-E4 stitched diagnostic
  matrix through `+1.0 mm`.
- Reason:
  The v72 run at `runs/positive_full_stitched_recovery/20260524T192854`
  evaluates eight positive deltas from `+0.05 mm` through `+1.0 mm` with
  `paper_time_scale = 0.005`, `qdot_limit_rad_s = 0.15`, and the run-local
  `0.12 rad` relaxed orientation gate. Stitched pass count is `8 / 8`; every
  row reports Stage A pass and Stage B handoff `4 / 4`. The maximum Stage B
  qdot saturation fraction is `0.006`, and the maximum Stage B orientation
  error is `0.1199788204275829 rad`.
- Consequence:
  The next branch should stress-test the v72 recovered positive stitched
  policy under a compact sensitivity matrix. This is still diagnostic-label
  simulation evidence, not a robustness proof, strict paper-equivalent
  feasibility, contact-model calibration, or hardware readiness.

## D078: Treat Positive Stitched Sensitivity As A Boundary, Not Robustness

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v73 as evidence that the v72 positive stitched diagnostic recovery
  survives nominal replay and a shorter `14.5 s` Stage A replay, but not the
  full compact sensitivity matrix.
- Reason:
  The v73 run at `runs/positive_stitched_sensitivity/20260524T193845`
  evaluates five scenarios across eight positive deltas. The compact matrix
  passes `37 / 40` stitched cells. `nominal_v72` and `stage_a_14p5s` pass
  `8 / 8`. `qdot012_stage_a18s` fails `+0.2 mm` because Stage A leaves a
  `2.8323382178791726e-05 rad` final tracking residual while Stage B remains
  `4 / 4`. `paper_time_scale_0p0075` fails `+1.0 mm` because E2 fails qdot
  saturation, tail qdot utilization, and max orientation error. The tightened
  `orientation_gate_0p119` case fails `+1.0 mm` on both Stage A terminal
  orientation and all Stage B orientation rows.
- Consequence:
  The next branch should isolate the `qdot012_stage_a18s` `+0.2 mm` Stage A
  final-tracking boundary with a small duration/path-retiming margin audit.
  The faster-timing and tighter-orientation `+1.0 mm` failures remain explicit
  sensitivity limits unless a separate model/control change is made. The
  project still must not claim robustness, strict paper-equivalent feasibility,
  contact-model calibration, or hardware readiness.

## D079: Treat Qdot012 Positive Failure As A Narrow Stage A Margin

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v74 as evidence that the v73 `qdot012_stage_a18s` `+0.2 mm` failure
  is a narrow Stage A replay duration margin, not a Stage B handoff failure.
- Reason:
  The v74 run at `runs/qdot012_stage_a_margin/20260524T194817` holds the v70
  relaxed terminal/path setup, `qdot_limit_rad_s = 0.12`, `paper_time_scale =
  0.005`, and `max_orientation_error_rad = 0.12` fixed while sweeping Stage A
  duration for the `+0.2 mm` cell. Stage B passes `4 / 4` at every duration.
  Stage A final tracking fails through `18.03 s` with residual
  `3.2284410533080015e-07 rad`, then passes at `18.035 s` with zero final
  tracking error and max Stage A qdot `0.1199690367457867 rad/s`.
- Consequence:
  The project may either fold the `18.035 s` qdot012 duration margin into a
  compact positive stitched recovery matrix or move to the harder `+1.0 mm`
  faster-timing/orientation sensitivity limits. This remains diagnostic-label
  simulation evidence only, not a robustness proof, strict paper-equivalent
  feasibility, contact-model calibration, or hardware readiness.

## D080: Treat Qdot012 Positive Matrix As Recovered At 18.035 Seconds

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v75 as evidence that the qdot012 positive stitched diagnostic matrix
  recovers when the v74 `18.035 s` Stage A duration is applied to all positive
  deltas.
- Reason:
  The v75 run at `runs/positive_full_stitched_recovery/20260524T195501` reuses
  the v70 relaxed terminal/path setup with `qdot_limit_rad_s = 0.12`,
  `stage_a_duration_s = 18.035`, `paper_time_scale = 0.005`, and the run-local
  `0.12 rad` orientation gate. Stitched pass count is `8 / 8` through
  `+1.0 mm`; every row reports Stage A pass and Stage B handoff `4 / 4`.
  Maximum Stage B qdot saturation fraction is `0.001`, and maximum Stage B
  orientation error is `0.11997895388586574 rad`.
- Consequence:
  The qdot012 branch of the v73 sensitivity failure is recovered under the
  diagnostic label. The harder `paper_time_scale_0p0075` and
  `orientation_gate_0p119` `+1.0 mm` limits remain unresolved. The project
  still must not claim robustness, strict paper-equivalent feasibility,
  contact-model calibration, or hardware readiness.

## D081: Treat The Faster-Timing Failure As An E2 Orientation Boundary

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v76 as evidence that the v73 `paper_time_scale_0p0075` `+1.0 mm`
  failure is first an E2 orientation-margin boundary under the current
  diagnostic `0.12 rad` gate.
- Reason:
  The v76 run at `runs/positive_timing_boundary/20260524T200236` holds the v70
  relaxed target/path setup, `stage_a_duration_s = 15.0`,
  `qdot_limit_rad_s = 0.15`, and `max_orientation_error_rad = 0.12` fixed while
  sweeping Stage B `paper_time_scale` for the hardest `+1.0 mm` row. Stage A
  passes every timing case. Stitched recovery passes at `0.005` and `0.0052`,
  then first fails at `0.0054` because E2 orientation reaches
  `0.12001811086329595 rad`. Qdot saturation remains low at the first failing
  scale and becomes severe only at `0.007` and above.
- Consequence:
  The faster-timing sensitivity limit is bounded but not recovered under the
  current diagnostic gate. The next branch should either move to the separate
  `orientation_gate_0p119` `+1.0 mm` limit or test a targeted Stage B
  orientation-margin/control change without relaxing the diagnostic gate. The
  project still must not claim robustness, strict paper-equivalent feasibility,
  contact-model calibration, or hardware readiness.

## D082: Treat The Tightened Orientation Failure As An E2 Gate Margin

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v77 as evidence that the v73 `orientation_gate_0p119` `+1.0 mm`
  failure is a narrow orientation-gate margin controlled by E2 under the v72
  timing, not an unresolved Stage A path or qdot issue.
- Reason:
  The v77 run at `runs/positive_orientation_gate_boundary/20260524T221842`
  holds the v70 relaxed target/path setup, `stage_a_duration_s = 15.0`,
  `paper_time_scale = 0.005`, and `qdot_limit_rad_s = 0.15` fixed while
  sweeping both the run-local Stage A terminal orientation gate and the Stage B
  orientation gate for the hardest `+1.0 mm` row. Stage A first passes at
  `0.1195 rad`, matching the terminal orientation value
  `0.11948560786547915 rad`. Full stitched recovery first passes at
  `0.11998 rad`, matching the maximum Stage B orientation error
  `0.1199788204275829 rad` from E2.
- Consequence:
  The tightened-orientation sensitivity limit is localized but not converted
  into a stronger robustness or paper-equivalent claim. The next branch should
  test a targeted Stage B orientation-margin/control change or revisit the
  terminal/contact model before claiming anything beyond diagnostic recovery.
  The project still must not claim robustness, strict paper-equivalent
  feasibility, contact-model calibration, or hardware readiness.

## D083: Reject Single-Gain Stage B Orientation Feedback As The Tightened-Gate Fix

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v78 as evidence that enabling the existing Stage B `orientation_kp`
  feedback hook is not a clean recovery for the v77 tightened-orientation
  `+1.0 mm` E2 boundary under the current linear-primary formulation.
- Reason:
  The v78 run at `runs/stage_b_orientation_kp_probe/20260524T222953` holds the
  v70 relaxed target/path setup, `stage_a_duration_s = 15.0`,
  `paper_time_scale = 0.005`, and a `0.11995 rad` Stage A/Stage B orientation
  gate fixed while sweeping qdot limits `[0.15, 0.16, 0.18, 0.2, 0.25] rad/s`
  and `orientation_kp` values `[0, 0.001, 0.002, 0.003, 0.005, 0.01]` for the
  localized E2 row. Stage A passes all `30 / 30` cells, but stitched recovery
  passes `0 / 30`. Low gains preserve qdot budget and still fail
  `max_orientation_error_rad`; gains that reduce E2 orientation below the gate
  fail qdot saturation and/or tail qdot utilization, even at relaxed qdot
  limits up to `0.25 rad/s`.
- Consequence:
  The next branch should revisit the terminal/contact model or test a
  redesigned Stage B priority/posture formulation that can create orientation
  margin without driving qdot saturation. The project still must not claim
  robustness, strict paper-equivalent feasibility, contact-model calibration,
  or hardware readiness.

## D084: Accept Planar-Primary Stage B Priority As A Localized Tightened-Gate Recovery

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v79 as evidence that a planar-primary Stage B priority formulation
  with normal-axis secondary weight `30` locally recovers the `+1.0 mm`,
  `0.11995 rad` tightened-orientation diagnostic row.
- Reason:
  The v79 run at `runs/stage_b_priority_recovery/20260524T224404` holds the
  v70 relaxed target/path setup, `stage_a_duration_s = 15.0`,
  `paper_time_scale = 0.005`, `qdot_limit_rad_s = 0.15`, and a `0.11995 rad`
  Stage A/Stage B orientation gate fixed while comparing seven priority
  scenarios over E1-E4. Stage A passes every scenario. Linear-primary controls
  still fail: no orientation feedback misses E2 orientation, linear-primary
  `orientation_kp = 0.003` saturates qdot, and adding handoff-posture
  regularization preserves qdot by giving up orientation correction.
  Planar-primary controls show a normal-force tradeoff, but normal-axis weight
  `30` passes E1-E4 for both `orientation_kp = 0.001` and `0.002`.
- Consequence:
  The v77/v78 localized tightened-gate row has a diagnostic Stage B priority
  recovery candidate. Do not generalize it yet to the full positive-delta
  matrix, robustness, strict paper-equivalent feasibility, contact-model
  calibration, or hardware readiness. The next branch should run the recovered
  planar-primary formulation across the full positive-delta matrix or stress
  it against faster timing/tighter gates.

## D085: Treat Planar-Primary Priority As A Full Positive-Matrix Diagnostic Recovery

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v80 as evidence that the v79 planar-primary Stage B priority
  formulation recovers the full positive-delta diagnostic matrix under the
  tested `0.11995 rad` tightened orientation gate.
- Reason:
  The v80 run at `runs/positive_planar_priority_matrix/20260524T225138` holds
  the v70 relaxed target/path setup, `stage_a_duration_s = 15.0`,
  `paper_time_scale = 0.005`, `qdot_limit_rad_s = 0.15`, and a `0.11995 rad`
  Stage A/Stage B orientation gate fixed. It evaluates both v79 passing
  candidates, `planar_normal30_kp0p001` and `planar_normal30_kp0p002`, across
  all eight positive deltas through `+1.0 mm` and all E1-E4 Stage B
  trajectories. Both scenarios pass `8 / 8`, for `16 / 16` total stitched
  passes. The larger-gain candidate has lower max orientation error
  (`0.11961552028823065 rad`) but a larger max tail force error
  (`0.1902561439715911 N`), still inside the gate.
- Consequence:
  The full positive-delta diagnostic matrix is recovered for the planar-primary
  formulation at the tested timing and gate. Do not generalize yet to
  faster-timing recovery, qdot012 tightened-gate recovery, robustness, strict
  paper-equivalent feasibility, contact-model calibration, or hardware
  readiness. The next branch should stress the recovered formulation against
  faster timing and the tighter `0.119 rad` orientation gate.

## D086: Keep V81 Planar-Priority Stress As Boundary Evidence, Not Robustness

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v81 as evidence that planar-primary priority improves the focused
  faster-timing and tightened-gate boundaries, but does not recover the full
  unresolved v73 stress faces.
- Reason:
  The v81 run at `runs/planar_priority_stress/20260524T230109` holds the v70
  relaxed target/path setup, `stage_a_duration_s = 15.0`, and
  `qdot_limit_rad_s = 0.15` fixed while testing both v80 candidates. Both
  candidates pass the focused `+1.0 mm` timing sweep through
  `paper_time_scale = 0.0065` and first fail at `0.007`. The focused
  tightened-gate sweep first passes at `0.1198 rad` for
  `orientation_kp = 0.001` and `0.1197 rad` for `orientation_kp = 0.002`.
  However, the full positive-delta `paper_time_scale = 0.0075`,
  `orientation_gate = 0.11995` stress fails `0 / 16` stitched cells across the
  two candidates, and the `orientation_gate = 0.119` stress still fails the
  `+1.0 mm` row for both candidates.
- Consequence:
  The planar-primary formulation is a useful diagnostic recovery, but it is
  still not a robustness, strict paper-equivalent, contact-calibrated, or
  hardware-ready control claim. The next branch should either redesign the E2
  faster-timing qdot/tail-utilization behavior at `paper_time_scale = 0.0075`,
  or revisit the terminal/contact model and orientation gate before further
  Stage B tuning of the `+1.0 mm`, `0.119 rad` case.

## D087: Treat Weighted Zero-Angular Priority As The Faster-Timing Recovery Candidate

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v82 as evidence that the v81 faster-timing failure is
  priority-formulation dependent and is recovered by weighted
  zero-angular-command Stage B priority under the tested `0.11995 rad` gate.
- Reason:
  The v82 run at `runs/weighted_timing_recovery/20260524T231454` compares
  linear-primary, the two v80 planar-primary candidates, and two weighted
  zero-angular-command candidates on the full positive-delta
  `paper_time_scale = 0.0075`, `orientation_gate = 0.11995 rad` stress face.
  Linear-primary passes `7 / 8` and still fails `+1.0 mm`; the two
  planar-primary candidates each pass `0 / 8`; both weighted candidates pass
  `8 / 8` through `+1.0 mm` with max Stage B orientation
  `0.11954627160547111 rad`, max qdot saturation `0.0`, max tail qdot
  utilization `0.5177926211135458`, and max tail force error
  `0.0009911909058976187 N`. The focused `+1.0 mm`
  `weighted_kp0_normal1` timing sweep passes every tested value from
  `paper_time_scale = 0.005` through `0.01`.
- Consequence:
  The faster-timing face is diagnostically recovered under the `0.11995 rad`
  gate, but weighted zero-angular priority is not yet a canonical controller
  default and does not recover the tighter `0.119 rad` gate. The next branch
  should stress this candidate against the tightened gate and decide whether a
  full positive-delta `paper_time_scale = 0.01` matrix is a meaningful
  diagnostic target.

## D088: Treat V83 As Timing Closure And Tightened-Gate Boundary Evidence

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v83 as evidence that the weighted zero-angular-command candidate
  closes the full positive-delta `paper_time_scale = 0.01` diagnostic matrix
  under the `0.11995 rad` gate, but still does not recover the tighter
  `0.119 rad` orientation gate at `+1.0 mm`.
- Reason:
  The v83 run at `runs/weighted_gate_time_matrix/20260524T232637` holds the
  v70 relaxed target/path setup, `stage_a_duration_s = 15.0`, and
  `qdot_limit_rad_s = 0.15` fixed while testing two weighted
  zero-angular-command scenarios. Under `orientation_gate = 0.11995 rad`, both
  scenarios pass all eight positive deltas at `paper_time_scale = 0.01`. Under
  `orientation_gate = 0.119 rad`, both tested timings pass only through
  `+0.75 mm` and fail the `+1.0 mm` row. The focused `+1.0 mm` gate boundary
  first passes at `0.11955 rad` for `paper_time_scale = 0.0075` and
  `0.1196 rad` for `paper_time_scale = 0.01`.
- Consequence:
  The faster-timing diagnostic face can be treated as closed under the
  `0.11995 rad` gate, but the remaining simulation blocker is the `+1.0 mm`,
  `0.119 rad` orientation-gate row. The next work should revisit the
  terminal/contact orientation definition or model calibration before more
  Stage B qdot tuning. This is not a canonical controller default, robustness
  proof, strict paper-equivalent feasibility, contact-model calibration, or
  hardware-readiness evidence.

## D089: Attribute The Remaining Tightened-Gate Miss To Orientation Model Margin

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v84 as evidence that the remaining `+1.0 mm`, `0.119 rad` weighted
  failure is a small orientation-model/gate-margin issue, not a faster-timing
  qdot saturation issue.
- Reason:
  The v84 run at
  `runs/weighted_orientation_model_sensitivity/20260524T233945` reads the v83
  weighted gate/time matrix and the v69 positive terminal orientation audit.
  The critical v83 weighted rows exceed the `0.119 rad` gate by less than
  `0.00057 rad` (`0.033 deg`) while reporting `0.0` qdot saturation. The v69
  current contact-point versus legacy sphere-center geometry convention shifts
  the +1.0 mm terminal orientation by `0.024227219479550713 rad`, much larger
  than the residual v83 miss.
- Consequence:
  Do not treat more Stage B qdot tuning as the next primary path for the
  `0.119 rad` row. The next work should tighten terminal/contact orientation
  definition, mounted-stack/contact geometry, plane/contact normal calibration,
  or the accepted diagnostic gate. This is not a recovery, calibrated model,
  robustness proof, strict paper-equivalent feasibility, or hardware-ready
  control claim.

## D090: Treat The Remaining 0.119 Rad Miss As A Calibration-Definition Margin

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record v85 as evidence that the remaining weighted `+1.0 mm`,
  `0.119 rad` diagnostic miss is small enough to be treated as a
  contact-orientation calibration/definition margin, not a reason for more
  Stage B qdot tuning.
- Reason:
  The v85 run at
  `runs/contact_orientation_calibration_margin/20260524T235723` reads the v84
  sensitivity audit, v83 weighted gate/time matrix, v69 positive terminal
  orientation audit, v77 focused orientation-gate boundary, and current
  contact/acceptance configs. The hardest remaining weighted row exceeds the
  `0.119 rad` gate by `0.0005664520369604714 rad`
  (`0.03245531101442353 deg`) with `0.0` qdot saturation. Under the v84
  high-end terminal slope proxy, that corresponds to
  `0.014963398168061883 mm` (`14.963398168061882 um`) of equivalent base-z or
  contact-point correction. The contact-point versus legacy-center convention
  shift is `0.024227219479550713 rad`, about `42.77` times larger than the
  remaining required rotation.
- Consequence:
  Existing metrics show scoped recovery at `0.11955`, `0.1196`, and
  `0.11995 rad`, but those gates are not accepted replacements without
  calibrated TCP/contact point, contact patch convention, plane normal, and
  force-frame evidence. The next work should collect or define those
  calibration facts before more controller tuning. This is not a recovery,
  calibrated model, robustness proof, strict paper-equivalent feasibility, or
  hardware-ready control claim.

## D091: Reject Current Local Records As Sufficient Calibration Evidence

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v86 as evidence that current local hardware, EOAT, CAD, config, and
  MJCF records are not sufficient to accept the v85 calibration margin or any
  replacement orientation gate.
- Reason:
  The v86 run at `runs/measured_geometry_readiness/20260525T000739` inspects
  the lab-vault hardware state, EOAT TCP note, v13 EOAT verification metadata,
  contact-point config/MJCF, and v85 metrics. The records show a CAD/design
  `85.0 mm` contact-point candidate, a temporary UR TCP readback
  `[0, 0, 0.12254, 0, 0, 0]` not validated for contact, an unverified KSM
  contact-patch/ball datum, an analytic MuJoCo `10 deg` plane normal rather
  than a measured robot-base-frame normal, and an unresolved force-source
  disagreement where direct TCP DAQ `READFT` reports about `-32.7 N` while
  RTDE/PolyScope force values are near zero.
- Consequence:
  Do not relax the orientation gate or claim hardware readiness from the v85
  margin. The next work should be a read-only measurement/SOP for mounted-stack
  TCP/contact point, KSM contact patch convention, plane normal, force-source
  reconciliation, and accepted orientation-gate semantics. This is not a
  recovery, calibrated model, robustness proof, strict paper-equivalent
  feasibility, or hardware-ready control claim.

## D092: Require A Read-Only Measurement SOP Before Calibration Claims

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v87 as the safety and evidence gate for collecting the measurements
  missing after v86. No contact-model update, orientation-gate relaxation, or
  hardware-readiness claim may proceed until the read-only SOP evidence is
  collected and passes its gates.
- Reason:
  The v87 SOP at `reports/read_only_calibration_measurement_sop.md` defines
  required artifacts, pass/fail gates, and abort conditions for mounted-stack
  TCP/contact point, KSM contact patch convention, plane normal in the robot
  base frame, force-source/frame reconciliation, and orientation-gate
  semantics. It ties acceptance directly to the v85 margins:
  `14.963398168061882 um` equivalent geometry and
  `0.03245531101442353 deg` normal rotation.
- Consequence:
  The next work may only execute safe read-only portions of the SOP after
  explicit user confirmation, or refine the SOP if a measurement path is
  ambiguous. The SOP itself is not a recovery, executed calibration,
  robustness proof, strict paper-equivalent feasibility, hardware-readiness
  claim, or authorization for motion, writes, zeroing, or force control.

## D093: Make Read-Only Measurement Evidence Collection Template-First

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v88 as a template/scaffold iteration for the v87 read-only SOP. The
  next calibration evidence collection should start from a generated run folder
  with explicit worksheets, safety flags, claim-boundary metrics, and git state
  rather than ad hoc notes.
- Reason:
  No live bench read was explicitly approved in this thread. The safe next
  action is therefore to make the SOP executable as a non-executed artifact:
  `templates/read_only_calibration_measurement/`,
  `scripts/create_read_only_calibration_measurement_run.py`, and
  `runs/read_only_calibration_measurement/20260525T012234`. The generated
  metrics mark live hardware access, robot motion, configuration writes,
  zeroing/biasing, force control, contact-model updates, gate relaxation, and
  hardware readiness as false.
- Consequence:
  Future SOP execution still requires explicit user approval for the exact
  read-only step. The template is not collected measurement evidence, not an
  accepted calibration, not a gate relaxation, and not authorization for robot
  motion, writes, zeroing, force control, or hardware claims.

## D094: Require Offline Run-Audit Before Treating Read-Only Worksheets As Evidence

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v89 as an offline audit gate for read-only calibration measurement
  run folders. A scaffolded or worksheet-filled run should be checked by
  `scripts/audit_read_only_calibration_measurement_run.py` before it is cited
  as evidence.
- Reason:
  The v89 audit at
  `runs/read_only_calibration_measurement_run_audit/20260525T012835` verifies
  required files, metrics YAML/JSON consistency, worksheet headers, non-executed
  status, false execution flags, false hardware/gate/calibration verdicts,
  false claim-boundary flags, expected missing-evidence statuses, and absence
  of heavy payloads. The v88 scaffold run passed with no violations.
- Consequence:
  Passing the audit only proves that the run remains internally consistent and
  claim-safe. It is not measurement evidence, not an accepted calibration, not
  a gate relaxation, and not authorization for robot motion, writes, zeroing,
  force control, or hardware claims.

## D095: Split Read-Only Run Audit Into Scaffold And Approved-Evidence Modes

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v90 as the audit-mode refinement for read-only calibration
  measurement runs. Use `--audit-mode scaffold` for untouched template runs and
  `--audit-mode approved-read-only` for future runs where the user explicitly
  approved a read-only evidence step.
- Reason:
  The v89 verifier was intentionally strict and only accepted non-executed
  scaffolds. A future approved read-only run may legitimately set
  `user_confirmed_read_only_step = true`, may record live read-only access, and
  may add worksheet rows. V90 allows those fields only in the approved mode,
  while continuing to hard-fail robot motion, configuration writes,
  zeroing/biasing, force control, contact-model updates, gate relaxation,
  hardware claims, and hardware readiness.
- Consequence:
  The audit mode must match the run state. Passing either mode is not itself an
  accepted calibration, gate relaxation, robustness proof, strict
  paper-equivalent claim, or hardware authorization.

## D096: Finalize Read-Only Evidence Runs Through An Explicit Offline Gate

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v91 as the required offline finalization gate for converting a
  scaffolded read-only calibration measurement run into
  `approved_read_only_evidence`.
- Reason:
  V90 allowed future approved read-only evidence runs, but manually editing
  metrics creates avoidable drift risk. The v91 finalizer requires the exact
  read-only approval phrase, approved step ID, operator, explicit
  `live_hardware_accessed` metadata, matching YAML/JSON metrics, default
  scaffold safety state, and at least one worksheet CSV row before it writes
  approval metadata and derived evidence statuses. It then self-checks the run
  with the v90 `approved-read-only` audit mode.
- Consequence:
  Future read-only worksheet evidence should use
  `scripts/finalize_read_only_calibration_measurement_evidence.py` before
  being cited. Passing this finalizer is not an executed calibration, accepted
  gate relaxation, robustness proof, strict paper-equivalent claim,
  hardware-readiness claim, or authorization for robot motion, writes, zeroing,
  or force control.

## D097: Make KSM And Orientation Semantics First-Class Read-Only Worksheets

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v92 as the worksheet coverage refinement for KSM contact patch
  convention and orientation-gate semantics evidence.
- Reason:
  V87-V91 tracked these evidence needs, but KSM convention and orientation
  semantics still depended on prose artifacts. V92 adds optional worksheet CSVs
  for both items, validates their headers when present, rejects worksheet rows
  in scaffold audit mode, and allows the finalizer to derive read-only evidence
  statuses from approved rows. This keeps future evidence capture structured
  without breaking older run folders.
- Consequence:
  A collected orientation semantics row is still evidence collection, not gate
  acceptance. Gate relaxation, contact-model update, hardware readiness, and
  robot motion remain disallowed until separately approved and audited.

## D098: Keep Orientation Evidence Separate From Gate Acceptance

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v93 as the explicit not-accepted orientation-gate boundary for
  read-only calibration measurement runs.
- Reason:
  V92 made orientation-gate semantics collectable as structured read-only
  evidence. Without a separate acceptance boundary, a worksheet row could be
  misread as a replacement orientation gate. V93 adds
  `orientation_gate_acceptance` metrics, keeps `decision = not_accepted`, marks
  the row as evidence-only, requires a separate gate audit, keeps accepted-gate
  fields null, and teaches the audit/finalizer to reject acceptance drift.
- Consequence:
  Orientation evidence may be collected without implying gate relaxation.
  Accepting any replacement gate remains a separate future workflow and cannot
  be produced by the read-only evidence finalizer.

## D099: Make Gate Acceptance A Separate Non-Default Review Path

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v94 as the separate orientation gate-acceptance review scaffold and
  audit path.
- Reason:
  V93 made the read-only evidence path preserve `not_accepted`, but future
  maintainers still need a place to review a possible gate without editing
  evidence-run metrics by hand. V94 creates
  `templates/orientation_gate_acceptance_review/` plus create/audit commands.
  The scaffold is not invoked by the read-only finalizer, defaults to
  `review_scaffold_not_executed`, keeps source evidence null, keeps the gate
  decision `not_accepted`, and rejects acceptance drift.
- Consequence:
  Gate acceptance is structurally separate from evidence collection. The new
  review scaffold still does not accept a gate, calibrate the contact model,
  prove robustness, or authorize hardware motion, writes, zeroing, force
  control, or hardware-readiness claims.

## D100: Classify Remaining Completion Work By Offline Versus Approval-Blocked

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v95 as the structured offline completion-blockers audit.
- Reason:
  After v94, most safety/evidence scaffolding exists, but it is easy to lose
  track of which remaining items are still blocked on live approved read-only
  evidence and which can continue offline. V95 adds
  `scripts/audit_offline_completion_blockers.py`, which reads current run
  metrics and emits machine-readable blocker classifications.
- Consequence:
  Future work should use the v95 audit before choosing the next branch. Strict
  paper-equivalent feasibility and robustness can advance offline only as
  non-final simulation/paper-platform work. Approved read-only evidence,
  calibrated contact geometry, orientation-gate acceptance, and hardware
  readiness remain blocked until explicit approval/evidence exists.

## D101: Quantify Strict Feasibility As A Setup-Tradeoff Blocker

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v96 as the strict-feasibility blocker audit for the non-final
  offline-actionable strict paper-equivalent item identified by v95.
- Reason:
  V95 said strict paper-equivalent full staged feasibility could still advance
  offline, but the next step needed to identify whether the remaining blocker
  was trajectory tracking or setup feasibility. V96 adds
  `scripts/audit_strict_feasibility_blockers.py`, which reads the existing
  posture-regularized and three-phase settle summaries plus the strict
  acceptance thresholds. It reports strict full staged feasibility `0 / 4`,
  three-phase setup terminal state `0 / 10`, and three-phase trajectory
  feasibility `8 / 10`.
- Consequence:
  Treat the strict-feasibility blocker as a strict setup terminal tradeoff, not
  as a solved trajectory problem. Future offline work may search for a setup
  policy that satisfies tangential, orientation, force, and qdot gates
  simultaneously, but v96 does not prove strict paper-equivalent feasibility,
  robustness, contact calibration, gate acceptance, hardware readiness, or any
  hardware authorization.

## D102: Quantify Robustness As An Accepted-Model Blocker

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v97 as the robustness blocker audit for the non-final
  offline-actionable robustness item identified by v95.
- Reason:
  The project has many diagnostic recovery runs, but they use different
  perturbation sets, timing settings, qdot limits, and relaxed orientation
  gates. V97 adds `scripts/audit_robustness_blockers.py`, which reads the
  existing baseline sensitivity, timing-margin, base-z recovery/bracket,
  positive sensitivity, qdot012 recovery, orientation sensitivity, and contact
  margin metrics. It reports baseline diagnostic stitched sensitivity `4 / 9`,
  positive stitched sensitivity `37 / 40`, and `robustness_complete = false`.
- Consequence:
  Treat recovered faces such as qdot012 positive recovery at `18.035 s` as
  diagnostic non-final evidence until a single accepted robustness matrix and
  accepted contact/gate model exist. V97 does not prove robustness, strict
  paper-equivalent feasibility, contact calibration, gate acceptance, hardware
  readiness, or any hardware authorization.

## D103: Keep The Diagnostic Robustness Matrix Candidate Non-Final

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v98 as a diagnostic robustness matrix candidate, not an accepted
  robustness proof.
- Reason:
  V97 showed that robustness evidence was scattered across baseline
  sensitivity, timing-margin, base-z recovery, positive-delta recovery, and
  orientation-sensitivity runs. V98 adds
  `scripts/audit_diagnostic_robustness_matrix_candidate.py`, which assembles a
  single 12-cell candidate matrix from current evidence. The matrix has 7
  diagnostic passes, 1 non-final diagnostic recovery, and 4 failed cells.
- Consequence:
  Future work can target the failed candidate cells directly. Passing a
  diagnostic matrix is still not enough for completion unless strict
  feasibility, approved read-only evidence, contact calibration, and gate
  acceptance are also closed. V98 does not prove robustness, strict
  paper-equivalent feasibility, contact calibration, gate acceptance, hardware
  readiness, or any hardware authorization.

## D104: Plan Failed Robustness Cells Before Running Heavy Experiments

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v99 as a planned-not-executed offline experiment matrix for the four
  failed v98 diagnostic robustness cells.
- Reason:
  V98 identified the remaining failed cells, but immediately running every
  recovery search would mix planning, execution, and claim interpretation. V99
  adds `scripts/create_failed_diagnostic_robustness_experiment_matrix.py`,
  which verifies the expected failed cells and writes a concrete `commands.sh`
  with one focused offline command per cell. The run remains
  `planned_not_executed`, so future work can execute and audit each cell
  independently.
- Consequence:
  Treat the v99 run as an execution queue, not evidence that any failed cell
  recovered. Running one command still needs a separate comparison audit
  before it can affect the diagnostic matrix. V99 does not prove robustness,
  strict paper-equivalent feasibility, contact calibration, gate acceptance,
  hardware readiness, or any hardware authorization.

## D105: Audit Executed Failed-Cell Commands Before Upgrading Status

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v100 as the first execution/audit pass over one v99 planned failed
  robustness cell, `base_z_plus1mm`.
- Reason:
  V99 deliberately separated experiment planning from execution. V100 runs the
  exact planned `base_z_plus1mm` command, then adds
  `scripts/audit_failed_diagnostic_robustness_experiment_execution.py` so the
  output is compared against the closure criteria instead of interpreted by
  prose alone. The executed row remains unresolved: start pass, terminal pass,
  path geometry pass, and duration recovery are all zero.
- Consequence:
  Do not upgrade the v98/v99 base-z failed cell. Future offline work may run
  one remaining planned command at a time or create a narrower base-z
  diagnostic probe, but every executed command still needs a comparison audit
  before it can affect the matrix. V100 does not prove robustness, strict
  paper-equivalent feasibility, contact calibration, gate acceptance, hardware
  readiness, or any hardware authorization.

## D106: Keep Fast-Timing Recovery Unresolved After Focused Execution

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v101 as the focused execution and audit of the v99
  `positive_fast_timing_0p0075` planned failed cell.
- Reason:
  V99 queued this row because the v98 diagnostic matrix still failed the
  `+1.0 mm`, `paper_time_scale = 0.0075` fast-timing case. V101 runs the
  exact planned command and extends the execution audit to compare the output
  against closure criteria. Stage A passes, but stitched recovery remains
  false: E2 fails qdot saturation, tail qdot utilization, and orientation.
- Consequence:
  Do not upgrade the `positive_fast_timing_0p0075` failed cell. The remaining
  planned cells are `positive_orientation_gate_0p119` and
  `weighted_plus1mm_0p119_gate`, and every future executed command still needs
  a comparison audit before it can affect the matrix. V101 does not prove
  robustness, strict paper-equivalent feasibility, contact calibration, gate
  acceptance, hardware readiness, or any hardware authorization.

## D107: Keep Orientation-Gate Recovery Unresolved At Current Gate

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v102 as the focused execution and audit of the v99
  `positive_orientation_gate_0p119` planned failed cell.
- Reason:
  V99 queued this row because the v98 diagnostic matrix still failed the
  `+1.0 mm`, `0.119 rad` orientation-gate case. V102 runs the exact planned
  orientation-gate sweep and extends the execution audit to compare the output
  against closure criteria. The current `0.119 rad` gate still fails; the
  diagnostic boundary first passes at `0.11998 rad`, which is not an accepted
  replacement gate.
- Consequence:
  Do not upgrade the `positive_orientation_gate_0p119` failed cell, and do not
  treat `0.11998 rad` as an accepted gate. The remaining planned cell is
  `weighted_plus1mm_0p119_gate`, and every future executed command still needs
  a comparison audit before it can affect the matrix. V102 does not prove
  robustness, strict paper-equivalent feasibility, contact calibration, gate
  acceptance, hardware readiness, or any hardware authorization.

## D108: Keep Weighted Gate Recovery Unresolved At Current Gate

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v103 as the focused execution and audit of the v99
  `weighted_plus1mm_0p119_gate` planned failed cell.
- Reason:
  V99 queued this row because the v98 diagnostic matrix still failed the
  weighted `+1.0 mm`, `0.119 rad` gate case. V103 runs the exact planned
  weighted gate/time command and extends the execution audit to compare the
  output against closure criteria. All current `0.119 rad` weighted rows still
  fail on orientation; the diagnostic boundaries first pass at `0.11955 rad`
  for time `0.0075` and `0.1196 rad` for time `0.01`.
- Consequence:
  Do not upgrade the `weighted_plus1mm_0p119_gate` failed cell, and do not
  treat either diagnostic boundary as an accepted gate. All four v99 planned
  commands have now been executed and audited, but none of the four failed
  cells is closed. Future offline work should use narrower probes or await
  approved read-only evidence before changing contact or gate interpretation.
  V103 does not prove robustness, strict paper-equivalent feasibility, contact
  calibration, gate acceptance, hardware readiness, or any hardware
  authorization.

## D109: Use V104 To Classify Remaining Plus1mm Signatures Without Upgrading Cells

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v104 as a post-hoc offline diagnostic probe over the existing
  v100-v103 failed-cell execution metrics.
- Reason:
  All four v99 planned commands have now been executed and audited, but all
  four cells remain unresolved. V104 avoids repeating those heavier commands
  and instead classifies the remaining `+1.0 mm` blocker signatures from the
  actual generated metrics. The probe confirms that
  `positive_fast_timing_0p0075` is the only remaining `+1.0 mm` row with a
  qdot-saturation blocker, while the weighted current-gate rows have max qdot
  saturation `0.0` and remain orientation-margin/gate-acceptance blocked.
- Consequence:
  Do not upgrade any v99 failed cell from v104. Future offline work should
  target either a `base_z_plus1mm` start-contact versus terminal-orientation
  split probe or a focused `positive_fast_timing_0p0075` E2 qdot/usage
  isolation probe. Contact-model and orientation-gate interpretation still
  require approved read-only evidence or an accepted gate review. V104 does not
  prove robustness, strict paper-equivalent feasibility, contact calibration,
  gate acceptance, hardware readiness, or any hardware authorization.

## D110: Stop Treating Positive Fast-Timing E2 As Pure Qdot-Limit Tuning

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v105 as a focused E2-only qdot/usage isolation probe for the
  `positive_fast_timing_0p0075` failed cell.
- Reason:
  V104 identified `positive_fast_timing_0p0075` as the only unresolved
  `+1.0 mm` cell with qdot saturation. V105 tests that hypothesis directly at
  the E2 row. Slowing timing first recovers E2 at `paper_time_scale = 0.0052`,
  but qdot-limit-only probes at `paper_time_scale = 0.0075` fail `0 / 5`
  through `0.3 rad/s`: qdot saturation falls to `0.0`, while orientation stays
  above the run-local `0.12 rad` gate.
- Consequence:
  Do not claim the `positive_fast_timing_0p0075` cell is closed and do not keep
  raising qdot limits as the primary recovery path. Future offline work should
  either probe orientation-margin reduction at `paper_time_scale = 0.0075`
  without accepting a relaxed gate, or switch to the `base_z_plus1mm`
  start-contact versus terminal-orientation split. V105 does not prove
  robustness, strict paper-equivalent feasibility, contact calibration, gate
  acceptance, hardware readiness, or any hardware authorization.

## D111: Treat Weighted Fast E2 Recovery As Diagnostic Scope Only

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v106 as an E2-only orientation-margin priority probe for the
  `positive_fast_timing_0p0075` failed cell.
- Reason:
  V105 showed the fast E2 row is not recovered by qdot-limit increases alone.
  V106 keeps `paper_time_scale = 0.0075`, `qdot_limit = 0.15 rad/s`, and the
  run-local `0.12 rad` orientation gate fixed, then compares a compact Stage B
  priority matrix. The weighted rows pass E2 with
  `max_orientation_error_rad = 0.11954627160547111`, qdot saturation `0.0`,
  and tail qdot utilization `0.5177926211135458`; the linear and planar
  probes still fail some combination of qdot, tail-qdot, orientation, or force
  gates.
- Consequence:
  Do not claim the `positive_fast_timing_0p0075` failed cell is closed from
  v106. The probe is E2-only and does not rerun the full E1-E4 audit, make
  `weighted` canonical, accept a replacement orientation gate, prove
  robustness, prove strict paper-equivalent feasibility, calibrate contact
  geometry, establish hardware readiness, or authorize hardware
  motion/configuration. Future offline work may run the full E1-E4 failed-cell
  audit with weighted priority at the fixed `0.12 rad` gate, or switch to the
  `base_z_plus1mm` start-contact versus terminal-orientation split.

## D112: Keep Weighted Full-Cell Fast Recovery As Candidate Until Accepted

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v107 as a full E1-E4 diagnostic recovery probe for the
  `positive_fast_timing_0p0075` face under weighted Stage B priority.
- Reason:
  V106 showed weighted priority clears the isolated E2 row. V107 tests the
  exact `+1.0 mm`, `paper_time_scale = 0.0075`, `qdot_limit = 0.15 rad/s`,
  `0.12 rad` full E1-E4 face. The linear-primary baseline still fails E2 with
  qdot saturation `0.999`, tail qdot utilization `1.0`, and orientation
  `0.12020305872871904 rad`. Both weighted rows pass `4 / 4` with maximum
  Stage B orientation `0.11954627160547111 rad`, qdot saturation `0.0`, and
  tail qdot utilization `0.5177926211135458`.
- Consequence:
  Treat weighted priority as a full-cell diagnostic recovery candidate, not as
  a closed original v99 failed cell. V107 does not accept `weighted` as a
  canonical controller default, prove robustness, prove strict
  paper-equivalent feasibility, calibrate contact geometry, accept a
  replacement orientation gate, establish hardware readiness, or authorize
  hardware motion/configuration. Future offline work should either audit the
  acceptance boundary for promoting weighted priority into a named diagnostic
  controller profile, or switch to the `base_z_plus1mm` start-contact versus
  terminal-orientation split.

## D113: Split Base-Z Plus1mm Without Closing The Failed Cell

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v108 as a post-hoc offline split audit for the unresolved
  `base_z_plus1mm` failed cell.
- Reason:
  V100 executed the exact v99 `base_z_plus1mm` command and found no start
  pass, terminal pass, path geometry pass, or duration recovery. V108 avoids
  rerunning MuJoCo and reads the existing v100, v68, v69, and v70 metrics to
  separate the failure modes. The exact planned start still fails, but the v68
  broader seed search recovers `+1.0 mm` start contact. The v69 terminal row
  passes force, x/y, and contact criteria, while orientation is
  `0.11948560786548146 rad`, exceeding the current `0.08 rad` gate by
  `0.039485607865481456 rad`. The v70 run-local `0.12 rad` gate recovers
  terminal and path feasibility with minimum path duration
  `10.018584837157274 s`, but stitched Stage B remains `3 / 4` at both tested
  durations.
- Consequence:
  Treat the `base_z_plus1mm` start miss as local seed-limited, and treat
  terminal/path recovery as orientation-gate limited under the current
  contact-point model. Do not close the original v99 failed cell, accept
  `0.12 rad` as a canonical gate, change canonical configs, prove robustness,
  prove strict paper-equivalent feasibility, calibrate contact geometry,
  establish hardware readiness, or authorize hardware motion/configuration.
  Future offline work can target weighted-priority acceptance or the relaxed
  `base_z_plus1mm` Stage B handoff blocker.

## D114: Keep Relaxed Base-Z Weighted Handoff Recovery Diagnostic

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v109 as a diagnostic weighted-priority handoff probe for the relaxed
  `base_z_plus1mm` path.
- Reason:
  V108 showed that the run-local `0.12 rad` gate recovers `base_z_plus1mm`
  Stage A endpoint/path evidence but leaves stitched Stage B at `3 / 4`. V109
  reruns the v70 relaxed path at Stage A durations `15.0 s` and `16.0 s`,
  comparing the linear-primary baseline with the two weighted priority rows.
  The baseline reproduces the E2 blocker at both durations with max
  orientation `0.12043140848858806 rad`, qdot saturation `0.997`, and tail
  qdot utilization `1.0`. Both weighted rows pass `4 / 4` at both durations
  with max orientation `0.11956645203696047 rad`, qdot saturation `0.0`, and
  tail qdot utilization `0.520987929048311`.
- Consequence:
  Treat weighted priority as a diagnostic recovery candidate for both the v107
  fast-timing face and the v109 relaxed base-z handoff, but do not close the
  original v99 failed cells. Do not accept `0.12 rad` as a canonical gate,
  accept weighted priority as a canonical controller default, change canonical
  configs, prove robustness, prove strict paper-equivalent feasibility,
  calibrate contact geometry, establish hardware readiness, or authorize
  hardware motion/configuration. Future offline work should define the
  acceptance boundary for a named diagnostic weighted profile without changing
  the canonical claim boundary.

## D115: Name Weighted Priority Only As A Diagnostic Profile

- Date: 2026-05-25
- Status: accepted
- Decision:
  Record v110 as the profile-boundary audit that supports the name
  `weighted_zero_angular_stage_b_diagnostic` for the covered v107 and v109
  diagnostic faces.
- Reason:
  V107 and v109 both reproduce a linear-primary E2 failure while recovering the
  covered E1-E4 Stage B rows under weighted priority. V107 has one baseline
  failed face and two weighted passes; v109 has two baseline failed duration
  rows and four weighted passes. Across the covered faces, weighted priority
  has maximum Stage B orientation `0.11956645203696047 rad`, maximum qdot
  saturation `0.0`, and maximum tail qdot utilization
  `0.520987929048311`.
- Consequence:
  The profile name may be used for diagnostic-label discussion of the covered
  faces, but it is not a canonical controller default. V110 does not accept
  the `0.12 rad` orientation gate as canonical, close any original v99 failed
  cell, prove robustness, prove strict paper-equivalent feasibility, calibrate
  contact geometry, establish hardware readiness, or authorize hardware
  motion/configuration. Future offline work may restate the diagnostic
  robustness matrix using this named profile only if those same boundaries are
  preserved.
