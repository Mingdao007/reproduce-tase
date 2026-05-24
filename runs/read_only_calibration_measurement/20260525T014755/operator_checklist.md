# Operator Checklist

Run status: `template_not_executed`

## Static Bench State

- [ ] Robot is not touching the environment.
- [ ] No force-control program is running.
- [ ] No one will press Play, Freedrive, Zero, TCP setup, or payload setup.
- [ ] EOAT and KSM-8N can be inspected without moving the robot.
- [ ] Cables have slack and are not under strain.
- [ ] Emergency stop path is known.

## Approval

- [ ] User approved the exact read-only step.
- [ ] The approved step does not include motion, writes, zeroing, or force
      control.

## Evidence Collection

- [ ] Mounted-stack TCP/contact worksheet completed or marked not executable.
- [ ] KSM contact patch convention worksheet completed or marked not
      executable in `ksm_contact_patch_convention.csv`.
- [ ] Plane-normal worksheet completed or marked not executable.
- [ ] Force-source worksheet completed or marked not executable.
- [ ] Orientation-gate worksheet completed in
      `orientation_gate_semantics.csv`, and decision completed or marked not
      accepted in `orientation_gate_decision.md`.
- [ ] Photos and external files listed in `photos_manifest.md`.
