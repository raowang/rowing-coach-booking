# rowing-coach-booking

赛艇教练预约微信小程序 - AI驱动的智能预约系统

## 项目结构

```
rowing-coach-booking/
├── frontend/          # 微信小程序前端
├── backend/           # FastAPI 后端服务
├── infrastructure/    # Docker Compose 配置
└── docs/             # 文档
```

## 技术栈

### 前端
- 微信小程序 (WXML/WXSS/JavaScript)
- AI 对话组件
- 微信订阅消息集成

### 后端
- FastAPI (Python 3.11+)
- Directus (API管理 + MCP集成)
- SQLite (共享数据库)
- Ollama (本地 AI 推理)

### AI 能力
- Whisper (语音识别)
- Llama 3.1 8B/70B (对话生成)

## 快速开始

### 前置条件
- Docker & Docker Compose
- Python 3.11+
- 微信开发者工具

### 启动基础设施

```bash
cd infrastructure
docker-compose up -d
```

访问 Directus: http://localhost:8055

### 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 启动前端

使用微信开发者工具打开 `frontend/` 目录

## 架构

```
┌─────────────────┐
│  微信小程序      │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────────┐
│       Docker Compose                  │
│  ┌───────────┐  ┌───────────────┐   │
│  │ SQLite   │  │  Directus    │   │
│  │(共享数据库) │  │  (API+MCP)  │   │
│  └─────┬─────┘  └───────────────┘   │
│        │              │              │
│        └──────┬───────┘              │
│               ▼                      │
│        ┌───────────────┐            │
│        │   FastAPI    │            │
│        │  (业务逻辑)  │            │
│        └───────────────┘            │
└─────────────────────────────────────┘
```

## 功能模块

1. **AI 智能教练推荐** - 基于会员画像智能匹配教练
2. **自然语言交互** - 支持文字/语音的 AI 对话
3. **智能日程管理** - 动态日程协调，微信通知确认
4. **练后反馈闭环** - 教练点评 + AI 改善建议
5. **个性化关怀** - 生日祝福、会籍续期提醒、活动推送

## License

MIT