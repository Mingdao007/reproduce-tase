# Positive Base-Z Start Contact Report

## Summary

v68 follows up the v67 bracket by checking whether the positive base-z
start-contact failures were true contact-model gaps or local optimizer
artifacts. The audit uses deterministic single-joint and paired-joint seed
sweeps plus random seeds for the Stage A start contact, while retaining the
compact terminal gate probe for the same positive deltas.

The formal run is:

- `runs/positive_base_z_start_contact/20260524T170350`
- command: `scripts/audit_positive_base_z_start_contact.py`
- parent commit before v68 changes: `df2790d834c4cb2b4fabc8c549444b28304a9d26`

The start-contact search passes all `8 / 8` positive deltas from `+0.05 mm`
through `+1.0 mm`. The terminal diagnostic gate still passes `0 / 8`; every
positive-delta terminal row fails the orientation gate.

## Metrics

From `runs/positive_base_z_start_contact/20260524T170350/metrics.yaml`:

- start pass count: `8 / 8`
- terminal pass count: `0 / 8`
- max start-pass delta: `+1.0 mm`
- max terminal-pass delta: `none`

| delta mm | start pass | start seed | start force err N | start x/y err m | terminal orientation rad |
| ---: | --- | --- | ---: | ---: | ---: |
| `+0.05` | `true` | `joint3_+0.003000__joint5_-0.009000` | `0.0043113621525501244` | `3.0003869991209083e-05` | `0.0838175590896232` |
| `+0.10` | `true` | `joint3_+0.004500__joint5_-0.012000` | `0.020717782163206522` | `0.00026250563903843817` | `0.08565245135290023` |
| `+0.15` | `true` | `joint3_+0.006000__joint5_-0.015000` | `0.0024986436865441775` | `0.0004950068174480885` | `0.0874945141256073` |
| `+0.20` | `true` | `joint3_+0.009000__joint5_-0.023500` | `0.04426348783838385` | `0.0005975372244772861` | `0.08934348318237911` |
| `+0.25` | `true` | `joint1_+0.022000__joint2_-0.028500` | `0.02572023701773496` | `0.000814917190296382` | `0.09119904265401833` |
| `+0.50` | `true` | `joint1_+0.027000__joint2_-0.033000` | `0.07328844161217152` | `0.00031519335583544885` | `0.10056247728510045` |
| `+0.75` | `true` | `joint1_+0.033500__joint2_-0.039500` | `0.07998720741366228` | `0.0013526627224379568` | `0.11002164736335575` |
| `+1.00` | `true` | `joint1_+0.033500__joint2_-0.037000` | `0.14209391841232932` | `0.0030145867556624815` | `0.11948560786548146` |

## Claim Boundary

This is diagnostic-label simulation evidence only. It is not:

- strict paper-equivalent feasibility
- terminal target recovery
- path or stitched trajectory recovery
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

The useful claim is narrow: under a broader start-contact seed search, positive
base-z perturbations through `+1.0 mm` can recover a 5 N target-pair start
contact within the diagnostic x/y gate. This corrects the v67 interpretation
that positive deltas necessarily lose start feasibility. The audited blocker
for the positive side is now the terminal diagnostic orientation gate.

## Next Step

Focus the next branch on positive-side terminal target orientation: determine
whether the `0.08 rad` diagnostic terminal gate, desired force-normal
orientation convention, or contact-point model is the actual limiting factor.
Do not spend the next iteration only on start-contact recovery.
