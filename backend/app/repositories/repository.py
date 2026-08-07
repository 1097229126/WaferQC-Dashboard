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
    def get_all_wafers(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        sort_by: str = None,
        sort_order: str = None,
        search: str = None
    ) -> Tuple[List[Wafer], int]:
        """分页获取所有晶圆及其统计信息（按创建时间倒序，新的在前）
        
        参数:
            skip: 跳过记录数
            limit: 返回记录数
            sort_by: 排序字段 (wafer_no, conc_mean, conc_max, conc_min, conc_uniformity, conc_tolerance, thick_mean, thick_max, thick_min, thick_uniformity, thick_tolerance)
            sort_order: 排序方向 (asc=正序, desc=倒序)
            search: 搜索关键字（晶片号模糊匹配）
        """
        from sqlalchemy import case
        
        # 构建查询
        query = db.query(Wafer)
        
        # 添加搜索条件（晶片号模糊匹配）
        if search and search.strip():
            search_keyword = search.strip()
            query = query.filter(Wafer.wafer_no.like(f'%{search_keyword}%'))
            
            # 如果有用户指定的排序，使用用户排序；否则按相似度排序
            if not (sort_by and sort_order):
                # 相似度排序：优先匹配开头，其次匹配中间，最后匹配结尾
                # 使用 CASE 语句实现相似度评分
                similarity_score = case(
                    (Wafer.wafer_no == search_keyword, 0),           # 完全匹配：优先级最高
                    (Wafer.wafer_no.startswith(search_keyword), 1),  # 开头匹配：优先级次高
                    (Wafer.wafer_no.endswith(search_keyword), 2),    # 结尾匹配：优先级中等
                    else_=3                                           # 中间匹配：优先级最低
                )
                query = query.order_by(similarity_score.asc(), Wafer.wafer_no.asc())
        
        # 获取总数
        total = query.count()
        
        # 确定排序方式
        if sort_by and sort_order:
            # 动态排序
            order_column = getattr(Wafer, sort_by, Wafer.created_at)
            if sort_order == 'desc':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        elif not (search and search.strip()):
            # 没有搜索条件且没有指定排序时，默认按创建时间倒序
            query = query.order_by(Wafer.created_at.desc())
        # 注意：有搜索条件但没有指定排序时，已经在上面添加了相似度排序
        
        # 获取晶圆列表
        wafers = query.offset(skip).limit(limit).all()
        
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
        
        # 浓度 Tolerance% (仅设备1): MAX(ABS(MAX-Target)/Target, ABS(MIN-Target)/Target) × 100%
        conc_tolerance = None
        if conc_max_result is not None and conc_min_result is not None and wafer.concentration_target and wafer.concentration_target != 0:
            max_deviation = abs(conc_max_result - wafer.concentration_target) / abs(wafer.concentration_target)
            min_deviation = abs(conc_min_result - wafer.concentration_target) / abs(wafer.concentration_target)
            conc_tolerance = max(max_deviation, min_deviation) * 100
        
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
        
        # 厚度 Tolerance% (仅设备1): MAX(ABS(MAX-Target)/Target, ABS(MIN-Target)/Target) × 100%
        thick_tolerance = None
        if thick_max_result is not None and thick_min_result is not None and wafer.thickness_target and wafer.thickness_target != 0:
            max_deviation = abs(thick_max_result - wafer.thickness_target) / abs(wafer.thickness_target)
            min_deviation = abs(thick_min_result - wafer.thickness_target) / abs(wafer.thickness_target)
            thick_tolerance = max(max_deviation, min_deviation) * 100

        # ==================== 一致性指标计算（设备1 vs 设备2）====================
        # 浓度点位一致性：对25个浓度点位（P1-P25），计算 ((设备1.Pi - 设备2.Pi) - 1) × 100%，然后取均值
        conc_consistency = None
        try:
            # 获取设备1的浓度数据（P1-P25）
            eq1_conc = db.query(Measurement.point_number, Measurement.value).filter(
                Measurement.wafer_no == wafer_no,
                Measurement.measurement_type == 1,
                Measurement.measurement_equipment == 1,
                Measurement.point_number.isnot(None)
            ).all()
            
            # 获取设备2的浓度数据（P1-P25）
            eq2_conc = db.query(Measurement.point_number, Measurement.value).filter(
                Measurement.wafer_no == wafer_no,
                Measurement.measurement_type == 1,
                Measurement.measurement_equipment == 2,
                Measurement.point_number.isnot(None)
            ).all()
            
            # 转换为字典便于查找
            eq1_dict = {row.point_number: row.value for row in eq1_conc}
            eq2_dict = {row.point_number: row.value for row in eq2_conc}
            
            # 计算每个点位的一致性
            consistency_values = []
            for point_num in range(1, 26):  # P1-P25
                if point_num in eq1_dict and point_num in eq2_dict:
                    val1 = eq1_dict[point_num]
                    val2 = eq2_dict[point_num]
                    # 公式：点位一致性 = ((设备1.Pi - 设备2.Pi) - 1) × 100%
                    consistency = ((val1 - val2) - 1) * 100
                    consistency_values.append(consistency)
            
            # 计算均值
            if consistency_values:
                conc_consistency = sum(consistency_values) / len(consistency_values)
        except Exception as e:
            print(f"计算浓度点位一致性失败: {str(e)}")
        
        # 厚度点位一致性：对25个厚度点位（T1-T25），计算 ((设备1.Ti - 设备2.Ti) - 1) × 100%，然后取均值
        thick_consistency = None
        try:
            # 获取设备1的厚度数据（T1-T25）
            eq1_thick = db.query(Measurement.point_number, Measurement.value).filter(
                Measurement.wafer_no == wafer_no,
                Measurement.measurement_type == 2,
                Measurement.measurement_equipment == 1,
                Measurement.point_number.isnot(None)
            ).all()
            
            # 获取设备2的厚度数据（T1-T25）
            eq2_thick = db.query(Measurement.point_number, Measurement.value).filter(
                Measurement.wafer_no == wafer_no,
                Measurement.measurement_type == 2,
                Measurement.measurement_equipment == 2,
                Measurement.point_number.isnot(None)
            ).all()
            
            # 转换为字典便于查找
            eq1_dict = {row.point_number: row.value for row in eq1_thick}
            eq2_dict = {row.point_number: row.value for row in eq2_thick}
            
            # 计算每个点位的一致性
            consistency_values = []
            for point_num in range(1, 26):  # T1-T25
                if point_num in eq1_dict and point_num in eq2_dict:
                    val1 = eq1_dict[point_num]
                    val2 = eq2_dict[point_num]
                    # 公式：点位一致性 = ((设备1.Ti - 设备2.Ti) - 1) × 100%
                    consistency = ((val1 - val2) - 1) * 100
                    consistency_values.append(consistency)
            
            # 计算均值
            if consistency_values:
                thick_consistency = sum(consistency_values) / len(consistency_values)
        except Exception as e:
            print(f"计算厚度点位一致性失败: {str(e)}")
        
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
            "conc_consistency": conc_consistency,
            # 厚度统计指标（基于设备1）
            "thick_mean": float(thick_mean_result) if thick_mean_result else None,
            "thick_max": float(thick_max_result) if thick_max_result else None,
            "thick_min": float(thick_min_result) if thick_min_result else None,
            "thick_uniformity": thick_uniformity,
            "thick_tolerance": thick_tolerance,
            "thick_consistency": thick_consistency
        }
    
    @staticmethod
    def create_wafer(db: Session, wafer_data: dict) -> Wafer:
        """创建新晶圆"""
        wafer = Wafer(**wafer_data)
        db.add(wafer)
        db.commit()
        db.refresh(wafer)
        return wafer


class MeasurementRepository:
    """测量数据仓库"""
    
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
        """获取指定晶圆的所有测量数据"""
        return db.query(Measurement).filter(
            Measurement.wafer_no == wafer_no
        ).all()
