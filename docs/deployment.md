# 部署文档 - Rowing Coach Booking

## 环境要求

### 基础设施
- Docker & Docker Compose v2+
- PostgreSQL 16
- Directus (latest)
- Valkey (latest)
- Qdrant (latest)

### 后端
- Python 3.11+
- Uvicorn

### 前端
- 微信开发者工具
- Node.js 18+

## 部署架构

```
┌─────────────────────────────────────────────┐
│              微信小程序 (客户端)               │
└─────────────────────┬───────────────────────┘
                      │ HTTPS
                      ▼
┌─────────────────────────────────────────────┐
│         云端 API 服务器 (2核4G)               │
│  ┌─────────────────────────────────────┐    │
│  │         FastAPI Backend              │    │
│  │   (PostgreSQL + Valkey + Ollama)    │    │
│  └─────────────────────────────────────┘    │
└─────────────────────┬───────────────────────┘
                      │ 内部调用
                      ▼
┌─────────────────────────────────────────────┐
│              Docker Compose                   │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐    │
│  │PostgreSQL│ │ Valkey  │ │  Qdrant  │    │
│  └──────────┘ └─────────┘ └──────────┘    │
│  ┌──────────────────────────────────┐      │
│  │         Directus                  │      │
│  └──────────────────────────────────┘      │
└─────────────────────────────────────────────┘
                      │
                      │ VPN/NAT
                      ▼
┌─────────────────────────────────────────────┐
│         本地 Mac Mini M5 Max (AI推理)         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ Whisper  │ │ bge-m3   │ │ Llama 8B │    │
│  └──────────┘ └──────────┘ └──────────┘    │
└─────────────────────────────────────────────┘
```

## 快速部署

### 1. 克隆代码

```bash
git clone <repository-url>
cd rowing-coach-booking
```

### 2. 配置环境变量

```bash
cd infrastructure
cp .env.example .env
# 编辑 .env 填入实际值
```

### 3. 启动基础设施

```bash
docker-compose up -d

# 验证服务状态
docker-compose ps

# 检查日志
docker-compose logs -f postgres valkey directus qdrant
```

### 4. 配置 Directus

访问 http://localhost:8055 登录管理后台，创建以下 Collections：

- **members** - 会员表
- **coaches** - 教练表
- **bookings** - 预约表
- **training_records** - 训练记录表
- **coach_schedules** - 教练日程表

### 5. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. 配置微信小程序

1. 在微信公众平台注册小程序
2. 获取 AppID 和 AppSecret
3. 在 `frontend/project.config.json` 中配置 AppID
4. 使用微信开发者工具打开 `frontend/` 目录

## 生产环境部署

### Docker Compose (推荐)

```bash
# 构建后端镜像
cd backend
docker build -t rowing-coach-backend:latest .

# 使用生产级 docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes

参考 `kubernetes/` 目录下的 YAML 配置：

```bash
kubectl apply -f kubernetes/
```

## 环境变量

### Backend (.env)

```env
# 数据库
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/rowing_coach

# Directus
DIRECTUS_URL=http://directus:8055
DIRECTUS_TOKEN=your-static-token

# Valkey
VALKEY_URL=valkey://valkey:6379/0

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Qdrant
QDRANT_URL=http://qdrant:6333

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 验证部署

### 健康检查

```bash
curl http://localhost:8000/health
# 返回: {"status":"healthy"}
```

### API 文档

访问 http://localhost:8000/docs 查看 Swagger UI

### 测试账号

Directus 初始账号:
- Email: admin@rowing.com
- Password: (见环境变量 DIRECTUS_ADMIN_PASSWORD)

## 监控与日志

### 日志配置

使用 Loguru 进行结构化日志：

```python
from loguru import logger

logger.info("Booking created", booking_id=123, member_id=456)
```

### 健康监控

- `/health` - 健康检查端点
- `/metrics` - Prometheus 指标端点 (可选)

## 故障排查

### 数据库连接失败

```bash
# 检查 PostgreSQL 日志
docker-compose logs postgres

# 测试连接
psql -h localhost -U rowing_user -d rowing_coach
```

### Directus 无法访问

```bash
# 检查 Directus 日志
docker-compose logs directus

# 重新初始化
docker-compose down -v
docker-compose up -d
```

### AI 推理服务无响应

```bash
# 检查 Ollama 状态
curl http://localhost:11434/api/tags

# 重启 Ollama
ollama serve
```

## 备份与恢复

### 数据库备份

```bash
# 备份 PostgreSQL
docker-compose exec postgres pg_dump -U rowing_user rowing_coach > backup.sql

# 恢复
docker-compose exec -T postgres psql -U rowing_user rowing_coach < backup.sql
```

### Directus 备份

Directus 数据存储在 PostgreSQL，自动随数据库备份。

## 安全配置

### 生产环境必做

1. **更换所有默认密码**
2. **配置 HTTPS**
3. **设置 CORS 白名单**
4. **启用数据库 SSL**
5. **配置防火墙规则**
6. **启用 Valkey 密码认证**