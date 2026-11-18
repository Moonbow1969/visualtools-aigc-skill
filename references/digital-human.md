# MiniMax 数字人口播

先确定“必须忠实于已有声音”还是“先要自然表演，再匹配声音”。默认用已审核口播音轨驱动，保留原始音频与台词时间轴。

## 固定音轨驱动

1. 准备全身/半身形象和一张清晰正脸，按全景→脸的顺序作为 `reference_images`。不要用混合多人或有分栏文字的人设板。
2. 审音频：台词完整，单一说话人、停顿清楚；转PCM WAV（推荐32kHz），按句间停顿切段，尾部可加短静音。每段≤124帧用于普通HD路线，native可到175帧。
3. 走高级 H3 REF2VA + `reference_audio`；FL2VA 不接受固定音轨。已有开场构图可加独立 `input_reference`，它不替代人物参考。
4. 两条候选检查口型、眼神与身体表现；“暖笑、快语速、自然对嘴”等同时叠加容易夸大张嘴，改为具体微动作。
5. 下载即验：首字、末字、停顿、双唇音，正常速度播放和逐帧检查都要做。不要只依赖唇间距均值。

```bash
curl -fsS "$VT/v1/h3/videos" -H 'Idempotency-Key: presenter-seg1-take1'  -F model=minimax-h3-ref2va -F frames=124 -F size=544x960 -F upscale=none  -F reference_images=@presenter.png -F reference_images=@face.png  -F reference_audio=@speech.wav -F action_lora=lockstab-v1:0.8  -F 'prompt=lockstab. <Picture 1> shows the presenter and clothing. <Picture 2> is a close view of the same face. The camera is centred on the presenter. The presenter speaks the supplied audio with small natural jaw motion, briefly pauses between phrases, and makes one restrained hand gesture.'
```

服务会将输入音轨作为输出声音，按视频长度裁/补静音；这不等于每个音素已经对齐。若开口异常先简化表情与动作，检查原音时序，再换候选。高清 refine 可能改脸或嘴；必须重新验收。

## 原生音画，再换声

可先让H3按 `(S1) <d>[Chinese] 台词</d>` 产生音画。先转写和回听确认没有漏字/重复/自加台词。提取原声作为时间基，选择保持时长的声音转换，或把新TTS按短语对齐到原片时窗。不要仅把另一段同台词的音频整段替换进去。

按短语时窗伸缩：tempo倍率 = 新声音片段长度 / 原片目标时窗长度；静音或低能量处切，短淡入淡出，保留辅音起止。之后逐句核对同步。声音模型、参考音色和身份素材由项目提供，本skill不捆绑私人声音或角色训练参数。

## 长口播

按自然停顿做独立段落，或使用多帧guide继续画面。需要连续主音轨时按原时间轴组装，扣除每段重叠帧对应的音频；不能按返回的名义seconds盲拼。超过单段模型限制不是把seconds改成30；使用多段并检查接缝。画面出现长期漂移或双人重影时，优先退回独立短段。
