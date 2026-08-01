"""
数据访问层仓储 - 适配现有数据库表结构
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from typing import List, Optional, Tuple

from app.models.models import Wafer, Measurement


class WaferRepository:
    """晶圆操作仓储"""
    
    @staticmethod
    def get_all_wafers(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[Wafer], int]:
        """分页获取所有晶圆及其统计信息（按创建时间倒序，新的在前）"""
        # 获取总数
        total = db.query(func.count(Wafer.id)).scalar()
        
        # 获取晶圆列表（按创建时间倒序）
        wafers = db.query(Wafer).order_by(Wafer.created_at.desc()).offset(skip).limit(limit).all()
        
        return wafers, total
    
    @staticmethod
    def get_wafer_by_no(db: Session, wafer_no: str) -> Optional[Wafer]:
        """根据晶片号获取晶圆"""
        return db.query(Wafer).filter(Wafer.wafer_no == wafer_no).first()
    
    @staticmethod
    def get_wafer_with_stats(db: Session, wafer_no: str) -> Optional[dict]:
        """获取晶圆及其平均浓度、平均厚度"""
        wafer = db.query(Wafer).filter(Wafer.wafer_no == wafer_no).first()
        if not wafer:
            return None
        
        # 计算平均浓度 (measurement_type = 1)
        avg_conc_result = db.query(func.avg(Measurement.value)).filter(
            Measurement.wafer_no == wafer_no,
            Measurement.measurement_type == 1
        ).scalar()
        
        # 计算平均厚度 (measurement_type = 2)
        avg_thick_result = db.query(func.avg(Measurement.value)).filter(
            Measurement.wafer_no == wafer_no,
            Measurement.measurement_type == 2
        ).scalar()
        
        # 统计测量次数
        measurement_count = db.query(func.count(Measurement.id)).filter(
            Measurement.wafer_no == wafer_no
        ).scalar()
        
        # ==================== 基于设备1的浓度统计指标 ====================
        # 浓度均值 (仅设备1)
        conc_mean_result = db.query(func.avg(Measurement.value)).filter(
            Measurement.wafer_no == wafer_no,
            Measurement.measurement_type == 1,
            Measurement.measurement_equipment == 1
        ).scalar()
        
        # 浓度最大值 (仅设备1)
        conc_max_result = db.query(func.max(Measurement.value)).filter(
            Measurement.wafer_no == wafer_no,
            Measurement.measurement_type == 1,
            Measurement.measurement_equipment == 1
        ).scalar()
        
        # 浓度最小值 (仅设备1)
        conc_min_result = db.query(func.min(Measurement.value)).filter(
            Measurement.wafer_no == wafer_no,
            Measurement.measurement_type == 1,
            Measurement.measurement_equipment == 1
        ).scalar()
        
        # 浓度均匀性 (仅设备1): STDEVA / AVG * 100%
        conc_uniformity = None
        if conc_mean_result and conc_mean_result != 0:
            conc_stdev_result = db.query(func.stddev_samp(Measurement.value)).filter(
                Measurement.wafer_no == wafer_no,
                Measurement.measurement_type == 1,
                Measurement.measurement_equipment == 1
            ).scalar()
            if conc_stdev_result:
                conc_uniformity = abs(conc_stdev_result / conc_mean_result * 100)
        
        # 浓度 Tolerance% (仅设备1): |AVG - Target| / Target * 100%
        conc_tolerance = None
        if wafer.concentration_target and wafer.concentration_target != 0 and conc_mean_result is not None:
            conc_tolerance = abs((conc_mean_result - wafer.concentration_target) / wafer.concentration_target * 100)
        
        # ==================== 基于设备1的厚度统计指标 ====================
        # 厚度均值 (仅设备1)
        thick_mean_result = db.query(func.avg(Measurement.value)).filter(
            Measurement.wafer_no == wafer_no,
            Measurement.measurement_type == 2,
            Measurement.measurement_equipment == 1
        ).scalar()
        
        # 厚度最大值 (仅设备1)
        thick_max_result = db.query(func.max(Measurement.value)).filter(
            Measurement.wafer_no == wafer_no,
            Measurement.measurement_type == 2,
            Measurement.measurement_equipment == 1
        ).scalar()
        
        # 厚度最小值 (仅设备1)
        thick_min_result = db.query(func.min(Measurement.value)).filter(
            Measurement.wafer_no == wafer_no,
            Measurement.measurement_type == 2,
            Measurement.measurement_equipment == 1
        ).scalar()
        
        # 厚度均匀性 (仅设备1): STDEVA / AVG * 100%
        thick_uniformity = None
        if thick_mean_result and thick_mean_result != 0:
            thick_stdev_result = db.query(func.stddev_samp(Measurement.value)).filter(
                Measurement.wafer_no == wafer_no,
                Measurement.measurement_type == 2,
                Measurement.measurement_equipment == 1
            ).scalar()
            if thick_stdev_result:
                thick_uniformity = abs(thick_stdev_result / thick_mean_result * 100)
        
        # 厚度 Tolerance% (仅设备1): |AVG - Target| / Target * 100%
        thick_tolerance = None
        if wafer.thickness_target and wafer.thickness_target != 0 and thick_mean_result is not None:
            thick_tolerance = abs((thick_mean_result - wafer.thickness_target) / wafer.thickness_target * 100)
        
        return {
            "wafer": wafer,
            "avg_concentration": float(avg_conc_result) if avg_conc_result else None,
            "avg_thickness": float(avg_thick_result) if avg_thick_result else None,
            "measurement_count": measurement_count or 0,
            # 浓度统计指标（基于设备1）
            "conc_mean": float(conc_mean_result) if conc_mean_result else None,
            "conc_max": float(conc_max_result) if conc_max_result else None,
            "conc_min": float(conc_min_result) if conc_min_result else None,
            "conc_uniformity": conc_uniformity,
            "conc_tolerance": conc_tolerance,
            # 厚度统计指标（基于设备1）
            "thick_mean": float(thick_mean_result) if thick_mean_result else None,
            "thick_max": float(thick_max_result) if thick_max_result else None,
            "thick_min": float(thick_min_result) if thick_min_result else None,
            "thick_uniformity": thick_uniformity,
            "thick_tolerance": thick_tolerance
        }
    
    @staticmethod
    def create_wafer(db: Session, wafer_data: dict) -> Wafer:
        """创建新晶圆"""
        wafer = Wafer(**wafer_data)
        db.add(wafer)
        db.commit()
        db.refresh(wafer)
        return wafer
    
    @staticmethod
    def delete_wafer(db: Session, wafer_no: str) -> bool:
        """删除晶圆（级联删除相关测量数据）"""
        wafer = db.query(Wafer).filter(Wafer.wafer_no == wafer_no).first()
        if wafer:
            # 先删除相关的测量数据
            db.query(Measurement).filter(Measurement.wafer_no == wafer_no).delete()
            # 再删除晶圆
            db.delete(wafer)
            db.commit()
            return True
        return False
    
    @staticmethod
    def batch_delete_wafers(db: Session, wafer_nos: List[str]) -> int:
        """批量删除晶圆（级联删除相关测量数据）
        
        参数:
            db: 数据库会话
            wafer_nos: 晶片号列表
            
        返回:
            成功删除的晶片数量
        """
        if not wafer_nos:
            return 0
        
        deleted_count = 0
        for wafer_no in wafer_nos:
            try:
                # 先删除相关的测量数据
                db.query(Measurement).filter(Measurement.wafer_no == wafer_no).delete()
                # 再删除晶圆
                wafer = db.query(Wafer).filter(Wafer.wafer_no == wafer_no).first()
                if wafer:
                    db.delete(wafer)
                    deleted_count += 1
            except Exception as e:
                print(f"删除晶片 {wafer_no} 失败: {str(e)}")
                continue
        
        # 提交事务
        db.commit()
        return deleted_count


class MeasurementRepository:
    """测量数据操作仓储"""
    
    @staticmethod
    def create_measurement(db: Session, measurement_data: dict) -> Measurement:
        """创建测量数据"""
        measurement = Measurement(**measurement_data)
        db.add(measurement)
        db.commit()
        db.refresh(measurement)
        return measurement
    
    @staticmethod
    def get_measurements_by_wafer(db: Session, wafer_no: str) -> List[Measurement]:
        """获取指定晶圆的测量数据（按测量设备、测量类型、测量点位排序）"""
        # 使用 CASE 表达式处理 NULL 值排序
        from sqlalchemy import case
        
        return db.query(Measurement).filter(
            Measurement.wafer_no == wafer_no
        ).order_by(
            Measurement.measurement_equipment.asc(),
            Measurement.measurement_type.asc(),
            case(
                (Measurement.point_number.is_(None), 1),
                else_=0
            ),
            Measurement.point_number.asc()
        ).all()
    
    @staticmethod
    def bulk_create_measurements(db: Session, measurements: List[dict]) -> List[Measurement]:
        """批量创建测量数据"""
        db_measurements = [Measurement(**data) for data in measurements]
        db.add_all(db_measurements)
        db.commit()
        for measurement in db_measurements:
            db.refresh(measurement)
        return db_measurements
