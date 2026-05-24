# Positive Full Stitched Recovery Summary

Run root: `/home/andy/reproduce-tase/runs/positive_full_stitched_recovery/20260524T192854`

- Case count: `8`
- Stitched pass count: `8`
- Max positive stitched-pass delta mm: `1.0`
- Max Stage B qdot saturation fraction: `0.006`
- Max Stage B tail qdot utilization: `0.3579877267896789`
- Max Stage B orientation error rad: `0.1199788204275829`

| delta mm | stitched | Stage B pass | Stage A max qdot | Stage B qdot sat | Stage B tail qdot | Stage B max orientation rad | failed rows |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `0.05` | `True` | `4/4` | `0.1419870794067211` | `0.0` | `0.0011174450770397085` | `0.08420730609192884` | `none` |
| `0.1` | `True` | `4/4` | `0.14206784149212412` | `0.0` | `0.0011308884153840362` | `0.08604620949512072` | `none` |
| `0.15` | `True` | `4/4` | `0.1421152405391769` | `0.0` | `0.0011447461949919925` | `0.0878924064819036` | `none` |
| `0.2` | `True` | `4/4` | `0.14424277184739456` | `0.0` | `0.0011590360490074817` | `0.08974563803371456` | `none` |
| `0.25` | `True` | `4/4` | `0.11996410618909473` | `0.0` | `0.0011741928187831813` | `0.0916056636457473` | `none` |
| `0.5` | `True` | `4/4` | `0.11224745619902818` | `0.0` | `0.0012551360354610581` | `0.10099329829600373` | `none` |
| `0.75` | `True` | `4/4` | `0.10367805178971796` | `0.0` | `0.3579877267896789` | `0.11048096113317912` | `none` |
| `1.0` | `True` | `4/4` | `0.10018584837167505` | `0.006` | `0.0014580486861575888` | `0.1199788204275829` | `none` |

Interpretation:

- The v70 relaxed terminal/path setup plus `paper_time_scale = 0.005` recovers the full positive E1-E4 stitched diagnostic matrix for all tested positive deltas.
- This is still diagnostic-label simulation evidence using a run-local `0.12 rad` orientation gate, not strict paper-equivalent, robust, calibrated, or hardware-ready evidence.
