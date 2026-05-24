from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import mujoco
import numpy as np

from tase_repro.contact import unit_vector
from tase_repro.contact_ladder import positive_contact_normal_force
from tase_repro.force_feedback import apply_base_z_offset
from tase_repro.kinematics import load_model, make_data, set_qpos


def _named_id(model: mujoco.MjModel, obj_type: mujoco.mjtObj, name: str) -> int:
    obj_id = mujoco.mj_name2id(model, obj_type, name)
    if obj_id < 0:
        raise ValueError(f"{obj_type.name} not found: {name}")
    return obj_id


def _list_or_none(value: np.ndarray | None) -> list[float] | None:
    if value is None:
        return None
    return [float(x) for x in value]


@dataclass(frozen=True)
class TcpContactModelAudit:
    model_path: str
    site_name: str
    contact_geom_name: str
    parent_body_name: str
    tcp_body_name: str
    plane_geom_name: str
    initial_q_rad: np.ndarray
    base_z_offset_m: float
    config_tcp_guess_m: np.ndarray
    eoat_note_contact_distance_m: float
    model_tcp_body_offset_m: np.ndarray
    model_site_local_pos_m: np.ndarray
    model_contact_geom_local_pos_m: np.ndarray
    contact_geom_radius_m: float
    tcp_guess_matches_model_body_offset: bool
    tcp_guess_matches_eoat_note_distance: bool
    site_coincident_with_contact_geom_center: bool
    contact_surface_offset_requires_model_decision: bool
    parent_to_site_distance_m: float
    normal_force_N: float
    contact_count: int
    contact_pair: list[str] | None
    contact_distance_m: float | None
    penetration_m: float | None
    contact_normal_world: np.ndarray | None
    site_world_m: np.ndarray
    contact_geom_center_world_m: np.ndarray
    contact_midpoint_world_m: np.ndarray | None
    sphere_surface_point_world_m: np.ndarray | None
    site_to_contact_midpoint_m: np.ndarray | None
    site_to_contact_midpoint_projection_on_normal_m: float | None
    site_to_sphere_surface_projection_on_normal_m: float | None
    parent_to_contact_midpoint_distance_m: float | None
    parent_to_sphere_surface_distance_m: float | None
    parent_to_sphere_surface_projection_along_parent_to_site_m: float | None
    surface_extension_beyond_declared_tcp_m: float | None
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_path": self.model_path,
            "site_name": self.site_name,
            "contact_geom_name": self.contact_geom_name,
            "parent_body_name": self.parent_body_name,
            "tcp_body_name": self.tcp_body_name,
            "plane_geom_name": self.plane_geom_name,
            "initial_q_rad": [float(x) for x in self.initial_q_rad],
            "base_z_offset_m": float(self.base_z_offset_m),
            "config_tcp_guess_m": [float(x) for x in self.config_tcp_guess_m],
            "eoat_note_contact_distance_m": float(self.eoat_note_contact_distance_m),
            "model_tcp_body_offset_m": [float(x) for x in self.model_tcp_body_offset_m],
            "model_site_local_pos_m": [float(x) for x in self.model_site_local_pos_m],
            "model_contact_geom_local_pos_m": [float(x) for x in self.model_contact_geom_local_pos_m],
            "contact_geom_radius_m": float(self.contact_geom_radius_m),
            "tcp_guess_matches_model_body_offset": bool(self.tcp_guess_matches_model_body_offset),
            "tcp_guess_matches_eoat_note_distance": bool(self.tcp_guess_matches_eoat_note_distance),
            "site_coincident_with_contact_geom_center": bool(self.site_coincident_with_contact_geom_center),
            "contact_surface_offset_requires_model_decision": bool(
                self.contact_surface_offset_requires_model_decision
            ),
            "parent_to_site_distance_m": float(self.parent_to_site_distance_m),
            "normal_force_N": float(self.normal_force_N),
            "contact_count": int(self.contact_count),
            "contact_pair": None if self.contact_pair is None else list(self.contact_pair),
            "contact_distance_m": None if self.contact_distance_m is None else float(self.contact_distance_m),
            "penetration_m": None if self.penetration_m is None else float(self.penetration_m),
            "contact_normal_world": _list_or_none(self.contact_normal_world),
            "site_world_m": [float(x) for x in self.site_world_m],
            "contact_geom_center_world_m": [float(x) for x in self.contact_geom_center_world_m],
            "contact_midpoint_world_m": _list_or_none(self.contact_midpoint_world_m),
            "sphere_surface_point_world_m": _list_or_none(self.sphere_surface_point_world_m),
            "site_to_contact_midpoint_m": _list_or_none(self.site_to_contact_midpoint_m),
            "site_to_contact_midpoint_projection_on_normal_m": (
                None
                if self.site_to_contact_midpoint_projection_on_normal_m is None
                else float(self.site_to_contact_midpoint_projection_on_normal_m)
            ),
            "site_to_sphere_surface_projection_on_normal_m": (
                None
                if self.site_to_sphere_surface_projection_on_normal_m is None
                else float(self.site_to_sphere_surface_projection_on_normal_m)
            ),
            "parent_to_contact_midpoint_distance_m": (
                None
                if self.parent_to_contact_midpoint_distance_m is None
                else float(self.parent_to_contact_midpoint_distance_m)
            ),
            "parent_to_sphere_surface_distance_m": (
                None
                if self.parent_to_sphere_surface_distance_m is None
                else float(self.parent_to_sphere_surface_distance_m)
            ),
            "parent_to_sphere_surface_projection_along_parent_to_site_m": (
                None
                if self.parent_to_sphere_surface_projection_along_parent_to_site_m is None
                else float(self.parent_to_sphere_surface_projection_along_parent_to_site_m)
            ),
            "surface_extension_beyond_declared_tcp_m": (
                None
                if self.surface_extension_beyond_declared_tcp_m is None
                else float(self.surface_extension_beyond_declared_tcp_m)
            ),
            "warnings": list(self.warnings),
        }


