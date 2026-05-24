# Three-Phase Setup Settle Probe Summary

Run root: `runs/staged_orientation_three_phase_settle/20260524T110039`

- Cases: `10`
- Setup terminal-state passes: `0 / 10`
- Trajectory feasibility passes: `8 / 10`
- Legacy trajectory-after-approach passes: `8 / 10`
- Planned setup-then-trajectory passes: `0 / 10`
- Full staged-feasibility passes: `0 / 10`

| case | setup pass | setup failed | setup orient | setup xy m | settle force N | traj pass | traj orient | planned pass |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| `baseline_no_recenter` | `False` | `final_tangential_position_error_m` | `0.0020290714973557108` | `0.008347977658392892` | `None` | `True` | `0.0203545748607252` | `False` |
| `lp4_no_settle` | `False` | `final_orientation_error_rad` | `0.06144921366675186` | `0.001202027969075075` | `None` | `False` | `0.08828833304324712` | `False` |
| `lp1_settle_w0p5` | `False` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.011139549031039307` | `0.007193845624799021` | `0.8225791490908131` | `True` | `0.02939550767657929` | `False` |
| `lp1_settle_w1` | `False` | `final_tangential_position_error_m` | `0.005558417503337856` | `0.007869579772205084` | `0.1393121211793803` | `True` | `0.02403096466832988` | `False` |
| `lp1_settle_w2` | `False` | `final_tangential_position_error_m` | `0.0025125657280091578` | `0.00828135120454356` | `0.003310079622609865` | `True` | `0.020860331353265302` | `False` |
| `lp2_settle_w1` | `False` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.008147569423222185` | `0.007543673110517419` | `0.4460386510159919` | `True` | `0.02659356165501424` | `False` |
| `lp2_settle_w2` | `False` | `final_tangential_position_error_m` | `0.002914947767721797` | `0.008224360494180138` | `0.010563335509174326` | `True` | `0.021294571846744433` | `False` |
| `lp4_settle_w1` | `False` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.010909888730768584` | `0.00721962222129202` | `0.9675117552611987` | `True` | `0.02918723865860162` | `False` |
| `lp4_settle_w2` | `False` | `final_tangential_position_error_m` | `0.0033403693502681454` | `0.008165765238665546` | `0.026269070988793494` | `True` | `0.02174260279275125` | `False` |
| `lp4_settle_lp4` | `False` | `final_orientation_error_rad` | `0.07228244179626259` | `0.00017396214319096055` | `0.0019523730245144177` | `False` | `0.10197948276546515` | `False` |
