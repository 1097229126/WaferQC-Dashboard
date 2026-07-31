"""
数据库初始化和种子数据 - 适配现有数据库表结构
"""
from sqlalchemy.orm import Session
from app.core.database import engine, Base, SessionLocal
from app.models.models import Wafer, Measurement
import random


def init_db():
    """初始化数据库表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功！")


def generate_sample_measurements(wafer_no: str, num_points: int = 25) -> list:
    """
    生成示例测量数据用于测试
    
    参数:
        wafer_no: 晶片号
        num_points: 测量点数量（默认25个点）
    
    返回:
        测量数据字典列表
    """
    measurements = []
    
    # 为每个点生成浓度和厚度测量数据
    for point_num in range(1, num_points + 1):
        # 模拟真实的浓度值 (1.5e15 ± 5%)
        base_concentration = 1.5e15
        concentration = base_concentration * (1 + random.uniform(-0.05, 0.05))
        
        # 模拟真实的厚度值 (10.0 μm ± 3%)
        base_thickness = 10.0
        thickness = base_thickness * (1 + random.uniform(-0.03, 0.03))
        
        # 添加浓度测量数据 (measurement_type = 1)
        measurements.append({
            'wafer_no': wafer_no,
            'measurement_type': 1,  # 浓度
            'value': round(concentration, 2)
        })
        
        # 添加厚度测量数据 (measurement_type = 2)
        measurements.append({
            'wafer_no': wafer_no,
            'measurement_type': 2,  # 厚度
            'value': round(thickness, 4)
        })
    
    return measurements


def seed_database():
    """用示例数据填充数据库"""
    db = SessionLocal()
    
    try:
        # 创建示例晶圆
        sample_wafers = [
            "WAFER-2024-001",
            "WAFER-2024-002",
            "WAFER-2024-003",
            "WAFER-2024-004",
            "WAFER-2024-005"
        ]
        
        for wafer_no in sample_wafers:
            # 检查晶圆是否已存在
            existing = db.query(Wafer).filter(
                Wafer.wafer_no == wafer_no
            ).first()
            
            if existing:
                print(f"晶圆 {wafer_no} 已存在，跳过...")
                continue
            
            # 创建晶圆
            wafer = Wafer(
                wafer_no=wafer_no,
                original_grade="A",
                concentration_target=1.5e15,
                thickness_target=10.0
            )
            db.add(wafer)
            db.commit()
            db.refresh(wafer)
            
            print(f"已创建晶圆: {wafer.wafer_no}")
            
            # 生成并添加测量数据
            measurements_data = generate_sample_measurements(wafer.wafer_no)
            measurements = [Measurement(**data) for data in measurements_data]
            db.add_all(measurements)
            db.commit()
            
            print(f"已为晶圆 {wafer.wafer_no} 添加 {len(measurements)} 条测量数据")
        
        print("数据库种子数据填充完成！")
        
    except Exception as e:
        db.rollback()
        print(f"填充数据库时出错: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_database()
