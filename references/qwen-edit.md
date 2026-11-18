# Qwen-Image 2.1：抽卡、参考图与风格转换

当前模型key `qwen_image_21_serv11`。JSON generations用于无图；multipart edits重复 `image` 字段，最多3张，顺序有意义；n最多2、按服务串行生成。做2–8张候选时分批请求，不把8塞进n。

## 基础编辑

```bash
curl -fsS "$VT/v1/images/edits" -F model=qwen_image_21_serv11  -F image=@source.png -F size=1024x1024 -F steps=4 -F n=2  -F 'prompt=Change only the blue vase to green. Preserve the camera, shape, lighting and background.'
```

始终显式设目标画幅；默认正方形会导致构图不符。Lightning内建：steps≤8使用加速路线、CFG1；steps>8切回base。先4步试意图，边缘/构图不稳时对照25步；不要断言25步必定保持原像素。编辑会重绘全画面，严格保留区域必须贴回。

## 参考图绑定

明确写“image1是要编辑的场景、image2提供什么”。不要把多张图当作分别生成多个输出的列表。除非某个LoRA约定相反，否则以源图先、目标参考后为起点；查具体model card。

| 工艺 | 有序输入 / 配方 | 检查 |
|---|---|---|
| 普通指令编辑 | image1源图，明确只改什么 | 相机/比例/文字漂移 |
| BFS head swap | image1目标身体场景，image2头部；`bfs_head_v1.1_qwen_2.1.safetensors` 1.0 | 颈线、耳朵、发际线；参考衣领可能泄漏 |
| 风格转换 | 原图 + 一种风格LoRA，先4步抽卡 | 形体/构图与身份是否一起被改 |
| 扩图 | 源图先补灰色#808080画布，边长32倍数；outpaint v2 | 原图贴回、接缝、尺寸 |

BFS提示起点：`head_swap: start with <image1> as the base image, preserve its lighting and environment, replace the head using <image2>, keep the pose and expression from <image1>.` 先把头参考裁干净，避免把领带或衣服当作身份特征。

## 漫画 → 真人

使用 `MoreReal_qwen21.safetensors`，起始0.6–0.9，提示从 `Convert this image into a photograph` 开始，说明想保留的姿势、布局、服装与光线。也可对照 `anything2real_qwen21.safetensors`，先查当前目录与作者说明。

```bash
curl -fsS "$VT/v1/images/edits" -F model=qwen_image_21_serv11  -F image=@drawing.png -F size=896x1152 -F steps=4 -F n=2  -F 'loras=[{"name":"MoreReal_qwen21.safetensors","strength_model":0.8}]'  -F 'prompt=Convert this image into a photograph. Preserve the composition, pose, outfit and lighting direction. Natural material textures.'
```

MoreReal可能把脸拉向自身风格，不能把“更写实”当作“更像参考”。身份严格时先做身份参考编辑，再弱风格对照；每一步检查，不无脑堆叠角色与强风格LoRA。跨动漫与真人的人脸embedding可能失效，视觉审查脸型、五官关系和特征。

## 扩图特殊处理

`qwen-image-2.1-outpaint-v2.safetensors` 1.0。上传已经补灰的画布，提示描述扩展区域，约1–2MP，边长32倍数。当前后端强制25步base、按画布尺寸输出、贴回原始像素；Lightning扩图容易留缝。不要把这套特殊规则推广到一般edit。

## 抽卡与修复

先固定源图、提示、LoRA及强度，做2–4个seed；再只改变一个因素。记录输出是否改变了文字、边缘、旁人、肢体。条纹/网格先视为生成失败，不交给SeedVR2“修复”——超分会保留或强化它。选区编辑见 [mask工艺](masks-and-consistency.md)。

许可：[Qwen-Image 2.1 LICENSE](https://github.com/QwenLM/Qwen-Image-2.1/blob/main/LICENSE) 是research license；公开分享本skill不等于取得模型或派生LoRA的商业授权。
