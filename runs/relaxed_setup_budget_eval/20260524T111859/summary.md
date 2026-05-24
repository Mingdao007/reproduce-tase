# Relaxed Setup Budget Evaluation Summary

Run root: `/home/andy/reproduce-tase/runs/relaxed_setup_budget_eval/20260524T111859`

## Result

- Source run root: `/home/andy/reproduce-tase/runs/staged_orientation_e1e4_posture_regularized/20260524T102747`
- Cases: `4`
- Relaxed setup passes: `4`
- Trajectory feasibility passes: `4`
- UR10e adapted trajectory-after-relaxed-setup passes: `4`
- Strict full staged feasibility passes: `0`

| trajectory | relaxed setup | trajectory | adapted label | setup drift m | setup qdot sat |
|---|---:|---:|---:|---:|---:|
| `e1-cycloid` | `True` | `True` | `True` | `0.008347977658392892` | `1.0` |
| `e2-figure-eight` | `True` | `True` | `True` | `0.008347977658392892` | `1.0` |
| `e3-circle` | `True` | `True` | `True` | `0.008347977658392892` | `1.0` |
| `e4-cardioid` | `True` | `True` | `True` | `0.008347977658392892` | `1.0` |

## Limits

This is an acceptance-label evaluation. It does not convert the run into
paper-equivalent full staged feasibility, and it is not hardware-ready.
