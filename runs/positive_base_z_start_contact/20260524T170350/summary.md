# Positive Base-Z Start Contact Summary

Run root: `/home/andy/reproduce-tase/runs/positive_base_z_start_contact/20260524T170350`

- Case count: `8`
- Start pass count: `8`
- Terminal pass count: `0`
- Contact-without-start-pass count: `0`
- Max start-pass delta mm: `1.0`
- Max terminal-pass delta mm: `None`

| delta mm | start pass | start best seed | start force err N | start x/y err m | terminal pass | terminal orientation rad |
| ---: | --- | --- | ---: | ---: | --- | ---: |
| `0.05` | `True` | `joint3_+0.003000__joint5_-0.009000` | `0.0043113621525501244` | `3.0003869991209083e-05` | `False` | `0.0838175590896232` |
| `0.1` | `True` | `joint3_+0.004500__joint5_-0.012000` | `0.020717782163206522` | `0.00026250563903843817` | `False` | `0.08565245135290023` |
| `0.15` | `True` | `joint3_+0.006000__joint5_-0.015000` | `0.0024986436865441775` | `0.0004950068174480885` | `False` | `0.0874945141256073` |
| `0.2` | `True` | `joint3_+0.009000__joint5_-0.023500` | `0.04426348783838385` | `0.0005975372244772861` | `False` | `0.08934348318237911` |
| `0.25` | `True` | `joint1_+0.022000__joint2_-0.028500` | `0.02572023701773496` | `0.000814917190296382` | `False` | `0.09119904265401833` |
| `0.5` | `True` | `joint1_+0.027000__joint2_-0.033000` | `0.07328844161217152` | `0.00031519335583544885` | `False` | `0.10056247728510045` |
| `0.75` | `True` | `joint1_+0.033500__joint2_-0.039500` | `0.07998720741366228` | `0.0013526627224379568` | `False` | `0.11002164736335575` |
| `1.0` | `True` | `joint1_+0.033500__joint2_-0.037000` | `0.14209391841232932` | `0.0030145867556624815` | `False` | `0.11948560786548146` |

Interpretation:

- Positive-side start contact is recoverable for the listed passing deltas under this broad seed search.
- Terminal orientation remains a separate gate; this audit is not path recovery or robustness evidence.
