# 来源与迁移说明

公开版是重新编排的程序知识，不是总库压缩包。原始实验和运维笔记保留在维护者本地；公开版不要求读者访问它们。

| 来源类别 | 迁移内容 | 公开落点 |
|---|---|---|
| H3 prompting / service-api / profiles | 真实图节点、TaoMate、FL/REF区别、尺寸帧长限制 | API、H3 sampling |
| keyframes-and-chaining / loop-chains | 单末帧、多帧clean guide、运动上下文、重叠裁接区别 | continuation |
| loras / character-swap-relay | trigger/strength、训练底模、Swap与Relay分工 | effects |
| digital-human h3-recipe / voice-replacement / refine分析 | 音频优先、口型检查、分段、refine不是单纯放大 | digital-human、sampling |
| image-editing / segmentation / pasteback工具 | mask坐标、实例匹配、保护区、参考顺序 | masks、Qwen |
| 社区LoRA部署笔记和线上模型目录 | Illustrious/KREA参数、角色/风格/工具适配器区分 | community-loras |
| SeedVR2部署与图像处理代码 | 处理API、约1MP输入预算、后端回退 | upscale |
| 线上OpenAPI与部署源码 | 公开网关实际合同、旧文档矛盾修正 | API、verification |

## 本轮解决的主要矛盾

- 本地旧H3 README写只支持5秒单图，新部署已支持更短/长帧格、REF2VA和特效；以当前部署与实际请求验证为准。
- 本地底层功能不等于公开网关功能。本轮新增独立 `/v1/h3` 前缀，保留旧 `/v1/videos`，不让高级参数悄悄丢失。
- 多帧guide是续接机制，不以底模FL2VA/REF2VA名称代替机制解释。
- 旧 docs 将SAM2擦除和新SAM3选区混在一起；公开版按接口和输出分开。
- 本地私人肖像LoRA、训练结果和评分未迁移；自动检测只写通用流程与可验证行为。
- 旧docs模型默认值、可用后端与本地文件列表不一致；改为运行时发现和显式model。
- 社区作者slider强度可能超过服务范围；公开版同时写明作者起点与API限制，不假定全范围可执行。

## 公共上游

- [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3)
- [LightX2V H3](https://github.com/ModelTC/LightX2V/tree/main/scripts/minimax_h3)
- [H3 Relay](https://github.com/akatz-ai/h3-relay)
- [Qwen-Image2.1许可](https://github.com/QwenLM/Qwen-Image-2.1/blob/main/LICENSE)
- [SeedVR2官方仓库](https://github.com/ByteDance-Seed/SeedVR)
- [本部署在线API文档](https://visualtools.frederickpi.com/docs)

上游模型能力、具体部署能力、历史小样本视觉结果分别记录。公开skill不搬运第三方权重或完整模型说明书。
