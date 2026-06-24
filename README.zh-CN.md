# Agentech Edge Project - Scenario People Check (SPC) - LV1.5 SKILLS

[中文](README.zh-CN.md) | [English](README.en.md)

这是一个本地优先的“场景人物检查”与人脸识别 API，面向舞蹈学校、课程照片、
教室截图、摄像头画面、工作流 App 等边缘场景。

第一版 MVP 不做完整教务系统，也不做完整签到 App。它只做一个可复用的
Scenario People Check API：给一张照片，检测人脸，匹配已知学生/老师/员工，
统计未知人脸，并把 JSON 结果返回给外部工作流系统。

## 产品承诺

一张照片进去，识别结果出来。

第一版 API 的流程是：

1. 创建人物：学生、老师、员工或未知人。
2. 为已知人物录入人脸照片。
3. 上传一张来自 iPhone、摄像头、监控截图或其他 App 的照片。
4. 返回人脸数量、已匹配人物、不确定人物和未知人物。
5. 后续可以把不确定/未知人脸分配给某个人，让系统逐步学习。

## 架构形态

```text
apps/
  mac-console/           Mac 本地控制台入口
  iphone-capture/        iPhone 浏览器拍照入口
services/
  recognition-worker/    人脸检测、embedding、匹配任务
  camera-watch/          未来 RTSP/ONVIF/NVR 摄像头接入
packages/
  core/                  共享领域模型、agent contract、skill interface
src/
  sa_attendance_system/  Python CLI、HTTP API、SDK、服务层
tests/
  test_face_api_service.py
db/
  schema.sql             SQLite-first 数据库 schema
docs/
  architecture.md
  api.md
  database-memory-skills-terminal.md
  decisions.md
  privacy-and-consent.md
  product-roadmap.md
  pricing.md
  sdk.md
logs/
  project-log.md          项目流水账
config/
  school.example.toml
data/
  本地运行数据，不进入 git
```

## 核心抽象

- Actor：老师、iPhone、摄像头、监控系统或未来机器人。
- Sensor：照片上传、视频帧、摄像头流、手动输入。
- Observation：系统在照片里看到的东西，还不是最终业务结论。
- Person：学生、老师、员工或未知身份。
- Memory：让系统越来越懂场景的稳定事实和学习结果。
- Skill：可替换能力，例如拍照、人脸识别、人工分配、导出。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
sa-attendance init --db data/attendance.sqlite
sa-attendance serve --db data/attendance.sqlite --media-dir data/media
```

第一版不依赖云端。人物数据和人脸数据默认应该保存在学校 Mac 或本地 edge node 上。

## SPC API 快速测试

```bash
PYTHONPATH=src python3 -m sa_attendance_system.cli create-person "Sarah" --type student
PYTHONPATH=src python3 -m sa_attendance_system.cli enroll-face person_xxx photos/sarah.jpg
PYTHONPATH=src python3 -m sa_attendance_system.cli recognize photos/class-photo.jpg
```

HTTP API 和 Python SDK 用法见 `docs/api.md` 和 `docs/sdk.md`。

## 第一版商业化 SKU

Scenario People Check 可以按学生数量或场景节点数量按月收费：

- Starter：最多 20 个学生
- Studio：21 到 100 个学生
- School：100 个以上学生

第一版价格模型见 `docs/pricing.md`。

