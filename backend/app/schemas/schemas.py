"""
Pydantic 数据验证模式 - 适配现有数据库表结构
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== 晶圆相关模式 ====================

class WaferBase(BaseModel):
    """晶圆基础模式"""
    wafer_no: str = Field(..., description="晶片号")
    original_grade: Optional[str] = Field(None, description="原始等级")
    concentration_target: Optional[float] = Field(None, description="浓度目标值")
    thickness_target: Optional[float] = Field(None, description="厚度目标值")


class WaferCreate(WaferBase):
    """创建晶圆模式"""
    pass


class WaferResponse(WaferBase):
    """晶圆响应模式"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WaferWithStats(WaferResponse):
    """带统计信息的晶圆响应"""
    avg_concentration: Optional[float] = Field(None, description="平均浓度")
    avg_thickness: Optional[float] = Field(None, description="平均厚度")
    measurement_count: Optional[int] = Field(0, description="测量次数")
    
    # 浓度统计指标（基于设备1）
    conc_mean: Optional[float] = Field(None, description="浓度均值")
    conc_max: Optional[float] = Field(None, description="浓度最大值")
    conc_min: Optional[float] = Field(None, description="浓度最小值")
    conc_uniformity: Optional[float] = Field(None, description="浓度均匀性 (%)")
    conc_tolerance: Optional[float] = Field(None, description="浓度 Tolerance%")
    
    # 厚度统计指标（基于设备1）
    thick_mean: Optional[float] = Field(None, description="厚度均值")
    thick_max: Optional[float] = Field(None, description="厚度最大值")
    thick_min: Optional[float] = Field(None, description="厚度最小值")
    thick_uniformity: Optional[float] = Field(None, description="厚度均匀性 (%)")
    thick_tolerance: Optional[float] = Field(None, description="厚度 Tolerance%")


# ==================== 测量数据相关模式 ====================

class MeasurementBase(BaseModel):
    """测量数据基础模式"""
    wafer_no: str = Field(..., description="晶片号")
    measurement_type: int = Field(..., description="测量类型 (1=浓度, 2=厚度)")
    point_number: Optional[int] = Field(None, description="测量点位 (1-25)")
    value: Optional[float] = Field(None, description="测量值")
    measurement_equipment: Optional[int] = Field(1, description="测量设备")


class MeasurementCreate(MeasurementBase):
    """创建测量数据模式"""
    pass


class MeasurementResponse(MeasurementBase):
    """测量数据响应模式"""
    id: int
    measured_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 列表响应模式 ====================

class WaferListResponse(BaseModel):
    """晶圆列表响应"""
    total: int = Field(..., description="总数")
    items: List[WaferWithStats] = Field(..., description="晶圆列表")
