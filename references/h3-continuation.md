# 先生成第一段，再用多帧关键帧续接

这里的核心是 **clean keyframe / guide clip conditioning**。FL2VA / REF2VA 是底模和输入族；续接是独立的时间条件机制。不是在同一个首尾帧任务中指定终点，也不是把前一段当作普通语义参考视频。

## 三种方法不要混淆

| 方法 | 实际输入 | 接缝表现 |
|---|---|---|
| 单末帧接力 | A末帧 → B的input_reference | 外观可衔接，速度常重新起步 |
| 多帧 guide 续接 | A末尾22帧 → B的start_frames | 提供姿态和运动历史；输出包含重叠22帧 |
| 原生 latent Motion Context | 前段保存的AV latent | 另一种上下文方法；本公开入口不接受 latent |

`start_frames` 经 VAE 编码为干净 latent keyframes，通过 `MiniMaxH3AddGuide(frame_idx=0)` 加入条件，采样的是新段原始 latent。单张 first/last pin 也使用关键帧机制，但不足以携带运动速度。guide 是软约束，不能保证永不漂移。

## 约10秒两段 recipe

1. A：124帧、24fps、`upscale=none`。末尾设计成仍在进行的、下一段能延续的运动。下载并先验收A。
2. 无损按解码顺序取A的帧102…123（22张）。不用按容器秒数近似截取；不要用缩略图。
3. B：141帧，按顺序重复上传22个 `start_frames`，不再上传 `input_reference`。目标宽高与这22帧完全一致。`profile=turbo8` 是质量起点；TaoMate可做便宜对照。
4. B的提示从原速度/方向继续，再逐渐过渡，不要要求立刻反向运动。必要时用B的 `last_frame` 收束到已核对的终姿态。
5. B输出含前22帧的历史。保留A全部 + B[22:]，合计 `124+141−22=243`帧 =10.125秒。精确10秒从这个通过验收的时间轴裁出240帧，而不是改播放速度或盲删音频。
6. 接缝前后各检查至少0.5秒。guide不是原像素拷贝，必须看重绘误差、光线跳动、运动速度和身份。小幅色调差可对齐；重影、反向或身份跳变要重抽B。

```bash
mkdir -p tail
ffmpeg -v error -i A.mp4 -vf 'select=between(n\,102\,123)'  -fps_mode passthrough tail/%03d.png
# Bash 数组保证重复字段的时间顺序：
args=()
for f in tail/*.png; do args+=(-F "start_frames=@$f"); done
curl -fsS "$VT/v1/h3/videos" -H 'Idempotency-Key: sequence-B-take1'  -F model=minimax-h3-fl2va -F profile=turbo8 -F frames=141  -F size=544x960 -F upscale=none -F 'prompt=Continue the same slow forward move at the same pace, then gradually approach the vase.'  "${args[@]}" > B-receipt.json
```

下载B后先输出无音轨的准确画面时间线（A/B必须相同尺寸、native24）：

```bash
ffmpeg -i A.mp4 -i B.mp4 -filter_complex  '[0:v]setpts=PTS-STARTPTS[a];[1:v]trim=start_frame=22,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0,trim=end_frame=240,setpts=N/24/TB[v]'  -map '[v]' -r 24 -c:v libx264 -crf 12 -pix_fmt yuv420p joined-10s.mp4
```

音频另建时间线：A原音0…124/24，B从22/24起；接缝若有轻微噪声用短音频交叉淡化，保持最终240帧的视频时间基。口播优先用连续主音轨，逐句核对起止，不把帧重叠当成整段音频重复。

## 中间关键帧和循环

先审中间静帧，再写段落提示；静帧即使“像同一个人”也可能机位偏移。50%叠图检查背景、比例和位置，不能仅看缩略图。有条件时将批准的末姿态 pin 在前段末帧，并从其前22帧延续下一段。自由运动段过长容易漂移；让关键帧是自然可停顿的姿态。

循环末端的多帧 end guide、任意中间 frame_idx、原生 latent续接、自动 Relay 长片循环仍属于 ComfyUI 高级工作流，当前公开接口仅提供 start clip + FL2VA单末帧。不要把不可调用能力写成现成接口。

## 本次公开入口复核后的选择建议

同一花瓶首段上，Turbo8的自由续接发生拉远/形变；增加单末帧后仍出现中途跳到俯视。TaoMate +22帧history +单末帧、明确“结束运动后保持同一机位”通过抽帧检查。这个成功案例是推近后停稳，不是持续匀速穿越空间。优先各做一条TaoMate与Turbo8对照，选择实际通过者；不要把8步当作自动质量升级。详见verification。
