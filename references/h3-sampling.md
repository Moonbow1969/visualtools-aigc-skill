# H3 抽卡与 3 / 4 / 8 步

## 选择表

| 目的 | 起点 | 为什么 / 限制 |
|---|---|---|
| 已有首帧，快速试动作/构图 | TaoMate 3-step | 低清多候选便宜；FL2VA、有图条件；不是 REF2VA 通用加速器 |
| 无图 T2V | FL2VA Turbo4 | TaoMate 路线需要帧；不能仅改步数冒充 TaoMate |
| 多图身份/场景或固定口播 WAV | REF2VA Turbo4 | 参考图与音频属于 REF2VA 输入合同 |
| 有计划的关键帧、续接对齐质量优先 | FL2VA Turbo8 | 慢一些，作为 TaoMate 的质量对照；仍需检查自由帧身份和运动 |
| 视频换角色 | Character Swap profile | REF2VA + Swap V1.5 + 专用8步组合；见 effects |
| 高分辨率小细节 | 原生目标分辨率重新抽卡 | 低清小脸的信息无法靠后期完整补回 |

### TaoMate 3-step 工艺

1. 先审首帧：画幅正确、人物/物体不残缺、没有网格、文字污染。首帧决定开场姿态，不能用提示词把它变成另一个机位。
2. 设 `model=minimax-h3-fl2va`、`upscale=none`、`output_fps=24`、`action_lora=taomate-fl2va-3step`。2–4 个独立任务，每条换幂等 key。
3. 从原片挑动作与镜头，不先挑锐度。先检查全画幅，再看首秒、动作峰值、末秒。
4. 通过后再决定原生高清重抽、非生成式处理或 H3 refine；每次改变分辨率/精炼都重新验收。

实际图合同：TaoMate strength=1；SigmaShift video12/audio3；Kitchen attention；Euler；手动 sigmas `1.0, 0.9612, 0.8533, 0.0`。3-step 是这一整套配方，不是把普通 Turbo 的 steps 改成3。TaoMate 会替代首遍 Turbo，不把两个速度 LoRA 同时叠上。

### 4-step 与 8-step 要区分底模和阶段

- FL2VA Turbo4：本部署 v1.3 768p，`res_multistep/simple`，4步。REF2VA 使用它自己的 Turbo4 v1.0 768p。
- `profile=turbo8`：FL2V Turbo8 v1.0，`res_multistep/simple`，8步；不能同时加 TaoMate。
- 当前 `h3_refine_x2`：FL2VA 二次采样 Turbo4、denoise0.45；REF2VA 为0.30。TaoMate 初采样后的 refine 不继承首遍的特效组合。
- 历史 HD 网格修复曾用8步 + 低起始 sigma0.30 + Euler。单独增加步数并不是修复；这是不同的 refine 配方，当前 `profile=turbo8` 指初采样，不代表把 refine 改成那套配方。
- 8步适合需比较对齐/细节的质量候选，不能承诺必然胜过4步。高速推近中 refine 可能把清楚的小脸抹糊；先看最快运动帧。

## 提示词

首帧 I2V 模板：

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] A live-action studio shot starts from the supplied image. The camera pushes in slowly with a small amplitude toward the blue vase. The vase remains on the table. End with its rim and glaze visible. One continuous shot.
overall_soundscape: Quiet room tone.
non_diegetic_music: N/A
```

一个主动作、一个明确终点、具体的固定物和光源。不要堆设备名和“epic”等抽象词。用图中真实方位描述左右。参考图多角度按顺序逐张声明，未提供的背面可能被编造。

短动作按动作长度生成：一个1.6秒的动作若生成5秒再裁，模型可能已经把动作摊慢。`frames=39` ≈1.625秒；`73` ≈3.042秒；`124` ≈5.167秒。名义 seconds 不是精确时长，交付用 ffprobe 检查。

抽卡协议：先固定输入/提示/profile做少量候选；动作反复失败才改提示或镜头。没有可指定 seed 的高级 H3 API 不支持严格同 seed A/B；不要把两个随机任务称为同 seed 对照。修改输出大小也是新分布。

来源：[H3 官方模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3)、[LightX2V H3 实现](https://github.com/ModelTC/LightX2V/tree/main/scripts/minimax_h3)；本文具体数值来自部署图与本地工艺记录，非所有实现的默认值。
