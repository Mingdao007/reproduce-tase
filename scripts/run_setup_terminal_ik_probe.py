#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

import yaml
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.setup_terminal_ik import SetupTerminalThresholds, solve_setup_terminal_ik


def parse_vector(text: str) -> np.ndarray:
    return np.asarray([float(part.strip()) for part in text.split(",")], dtype=float)


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    content = "\n".join(
        [
            "# Git State",
            "",
            f"- Branch: `{branch}`",
            f"- Commit: `{commit}`",
            f"- Dirty tree: `{bool(status)}`",
            "- Status:",
            "",
            "```text",
            status,
            "```",
            "",
            "- Command:",
            "",
            "```bash",
            " ".join(command),
            "```",
            "",
        ]
    )
    (out_dir / "git_state.md").write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e_tilted_plane.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--initial-q", default="0,-0.1,0.15,-0.05,0,0")
    parser.add_argument("--base-z-offset-m", type=float, default=None)
    parser.add_argument("--target-force-N", type=float, default=5.0)
    parser.add_argument("--surface-normal-world", default=None)
    parser.add_argument("--site-name", default="tcp_site_unverified_85mm")
    parser.add_argument("--contact-geom-name", default="contact_tip")
    parser.add_argument("--plane-geom-name", default="contact_plane")
    parser.add_argument("--max-force-error-N", type=float, default=0.25)
    parser.add_argument("--max-tangential-error-m", type=float, default=0.002)
    parser.add_argument("--max-orientation-error-rad", type=float, default=0.03)
    parser.add_argument("--random-seed-count", type=int, default=64)
    parser.add_argument("--random-seed-std-rad", type=float, default=0.15)
    parser.add_argument("--random-seed", type=int, default=37)
    parser.add_argument("--max-nfev", type=int, default=300)
    parser.add_argument("--posture-weight", type=float, default=1e-4)
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    contact_cfg = cfg["ur10e_mujoco"]["contact"]
    base_z_offset = (
        float(contact_cfg["calibrated_bend_0p10_base_z_offset_m_for_5N"])
        if args.base_z_offset_m is None
        else float(args.base_z_offset_m)
    )
    surface_normal = (
        np.asarray(contact_cfg["expected_normal_world"], dtype=float)
        if args.surface_normal_world is None
        else parse_vector(args.surface_normal_world)
    )
    thresholds = SetupTerminalThresholds(
        max_force_error_N=args.max_force_error_N,
        max_tangential_error_m=args.max_tangential_error_m,
        max_orientation_error_rad=args.max_orientation_error_rad,
    )
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "setup_terminal_ik_audit" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    result = solve_setup_terminal_ik(
        model_path,
        initial_q=parse_vector(args.initial_q),
        base_z_offset_m=base_z_offset,
        target_force_N=args.target_force_N,
        thresholds=thresholds,
        surface_normal_world=surface_normal,
        site_name=args.site_name,
        contact_geom_name=args.contact_geom_name,
        plane_geom_name=args.plane_geom_name,
        random_seed_count=args.random_seed_count,
        random_seed_std_rad=args.random_seed_std_rad,
        random_seed=args.random_seed,
        max_nfev=args.max_nfev,
        posture_weight=args.posture_weight,
    )
    metrics = {
        "config": str(config_path),
        "model": str(model_path),
        "run_id": run_id,
        "base_z_offset_m": base_z_offset,
        "target_force_N": float(args.target_force_N),
        "site_name": args.site_name,
        "contact_geom_name": args.contact_geom_name,
        "plane_geom_name": args.plane_geom_name,
        "random_seed_count": int(args.random_seed_count),
        "random_seed_std_rad": float(args.random_seed_std_rad),
        "random_seed": int(args.random_seed),
        "max_nfev": int(args.max_nfev),
        "posture_weight": float(args.posture_weight),
        **result.to_dict(),
        "warnings": [
            "terminal nonlinear least-squares feasibility audit only",
            "not a path or velocity-controller feasibility proof",
            "uses approximate tilted-plane MuJoCo model and unverified 85 mm TCP",
            "simulation-only and not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    best = result.best_candidate
    initial = result.initial_candidate
    summary_lines = [
        "# Setup Terminal IK Audit Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        "## Result",
        "",
        f"- Candidate count: `{len(result.candidates)}`",
        f"- Terminal setup pass count: `{result.pass_count}`",
        f"- Initial orientation error: `{initial.orientation_error_rad}`",
        f"- Initial x/y error: `{initial.tangential_error_m}`",
        f"- Initial force error: `{initial.force_error_N}`",
        f"- Best seed: `{best.seed_label}`",
        f"- Best pass: `{best.passed}`",
        f"- Best failed criteria: `{';'.join(best.failed_criteria) or 'none'}`",
        f"- Best max gate ratio: `{best.max_gate_ratio}`",
        f"- Best force error N: `{best.force_error_N}`",
        f"- Best x/y error m: `{best.tangential_error_m}`",
        f"- Best orientation error rad: `{best.orientation_error_rad}`",
        "",
        "## Limits",
        "",
        "This probe optimizes only terminal state. It does not prove that a path",
        "exists under the Stage A velocity law, and it is not a global infeasibility",
        "proof.",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
