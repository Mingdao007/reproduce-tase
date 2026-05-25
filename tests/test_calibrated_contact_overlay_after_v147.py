from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import mujoco
import yaml

from scripts.audit_calibrated_contact_overlay_after_v147 import ROOT, build_payload


SOURCE_CONFIG = ROOT / "configs" / "mujoco_ur10e_calibrated_20260525T1641_tcp_offset.yaml"
PREVIOUS = ROOT / "runs" / "calibrated_mjcf_replay_after_v147" / "20260525T212000" / "metrics.yaml"


def test_calibrated_contact_overlay_generates_consistent_geometry(tmp_path: pathlib.Path) -> None:
    overlay_mjcf = tmp_path / "overlay.xml"
    overlay_config = tmp_path / "overlay.yaml"

    payload = build_payload(
        source_config_path=SOURCE_CONFIG,
        previous_metrics_path=PREVIOUS,
        overlay_mjcf_path=overlay_mjcf,
        overlay_config_path=overlay_config,
        run_id="test",
        tip_radius_m=0.045,
        plane_tilt_rad_about_y=0.1745329252,
        normal_world=[0.1736481777, 0.0, 0.9848077530],
        tolerance_m=1.0e-6,
        activation_probe_penetration_m=1.0e-3,
        write_overlay=True,
    )
    summary = payload["summary"]

    assert overlay_mjcf.exists()
    assert overlay_config.exists()
    assert summary["audit_passed"] is True
    assert summary["overlay_model_loads"] is True
    assert summary["current_tcp_site_on_diagnostic_plane"] is True
    assert summary["contact_tip_surface_tangent_to_plane"] is True
    assert summary["non_target_contact_count_at_seed"] == 0
    assert summary["seed_has_no_non_target_contacts"] is True
    assert summary["activation_probe_target_contact_pair_count"] == 1
    assert summary["activation_probe_non_target_contact_count"] == 0
    assert summary["activation_probe_target_normal_force_N"] > 0.0
    assert summary["activation_probe_clean_target_contact"] is True
    assert summary["simulation_can_start_from_diagnostic_overlay"] is True
    assert summary["diagnostic_overlay_acceptance_status"] == "not_accepted"
    assert summary["completion_claim_allowed"] is False
    assert payload["claim_boundary"]["contact_calibration_claim"] is False
    assert payload["claim_boundary"]["hardware_readiness"] is False


def test_calibrated_contact_overlay_mjcf_loads_with_plane_and_tip(tmp_path: pathlib.Path) -> None:
    overlay_mjcf = tmp_path / "overlay.xml"
    overlay_config = tmp_path / "overlay.yaml"
    build_payload(
        source_config_path=SOURCE_CONFIG,
        previous_metrics_path=PREVIOUS,
        overlay_mjcf_path=overlay_mjcf,
        overlay_config_path=overlay_config,
        run_id="test",
        tip_radius_m=0.045,
        plane_tilt_rad_about_y=0.1745329252,
        normal_world=[0.1736481777, 0.0, 0.9848077530],
        tolerance_m=1.0e-6,
        activation_probe_penetration_m=1.0e-3,
        write_overlay=True,
    )

    model = mujoco.MjModel.from_xml_path(str(overlay_mjcf))
    plane_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "diagnostic_contact_plane_unaccepted")
    tip_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "diagnostic_contact_tip_unaccepted")
    marker_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "tcp_live_offset_marker")

    assert model.nq == 6
    assert model.nsite == 1
    assert plane_id >= 0
    assert tip_id >= 0
    assert marker_id >= 0
    assert model.geom_contype[marker_id] == 0
    assert model.geom_conaffinity[marker_id] == 0


def test_calibrated_contact_overlay_rejects_previous_replay_drift(tmp_path: pathlib.Path) -> None:
    previous = yaml.safe_load(PREVIOUS.read_text())
    previous["summary"]["calibrated_mjcf_replay_matches_rtde_tcp"] = False
    drifted_previous = tmp_path / "previous.yaml"
    with drifted_previous.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(previous, handle, sort_keys=False)

    overlay_mjcf = tmp_path / "overlay.xml"
    overlay_config = tmp_path / "overlay.yaml"
    payload = build_payload(
        source_config_path=SOURCE_CONFIG,
        previous_metrics_path=drifted_previous,
        overlay_mjcf_path=overlay_mjcf,
        overlay_config_path=overlay_config,
        run_id="test",
        tip_radius_m=0.045,
        plane_tilt_rad_about_y=0.1745329252,
        normal_world=[0.1736481777, 0.0, 0.9848077530],
        tolerance_m=1.0e-6,
        activation_probe_penetration_m=1.0e-3,
        write_overlay=True,
    )

    assert payload["summary"]["audit_passed"] is False
    assert any("previous calibrated MJCF replay audit did not pass" in v for v in payload["summary"]["violations"])
    assert payload["summary"]["completion_claim_allowed"] is False


def test_calibrated_contact_overlay_cli_writes_no_alias_metrics(tmp_path: pathlib.Path) -> None:
    out_dir = tmp_path / "run"
    overlay_mjcf = tmp_path / "overlay.xml"
    overlay_config = tmp_path / "overlay.yaml"
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_calibrated_contact_overlay_after_v147.py",
            "--run-id",
            "test",
            "--output-dir",
            str(out_dir),
            "--overlay-mjcf",
            str(overlay_mjcf),
            "--overlay-config",
            str(overlay_config),
        ],
        cwd=ROOT,
        check=True,
    )

    metrics_text = (out_dir / "metrics.yaml").read_text()
    metrics_json = json.loads((out_dir / "metrics.json").read_text())

    assert "&id" not in metrics_text
    assert "*id" not in metrics_text
    assert metrics_json["summary"]["audit_passed"] is True
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
