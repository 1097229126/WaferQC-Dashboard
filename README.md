# WaferQC-Dashboard

基于半导体外延片生产过程中的质量检测数据，构建的可视化 BI 看板系统。

## 📋 项目概述

### 项目背景和价值
本系统旨在提升半导体外延片质量监控效率与数据分析能力，通过可视化的方式展示晶片浓度、厚度两大核心参数的全维度质量监控与分析结果。

### 核心功能
- **数据可视化**：展示晶圆的浓度、厚度测量数据统计
- **自动统计**：自动计算每个晶圆的平均浓度和平均厚度
- **一致性分析**：对比设备1和设备2的测量差异，计算浓度一致性和厚度一致性
- **测量明细**：点击可查看每条测量数据的详细信息
- **分页查询**：支持大量数据的分页浏览

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

### 晶圆管理
- `GET /api/v1/wafers/` - 分页获取晶圆列表（含平均浓度、平均厚度统计）
- `GET /api/v1/wafers/{wafer_no}` - 根据晶片号获取晶圆详情及统计信息
- `POST /api/v1/wafers/` - 创建新晶圆
- `DELETE /api/v1/wafers/{wafer_no}` - 删除晶圆
- `POST /api/v1/wafers/bulk-create` - 批量创建晶圆及其测量数据

### 测量数据管理
- `POST /api/v1/measurements/` - 创建测量数据（支持浓度和厚度两种类型）
- `GET /api/v1/wafers/{wafer_no}/measurements` - 获取指定晶圆的所有测量数据

### 响应示例

#### 晶圆列表响应
```
{
  "total": 5,
  "items": [
    {
      "id": 1,
      "wafer_no": "WAFER-2024-001",
      "original_grade": "A",
      "concentration_target": 1500000000000000.0,
      "thickness_target": 10.0,
      "avg_concentration": 1498765432100000.0,
      "avg_thickness": 10.0234,
      "measurement_count": 50,
      "conc_consistency": 0.0,
      "thick_consistency": 27.45,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

**新增字段说明**：
- `conc_consistency`: 浓度一致性 (%)，衡量设备1和设备2在浓度测量上的一致性
- `thick_consistency`: 厚度一致性 (%)，衡量设备1和设备2在厚度测量上的一致性

#### 测量数据响应
```
[
  {
    "id": 1,
    "wafer_no": "WAFER-2024-001",
    "measurement_type": 1,
    "value": 1440342974404205.2,
    "measured_at": "2024-01-01T12:00:00",
    "created_at": "2024-01-01T12:00:00"
  }
]
```

### 参数说明

#### 测量类型 (measurement_type)
- **1**: 浓度测量（单位：atoms/cm³）
- **2**: 厚度测量（单位：μm）

#### 查询参数
- `skip`: 跳过记录数（默认 0）
- `limit`: 返回记录数（默认 100，最大 1000）

## 🔧 开发指南

### 数据模型说明

#### Wafer（晶圆）表
- `wafer_no`: 晶片号（唯一标识）
- `original_grade`: 原始等级
- `concentration_target`: 浓度目标值
- `thickness_target`: 厚度目标值

#### Measurement（测量数据）表
- `wafer_no`: 关联的晶片号（外键）
- `measurement_type`: 测量类型（1=浓度，2=厚度）
- `value`: 测量值
- `measured_at`: 测量时间

### 均匀性计算公式
```
均匀性 = (Max - Min) / (Max + Min) × 100%
```

### 一致性指标计算（设备1 vs 设备2）

#### 浓度一致性
对25个浓度点位（P1-P25），计算每个点位的一致性百分比，然后取均值：
```
点位一致性 = ((设备1.Pi - 设备2.Pi) / 设备2.Pi) × 100%
浓度一致性 = AVG(所有25个点位的一致性)
```

#### 厚度一致性
对25个厚度点位（T1-T25），计算每个点位的一致性百分比，然后取均值：
```
点位一致性 = ((设备1.Ti - 设备2.Ti) / 设备2.Ti) × 100%
厚度一致性 = AVG(所有25个点位的一致性)
```

**说明**：
- 仅计算同时存在于设备1和设备2的数据点
- 如果设备2的值为0，则跳过该点位
- 如果没有任何有效点位，返回 null
- 前端显示时保留两位小数并添加 % 后缀

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
