# Positive Full Stitched Recovery Summary

Run root: `/home/andy/reproduce-tase/runs/positive_full_stitched_recovery/20260524T195501`

- Case count: `8`
- Stitched pass count: `8`
- Max positive stitched-pass delta mm: `1.0`
- Max Stage B qdot saturation fraction: `0.001`
- Max Stage B tail qdot utilization: `0.4474846584870986`
- Max Stage B orientation error rad: `0.11997895388586574`

| delta mm | stitched | Stage B pass | Stage A max qdot | Stage B qdot sat | Stage B tail qdot | Stage B max orientation rad | failed rows |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `0.05` | `True` | `4/4` | `0.11809294100915854` | `0.0` | `0.0013968063462996355` | `0.08420730609192884` | `none` |
| `0.1` | `True` | `4/4` | `0.11816011213646939` | `0.0` | `0.0014136105192300453` | `0.08604620949512072` | `none` |
| `0.15` | `True` | `4/4` | `0.11819953468738618` | `0.0` | `0.0014309327437399904` | `0.0878924064819036` | `none` |
| `0.2` | `True` | `4/4` | `0.1199690367457867` | `0.0` | `0.0014487950612593519` | `0.08974563803371456` | `none` |
| `0.25` | `True` | `4/4` | `0.09977607944751221` | `0.0` | `0.0014677410234789766` | `0.0916056636457473` | `none` |
| `0.5` | `True` | `4/4` | `0.09335801735430703` | `0.0` | `0.0015689200443263227` | `0.10099329829600373` | `none` |
| `0.75` | `True` | `4/4` | `0.08623070567481625` | `0.0` | `0.4474846584870986` | `0.11048096113317912` | `none` |
| `1.0` | `True` | `4/4` | `0.08332618384112458` | `0.001` | `0.0018234783869710625` | `0.11997895388586574` | `none` |

Interpretation:

- The v70 relaxed terminal/path setup plus `paper_time_scale = 0.005` recovers the full positive E1-E4 stitched diagnostic matrix for all tested positive deltas.
- This is still diagnostic-label simulation evidence using a run-local `0.12 rad` orientation gate, not strict paper-equivalent, robust, calibrated, or hardware-ready evidence.
