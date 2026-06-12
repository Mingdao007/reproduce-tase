# Phase 1 物理测量步骤

Fresh run：`20260525T213125_phase1_post_manual_reposition`

固定 datum：

```text
OnRobot tool-side sensor flange face
```

要量的距离：

```text
OnRobot tool-side sensor flange face -> mounted stack contact datum
```

## 现在做

1. 保持机器人静止。
   - 不移动。
   - 不按 Play。
   - 不 zero / bias。
   - 不改 TCP、payload、CoG、URCap、OnRobot、RTDE register。

2. 把量具放在 `OnRobot tool-side sensor flange face` 上。
   - 这个面是起点。
   - 不要把光学平台或打印未知曲面当 datum。

3. 量到实际 `contact datum`。
   - 对弹性接触球，终点选 `uncompressed ball top`。
   - 不要按进去量。
   - 不要加预压力。
   - 量具只能轻触球外表面，目标是“刚好接触、不压缩”。
   - notes 写：`uncompressed ball top; no preload`。

4. 判断 `tool_axis_sign`。
   - 如果从 datum 到 contact datum 是沿工具伸出方向，填 `+z`。
   - 如果不确定，先拍照问我，不要猜。

5. 选择一种可稳定读数的方法。
   - 首选：高度尺 / 表架百分表，从光学平台读 `H_face` 和 `H_ball`。
   - 次选：用一片已知厚度的硬平片贴住 flange face，把 datum 转移到可
     伸手的位置。
   - 不推荐：悬空用游标卡尺直接夹两个点。

6. 重复测量三次。
   - 每次重新放置量具。
   - `distance_mm` 只写数字，不写单位。

7. 方法 A：高度差法。
   - 不要把光学平台写成 `datum`。
   - 量 `H_face = optical table top -> OnRobot tool-side sensor flange face`。
   - 量 `H_ball = optical table top -> uncompressed ball top`。
   - 算 `distance_mm = H_face - H_ball`。
   - 三次重复都重新量 `H_face` 和 `H_ball`。
   - notes 写：`derived from optical table height difference; uncompressed ball top; no preload`。

8. 方法 B：平片转移法。
   - 找一片刚性平片，厚度记为 `T_plate`。
   - 让平片贴住 `OnRobot tool-side sensor flange face`。
   - 量平片外侧面到 `uncompressed ball top` 的距离，记为 `D_plate_to_ball`。
   - 算 `distance_mm = T_plate + D_plate_to_ball`。
   - notes 写：`derived from transfer plate; T_plate=<mm>; D_plate_to_ball=<mm>; uncompressed ball top; no preload`。

9. 不要为了这一步拆下来测。
   - 已经装配在 UR10e + OnRobot + EOAT 上，就优先在 mounted 状态测。
   - 如果方法 A/B 都不稳，先拍照告诉我，不要先拆。

10. 把三行 CSV 发给我。

```csv
tcp01,OnRobot tool-side sensor flange face,+z,<实测mm>,digital caliper,0.01,Mingdao,uncompressed ball top; no preload; calibration; photo
tcp02,OnRobot tool-side sensor flange face,+z,<实测mm>,digital caliper,0.01,Mingdao,repeat 2
tcp03,OnRobot tool-side sensor flange face,+z,<实测mm>,digital caliper,0.01,Mingdao,repeat 3
```

如果用高度差法，发这种 notes：

```csv
tcp01,OnRobot tool-side sensor flange face,+z,<H_face-H_ball>,digital caliper,0.01,Mingdao,derived from optical table height difference; H_face=<mm>; H_ball=<mm>; uncompressed ball top; no preload
```

如果用平片转移法，发这种 notes：

```csv
tcp01,OnRobot tool-side sensor flange face,+z,<T_plate+D_plate_to_ball>,digital caliper,0.01,Mingdao,derived from transfer plate; T_plate=<mm>; D_plate_to_ball=<mm>; uncompressed ball top; no preload
```

## 立即停止

- 有接触风险。
- 线缆受力。
- 姿态不稳。
- 量具需要推机器人或压 EOAT。
- 你不确定 contact datum 或 `tool_axis_sign`。
- 你只能通过压缩接触球才能读数。
- `H_face` 小于或等于 `H_ball`。
- 平片放上去会让机器人、EOAT 或球移动。

## 附录：为什么这样选 datum

- `OnRobot tool-side sensor flange face` 是工具栈上的刚性面，离 EOAT /
  adapter 更近，适合做这一步的起始基准。
- 光学平台和打印未知曲面是外部环境对象，不适合作为这个 CSV 的 primary
  `datum`。
- 这一步要的是 mounted stack 内部几何：从工具栈基准面到实际
  `contact datum` 的距离。
- 弹性球如果被压进去，量到的是某个受力状态下的 loaded patch，不是自由
  几何长度。当前 Phase 1 先需要无预载的自由几何，所以用
  `uncompressed ball top`。
- 悬空时直接用卡尺夹两端容易歪、压球或推 EOAT。高度差法把光学平台只当
  transfer reference，最后 CSV 仍然记录工具栈 datum 到接触球的距离。
- 平片转移法的作用是把难碰到的 flange face 转成一个更容易夹的平面。
  如果量的是平片外侧面到球顶，就要把平片厚度加回去。
- 拆下来测会失去 mounted stack 追溯性。拆下测量可以做辅助记录，但不能
  直接替代这个 run 的 mounted measurement。
