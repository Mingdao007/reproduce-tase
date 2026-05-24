#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

import numpy as np
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.contact_manifold_gate_audit import run_contact_manifold_gate_audit
from tase_repro.setup_terminal_ik import SetupTerminalThresholds


def parse_vector(text: str) -> np.ndarray:
    return np.asarray([float(part.strip()) for part in text.split(",")], dtype=float)


def parse_float_list(text: str) -> list[float]:
    return [float(part.strip()) for part in text.split(",") if part.strip()]


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
    parser.add_argument("--config", default="configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml")
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
    parser.add_argument("--random-seed", type=int, default=761)
    parser.add_argument("--random-seed-stds-rad", default="0.03,0.1,0.3,0.8")
    parser.add_argument("--random-seed-count-per-std", type=int, default=32)
    parser.add_argument("--max-nfev", type=int, default=800)
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
        else ROOT / "runs" / "contact_manifold_gate_audit" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    result = run_contact_manifold_gate_audit(
        model_path,
        initial_q=parse_vector(args.initial_q),
        base_z_offset_m=base_z_offset,
        target_force_N=args.target_force_N,
        thresholds=thresholds,
        surface_normal_world=surface_normal,
        site_name=args.site_name,
        contact_geom_name=args.contact_geom_name,
        plane_geom_name=args.plane_geom_name,
        random_seed=args.random_seed,
        random_seed_stds_rad=parse_float_list(args.random_seed_stds_rad),
        random_seed_count_per_std=args.random_seed_count_per_std,
        max_nfev=args.max_nfev,
    )
    metrics = {
        "config": str(config_path),
        "model": str(model_path),
        "run_id": run_id,
        "random_seed": int(args.random_seed),
        "random_seed_stds_rad": parse_float_list(args.random_seed_stds_rad),
        "random_seed_count_per_std": int(args.random_seed_count_per_std),
        "max_nfev": int(args.max_nfev),
        **result.to_dict(),
        "warnings": [
            "simulation-only gate-definition audit",
            "not a path or controller feasibility proof",
            "not a global infeasibility proof",
            "not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    strict = result.strict_case.best_candidate
    summary_lines = [
        "# Contact-Manifold Gate Audit Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        "## Result",
        "",
        f"- Seed count: `{len(result.seed_labels)}`",
        f"- Target signed surface distance m: `{result.target_signed_surface_distance_m}`",
        f"- Strict pass count: `{result.strict_case.pass_count}`",
        f"- Strict best failed criteria: `{';'.join(strict.failed_criteria) or 'none'}`",
        f"- Strict best max gate ratio: `{strict.max_gate_ratio}`",
        f"- Strict best force error N: `{strict.force_error_N}`",
        f"- Strict best x/y error m: `{strict.tangential_error_m}`",
        f"- Strict best orientation error rad: `{strict.orientation_error_rad}`",
        "",
        "## Gate Cases",
        "",
    ]
    for case in result.cases:
        best = case.best_candidate
        summary_lines.extend(
            [
                f"### {case.name}",
                "",
                f"- Optimized terms: `{','.join(case.optimized_terms)}`",
                f"- Pass count: `{case.pass_count} / {case.candidate_count}`",
                f"- Best failed criteria: `{';'.join(best.failed_criteria) or 'none'}`",
                f"- Best force error N: `{best.force_error_N}`",
                f"- Best x/y error m: `{best.tangential_error_m}`",
                f"- Best orientation error rad: `{best.orientation_error_rad}`",
                "",
            ]
        )
    summary_lines.extend(
        [
            "## Limits",
            "",
            "This audit probes terminal gate compatibility from target-contact",
            "neighborhoods. It does not prove global infeasibility and does not",
            "authorize hardware use.",
            "",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
