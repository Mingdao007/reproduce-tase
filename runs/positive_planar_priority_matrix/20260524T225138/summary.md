# Positive Planar-Priority Matrix Summary

Run root: `/home/andy/reproduce-tase/runs/positive_planar_priority_matrix/20260524T225138`

- Scenario count: `2`
- Total case count: `16`
- Total stitched pass count: `16 / 16`
- All scenarios pass all cases: `True`
- Passing scenarios: `planar_normal30_kp0p001, planar_normal30_kp0p002`

## Scenario Aggregates

| scenario | stitched pass | max pass delta mm | Stage A all pass | max orientation | max qdot sat | max tail qdot | max force err |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| `planar_normal30_kp0p001` | `8/8` | `1.0` | `True` | `0.11973133163816624` | `0.001` | `0.0010837631758864566` | `0.1223546677432889` |
| `planar_normal30_kp0p002` | `8/8` | `1.0` | `True` | `0.11961552028823065` | `0.001` | `0.0009960728846485063` | `0.1902561439715911` |

## Case Matrix

### `planar_normal30_kp0p001`

| delta mm | stitched | Stage B pass | max orientation | max qdot sat | max tail qdot | max force err | failed rows |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `0.05` | `True` | `4/4` | `0.08412748751352093` | `0.001` | `0.0010223919876026157` | `0.04207915062507256` | `none` |
| `0.1` | `True` | `4/4` | `0.08596210811967063` | `0.001` | `0.0010299934112193829` | `0.044296372376843605` | `none` |
| `0.15` | `True` | `4/4` | `0.08780371166094508` | `0.001` | `0.0010374407001096633` | `0.04666814024306122` | `none` |
| `0.2` | `True` | `4/4` | `0.0896520136255618` | `0.001` | `0.0010446802839200612` | `0.04920581056799254` | `none` |
| `0.25` | `True` | `4/4` | `0.09150667512837204` | `0.001` | `0.0010516453971833848` | `0.05192121718053611` | `none` |
| `0.5` | `True` | `4/4` | `0.10086123577833858` | `0.001` | `0.0010792061086426195` | `0.06861180342809926` | `none` |
| `0.75` | `True` | `4/4` | `0.110301295362831` | `0.001` | `0.0010837631758864566` | `0.09167439127198303` | `none` |
| `1.0` | `True` | `4/4` | `0.11973133163816624` | `0.001` | `0.0010367427075651814` | `0.1223546677432889` | `none` |

### `planar_normal30_kp0p002`

| delta mm | stitched | Stage B pass | max orientation | max qdot sat | max tail qdot | max force err | failed rows |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `0.05` | `True` | `4/4` | `0.08409199042866077` | `0.001` | `0.0009837332444987208` | `0.0658051040988823` | `none` |
| `0.1` | `True` | `4/4` | `0.08592425000269677` | `0.001` | `0.0009877852910090401` | `0.06953852895642919` | `none` |
| `0.15` | `True` | `4/4` | `0.08776333251291144` | `0.001` | `0.000991268545916313` | `0.07351555182402864` | `none` |
| `0.2` | `True` | `4/4` | `0.08960894307851132` | `0.001` | `0.0009940725140121052` | `0.07775059752571094` | `none` |
| `0.25` | `True` | `4/4` | `0.0914607343920079` | `0.001` | `0.0009960728846485063` | `0.08225749906102553` | `none` |
| `0.5` | `True` | `4/4` | `0.10079789673218484` | `0.001` | `0.0009884906887160018` | `0.10937518068803388` | `none` |
| `0.75` | `True` | `4/4` | `0.1102147893358667` | `0.001` | `0.0009343671617656555` | `0.14519444906619758` | `none` |
| `1.0` | `True` | `4/4` | `0.11961552028823065` | `0.001` | `0.0007980873518407317` | `0.1902561439715911` | `none` |

Interpretation:

- The v79 planar-primary priority recovery is tested here across the full positive-delta matrix rather than only the `+1.0 mm` row.
- The claim remains tied to a run-local `0.11995 rad` orientation gate and the diagnostic staged setup.
- This is not strict paper-equivalent, robustness, contact calibration, or hardware evidence.
