#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from dataclasses import asdict

import numpy as np
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.paper_7dof import (  # noqa: E402
    PaperSectionV7DofConfig,
    simulate_paper_section_v_7dof,
    summarize_paper_section_v_7dof,
)


def git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except subprocess.CalledProcessError:
        return "unavailable"


def write_summary(out_dir: pathlib.Path, run_id: str, metrics: dict, config: PaperSectionV7DofConfig) -> None:
    lines = [
        "# Paper 7DOF Section V Diagnostic",
        "",
        f"Run id: `{run_id}`",
        "",
        "Scope: separate paper-platform 7DOF executable diagnostic for the paper Section V setup.",
        "This is not a UR10e adapted run and not a hardware gate.",
        "",
        "Implemented coverage:",
        "",
        "- 7 joint Panda/Franka DH kinematics ported from the legacy MATLAB `forward_panda.m` and `getJacobian_panda.m` files.",
        "- Paper Section V q0, circle trajectory, 5 N normal force target, joint limits, velocity limits, and finite-time inner-loop projection.",
        "- Explicit `z0` convention: q0 forward-kinematics height, because Section V uses `z0` without defining it.",
        "",
        "Known limits:",
        "",
        "- The Panda DH parameters remain inherited from the legacy MATLAB audit and still need vendor/manual verification.",
        "- The paper's force-derived desired-rotation equation is dimensionally ambiguous; this line uses the documented shortest-arc force-normal interpretation.",
        "- The run is a diagnostic executable line, not a claim of Fig. 5/Fig. 6 numerical parity.",
        "",
        "Key metrics:",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key in [
        "execution_success",
        "contact_force_tail_success",
        "duration_s",
        "sample_count",
        "max_abs_q_rad",
        "max_abs_qdot_rad_s",
        "q_bound_violation_count",
        "qdot_bound_violation_count",
        "velocity_clamp_fraction",
        "contact_fraction",
        "tail_contact_fraction",
        "task_residual_rms",
        "tail_position_error_mean_m",
        "tail_orientation_error_mean_rad",
        "tail_force_error_mean_N",
    ]:
        lines.append(f"| `{key}` | `{metrics[key]}` |")
    lines.extend(
        [
            "",
            "Config snapshot:",
            "",
            "```yaml",
            yaml.safe_dump(asdict(config), sort_keys=False).strip(),
            "```",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-s", type=float, default=5.0)
    parser.add_argument("--dt-s", type=float, default=0.002)
    parser.add_argument("--solver-mode", choices=["kkt_projection", "pinv_bounded"], default="kkt_projection")
    parser.add_argument("--orientation-mode", choices=["force_shortest_arc", "normal_only"], default="force_shortest_arc")
    parser.add_argument("--communication-delay-s", type=float, default=0.032)
    parser.add_argument("--force-integral-limit", type=float, default=float("inf"))
    parser.add_argument("--force-integral-leak", type=float, default=0.0)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    git_commit = git_value(["rev-parse", "HEAD"])
    git_status_short = git_value(["status", "--short"])
    out_dir = pathlib.Path(args.output_dir) if args.output_dir else ROOT / "runs" / "paper_7dof_section_v" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    config = PaperSectionV7DofConfig(
        duration_s=args.duration_s,
        dt_s=args.dt_s,
        solver_mode=args.solver_mode,
        orientation_mode=args.orientation_mode,
        communication_delay_s=args.communication_delay_s,
        force_integral_limit=args.force_integral_limit,
        force_integral_leak=args.force_integral_leak,
    )
    result = simulate_paper_section_v_7dof(config)
    metrics = summarize_paper_section_v_7dof(result)
    payload = {
        "run_id": run_id,
        "git_commit": git_commit,
        "git_status_short": git_status_short,
        "metrics": metrics,
        "config": asdict(config),
    }

    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    np.savez(
        out_dir / "paper_7dof_section_v_raw.npz",
        t_s=result.t_s,
        q_rad=result.q_rad,
        qdot_rad_s=result.qdot_rad_s,
        position_m=result.position_m,
        desired_position_m=result.desired_position_m,
        position_error_m=result.position_error_m,
        orientation_error_rad=result.orientation_error_rad,
        task_residual_norm=result.task_residual_norm,
        force_error_N=result.force_error_N,
        measured_force_N=result.measured_force_N,
        contact_active=result.contact_active,
        commanded_task_velocity=result.commanded_task_velocity,
        projected_qdot=result.projected_qdot,
    )
    write_summary(out_dir, run_id, metrics, config)
    print(f"wrote {out_dir}")
    print(yaml.safe_dump(metrics, sort_keys=False).strip())
    return 0 if metrics["execution_success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
