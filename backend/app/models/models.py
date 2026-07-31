"""
晶圆检测数据模型 - 适配现有数据库表结构
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta

from app.core.database import Base

# 定义中国时区（UTC+8）
CHINA_TZ = timezone(timedelta(hours=8))


def china_now():
    """获取中国时区的当前时间"""
    return datetime.now(CHINA_TZ)


class Wafer(Base):
    """晶圆模型 - 对应 wafer 表"""
    __tablename__ = "wafer"

    id = Column(Integer, primary_key=True, index=True)
    wafer_no = Column(String(50), unique=True, nullable=False, index=True)  # 晶片号
    original_grade = Column(String(50), nullable=True)  # 原始等级
    concentration_target = Column(Float, nullable=True)  # 浓度目标值
    thickness_target = Column(Float, nullable=True)  # 厚度目标值
    created_at = Column(DateTime, default=china_now)
    updated_at = Column(DateTime, default=china_now, onupdate=china_now)

    # 关系映射
    measurements = relationship("Measurement", back_populates="wafer")


class Measurement(Base):
    """测量数据模型 - 对应 measurement 表"""
    __tablename__ = "measurement"

    id = Column(Integer, primary_key=True, index=True)
    wafer_no = Column(String(50), ForeignKey("wafer.wafer_no"), nullable=False, index=True)  # 外键关联晶片号
    measurement_type = Column(SmallInteger, nullable=False, index=True)  # 测量类型 (1=浓度, 2=厚度)
    point_number = Column(Integer, nullable=True, index=True)  # 测量点位 (1-25)
    value = Column(Float, nullable=True)  # 测量值
    measurement_equipment = Column(Integer, nullable=True, default=1)  # 测量设备
    measured_at = Column(DateTime, default=china_now)
    created_at = Column(DateTime, default=china_now)

    # 关系映射
    wafer = relationship("Wafer", back_populates="measurements")

