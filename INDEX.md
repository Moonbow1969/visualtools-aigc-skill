# 总索引 / Review Index

按编号review；文件内记录适用条件、真实字段、失败处理。版本日期：2026-11-17。

| 编号 | 文档 | 主要检查点 |
|---|---|---|
| 00 | [README](README.md) | 安装、公开版与本地总库边界 |
| 01 | [SKILL](SKILL.md) | Agent触发、路由与交付门槛 |
| 02 | [API合同](references/api-contract.md) | model key、上传字段、任务命名空间、过期与重试 |
| 03 | [H3抽卡 / profiles](references/h3-sampling.md) | TaoMate3步、FL/REF4步、8步、refine区别 |
| 04 | [H3多帧关键帧续接](references/h3-continuation.md) | 先首段、22帧history、10秒精确裁接 |
| 05 | [H3特效 / Character Swap](references/h3-effects.md) | 触发词、底模、强度、源动作、局部重做 |
| 06 | [数字人口播](references/digital-human.md) | 固定音轨、原生音画后换声、长口播同步 |
| 07 | [Qwen图像编辑](references/qwen-edit.md) | 多参考顺序、4/25步、漫画转真人、扩图 |
| 08 | [SAM选区 / 一致性 / 自动检测](references/masks-and-consistency.md) | 实例消歧、裁图贴回、脸检测与质量门槛 |
| 09 | [Illustrious / KREA社区LoRA](references/community-loras.md) | 生态选择、作者配置、抽卡矩阵、slider范围 |
| 10 | [SeedVR2](references/upscale.md) | 处理路由、尺寸预算、回退与细节重绘 |
| 11 | [验收与证据](references/quality-and-evidence.md) | 合同/执行/内容三层、可复现记录、公开发布 |
| 12 | [验证记录](references/verification.md) | 本次实际跑了什么、哪些仍有限制 |
| 13 | [来源与迁移](references/provenance.md) | 本地经验到公开配方的映射、矛盾如何处理 |

## 脚本与测试

| 文件 | 用途 |
|---|---|
| [scripts/visualtools.py](scripts/visualtools.py) | 公共图片/分割/超分、基础视频提交、两种视频命名空间下载 |
| [scripts/mask_edit.py](scripts/mask_edit.py) | 选区裁图与保护区像素严格不变的贴回 |
| [tests/test_tools.py](tests/test_tools.py) | 能力拒绝、失败/过期、base64、EXIF、mask和alpha边界 |
| [requirements.txt](requirements.txt) | 客户端运行依赖 |
| [LICENSE](LICENSE) | 本仓库原创代码/文档许可，不覆盖权重 |

## 用户需求覆盖

- MiniMax：03→3-step /4-step /8-step；04→10秒关键帧拼接；05→特效/Swap；06→数字人。
- Qwen：08→SAM3.1选区/auto-detect；07→风格和参照图编辑；07+08→通用一致性，不含私人肖像LoRA实验。
- Illustrious/KREA：09；SeedVR2：10。
- 所有工艺先对02核实调用方式，再以12区分实际验证与待复核效果。
