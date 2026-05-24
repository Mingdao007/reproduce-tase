# Git State

- Branch: `exp/tase-ur10e-v37-terminal-ik-audit`
- Commit: `8d83f0117875c757051f1b7806a018caa4d70702`
- Dirty tree: `True`
- Status:

```text
?? runs/setup_terminal_ik_audit/
?? scripts/run_setup_terminal_ik_probe.py
?? src/tase_repro/setup_terminal_ik.py
?? tests/test_setup_terminal_ik.py
```

- Command:

```bash
/usr/bin/python3 scripts/run_setup_terminal_ik_probe.py --config configs/mujoco_ur10e_tilted_plane.yaml --random-seed-count 64 --random-seed-std-rad 0.15 --random-seed 37 --max-nfev 300 --posture-weight 0.0001
```
