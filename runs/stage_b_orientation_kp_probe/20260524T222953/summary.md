# Stage B Orientation Kp Probe Summary

Run root: `/home/andy/reproduce-tase/runs/stage_b_orientation_kp_probe/20260524T222953`

- Case count: `30`
- Stitched pass count: `0 / 30`
- Stage A passed every case: `True`
- E2 orientation gate: `0.11995`
- Orientation-ok cases: `13 / 30`
- Min E2 orientation error: `0.11990689588867036`
- Min E2 qdot saturation fraction: `0.0`
- Min E2 tail qdot utilization: `0.000874717789387994`

Best orientation-error case:

- qdot limit: `0.2`
- orientation_kp: `0.01`
- E2 orientation error: `0.11990689588867036`
- E2 failed criteria: `qdot_saturation_fraction,tail_max_qdot_utilization`

Best qdot-saturation case:

- qdot limit: `0.2`
- orientation_kp: `0.0`
- E2 orientation error: `0.11997883364101876`
- E2 qdot saturation fraction: `0.0`
- E2 failed criteria: `max_orientation_error_rad`

| qdot limit | orientation_kp | stitched | E2 pass | E2 orientation | E2 qdot sat | E2 tail qdot | E2 angular slack | E2 failed criteria |
| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| `0.15` | `0.0` | `False` | `False` | `0.1199788204275829` | `0.006` | `0.0014580486861575888` | `0.0005538797209998642` | `max_orientation_error_rad` |
| `0.15` | `0.001` | `False` | `False` | `0.11997874469916661` | `0.001` | `0.8855464939834751` | `0.0006090385228046052` | `max_orientation_error_rad` |
| `0.15` | `0.002` | `False` | `False` | `0.11997873892631489` | `0.006` | `1.0` | `0.0008132405161230988` | `tail_max_qdot_utilization,max_orientation_error_rad` |
| `0.15` | `0.003` | `False` | `False` | `0.11994467909936898` | `1.0` | `1.0` | `0.0008524399653657364` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.15` | `0.005` | `False` | `False` | `0.11994466394324031` | `1.0` | `1.0` | `0.0011556982448482035` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.15` | `0.01` | `False` | `False` | `0.11994484651640967` | `1.0` | `1.0` | `0.0018556489852891182` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.16` | `0.0` | `False` | `False` | `0.11997890051688354` | `0.005` | `0.0013705812328760553` | `0.0005576925458282285` | `max_orientation_error_rad` |
| `0.16` | `0.001` | `False` | `False` | `0.11997879530524458` | `0.001` | `0.0013688991173871493` | `0.0006090385228046052` | `max_orientation_error_rad` |
| `0.16` | `0.002` | `False` | `False` | `0.11997790932201319` | `0.031` | `1.0` | `0.0010392832140945344` | `qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` |
| `0.16` | `0.003` | `False` | `False` | `0.11997858121233616` | `0.01` | `0.0013696552837040988` | `0.0009668149236417671` | `max_orientation_error_rad` |
| `0.16` | `0.005` | `False` | `False` | `0.1199434647427369` | `0.724` | `1.0` | `0.0012364308944162368` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.16` | `0.01` | `False` | `False` | `0.11993904379267531` | `1.0` | `1.0` | `0.0019487329905990842` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.18` | `0.0` | `False` | `False` | `0.11997883369080364` | `0.001` | `0.0012164315394331549` | `0.0005749747962071729` | `max_orientation_error_rad` |
| `0.18` | `0.001` | `False` | `False` | `0.11997873184090838` | `0.003` | `0.0012163449638093547` | `0.0007110425658224881` | `max_orientation_error_rad` |
| `0.18` | `0.002` | `False` | `False` | `0.11997869112252067` | `0.004` | `1.0` | `0.0008596551103035617` | `tail_max_qdot_utilization,max_orientation_error_rad` |
| `0.18` | `0.003` | `False` | `False` | `0.11997869558475543` | `0.006` | `0.0012172591882030515` | `0.0009999196258722346` | `max_orientation_error_rad` |
| `0.18` | `0.005` | `False` | `False` | `0.11992440351683623` | `0.998` | `1.0` | `0.0011733614273446952` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.18` | `0.01` | `False` | `False` | `0.11992494527423396` | `1.0` | `1.0` | `0.0016415848897642967` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.2` | `0.0` | `False` | `False` | `0.11997883364101876` | `0.0` | `0.0010947845693568656` | `0.0005749927146877785` | `max_orientation_error_rad` |
| `0.2` | `0.001` | `False` | `False` | `0.11997855049509872` | `0.004` | `0.6695910941469454` | `0.0008500542508541753` | `max_orientation_error_rad` |
| `0.2` | `0.002` | `False` | `False` | `0.1199783758450804` | `0.014` | `1.0` | `0.0010359317709081176` | `qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` |
| `0.2` | `0.003` | `False` | `False` | `0.11990910433598108` | `0.919` | `1.0` | `0.0014945801428582711` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.2` | `0.005` | `False` | `False` | `0.11990763721579334` | `0.989` | `1.0` | `0.0015128056025265082` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.2` | `0.01` | `False` | `False` | `0.11990689588867036` | `0.999` | `1.0` | `0.0018655707508281696` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.25` | `0.0` | `False` | `False` | `0.11997883364101876` | `0.0` | `0.0008758276554854925` | `0.0005749927146877785` | `max_orientation_error_rad` |
| `0.25` | `0.001` | `False` | `False` | `0.11997875722613961` | `0.0` | `0.000874717789387994` | `0.0007132664474624206` | `max_orientation_error_rad` |
| `0.25` | `0.002` | `False` | `False` | `0.11997766024743767` | `0.014` | `1.0` | `0.0012613589075613676` | `qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` |
| `0.25` | `0.003` | `False` | `False` | `0.11992270620345662` | `0.477` | `1.0` | `0.0019041558078731935` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.25` | `0.005` | `False` | `False` | `0.11993417814818061` | `0.986` | `1.0` | `0.001737410325037156` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.25` | `0.01` | `False` | `False` | `0.11993465286899524` | `0.997` | `1.0` | `0.002332408246736749` | `qdot_saturation_fraction,tail_max_qdot_utilization` |

Interpretation:

- Low orientation feedback gains preserve the qdot budget but still miss the tightened E2 orientation gate.
- Gains that reduce E2 orientation below the gate consume the qdot budget and fail qdot saturation and/or tail qdot utilization.
- This probe does not change the canonical controller configuration or remove the v77 tightened-orientation boundary.
