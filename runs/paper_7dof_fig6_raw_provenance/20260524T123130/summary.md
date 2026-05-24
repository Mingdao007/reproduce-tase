# Paper 7DOF Fig.6 Raw Provenance Comparison

Run id: `20260524T123130`

Scope: compare the current Python Fig.6 candidate against ignored local legacy MATLAB/RNN raw Fig.6 arrays.
Raw `.mat` and `.npz` arrays remain outside ordinary Git; this run records derived lightweight metrics only.

Summary:

```yaml
python_fk_matches_sampled_legacy_raw: true
legacy_formula_force_loop_mode: paper_literal
legacy_figure_force_loop_mode: admittance_proxy
python_force_loop_mode: paper_literal
legacy_figure_q7_at_22_s_rad: 2.4999999999358065
python_q7_at_22_s_rad: 1.6680622878116045
formula_q7_at_22_s_rad: 1.1241793710124022
python_abs_delta_to_figure_q7_at_22_s_rad: 0.831937712124202
python_abs_delta_to_formula_q7_at_22_s_rad: 0.5438829167992023
legacy_figure_q7_exact_upper_limit_count: 17829
legacy_figure_q7_first_near_upper_limit_time_s: 11.872999999998859
legacy_figure_acceptance_mode: landmark
```

Run metadata:

| Run | Solver | Orientation | Force loop | Acceptance | q7@22 rad | q7 limit samples | qdot limit hits |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `legacy_formula_faithful` | `kkt_projection` | `force_shortest_arc` | `paper_literal` | `diagnostic` | `1.1241793710124022` | `0` | `0` |
| `legacy_figure_match` | `pinv_bounded` | `normal_only` | `admittance_proxy` | `landmark` | `2.4999999999358065` | `17829` | `148` |
| `python_v47_uncapped_kkt` | `kkt_projection` | `force_shortest_arc` | `paper_literal` | `candidate` | `1.6680622878116045` | `0` | `0` |

Joint-trajectory comparisons:

| Reference | Candidate | q7 delta @22 rad | q7 RMSE rad | joint RMSE rad |
| --- | --- | ---: | ---: | ---: |
| `legacy_formula_faithful` | `python_v47_uncapped_kkt` | `0.5438829167992287` | `0.5680000838185039` | `0.23473749435738336` |
| `legacy_figure_match` | `python_v47_uncapped_kkt` | `-0.8319377121241756` | `0.7395891219830576` | `0.6121241447298901` |
| `legacy_formula_faithful` | `legacy_figure_match` | `1.3758206289234043` | `1.2905082815516138` | `0.6776166090314514` |

Kinematics source checks:

| Legacy run | max position error m | max quaternion delta norm | max condJ error |
| --- | ---: | ---: | ---: |
| `legacy_formula_faithful` | `0.0` | `1.1274399064233892e-16` | `8.881784197001252e-15` |
| `legacy_figure_match` | `1.1102230246251565e-16` | `1.1485179310268942e-16` | `6.217248937900877e-15` |

Interpretation:

- Python Panda FK and Jacobian conditioning match the sampled legacy raw states to numerical precision.
- The legacy figure-match q7 landmark comes from a documented landmark/tuning line using `pinv_bounded`, `normal_only`, and `admittance_proxy`, not the formula-faithful `paper_literal` line.
- The figure-match q7 trajectory is upper-limit pinned for most of the run; this is a provenance difference to audit before changing the strict parity candidate.
