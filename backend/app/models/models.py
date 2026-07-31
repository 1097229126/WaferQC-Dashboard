"""
晶圆检测数据模型 - 适配现有数据库表结构
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Wafer(Base):
    """晶圆模型 - 对应 wafer 表"""
    __tablename__ = "wafer"

    id = Column(Integer, primary_key=True, index=True)
    wafer_no = Column(String(50), unique=True, nullable=False, index=True)  # 晶片号
    original_grade = Column(String(50), nullable=True)  # 原始等级
    concentration_target = Column(Float, nullable=True)  # 浓度目标值
    thickness_target = Column(Float, nullable=True)  # 厚度目标值
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系映射
    measurements = relationship("Measurement", back_populates="wafer")


class Measurement(Base):
    """测量数据模型 - 对应 measurement 表"""
    __tablename__ = "measurement"

    id = Column(Integer, primary_key=True, index=True)
    wafer_no = Column(String(50), ForeignKey("wafer.wafer_no"), nullable=False, index=True)  # 外键关联晶片号
    measurement_type = Column(SmallInteger, nullable=False, index=True)  # 测量类型 (1=浓度, 2=厚度)
    value = Column(Float, nullable=True)  # 测量值
    measured_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系映射
    wafer = relationship("Wafer", back_populates="measurements")

"""晶圆测量数据模型
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class WaferBatch(Base):
    """晶圆批次模型 - 代表一个生产批次"""
    __tablename__ = "wafer_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String(50), unique=True, index=True, nullable=False)
    equipment_id = Column(String(50), index=True, nullable=False)
    production_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系映射
    measurements = relationship("WaferMeasurement", back_populates="batch")


class WaferMeasurement(Base):
    """晶圆测量模型 - 存储25点位测量数据"""
    __tablename__ = "wafer_measurements"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("wafer_batches.id"), nullable=False)
    wafer_position = Column(String(10), nullable=False)  # "A" 或 "B" 代表两片晶圆
    point_number = Column(Integer, nullable=False)  # 1-25 测量点
    
    # 测量值
    concentration = Column(Float, nullable=True)  # 浓度值
    thickness = Column(Float, nullable=True)  # 厚度值
    
    # 计算指标
    uniformity_concentration = Column(Float, nullable=True)
    uniformity_thickness = Column(Float, nullable=True)
    
    # 质量评定
    tolerance_status = Column(String(20), nullable=True)  # "PASS" 或 "FAIL"
    grade = Column(String(10), nullable=True)  # 质量等级
    
    measured_at = Column(DateTime, default=datetime.utcnow)

    # 关系映射
    batch = relationship("WaferBatch", back_populates="measurements")
