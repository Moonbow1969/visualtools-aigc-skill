# Visual Tools 接口合同

核对日期：2026-11-17。部署名称是 API key，不是可任意替换的营销型号。这里的 H3 指部署的 `minimax-h3-fl2va` / `minimax-h3-ref2va`；不把 Hailuo-02 商业 API 的字段直接套进本地 H3。Qwen 路线是此部署的 Qwen-Image 2.1 edit，不能把旧 Qwen-Image-Edit 工作流不加验证地混用。

## 入口与发现

```bash
export VT=https://visualtools.frederickpi.com
curl -fsS "$VT/api/health"
curl -fsS "$VT/v1/models"
curl -fsS "$VT/api/config"
curl -fsS "$VT/api/openapi.json"
curl -fsS "$VT/v1/h3/capabilities?model=minimax-h3-fl2va"
```

`/v1/models` 查生成模型，`/api/config.task_model_options` 查处理模型。`worker_count` 是配置副本数；`healthy_worker_count` 才是当时健康探测，仍不能代替一次实际推理。检查 `max_reference_images`、`max_outputs`、`supported_parameters`、`parameter_schema` 和 `parameter_options.lora_name`。模型列表可能有不适合公开示例的个人适配器，不要整体复制入文档。

当前公开部署的只读发现无需 API key；客户端支持可选 `VISUALTOOLS_API_KEY`，用于配置了 bearer 校验的实例。不要把别的模型服务密钥传给网关。入口整体可通过环境变量更换。

## 路由表

| 能力 | 路由 / 模型 | 编码与返回 |
|---|---|---|
| Qwen 生成/编辑 | `/v1/images/generations` / `/v1/images/edits`，`qwen_image_21_serv11` | JSON / multipart，`data[].b64_json` |
| Illustrious 文生图 | generations，`illustrious_sdxl_momentum` | JSON；无参考图 edit |
| KREA 生成/编辑 | 两个 images 路由，`krea2_turbo_momentum` | edit 最多 2 张、有序 |
| SAM 3.1 | `/v1/segment` | multipart，`masks[]` base64 PNG、`boxes` |
| SeedVR2 图片 | `/api/process`，`task_type=super_resolution`，`model_key=seedvr2_3b_serv11` | multipart；指定 `response_format=json`，`files[].base64` |
| 基础 H3 | `/v1/videos`，`minimax_h3_titanium` | 旧兼容接口；名义 5 秒、两种基础画幅 |
| 高级 H3 | `/v1/h3/videos`，`minimax-h3-fl2va` / `minimax-h3-ref2va` | multipart；TaoMate、LoRA、音频、profile、多帧引导 |
| 处理任务异步 | POST `/api/jobs` → GET `/api/jobs/{id}` | JSON 任务完成后内联结果；ZIP 用 `/download` |

## 高级 H3 字段

| 字段 | 含义 |
|---|---|
| `prompt`、`model`、`size` | 明确的任务、权重族、宽×高 |
| `seconds` 或 `frames` | frames 优先；22/39/56/73/90/107/124/141/158/175 帧，24 fps |
| `upscale` | `none` / `h3_refine_x2` / `realesrgan_x2`；抽卡显式用 none |
| `profile` | `auto` / `turbo4` / `turbo8` / `character-swap` |
| `action_lora` | 逗号分隔 ID，可带 `:strength`，最多 4 个；先查 capabilities |
| `input_reference`、`last_frame` | 单首帧 / FL2VA 末帧；REF2VA 不接受 last_frame |
| `reference_images` | REF2VA 1–4 张有序参考 |
| `reference_audio` | REF2VA PCM WAV；驱动画面且作为输出音轨 |
| `start_frames` | 重复上传 5/22/39 张，严格时间顺序、与目标尺寸相同；替代 input_reference |
| `reference_video` | Character Swap 源视频，≤50 MiB、≤8 秒、≤4MP，源片覆盖请求长度、画幅匹配 |
| `Idempotency-Key` | Header：同 key 同内容返回同任务；改内容需新 key |

`turbo8` 用 FL2VA；`character-swap` 用 REF2VA 的特定已验证组合，不是任意跨底模加载。高级 profile 和多帧引导限制 native24 / upscale=none。REF2VA 音轨和 Swap 源片音轨不同时传入。普通 profile 超过124帧也限制 native24 / none。未知字段应明确报错，不能靠“POST 成功”猜测是否生效。

## 生命周期

```bash
curl -fsS "$VT/v1/h3/videos" -H 'Idempotency-Key: example-shot1-take1'  -F model=minimax-h3-fl2va -F frames=73 -F size=544x960 -F upscale=none  -F action_lora=taomate-fl2va-3step -F input_reference=@first.png  -F 'prompt=The camera slowly pushes toward the vase; one continuous shot.' > receipt.json
# 保存返回的 UUID；在同一路由前缀轮询和下载：
curl -fsS "$VT/v1/h3/videos/JOB_UUID"
curl -fS "$VT/v1/h3/videos/JOB_UUID/content" -o shot.mp4
```

基础网关 ID 为 `video_…`，高级入口 ID 为 UUID。不可互换。`completed` 后立即下载，参考 `expires_at`；高级 H3 默认完成后约30分钟过期。旧处理任务 TTL 是另外的配置。

HTTP 4xx 先改请求；429 按队列等待；超时若已取得任务 ID，继续查原任务。没有拿到响应时，仅具有幂等 key 的请求可安全重发。图像 POST 没有此保证，不自动重试。失败任务记录原因，不无限轮询。客户端 deadline 不会自动取消正在跑的 GPU 工作。

处理 API 的 HTTP200 仍可能带 `warnings`、空 `files` 或发生模型回退。必须验证预期文件数、解码、真实尺寸和实际后端证据。公开实例是共享队列，端口不同不等于 GPU 独占。
