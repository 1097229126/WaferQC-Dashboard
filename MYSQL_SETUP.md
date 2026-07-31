# MySQL 数据库配置指南

## 📋 前置要求

- MySQL 5.7 或更高版本
- Python 3.9+
- pymysql 驱动（已包含在 requirements.txt 中）

## 🔧 配置步骤

### 1. 创建数据库

使用以下 SQL 命令创建数据库：

```sql
CREATE DATABASE wafer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

或者执行提供的初始化脚本：

```bash
mysql -u root -p < backend/init_database.sql
```

### 2. 配置环境变量

复制 `backend/.env.example` 为 `backend/.env`：

```bash
cd backend
copy .env.example .env
```

编辑 `.env` 文件，修改数据库连接信息：

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=Root@123456
MYSQL_DATABASE=wafer_db
MYSQL_CHARSET=utf8mb4
```

### 3. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 4. 初始化数据库表

运行初始化脚本创建数据表和种子数据：

```bash
python init_db.py
```

这将：
- 创建所有必要的表结构
- 插入示例数据（3个批次，每个批次50条测量记录）

### 5. 启动服务

```bash
uvicorn main:app --reload
```

## 🗄️ 数据库表结构

### wafer_batches (批次表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| batch_number | VARCHAR(50) | 批次号，唯一 |
| equipment_id | VARCHAR(50) | 设备ID |
| production_date | DATETIME | 生产日期 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### wafer_measurements (测量数据表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| batch_id | INT | 外键，关联批次表 |
| wafer_position | VARCHAR(10) | 晶圆位置 (A/B) |
| point_number | INT | 测量点编号 (1-25) |
| concentration | DOUBLE | 浓度值 |
| thickness | DOUBLE | 厚度值 |
| uniformity_concentration | DOUBLE | 浓度均匀性 (%) |
| uniformity_thickness | DOUBLE | 厚度均匀性 (%) |
| tolerance_status | VARCHAR(20) | 公差状态 (PASS/FAIL) |
| grade | VARCHAR(10) | 质量等级 (A/B/C/D) |
| measured_at | DATETIME | 测量时间 |

## 🔍 验证配置

### 检查数据库连接

```python
# 测试脚本
from app.core.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("数据库连接成功！")
except Exception as e:
    print(f"数据库连接失败: {e}")
```

### 查看数据

```sql
-- 查看所有批次
SELECT * FROM wafer_batches;

-- 查看某个批次的测量数据
SELECT * FROM wafer_measurements WHERE batch_id = 1;

-- 统计信息
SELECT 
    COUNT(*) as total_batches,
    AVG(concentration) as avg_concentration,
    AVG(thickness) as avg_thickness
FROM wafer_measurements;
```

## ⚠️ 常见问题

### 1. 连接被拒绝

**问题**: `Access denied for user 'root'@'localhost'`

**解决**: 
- 检查用户名和密码是否正确
- 确认 MySQL 服务正在运行
- 检查用户权限

### 2. 数据库不存在

**问题**: `Unknown database 'wafer_db'`

**解决**: 
```sql
CREATE DATABASE wafer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 字符集问题

**问题**: 中文显示乱码

**解决**: 
确保数据库、表和连接都使用 utf8mb4 字符集

### 4. 端口冲突

**问题**: 无法连接到 3306 端口

**解决**: 
- 检查 MySQL 是否在其他端口运行
- 修改 `.env` 中的 `MYSQL_PORT` 配置

## 🔐 安全建议

1. **生产环境**: 
   - 不要使用 root 用户
   - 创建专用数据库用户
   - 设置强密码
   - 限制访问IP

2. **创建专用用户示例**:
```sql
CREATE USER 'waferqc'@'localhost' IDENTIFIED BY 'StrongPassword123!';
GRANT ALL PRIVILEGES ON wafer_db.* TO 'waferqc'@'localhost';
FLUSH PRIVILEGES;
```

3. **备份策略**:
```bash
# 备份数据库
mysqldump -u root -p wafer_db > backup_$(date +%Y%m%d).sql

# 恢复数据库
mysql -u root -p wafer_db < backup_20240101.sql
```

## 📊 性能优化

### 添加索引

如果数据量较大，可以考虑添加更多索引：

```sql
-- 为常用查询字段添加索引
CREATE INDEX idx_grade ON wafer_measurements(grade);
CREATE INDEX idx_tolerance_status ON wafer_measurements(tolerance_status);
CREATE INDEX idx_measured_at ON wafer_measurements(measured_at);
```

### 连接池配置

已在 `database.py` 中配置：
- `pool_size=10`: 连接池大小
- `max_overflow=20`: 最大溢出连接数
- `pool_recycle=3600`: 连接回收时间（秒）

根据实际需求调整这些参数。

## 🚀 下一步

配置完成后，你可以：

1. 启动后端服务：`uvicorn main:app --reload`
2. 访问 API 文档：http://localhost:8000/docs
3. 启动前端：`cd frontend && npm run dev`
4. 访问前端应用：http://localhost:5173

祝使用愉快！🎉
