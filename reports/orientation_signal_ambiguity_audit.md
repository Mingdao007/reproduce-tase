# Orientation Signal Ambiguity Audit

Date: 2026-05-24

Branch: `exp/tase-ur10e-v20-orientation-signal-audit`

Starting commit: `6ef9a6cfa5bf626adba0d8bceaacc029b5904318`

## Scope

Determine whether the Section V orientation signal can be resolved from the
paper PDF before implementing a paper-faithful desired-orientation generator.

This audit only inspects the local paper PDF and derived text/XML extraction
artifacts. It does not run or modify real robot hardware.

## Commands

```bash
pdftotext -layout "<paper-pdf>" /tmp/tase_paper_layout.txt
pdftotext -raw "<paper-pdf>" /tmp/tase_paper_raw.txt
pdftotext -fixed 3 "<paper-pdf>" /tmp/tase_paper_fixed3.txt
pdftohtml -xml -f 3 -l 4 -stdout "<paper-pdf>" > /tmp/tase_paper_p3_4.xml
pdftohtml -xml -f 5 -l 8 -stdout "<paper-pdf>" > /tmp/tase_paper_p5_8.xml
pdftotext -bbox-layout -f 3 -l 5 "<paper-pdf>" /tmp/tase_paper_p3_5_bbox.html
rg -n "u =|cos\\(0\\.1t|sin\\(0\\.1t|Rd =|sin\\(u\\)|F/kFk" /tmp/tase_paper_*.txt /tmp/tase_paper_*.xml /tmp/tase_paper_*.html
```

## Evidence

`pdftotext -layout` shows the Section III orientation variable as a
three-component vector from force feedback:

```text
u = F/||F||, u = [u1, u2, u3]^T
```

It also shows Eq. (9) as the skew matrix using `u1`, `u2`, and `u3`, and Eq.
(10) as:

```text
Rd = I + sin(u)S + (1 - cos(u))S^2
```

Evidence: `/tmp/tase_paper_layout.txt:250-271`.

The XML extraction preserves the same structure. In
`/tmp/tase_paper_p3_4.xml`, the components appear as separate tokens `u`,
subscript `1`, `u`, subscript `2`, and `u`, subscript `3`; Eq. (10) uses the
single symbol `u` inside `sin(...)` and `cos(...)`.

The Section V simulation line is consistent across extraction modes. Layout,
raw text, fixed-width text, and XML all give exactly:

```text
u = [cos(0.1t), sin(0.1t)]
```

Evidence:

- `/tmp/tase_paper_layout.txt:457-463`
- `/tmp/tase_paper_raw.txt:735-736`
- `/tmp/tase_paper_fixed3.txt:523-524`
- `/tmp/tase_paper_p5_8.xml:1346-1356`

The XML token stream around the Section V line closes the bracket immediately
after the `sin(0.1t)` term, then continues with the boundary-constraints
sentence. There is no hidden third component in the text layer.

## Finding

The ambiguity is real in the PDF text layer, not just a `pdftotext -layout`
artifact:

- Section III defines `u` as a 3D normalized force vector.
- Eq. (9) requires all three components of `u`.
- Eq. (10) applies scalar trigonometric notation to that same symbol.
- Section V gives only a 2D time-varying signal for `u`.

No extraction mode inspected in this audit provides evidence for a third
component, a scalar angle, or a convention that maps the two Section V entries
onto the Section III force-normal law.

## Resolution For This Repo

Treat `orientation_signal_dimension_resolution` as verified ambiguous rather
than pending PDF verification.

The reproduction code must not infer a hidden third component for Section V or
call such an inference paper truth. A future paper-faithful orientation module
may implement the Section III force-normal law, `u = F / ||F||`, if it is
driven by a measured or simulated 3D force/contact-normal vector. Any
time-varying 2D orientation schedule derived from the Section V line must be
labeled an adapted assumption.

## Remaining Paper-Truth Gap

V40 closes the former Section V `z0_source` pending-verification field. The PDF
evidence shows that `z0` is explicitly defined in Section VI for experiments
as the initial manipulator z position, while Section V simulation text uses
`z0` without defining it. This is now recorded as a verified Section V paper
ambiguity, not a pending extraction field.

## Next Step

Implement paper-orientation work from the 3D Section III force-normal contract,
not from the 2D Section V signal. If future code needs a Section V simulation
`z0`, choose and document an adapted convention rather than silently importing
the Section VI experimental definition.
