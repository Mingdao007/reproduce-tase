# Master Plan

## Scope

Coordinate the TASE finite-time force-motion reproduction as a Git-backed
research project. The immediate milestone is a clean `v0-paper-audit` baseline
in `Mingdao007/reproduce-tase` that captures existing local work without
pretending it is complete.

## Assumptions

- MuJoCo remains the baseline simulator.
- Existing local artifacts are source material, not authoritative repo state.
- Current UR10e hardware facts come from the lab vault and must be re-read
  before hardware decisions.
- Current work is no-motion and no-write for the real robot.

## Exact Files Touched

- `README.md`
- `.gitignore`
- `REPRODUCTION_PLAN.md`
- `docs/goal.md`
- `configs/*`
- `assets/mjcf/ur10e_nominal.xml`
- `assets/urdf/ur10e_nominal.urdf`
- `scripts/*`
- `src/tase_repro/*`
- `plans/*.md`
- `reports/*.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`

## Commands To Run

```bash
git status --short --branch
scripts/run_tests.sh
python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml
python3 scripts/run_ur10e_mujoco_adaptation.py --config configs/mujoco_ur10e.yaml --smoke
```

## Expected Outputs

- Dedicated branch with migrated source, configs, plans, reports, and
  lightweight run metadata.
- A clear audit of what is verified, synthetic, placeholder, or omitted.
- No real robot writes or motion.

## Pass/Fail Criteria

Pass:

- Repo has a branch and commit that can be pushed to `Mingdao007/reproduce-tase`.
- Mandatory plan and log files exist.
- Large omitted artifacts are listed in a manifest.
- Existing smoke scripts can be re-run or failures are documented.

Fail:

- Reproduction work remains only in the old UR10e workspace.
- Large raw artifacts are committed without an explicit Git LFS decision.
- UR10e adapted results are described as original paper-platform reproduction.

## Rollback Point Or Recovery Command

Before the initial commit, rollback is:

```bash
rm -rf /home/andy/reproduce-tase
```

After push, rollback is a branch revert or deletion after confirming no needed
work exists only on that branch.

## Unresolved Risks

- Paper truth is still not PDF-verified.
- UR10e MJCF is approximate and not calibrated. v54 adds a contact-point
  variant that separates the 85 mm TCP site from the colliding sphere center,
  but v55 still finds `0 / 513` strict terminal passes after enforcing the
  intended `contact_plane` / `contact_tip` force pair. v56 shows the remaining
  strict setup blocker is a gate-definition conflict. v57 adds a diagnostic
  terminal setup label only; v58 selects that label as the next Stage A
  simulation prototype target. v59 shows direct Stage B handoff from that
  target still fails `0 / 4` on qdot saturation. v60 shows a slowed low-gain
  diagnostic handoff can pass `4 / 4`. v61 finds an offline qdot-limited
  contact path to the selected target, v62 tracks that path with a qdot-limited
  joint replay, and v63 stitches the tracker to the slowed handoff with `4 / 4`
  Stage B passes. v64 stress-tests the stitched policy and passes only `4 / 9`
  sensitivity cases, so this is still nominal diagnostic-label simulation
  evidence. v65 recovers the qdot/timing side with explicit margins. v66
  recovers only the `-1 mm` base-z side with a rebalanced start, reoptimized
  path, and `16.0 s` Stage A duration; the exact `15.0 s` `-1 mm` reference
  and `+1 mm` case remain unresolved. v67 brackets the positive side and shows
  recovery already fails at `+0.05 mm` under the current diagnostic
  start/terminal gates. v68 shows the positive-side start contact is
  recoverable through `+1.0 mm` with broader seeds, leaving terminal
  orientation as the audited blocker. v69 shows that, in the current
  contact-point model, force/x-y/contact passes all positive terminal cases,
  while orientation passes none; full-rotation and force-normal-only errors are
  numerically identical, so yaw is not the limiter. This is still not robust,
  paper-equivalent, or hardware evidence.
- OnRobot direct TCP DAQ force values disagree with PolyScope/RTDE readings.
- EOAT TCP and payload are not physically verified for control use.

## Next Executable Step

Test positive-side path/stitched recovery only under an explicit justified
`0.12 rad` terminal orientation envelope, or revisit the contact-point/terminal
target definition if that envelope is unacceptable. Keep strict
paper-equivalent setup, v38 relaxed trajectory-after-setup, and v63-v69
diagnostic staged labels separate.
