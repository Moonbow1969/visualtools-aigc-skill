---
name: visualtools-aigc
description: "Visual Tools AIGC production: MiniMax H3 sampling, motion continuation, effects and talking heads; Qwen image edits with SAM selections; Illustrious and KREA community LoRAs; SeedVR2 restoration. Use for executing and reviewing image/video tasks through capability-checked APIs."
---

# Visual Tools AIGC

把图片与视频任务转换成可执行、可检查的流程。公开 API：`https://visualtools.frederickpi.com`；通过 `VISUALTOOLS_BASE_URL` 改入口。先读 [总索引](INDEX.md) 和 [接口合同](references/api-contract.md)，再只加载当前任务所需配方。

## 决策原则

- 先查实时模型和能力，再构造参数；接口接受、GPU 完成和视觉验收是三件事。
- 明确指定 model。通用 `/v1/videos` 与高级 `/v1/h3/videos` 是不同任务命名空间，不能混用 ID。
- H3 先小批量低清抽卡，选设计和动作；改变分辨率是新抽卡，不能宣称保留原 seed 的同一表演。
- 把续接看成时间轴上的干净帧引导；多帧引导携带运动，单末帧接力只携带外观。
- Qwen 没有公开原生 mask 入参。严格局部编辑使用 SAM 选区、裁图生成、选区内贴回。
- 不把某个肖像训练实验的权重、触发词、素材或身份分数变成通用要求。
- 保存每次 request、模型/profile、输入哈希、任务 ID、输出、失败原因与挑选理由；下载完成结果后再处理下一批。
- 模型与社区 LoRA 的许可单独核查；本仓库的许可不覆盖模型权重。

## 工作流与读取路径

| 任务 | 阅读 | 产物 |
|---|---|---|
| 连接与发现 | [API](references/api-contract.md) | 能力快照、明确模型 |
| H3 快速抽卡 / 3、4、8 步选择 | [H3 profiles](references/h3-sampling.md) | 2–4 条候选、选片记录 |
| 10 秒以上连续镜头 | [续接](references/h3-continuation.md) | 分段原片、重叠帧、裁接清单 |
| 特效 / 换角色 | [LoRA 与 Swap](references/h3-effects.md) | 配对候选、源动作对照 |
| 数字人口播 | [数字人](references/digital-human.md) | 分句音轨、口型验收视频 |
| 局部编辑 / 风格转换 / 一致性 | [Qwen](references/qwen-edit.md)、[选区与检测](references/masks-and-consistency.md) | mask、候选、合成图 |
| 社区 LoRA 抽卡 | [Illustrious / KREA](references/community-loras.md) | 单变量抽卡矩阵 |
| 高清修复 | [SeedVR2](references/upscale.md) | 原片与高清对照 |
| 交付 | [验收](references/quality-and-evidence.md) | 可播放/可解码文件、复现记录 |

## 工具

安装 `requirements.txt`。`scripts/visualtools.py --help` 提供发现、图片生成/编辑、SAM、超分和基础视频生命周期；`scripts/mask_edit.py --help` 提供确定性裁图与贴回。高级 H3 使用本文引用的 curl 配方。每批先跑一个请求，成功后再跑 2–4 个候选；不要一次把共享 GPU 队列灌满。昂贵步骤只用于已通过前一阶段验收的素材。

所有参考与脚本的完整文件表见 [INDEX.md](INDEX.md)。版本状态与实测范围见 [验证记录](references/verification.md)。
