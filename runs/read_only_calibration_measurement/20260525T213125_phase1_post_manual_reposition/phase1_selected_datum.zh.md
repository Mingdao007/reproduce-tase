# Phase 1 已选择的测量基准

当前 fresh run：

```text
20260525T213125_phase1_post_manual_reposition
```

已选择的 `datum`：

```text
OnRobot tool-side sensor flange face
```

含义：OnRobot HEX-E sensor 靠 EOAT / adapter 的那一侧 flange face。
它是本次 `tcp_contact_measurements.csv` 的起始基准面。

下一步需要测量：

```text
OnRobot tool-side sensor flange face -> mounted stack contact datum
```

仍需现场确认的字段：

- `tool_axis_sign`：通常会是 `+z`，但以现场工具坐标方向为准。
- `distance_mm`：从该 flange face 到实际 contact datum 的物理距离。
- `instrument`：例如 `digital caliper` 或 `height gauge`。
- `resolution_mm`：例如 `0.01`。
- `notes`：写明 contact datum 是 ball top、receiver face、local patch，
  或其他你实际采用的定义；同时写校准状态和照片状态。

请重复测量三次，每次重新放置量具。
