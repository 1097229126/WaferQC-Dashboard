"""
数据库迁移脚本 - 添加测量批次字段
"""
from sqlalchemy import text
from app.core.database import engine


def add_measurement_batch_column():
    """为 wafer_measurements 表添加 measurement_batch 字段"""
    
    print("开始执行数据库迁移...")
    
    try:
        # 创建数据库连接
        with engine.connect() as conn:
            # 检查字段是否已存在
            check_column_sql = """
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'wafer_measurements'
                AND COLUMN_NAME = 'measurement_batch'
            """
            result = conn.execute(text(check_column_sql))
            column_exists = result.scalar() > 0
            
            if column_exists:
                print("✓ measurement_batch 字段已存在，跳过迁移")
                return
            
            # 添加新字段，默认值为1
            alter_sql = """
                ALTER TABLE wafer_measurements 
                ADD COLUMN measurement_batch INTEGER NOT NULL DEFAULT 1
            """
            conn.execute(text(alter_sql))
            conn.commit()
            
            print("✓ 成功添加 measurement_batch 字段（默认值：1）")
            print("✓ 数据库迁移完成！")
            
    except Exception as e:
        print(f"✗ 数据库迁移失败: {e}")
        raise


if __name__ == "__main__":
    add_measurement_batch_column()
