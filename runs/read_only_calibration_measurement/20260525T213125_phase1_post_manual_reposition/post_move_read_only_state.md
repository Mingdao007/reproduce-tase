# 手动移动后的只读状态

记录时间：`2026-05-25T21:32:06+08:00`

操作者说明：之后给出指令时，默认满足下面这个 fresh read-only run
确认条件：

```text
Moved and stable; no contact; no program running; ready for a fresh read-only run.
```

在这个 run 中，Codex 只把这句话当作“允许进行只读验证”的确认。
它不授权机器人运动、force control、zeroing/biasing、TCP/payload/CoG
写入、URCap 写入、OnRobot 写入或 RTDE register 写入。

## Run 边界

- Fresh run：`20260525T213125_phase1_post_manual_reposition`
- 上一个 run 在创建后发生过手动移动，因此保持 unfinalized。
- 这个 run 仍然需要物理测量行写入 `tcp_contact_measurements.csv` 后，
  才能 finalize。

## 网络和接口

- Robot host：`192.168.1.18`
- Ubuntu 直连网卡：`enp3s0`
- Ubuntu IPv4：`192.168.1.10/24`
- Same subnet：`true`
- Default route on direct link：`false`
- Ping：`2 transmitted, 2 received, 0% packet loss`
- 必要端口打开：`29999`、`30002`、`30004`

## Dashboard

- Remote control：`false`
- Safety mode：`Safetymode: NORMAL`
- Robot mode：`Robotmode: RUNNING`
- Program running：`false`
- Program state：`STOPPED <unnamed>`
- Loaded program：`/programs/<unnamed>.urp`
- PolyScope version：`URSoftware 5.11.9.1010452 (Jan 24 2022)`

## RTDE 状态

- Payload：`0.44`
- Payload CoG：`[0.005, -0.005, 0.025]`
- TCP offset：`[0.0, 0.0, 0.12254000000000001, 0.0, 0.0, 0.0]`
- `actual_q` radians:
  `[0.592383086681366, -1.3196426194957276, -2.0418405532836914, -1.3557539147189637, 1.5732166767120361, -0.9888108412372034]`
- `actual_q` degrees:
  `[33.94105072177468, -75.60995256269359, -116.9888461418124, -77.67897737173595, 90.13867583519693, -56.65468793967226]`
- `actual_TCP_pose`:
  `[0.5320423088152189, 0.14822908575673194, 0.41126247986678166, 3.1374815984793436, 0.014716840672296665, -0.0061583997668157205]`
- `actual_TCP_force`:
  `[0.0968496250643611, -7.741900252022139, -17.64227811978721, 0.25997760026984856, -0.0021224548429638348, -0.14724258902189347]`
- Force norm：`19.266457292871934 N`
- Torque norm：`0.2987862739124738 Nm`

## 解释和确认

RTDE 读到的 force norm 高于移动前快照，但操作者随后确认：
实际完全没有任何接触。

因此，这个 `19.266457292871934 N` 只作为 UR 内置 `actual_TCP_force`
的一次只读观测值记录；它不是接触证据，也不能单独用于判断接触状态。
后续物理测量仍以现场视觉确认和手工量具读数为准。