def audit_tcp_contact_model(
    model_path: str | Path,
    *,
    initial_q: np.ndarray,
    base_z_offset_m: float,
    config_tcp_guess_m: np.ndarray,
    expected_surface_normal_world: np.ndarray,
    eoat_note_contact_distance_m: float = 0.085,
    site_name: str = "tcp_site_unverified_85mm",
    contact_geom_name: str = "contact_tip",
    parent_body_name: str = "onrobot_hex_v1_primitive",
    tcp_body_name: str = "eoat_v13_tcp_guess",
    plane_geom_name: str = "contact_plane",
    coincidence_tolerance_m: float = 1e-9,
    distance_tolerance_m: float = 1e-6,
) -> TcpContactModelAudit:
    """Audit the current TCP/site/contact-surface relationship in simulation.

    This probe reads MJCF geometry and evaluates one fixed posture. It does
    not command a robot or change controller settings.
    """
    model_path = Path(model_path)
    model = load_model(model_path)
    apply_base_z_offset(model, base_z_offset_m)
    data = make_data(model)
    q = np.asarray(initial_q, dtype=float)
    set_qpos(model, data, q)

    site_id = _named_id(model, mujoco.mjtObj.mjOBJ_SITE, site_name)
    contact_geom_id = _named_id(model, mujoco.mjtObj.mjOBJ_GEOM, contact_geom_name)
    parent_body_id = _named_id(model, mujoco.mjtObj.mjOBJ_BODY, parent_body_name)
    tcp_body_id = _named_id(model, mujoco.mjtObj.mjOBJ_BODY, tcp_body_name)
    plane_geom_id = _named_id(model, mujoco.mjtObj.mjOBJ_GEOM, plane_geom_name)

    config_tcp_guess = np.asarray(config_tcp_guess_m, dtype=float)
    if config_tcp_guess.shape != (3,):
        raise ValueError(f"config_tcp_guess_m shape {config_tcp_guess.shape} does not match (3,)")
    normal = unit_vector(np.asarray(expected_surface_normal_world, dtype=float))
    tcp_body_offset = model.body_pos[tcp_body_id].copy()
    site_local = model.site_pos[site_id].copy()
    geom_local = model.geom_pos[contact_geom_id].copy()
    contact_geom_radius = float(model.geom_size[contact_geom_id, 0])
    site_center_delta = site_local - geom_local
    parent_to_site_local = tcp_body_offset + site_local
    parent_to_site_distance = float(np.linalg.norm(parent_to_site_local))

    contact_idx = None
    for idx in range(data.ncon):
        geom_pair = {int(data.contact[idx].geom[0]), int(data.contact[idx].geom[1])}
        if contact_geom_id in geom_pair and plane_geom_id in geom_pair:
            contact_idx = idx
            break
    if contact_idx is None and data.ncon:
        contact_idx = 0

    contact_pair = None
    contact_distance = None
    penetration = None
    contact_normal = None
    contact_midpoint = None
    sphere_surface = None
    site_to_contact = None
    site_to_contact_projection = None
    site_to_surface_projection = None
    parent_to_contact_distance = None
    parent_to_surface_distance = None
    parent_to_surface_projection = None
    surface_extension = None

    site_world = data.site_xpos[site_id].copy()
    geom_center_world = data.geom_xpos[contact_geom_id].copy()
    parent_world = data.xpos[parent_body_id].copy()
    parent_to_site_world = site_world - parent_world

    if contact_idx is not None:
        contact = data.contact[contact_idx]
        contact_pair = [
            str(mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, int(geom_id)))
            for geom_id in contact.geom
        ]
        contact_distance = float(contact.dist)
        penetration = max(0.0, -contact_distance)
        contact_normal = contact.frame.reshape(3, 3)[0].copy()
        if float(np.dot(contact_normal, normal)) < 0.0:
            contact_normal = -contact_normal
        contact_midpoint = contact.pos.copy()
        sphere_surface = geom_center_world - contact_geom_radius * contact_normal
        site_to_contact = site_world - contact_midpoint
        site_to_contact_projection = float(np.dot(site_to_contact, contact_normal))
        site_to_surface_projection = float(np.dot(site_world - sphere_surface, contact_normal))
        parent_to_contact_distance = float(np.linalg.norm(contact_midpoint - parent_world))
        parent_to_surface_distance = float(np.linalg.norm(sphere_surface - parent_world))
        parent_to_site_axis_norm = float(np.linalg.norm(parent_to_site_world))
        if parent_to_site_axis_norm > 0.0:
            parent_to_site_axis = parent_to_site_world / parent_to_site_axis_norm
            parent_to_surface_projection = float(np.dot(sphere_surface - parent_world, parent_to_site_axis))
            surface_extension = float(parent_to_surface_projection - parent_to_site_distance)

    tcp_guess_matches_offset = bool(
        np.linalg.norm(config_tcp_guess - tcp_body_offset) <= float(distance_tolerance_m)
    )
    tcp_guess_matches_note = bool(
        abs(float(np.linalg.norm(config_tcp_guess)) - float(eoat_note_contact_distance_m))
        <= float(distance_tolerance_m)
    )
    site_coincident = bool(np.linalg.norm(site_center_delta) <= float(coincidence_tolerance_m))
    offset_requires_decision = bool(site_coincident and contact_geom_radius > float(distance_tolerance_m))

    warnings = [
        "simulation-only TCP/contact geometry audit",
        "EOAT 85 mm contact point remains unverified for hardware",
        "do not write this TCP/contact model to UR or ROS control settings",
    ]
    if offset_requires_decision:
        warnings.append(
            "TCP site is coincident with the colliding sphere center, so the MuJoCo contact surface is offset by the sphere radius"
        )
    if contact_idx is None:
        warnings.append("no matching contact was present at the audited posture")

    return TcpContactModelAudit(
        model_path=str(model_path),
        site_name=site_name,
        contact_geom_name=contact_geom_name,
        parent_body_name=parent_body_name,
        tcp_body_name=tcp_body_name,
        plane_geom_name=plane_geom_name,
        initial_q_rad=q.copy(),
        base_z_offset_m=float(base_z_offset_m),
        config_tcp_guess_m=config_tcp_guess.copy(),
        eoat_note_contact_distance_m=float(eoat_note_contact_distance_m),
        model_tcp_body_offset_m=tcp_body_offset,
        model_site_local_pos_m=site_local,
        model_contact_geom_local_pos_m=geom_local,
        contact_geom_radius_m=contact_geom_radius,
        tcp_guess_matches_model_body_offset=tcp_guess_matches_offset,
        tcp_guess_matches_eoat_note_distance=tcp_guess_matches_note,
        site_coincident_with_contact_geom_center=site_coincident,
        contact_surface_offset_requires_model_decision=offset_requires_decision,
        parent_to_site_distance_m=parent_to_site_distance,
        normal_force_N=positive_contact_normal_force(model, data),
        contact_count=int(data.ncon),
        contact_pair=contact_pair,
        contact_distance_m=contact_distance,
        penetration_m=penetration,
        contact_normal_world=contact_normal,
        site_world_m=site_world,
        contact_geom_center_world_m=geom_center_world,
        contact_midpoint_world_m=contact_midpoint,
        sphere_surface_point_world_m=sphere_surface,
        site_to_contact_midpoint_m=site_to_contact,
        site_to_contact_midpoint_projection_on_normal_m=site_to_contact_projection,
        site_to_sphere_surface_projection_on_normal_m=site_to_surface_projection,
        parent_to_contact_midpoint_distance_m=parent_to_contact_distance,
        parent_to_sphere_surface_distance_m=parent_to_surface_distance,
        parent_to_sphere_surface_projection_along_parent_to_site_m=parent_to_surface_projection,
        surface_extension_beyond_declared_tcp_m=surface_extension,
        warnings=warnings,
    )
