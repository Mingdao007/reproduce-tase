from __future__ import annotations

from pathlib import Path

import numpy as np

from tase_repro.tcp_contact_model_audit import audit_tcp_contact_model

ROOT = Path(__file__).resolve().parents[1]
TILTED_MODEL_PATH = ROOT / "assets" / "mjcf" / "ur10e_tilted_plane_10deg.xml"
TCP_CONTACT_POINT_MODEL_PATH = (
    ROOT / "assets" / "mjcf" / "ur10e_tilted_plane_10deg_tcp_contact_point.xml"
)


def test_tcp_contact_audit_flags_sphere_surface_offset() -> None:
    audit = audit_tcp_contact_model(
        TILTED_MODEL_PATH,
        initial_q=np.array([0.0, -0.1, 0.15, -0.05, 0.0, 0.0]),
        base_z_offset_m=-0.0011631221220595766,
        config_tcp_guess_m=np.array([0.0, 0.0, -0.085]),
        expected_surface_normal_world=np.array([0.1736481777, 0.0, 0.9848077530]),
    )

    assert audit.tcp_guess_matches_model_body_offset
    assert audit.tcp_guess_matches_eoat_note_distance
    assert audit.site_coincident_with_contact_geom_center
    assert audit.contact_surface_offset_requires_model_decision
    assert audit.contact_count == 1
    assert audit.contact_pair == ["contact_plane", "contact_tip"]
    np.testing.assert_allclose(audit.contact_geom_radius_m, 0.045, atol=1e-12)
    np.testing.assert_allclose(
        audit.site_to_sphere_surface_projection_on_normal_m,
        audit.contact_geom_radius_m,
        atol=1e-9,
    )
    assert audit.parent_to_sphere_surface_distance_m is not None
    assert audit.parent_to_sphere_surface_distance_m > 0.12
    assert audit.surface_extension_beyond_declared_tcp_m is not None
    assert audit.surface_extension_beyond_declared_tcp_m > 0.04


def test_tcp_contact_audit_serializes_nullable_contact_fields() -> None:
    audit = audit_tcp_contact_model(
        TILTED_MODEL_PATH,
        initial_q=np.array([0.0, -0.1, 0.15, -0.05, 0.0, 0.0]),
        base_z_offset_m=0.05,
        config_tcp_guess_m=np.array([0.0, 0.0, -0.085]),
        expected_surface_normal_world=np.array([0.1736481777, 0.0, 0.9848077530]),
    )
    data = audit.to_dict()

    assert data["contact_count"] == 0
    assert data["contact_pair"] is None
    assert data["site_to_sphere_surface_projection_on_normal_m"] is None
    assert data["contact_surface_offset_requires_model_decision"] is True


def test_tcp_contact_point_variant_offsets_sphere_center_from_tcp_site() -> None:
    audit = audit_tcp_contact_model(
        TCP_CONTACT_POINT_MODEL_PATH,
        initial_q=np.array([0.0, -0.1, 0.15, -0.05, 0.0, 0.0]),
        base_z_offset_m=-0.04612594095298278,
        config_tcp_guess_m=np.array([0.0, 0.0, -0.085]),
        expected_surface_normal_world=np.array([0.1736481777, 0.0, 0.9848077530]),
    )

    assert audit.tcp_guess_matches_model_body_offset
    assert audit.tcp_guess_matches_eoat_note_distance
    assert not audit.site_coincident_with_contact_geom_center
    assert not audit.contact_surface_offset_requires_model_decision
    np.testing.assert_allclose(audit.model_contact_geom_local_pos_m, [0.0, 0.0, 0.045])
    np.testing.assert_allclose(audit.contact_geom_radius_m, 0.045, atol=1e-12)
    assert audit.contact_count == 1
    np.testing.assert_allclose(audit.normal_force_N, 5.0, atol=1e-6)
    assert audit.site_to_sphere_surface_projection_on_normal_m is not None
    assert audit.site_to_sphere_surface_projection_on_normal_m < 0.001
