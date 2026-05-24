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

from tase_repro.tcp_contact_model_audit import audit_tcp_contact_model


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
    parser.add_argument("--surface-normal-world", default=None)
    parser.add_argument("--site-name", default="tcp_site_unverified_85mm")
    parser.add_argument("--contact-geom-name", default="contact_tip")
    parser.add_argument("--parent-body-name", default="onrobot_hex_v1_primitive")
    parser.add_argument("--tcp-body-name", default="eoat_v13_tcp_guess")
    parser.add_argument("--plane-geom-name", default="contact_plane")
    parser.add_argument("--eoat-note-contact-distance-m", type=float, default=0.085)
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

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "tcp_contact_model_audit" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    audit = audit_tcp_contact_model(
        model_path,
        initial_q=parse_vector(args.initial_q),
        base_z_offset_m=base_z_offset,
        config_tcp_guess_m=np.asarray(contact_cfg["tcp_guess_m"], dtype=float),
        expected_surface_normal_world=surface_normal,
        eoat_note_contact_distance_m=args.eoat_note_contact_distance_m,
        site_name=args.site_name,
        contact_geom_name=args.contact_geom_name,
        parent_body_name=args.parent_body_name,
        tcp_body_name=args.tcp_body_name,
        plane_geom_name=args.plane_geom_name,
    )
    metrics = {
        "config": str(config_path),
        "model": str(model_path),
        "run_id": run_id,
        **audit.to_dict(),
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    if audit.site_coincident_with_contact_geom_center:
        interpretation_lines = [
            "The current model places the TCP site at the center of the colliding",
            "sphere. If the 85 mm EOAT note is intended to be the actual contact",
            "point, then this model adds a contact-surface offset of roughly the",
            "sphere radius. If it is intended to be the sphere center, the physical",
            "contact point is not the configured TCP. This remains simulation-only",
            "and is not hardware-ready.",
        ]
    else:
        interpretation_lines = [
            "The current model separates the TCP site from the colliding sphere",
            "center. This resolves the v53 center/site coincidence for a",
            "contact-point convention, but it remains an approximate simulation",
            "proxy. Any residual site-to-surface projection reflects the current",
            "posture and plane-normal alignment; hardware use still requires",
            "mounted-stack measurement and explicit approval.",
        ]

    summary_lines = [
        "# TCP Contact Model Audit Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        "## Result",
        "",
        f"- Config TCP guess matches model body offset: `{audit.tcp_guess_matches_model_body_offset}`",
        f"- Config TCP guess matches EOAT note distance: `{audit.tcp_guess_matches_eoat_note_distance}`",
        f"- Site coincident with contact geom center: `{audit.site_coincident_with_contact_geom_center}`",
        f"- Contact surface offset requires model decision: `{audit.contact_surface_offset_requires_model_decision}`",
        f"- Parent-to-site distance m: `{audit.parent_to_site_distance_m}`",
        f"- Contact geom local pos m: `{audit.model_contact_geom_local_pos_m.tolist()}`",
        f"- Contact geom radius m: `{audit.contact_geom_radius_m}`",
        f"- Contact count: `{audit.contact_count}`",
        f"- Normal force N: `{audit.normal_force_N}`",
        f"- Site-to-sphere-surface projection on normal m: `{audit.site_to_sphere_surface_projection_on_normal_m}`",
        f"- Parent-to-sphere-surface distance m: `{audit.parent_to_sphere_surface_distance_m}`",
        f"- Surface extension beyond declared TCP m: `{audit.surface_extension_beyond_declared_tcp_m}`",
        "",
        "## Interpretation",
        "",
        *interpretation_lines,
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
