# SAM 3.1 选区、自动检测与一致性

## 网页操作

进入Visual Tools的workbench，打开源图，使用SAM点选或文本选对象，检查选区后设为selection。局部重绘中选Qwen，填写只改目标对象的指令，配置LoRA，抽2–8张候选，审边界后采用。网页裁选区附近、发edit、只在选区内贴回。API客户端必须自行完成同一流程。

## SAM合同

```bash
curl -fsS "$VT/v1/segment" -F image=@source.png  -F 'text=person:3' -F individual=true -F threshold=0.5 > masks.json
# 点选与排除点：坐标是EXIF方向校正后的原图像素，不是0..1归一化值
curl -fsS "$VT/v1/segment" -F image=@source.png  -F 'positive_coords=[[310,220]]' -F 'negative_coords=[[500,220]]'
```

返回 `{width,height,count,masks,boxes,wall_s}`。每个mask是base64 PNG，白=目标、黑=保护；`individual=true` 保留实例，不能先把三个人的mask全并起来再说只编辑一个。text、正负点、boxes至少提供一项；boxes是`[[x0,y0,x1,y1],…]`。

SAM 3.1分割不是SAM2+LaMa擦除。后者属于 `task_type=sam_inpaint`、不同模型与目的。Qwen edits没有`mask`或`selection_mask_png_base64`字段，不能直接传一个mask就期待生效。

## 可执行本地闭环

1. `visualtools.py segment` 保存mask；目检目标，选择其中一张。
2. `mask_edit.py prepare` 按非空mask求bbox、加上下文padding，保存裁图、mask与坐标manifest。
3. 将裁图作为edit的image1，参考图按模型约定补上。输出应与准备后的画布尺寸一致。
4. `mask_edit.py compose` 从manifest反向映射，仅在原选区内贴回。保护区逐像素等同原图；PNG保留source alpha。
5. 目检选区边缘、人物姿态和几何。严格保留外部像素并不能保证内部没有错误。构图被重画时先拒绝，不靠缩放强行对齐。

## 各种自动检测如何衔接

| 自动化 | 结果 | 失败时 |
|---|---|---|
| SAM文本检测person / clothes / object | 多个实例mask和bbox | 没有候选就报错；多候选用位置/点/box消歧 |
| 面部检测器（可选本地组件） | face bbox / landmarks | 侧脸、遮挡、动漫可能漏检，不把零检测当作身份正确 |
| 身份embedding（可选本地组件） | 与项目参考的相似度排序 | 不设跨人群/跨风格的万能阈值；只作候选排序 |
| 源/编辑实例匹配 | 位置或mask IoU | 低重合表明位移或选错人；拒绝或重审 |
| 背景边缘对齐 | 保护区边缘重合 | 纹理太少不能证明对齐；改用轮廓与人工对照 |
| 口型/眼睛检测 | landmarks随时间曲线 | 缺帧要标注，不能补成“没有运动” |

公开API只承诺SAM，未提供人脸识别或专用ArcFace评分端点；不要捏造 `/faces`。可在自己环境安装合适的检测器，但本包不捆绑肖像模型、私人质心或训练数据。

## 一致性检查顺序

先确认正确对象，再看几何位置，最后比身份和风格。多人图绝不能默认“最大的脸就是目标”。用衣服/位置+点击明确选择；头部替换还应检查耳朵、头发、颈线和遮挡。固定源图与参考，跑多个候选；像素保护只对mask外成立。衣服、头发变大需要先扩大并复核授权选区，不在合成时偷偷扩大它。

本次实跑的花瓶局部变色：4步产生内侧轮廓偏移，直接贴回可见边缘；25步加“保持精确轮廓与位置”的指令后改善。自动工具只保证mask外不变，不能替代这一步目检。
