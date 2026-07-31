"""
业务逻辑层 - 适配现有数据库表结构
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple

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
        获取晶圆列表及其统计信息
        
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
                    measurement_count=stats["measurement_count"]
                )
                wafer_list.append(wafer_data)
        
        return wafer_list, total
    
    def create_wafer_with_measurements(self, wafer_no: str, 
                                      measurements: List[Dict]) -> Wafer:
        """
        创建晶圆及其测量数据
        
        参数:
            wafer_no: 晶片号
            measurements: 测量数据列表
            
        返回:
            创建的晶圆对象
        """
        # 检查晶片号是否已存在
        existing = self.wafer_repo.get_wafer_by_no(self.db, wafer_no)
        if existing:
            raise ValueError(f"晶片号 {wafer_no} 已存在")
        
        # 创建晶圆
        wafer_data = {"wafer_no": wafer_no}
        wafer = self.wafer_repo.create_wafer(self.db, wafer_data)
        
        # 添加测量数据
        for measurement in measurements:
            measurement['wafer_no'] = wafer_no
        self.measurement_repo.bulk_create_measurements(self.db, measurements)
        
        return wafer