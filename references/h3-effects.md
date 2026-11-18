# 特效 LoRA 与 Character Swap

速度 LoRA 负责采样 profile；特效 LoRA 改动作或画面，两者分开记录。先跑无特效候选，再只加一个效果；少量配对候选比较，避免两个强运动 LoRA 互相覆盖。

## 精选注册 ID

以下是本地工艺起点，提交前仍以当前 model 的 capabilities 为准。未注明“本次验证”的强度是既有经验，不代表本次重新做过全矩阵。

| ID | 用途 / 触发 | 起始强度 | 底模提示 |
|---|---|---:|---|
| `lockstab-v1` | `lockstab` + `the camera is centred on the subject`，口播/行走锁人 |0.8|REF2VA训练；既有FL2VA组合可作为实测特例，不推广到其他LoRA |
| `crash-zoom` | `crash_zm`，快速推近 |0.9|训练底模记录不足；只在已测试FL2VA组合试用 |
| `slapface` | `slapface`，明确接触动作 |0.5|作者声明多个模式；检查接触点和因果 |
| `wushu-v7` | `wushu_action,`，武术动作 |0.8|FL2VA；低步数中间动作可能糊 |
| `fight-flow-v2` | `Unarmed combat interaction` 等指定动作类型 |0.65|REF2VA训练；不要因成功加载就认定任意底模匹配 |
| `vbvr-i2v` | 无强制触发，减少重复/穿插 |1.0|FL2VA；仍需逐帧看接触 |
| `cinematic-v2` | 电影质感，无强制触发 |0.85|REF2VA；已有记录提示非商业输出限制，使用前核查作者许可 |
| `ball-kicking` | 球类动作，明确脚与球接触 |0.5–0.8|FL2VA；效果强度需按场景验证 |

```bash
curl -fsS "$VT/v1/h3/videos" -H 'Idempotency-Key: zoom-take1'  -F model=minimax-h3-fl2va -F frames=73 -F size=544x960 -F upscale=none  -F 'action_lora=taomate-fl2va-3step,crash-zoom:0.9' -F input_reference=@first.png  -F 'prompt=crash_zm. A sudden crash zoom toward the blue vase. The vase stays still on the table.'
```

TaoMate strength固定1，其他效果按实际注册范围。动作效果只影响首遍还是精炼也生效，见 sampling。公开服务的注册列表包含兼容历史，不能代替训练底模确认。

## Character Swap V1.5

目标：保留源视频动作、构图、节奏，把角色换成有权使用的参考形象。Swap LoRA自身不负责长窗续接；续接来自guide frames。先选择短源片与一张清楚全身参考，裁去人设板文字。源视频先归一化为24fps、目标画幅；加速动作应先 retime 源片，不能指望速度 LoRA覆盖源动作时间线。

公开 profile：`model=minimax-h3-ref2va`、`profile=character-swap`、`reference_video`、有序 `reference_images`、native24 / none。组合为 REF2VA + SigmaShift12/3 + 特定 FL2V Turbo8 768p + SwapV1.5，`er_sde/normal`、8步。这是已有视频替换图的特例，不是建议普遍混搭FL和REF加速器。

```bash
curl -fsS "$VT/v1/h3/videos" -H 'Idempotency-Key: swap-short-take1'  -F model=minimax-h3-ref2va -F profile=character-swap -F frames=73  -F size=544x960 -F upscale=none -F reference_video=@source-24fps.mp4  -F reference_images=@character.png  -F 'prompt=Replace the person in <Video 1> with the character in <Picture 1>. Follow the source pose, gaze, expression and movement in every frame. Preserve the camera and scene.'
```

先检查完整画面的肢体与时序，再在人物最大的帧检查脸和衣服。源片翻滚、遮挡时，用提示明确姿势；缩略图常看不出浮空或关节错误。

### 局部重做与长片

选安静接点J；源片从J截取所需区间；前一条认可结果J…J+4的5帧作 `start_frames`，只重抽这个窗口。组装保留原片[0:J+5] + 新窗[5:]，防止重复或漏帧。多人物时当前公开Swap没有选人mask入口，不应声称精确保留路人；使用 [H3 Relay](https://github.com/akatz-ai/h3-relay) 的SAM选人和history carry工作流，或拆成明确的单人镜头。Relay现有本地能力不等于公开HTTP已提供完整自动编排。

本次公开入口复核：高饱和红色服装参考产生橙色发光边；换成低饱和、漫反射服装参考后，同源表演的Swap候选正常。若参考图有极亮边缘、强饱和衣物或风格化高光，先做中性色/自然光对照，不把发光边当作正常“高清增强”。
