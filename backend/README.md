# rowing-coach-booking
赛艇教练预约微信小程序后端服务

## 技术栈

- **框架**: FastAPI (Python 3.11+)
- **数据库**: PostgreSQL + Directus
- **缓存**: Valkey
- **向量库**: Qdrant
- **AI**: Ollama (Whisper, bge-m3, Llama)

## 环境配置

1. 复制环境变量文件:
```bash
cp infrastructure/.env.example infrastructure/.env
# 编辑 .env 填入实际值
```

2. 启动基础设施:
```bash
cd infrastructure
docker-compose up -d
```

## 开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

启动后访问: http://localhost:8000/docs

## 目录结构

```
backend/
├── app/
│   ├── api/          # API 路由
│   ├── core/         # 核心模块 (DB, Auth, Ollama)
│   ├── models/       # Pydantic 模型
│   ├── services/     # 业务逻辑
│   └── main.py       # 应用入口
├── requirements.txt
└── Dockerfile
```