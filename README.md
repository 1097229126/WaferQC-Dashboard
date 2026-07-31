# WaferQC-Dashboard

基于半导体外延片生产过程中的质量检测数据，构建的可视化 BI 看板系统。

## 📋 项目概述

### 项目背景和价值
本系统旨在提升半导体外延片质量监控效率与数据分析能力，通过可视化的方式展示晶片浓度、厚度两大核心参数的全维度质量监控与分析结果。

### 核心功能
- **数据可视化**：展示两片批次/设备的 25 点位检测结果
- **均匀性计算**：自动计算检测点的均匀性指标
- **公差判定**：依据标准对数据进行公差范围判断
- **等级评定**：根据检测结果进行质量等级评定

## 🏗️ 技术架构

### 整体架构
采用 FastAPI + Vue3 前后端分离架构

### 技术栈

#### 后端
- **框架**: FastAPI + Pydantic
- **数据库**: MySQL（开发和生产）
- **ORM**: SQLAlchemy
- **其他依赖**: uvicorn, alembic, python-jose, pymysql

#### 前端
- **框架**: Vue3 + Vite
- **UI 组件库**: Element Plus
- **图表库**: ECharts
- **HTTP 客户端**: Axios
- **路由**: Vue Router

## 📁 项目结构

```
WaferQC-Dashboard/
├── backend/                    # 后端服务
│   ├── app/                   # 应用主目录
│   │   ├── api/              # API 路由层（Controller）
│   │   │   └── api.py        # API 端点定义
│   │   ├── core/             # 核心配置
│   │   │   ├── config.py     # 应用配置
│   │   │   └── database.py   # 数据库配置
│   │   ├── models/           # 数据模型层
│   │   │   └── models.py     # SQLAlchemy 模型
│   │   ├── schemas/          # Pydantic 数据验证
│   │   │   └── schemas.py    # 请求/响应 schema
│   │   ├── services/         # 业务逻辑层（Service）
│   │   │   └── service.py    # 业务逻辑实现
│   │   └── repositories/     # 数据访问层（Repository）
│   │       └── repository.py # 数据访问操作
│   ├── tests/                # 测试文件
│   │   └── test_api.py       # API 测试
│   ├── init_db.py            # 数据库初始化脚本
│   ├── requirements.txt      # Python 依赖
│   ├── .env                  # 环境配置文件
│   ├── .env.example          # 环境配置示例
│   └── main.py              # 应用入口
├── frontend/                  # 前端项目
│   ├── src/
│   │   ├── views/            # 页面视图
│   │   │   ├── DashboardView.vue      # 仪表板
│   │   │   ├── BatchListView.vue      # 批次列表
│   │   │   └── BatchDetailView.vue    # 批次详情
│   │   ├── components/       # 可复用组件
│   │   ├── api/              # API 调用
│   │   │   └── index.js      # API 客户端
│   │   ├── router/           # 路由配置
│   │   │   └── index.js      # 路由定义
│   │   ├── App.vue           # 根组件
│   │   └── main.js           # 应用入口
│   ├── index.html            # HTML 入口
│   ├── package.json          # Node.js 依赖
│   └── vite.config.js        # Vite 配置
└── README.md                 # 项目文档
```

## 🚀 快速开始

### 环境要求
- Python >= 3.9
- Node.js >= 16
- MySQL >= 5.7
- npm 或 yarn

### 数据库准备

1. 创建 MySQL 数据库
```sql
CREATE DATABASE wafer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 配置数据库连接
复制 `backend/.env.example` 为 `backend/.env`，并修改数据库配置：
```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的密码
MYSQL_DATABASE=wafer_db
MYSQL_CHARSET=utf8mb4
```

### 后端启动

1. 进入后端目录
```bash
cd backend
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 初始化数据库
```bash
python init_db.py
```

4. 启动服务
```bash
uvicorn main:app --reload
```

后端服务将运行在: http://localhost:8000

API 文档: http://localhost:8000/docs

### 前端启动

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

前端应用将运行在: http://localhost:5173

## 📊 API 接口

### 批次管理
- `POST /api/v1/batches/` - 创建新批次
- `GET /api/v1/batches/` - 获取所有批次（支持分页）
- `GET /api/v1/batches/{batch_id}` - 获取指定批次详情
- `PUT /api/v1/batches/{batch_id}` - 更新批次信息
- `DELETE /api/v1/batches/{batch_id}` - 删除批次

### 测量数据管理
- `POST /api/v1/measurements/` - 创建测量数据
- `GET /api/v1/batches/{batch_id}/measurements` - 获取批次的所有测量数据
- `PUT /api/v1/measurements/{measurement_id}` - 更新测量数据

### 质量分析
- `GET /api/v1/batches/{batch_id}/uniformity` - 计算批次均匀性
- `GET /api/v1/batches/{batch_id}/quality` - 获取质量评定结果
- `POST /api/v1/batches/{batch_id}/analyze` - 运行完整分析并更新数据
- `POST /api/v1/batches/bulk-create` - 批量创建批次和测量数据

## 🔧 开发指南

### 均匀性计算公式
```
均匀性 = (Max - Min) / (Max + Min) × 100%
```

### 质量等级标准
- **A 级**: 浓度均匀性 ≤ 2.0%，厚度均匀性 ≤ 1.5%
- **B 级**: 浓度均匀性 ≤ 3.5%，厚度均匀性 ≤ 2.5%
- **C 级**: 浓度均匀性 ≤ 5.0%，厚度均匀性 ≤ 3.0%
- **D 级**: 超出 C 级标准

### 公差判定
- 浓度公差阈值: 默认 5.0%
- 厚度公差阈值: 默认 3.0%
- 状态: PASS（合格）/ FAIL（不合格）

## 🧪 测试

### 运行后端测试
```bash
cd backend
pytest tests/ -v
```

注意：测试使用 SQLite 数据库，无需额外配置。

## 🐳 Docker 部署（可选）

### 构建镜像
```bash
docker build -t waferqc-backend ./backend
docker build -t waferqc-frontend ./frontend
```

### 运行容器
```bash
docker-compose up -d
```

## 📝 注意事项

1. **数据库配置**: 项目使用 MySQL 数据库，请确保 MySQL 服务已启动并正确配置 `.env` 文件
2. **安全配置**: 生产环境务必修改 `.env` 中的 `SECRET_KEY` 和 CORS 配置
3. **性能优化**: 大量数据时建议添加数据库索引和查询优化
4. **字符集**: 数据库使用 utf8mb4 字符集，支持完整的 Unicode 字符

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**WaferQC-Dashboard** - 让半导体质量检测更智能、更高效！ 🚀
