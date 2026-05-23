from __future__ import annotations

from pathlib import Path

import mujoco
import numpy as np


def load_model(model_path: str | Path) -> mujoco.MjModel:
    """Load a MuJoCo model from an XML/MJCF path."""
    return mujoco.MjModel.from_xml_path(str(Path(model_path)))


def make_data(model: mujoco.MjModel) -> mujoco.MjData:
    return mujoco.MjData(model)


def set_qpos(model: mujoco.MjModel, data: mujoco.MjData, qpos: np.ndarray) -> None:
    q = np.asarray(qpos, dtype=float)
    if q.shape != (model.nq,):
        raise ValueError(f"qpos shape {q.shape} does not match model.nq={model.nq}")
    data.qpos[:] = q
    data.qvel[:] = 0.0
    mujoco.mj_forward(model, data)


def joint_names(model: mujoco.MjModel) -> list[str]:
    return [
        mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, idx)
        for idx in range(model.njnt)
    ]


def joint_ranges(model: mujoco.MjModel) -> tuple[np.ndarray, np.ndarray]:
    return model.jnt_range[:, 0].copy(), model.jnt_range[:, 1].copy()


def site_position(model: mujoco.MjModel, data: mujoco.MjData, site_name: str) -> np.ndarray:
    site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, site_name)
    if site_id < 0:
        raise ValueError(f"site not found: {site_name}")
    return data.site_xpos[site_id].copy()


def site_jacobian(model: mujoco.MjModel, data: mujoco.MjData, site_name: str) -> tuple[np.ndarray, np.ndarray]:
    site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, site_name)
    if site_id < 0:
        raise ValueError(f"site not found: {site_name}")
    jacp = np.zeros((3, model.nv), dtype=float)
    jacr = np.zeros((3, model.nv), dtype=float)
    mujoco.mj_jacSite(model, data, jacp, jacr, site_id)
    return jacp, jacr


def finite_difference_site_position_jacobian(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    site_name: str,
    qpos: np.ndarray,
    *,
    eps: float = 1e-6,
) -> np.ndarray:
    """Central-difference position Jacobian for hinge-only models."""
    if model.nq != model.nv:
        raise ValueError("finite difference helper assumes nq == nv")

    q0 = np.asarray(qpos, dtype=float).copy()
    jac = np.zeros((3, model.nv), dtype=float)
    for idx in range(model.nv):
        q_plus = q0.copy()
        q_minus = q0.copy()
        q_plus[idx] += eps
        q_minus[idx] -= eps
        set_qpos(model, data, q_plus)
        p_plus = site_position(model, data, site_name)
        set_qpos(model, data, q_minus)
        p_minus = site_position(model, data, site_name)
        jac[:, idx] = (p_plus - p_minus) / (2.0 * eps)
    set_qpos(model, data, q0)
    return jac

