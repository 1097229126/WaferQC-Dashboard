"""
业务逻辑层 - 适配现有数据库表结构
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple
import pandas as pd
import os

from app.models.models import Wafer, Measurement
from app.repositories.repository import WaferRepository, MeasurementRepository
from app.schemas.schemas import WaferWithStats


class WaferService:
    """晶圆业务服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.wafer_repo = WaferRepository()
        self.measurement_repo = MeasurementRepository()
    
    def get_wafers_with_stats(self, skip: int = 0, limit: int = 100) -> Tuple[List[WaferWithStats], int]:
        """
        获取晶片列表及其统计信息
        
        参数:
            skip: 跳过记录数
            limit: 返回记录数
            
        返回:
            (晶圆列表, 总数)
        """
        wafers, total = self.wafer_repo.get_all_wafers(self.db, skip, limit)
                
        # 为每个晶圆计算统计数据
        wafer_list = []
        for wafer in wafers:
            stats = self.wafer_repo.get_wafer_with_stats(self.db, wafer.wafer_no)
            if stats:
                wafer_data = WaferWithStats(
                    id=stats["wafer"].id,
                    wafer_no=stats["wafer"].wafer_no,
                    original_grade=stats["wafer"].original_grade,
                    concentration_target=stats["wafer"].concentration_target,
                    thickness_target=stats["wafer"].thickness_target,
                    created_at=stats["wafer"].created_at,
                    updated_at=stats["wafer"].updated_at,
                    avg_concentration=stats["avg_concentration"],
                    avg_thickness=stats["avg_thickness"],
                    measurement_count=stats["measurement_count"],
                    # 浓度统计指标（基于设备1）
                    conc_mean=stats.get("conc_mean"),
                    conc_max=stats.get("conc_max"),
                    conc_min=stats.get("conc_min"),
                    conc_uniformity=stats.get("conc_uniformity"),
                    conc_tolerance=stats.get("conc_tolerance"),
                    # 厚度统计指标（基于设备1）
                    thick_mean=stats.get("thick_mean"),
                    thick_max=stats.get("thick_max"),
                    thick_min=stats.get("thick_min"),
                    thick_uniformity=stats.get("thick_uniformity"),
                    thick_tolerance=stats.get("thick_tolerance")
                )
                wafer_list.append(wafer_data)
                
        return wafer_list, total