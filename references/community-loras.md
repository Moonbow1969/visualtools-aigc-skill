# Illustrious 与 KREA 社区 LoRA 抽卡

## 先选生态

| | Illustrious SDXL | KREA 2 Turbo |
|---|---|---|
| 当前key | `illustrious_sdxl_momentum` | `krea2_turbo_momentum` |
| 输入 | 文生图 | 文生图 / 1–2图edit |
| 提示习惯 | SDXL tag、negative prompt、触发词 | 自然语言、明确主体关系、触发词靠前 |
| 起点 | 28步、CFG5.5、1024²、dpmpp_2m/karras | 文生图8步、CFG关闭；edit10步 |
| 同时LoRA上限 | 4 | 3 |
| 强度API范围 | -2…2 | -2…2 |

模型文件能被加载不证明兼容。SDXL/Illustrious的LoRA不能直接用于KREA/Qwen；加速LoRA也要与采样器和步数匹配。不要为了“四步”随手加载目录里任意DMD/Lightning文件。

## 一次可复核抽卡

1. 选择已注册、底模匹配的LoRA。记录作者、版本/哈希、触发词、推荐强度、许可及用途。
2. 同一个构图先做无LoRA基线；再单LoRA作者强度。固定其余设置，对2–4个seed比较。
3. 在初始强度上下各试一个小变化（例如±0.2），检查效果是否增强、身体/物体是否变形、是否覆盖构图。
4. 需要两个LoRA时先分别通过，再叠加；风格、身份、动作各自职责明确。失败时移除最近加入的一项。
5. 只把通过的图送SeedVR2。保留原图，不用锐度掩盖内容错误。

### Illustrious中性示例

```bash
curl -fsS "$VT/v1/images/generations" -H 'Content-Type: application/json' -d '{
 "model":"illustrious_sdxl_momentum", "prompt":"scenery, watercolor mountain village, morning light, detailed background",
 "negative_prompt":"blurry, low quality", "size":"1024x1024", "steps":28, "guidance_scale":5.5,
 "seed":42, "n":1,
 "loras":[{"name":"NIK_illustriousXL.safetensors","strength_model":0.7,"strength_clip":0.7}]}'
```

`strength_model`与`strength_clip`独立记录，不默认所有LoRA都需要修改CLIP。先查发现接口确认该文件存在。

### KREA edit 与工具LoRA

1张图默认General Edit V2；2张图默认Identity Edit V2，顺序是场景→身份参考。显式提供edit LoRA会替换默认edit适配器。`steps=10`、画幅与源图匹配。复杂多人缠绕姿势优先对照Qwen。

| 用途 | 部署文件 / 起点 | 提示 |
|---|---|---|
| 草图完成 | `krea2_sketch2art_s5000.safetensors` 1.0 | `把草稿改成完成稿` |
| 镜头角度 | `krea2_camera_angles_v2.safetensors` 1.0 | `low angle shot`等具体角度 |
| 电影镜头 | `krea2_cinematic_movie_still.safetensors` 1.0 | `cinematic movie still` |
| 水墨 | `krea2_sumi_ink.safetensors` 0.9 | `SumiInk` |
| 光束 | `krea2_god_rays.safetensors` 1.0 | `KGodRays` |
| 角色设计板 | `krea2_character_design_v1.safetensors` 1.0 | `Character design` |

这些是作者/部署起点，不是每项都已验证成功。KREA四视图edit曾出现重复格、换色、缺侧面；不能以“装了LoRA”承诺可靠四视图，优先逐视角生成并验证。Slider作者可能建议±6或±15，当前网关只收-2…2；不要照抄超范围值，也不要把截断后的值当作作者原效果。

## 新LoRA进入服务

普通用户只能提交注册名称，不能提交任意文件路径或下载URL。管理员先核实许可证与架构，获取确切版本，登记文件名/default strength/trigger/role，更新服务目录，再用 `/v1/models` 确认。某些Comfy节点自动发现新文件，但API注册目录可能需reload；两层不是一回事。先做一个最小生成并视觉验证后才宣布可用。

许可需按具体文件核查；尤其KREA社区edit适配器已有个人/非商业限制记录。不要把社区可下载称为无限制开源商用。
