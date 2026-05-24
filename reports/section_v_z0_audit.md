# Section V z0 Audit

Date: 2026-05-24

Branch: `exp/tase-ur10e-v40-section-v-z0-audit`

## Scope

This audit closes the last `pending_pdf_verify` item in
`configs/paper_truth.yaml`: the source of `z0` in the paper's Section V
simulation trajectory.

The question is narrow: does Section V define `z0`, or should the repo record
that the Section V simulation text uses `z0` without defining it?

## Commands

```bash
pdftotext -layout "<paper-pdf>" /tmp/tase_paper_v40_layout.txt
rg -n -C 8 "z0|z_0|0\\.2 cos|0\\.2cos|cos\\(0\\.2|SIMULATION|V\\." /tmp/tase_paper_v40_layout.txt

pdftotext -raw "<paper-pdf>" /tmp/tase_paper_v40_raw.txt
rg -n -C 8 "z0|z_0|0\\.2 cos|0\\.2cos|cos\\(0\\.2|SIMULATION|V\\." /tmp/tase_paper_v40_raw.txt

pdfinfo "<paper-pdf>"
```

## Evidence

Layout extraction shows Section V at lines 457-462:

```text
V. SIMULATION VERIFICATION
... desired trajectory
and orientation is xpd = [0.2 cos(0.2t); 0.2 sin(0.2t); z0 ], and
u = [cos(0.1t), sin(0.1t)].
```

Raw extraction shows the same content at lines 731-736:

```text
V. SIMULATION VERIFICATION
... desired trajectory
and orientation is xpd = [0.2 cos(0.2t); 0.2 sin(0.2t); z0], and
u = [cos(0.1t), sin(0.1t)].
```

The same searches find Section VI defining `z0` for the experimental section,
not Section V:

```text
Considering the influence of the primary force control on the mechanical
manipulator's position along the z-axis, we denote the anticipated position
along this axis in the desired trajectory as the initial position of the
mechanical manipulator, z0.
```

Layout extraction places that Section VI definition at lines 487-495; raw
extraction places it at lines 790-798.

## Decision

Section V `z0` is now recorded as PDF-verified undefined in the Section V
simulation text. This is not a hidden extraction gap.

The repo must not silently transfer the Section VI experimental definition
into Section V simulation truth. If future code needs a Section V simulation
`z0`, it must choose an explicit adapted convention and label it as such.

## Config Update

`configs/paper_truth.yaml` now sets:

```yaml
v1:
  allow_pending_pdf_verify: false
paper:
  section_v:
    pending_pdf_verify: []
    trajectory:
      z: "z0"
    z0_source_status: "verified_undefined_in_section_v_text"
```

## Remaining Paper Ambiguities

The Section V orientation signal remains a verified paper ambiguity because
the paper gives a 2D signal, while Section III defines a 3D force-normal
orientation input. That is no longer a pending PDF extraction field.
