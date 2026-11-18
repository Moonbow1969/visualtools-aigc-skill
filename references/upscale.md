# SeedVR2 高分辨率修复

公开图片路线：`POST /api/process`，`task_type=super_resolution`，`model_key=seedvr2_3b_serv11`，`response_format=json`。发现入口是 `/api/config`，不是images生成模型列表。

```bash
curl -fsS "$VT/api/process" -F task_type=super_resolution  -F model_key=seedvr2_3b_serv11 -F response_format=json -F files=@keeper.png > upscale.json
```

解码 `files[].base64`（可能带data URI前缀），核对非空文件、warnings、尺寸和真实像素。`visualtools.py upscale` 会做基本检查。

## 用在哪一步

抽卡→语义/构图/身份通过→SeedVR2→1:1细节复核。它是扩散修复，能重建材质，也可能轻微改变眼睛、字和细部；不是数学意义无损放大。SeedVR2不修错误动作、错误人物、重影或条纹。用于已认可原片，不替代前置验收。

当前处理管线将超过约1MP的输入先缩至预算，再4倍放大，因此输出接近最多16MP；并非任意原始4K图片都得到原尺寸的4倍。公开process不提供任意scale参数。输入alpha按管线保留，但仍验实际透明通道。

## 与其他路线区分

- Real-ESRGAN是另一处理模型，速度/质感不同；选择key `real_esrgan_x4plus_serv6`。
- H3 latent x2+refine是在视频生成中改变latent并重新采样，可能改变内容；不是SeedVR2。
- RIFE是插帧，增加fps，不增加空间细节。
- 本部署SeedVR2失败时处理管线可能回退到Real-ESRGAN。保存warnings与返回的model/backend字段；如果返回未证明实际后端，标注“请求SeedVR2、后端未确认”，不要把它算SeedVR2性能或效果证据。

原生SeedVR2有视频恢复能力，已有本地视频路线；当前公开 `/api/process` 这份合同仅用于图片，不把MP4当图片files上传。整段视频处理须由单独经验证的接口/工作流提供，不能逐帧图片超分后默认不存在闪烁。

来源：[ByteDance SeedVR / SeedVR2](https://github.com/ByteDance-Seed/SeedVR)。模型许可与权重发行说明独立于本仓库。
