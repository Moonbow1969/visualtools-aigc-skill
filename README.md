# Visual Tools AIGC Skill

可交付的图片 / 视频制作工艺库：**MiniMax H3、Qwen-Image 2.1、SAM 3.1、Illustrious、KREA 2、SeedVR2**。面向使用 Visual Tools 的队友，也可作为 agent skill 加载。

**[从总目录 INDEX.md 开始](INDEX.md)** · [Agent 入口](SKILL.md) · [API 合同](references/api-contract.md) · [实测与限制](references/verification.md)

## 快速开始

```bash
git clone https://github.com/Moonbow1969/visualtools-aigc-skill.git
cd visualtools-aigc-skill
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export VISUALTOOLS_BASE_URL=https://visualtools.frederickpi.com
python scripts/visualtools.py discover
```

Python客户端只依赖requests和Pillow；视频帧提取、拼接与解码验证还需系统安装FFmpeg/ffprobe，curl示例使用Bash。模型推理在服务端执行，本机无需模型权重或GPU。

先选模型，再读对应工艺。基础图片示例：

```bash
python scripts/visualtools.py generate --model qwen_image_21_serv11   --prompt 'A clean studio photograph of one blue ceramic vase on a wooden table'   --size 512x512 --steps 4 --n 1 --out runs/vase
```

网页入口：[Visual Tools](https://visualtools.frederickpi.com/#workbench)。模型字段与上传参数以 [在线文档](https://visualtools.frederickpi.com/docs) 和实时发现为准。

## 包含什么

- 按场景选择 3/4/8 步、关键帧续接、特效 LoRA 与数字人口型流程。
- SAM 选区与 Qwen edit 的完整衔接，参考图顺序、一致性检查、自动检测失效处理。
- Illustrious / KREA 的社区 LoRA 选择、触发词、抽卡矩阵和失败修复。
- SeedVR2 超分、模型回退辨别和高清验收。
- 可运行客户端、局部合成工具、离线测试和明确的验证记录。

这里是经过筛选的对外版本。本地总库仍保留完整历史、运维记录和私人实验；不会把本地目录、私网地址、凭证、私人肖像 LoRA、训练集或原始聊天日志同步到这里。发布采用白名单文件导出，不复制总库 Git 历史。

## 作为 skill 使用

把本仓库目录作为一个 skill 提供给支持 `SKILL.md` 的 agent；无需下载模型权重。普通用户可放进自己管理的技能目录。使用统一技能注册表的环境应通过其 adopt/link 工作流安装，避免出现多份源文件。

贡献和勘误请引用 INDEX 中的编号，给出模型 key、接口、参数、观察到的现象和可公开的证据。不要在 issue 中上传私人素材或服务密钥。
