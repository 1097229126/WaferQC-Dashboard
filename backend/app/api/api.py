"""
WaferQC-Dashboard API 路由 - 适配现有数据库表结构
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict
import tempfile
import os

from app.core.database import get_db
from app.models.models import Wafer, Measurement
from app.schemas.schemas import (
    WaferCreate, WaferResponse, WaferWithStats, WaferListResponse,
    MeasurementCreate, MeasurementResponse
)
from app.services.service import WaferService
from app.repositories.repository import WaferRepository, MeasurementRepository

router = APIRouter()


# ==================== 晶圆 API ====================

@router.get("/wafers/", response_model=WaferListResponse)
def get_wafers(
    skip: int = 0, 
    limit: int = 100, 
    sort_by: str = None,
    sort_order: str = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    """分页获取晶圆列表及其统计信息（平均浓度、平均厚度）
    
    参数:
        skip: 跳过的记录数
        limit: 每页数量
        sort_by: 排序字段 (wafer_no, conc_mean, conc_max, conc_min, conc_uniformity, conc_tolerance, thick_mean, thick_max, thick_min, thick_uniformity, thick_tolerance)
        sort_order: 排序方向 (asc=正序, desc=倒序)
        search: 搜索关键字（晶片号模糊匹配）
    """
    service = WaferService(db)
    wafers, total = service.get_wafers_with_stats(skip, limit, sort_by, sort_order, search)
    return {"total": total, "items": wafers}


@router.post("/wafers/", response_model=WaferResponse, status_code=201)
def create_wafer(wafer: WaferCreate, db: Session = Depends(get_db)):
    """创建新晶圆"""
    wafer_repo = WaferRepository()
    
    # 检查晶片号是否已存在
    existing = wafer_repo.get_wafer_by_no(db, wafer.wafer_no)
    if existing:
        raise HTTPException(status_code=400, detail="晶片号已存在")
    
    wafer_data = wafer.model_dump()
    return wafer_repo.create_wafer(db, wafer_data)


@router.post("/wafers/batch-delete")
def batch_delete_wafers(request: dict, db: Session = Depends(get_db)):
    """批量删除晶圆"""
    wafer_nos = request.get("wafer_nos", [])
    if not wafer_nos:
        raise HTTPException(status_code=400, detail="请选择要删除的晶圆")
    
    wafer_repo = WaferRepository()
    deleted_count = wafer_repo.batch_delete_wafers(db, wafer_nos)
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="未找到任何晶圆")
    
    return {"message": f"成功删除 {deleted_count} 个晶圆", "deleted_count": deleted_count}


@router.post("/wafers/import-excel")
async def import_wafers_from_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    从Excel文件导入晶片数据
    
    文件格式要求：
    - 包含两个Sheet："数据1"（设备1）和"数据2"（设备2）
    - 双层表头结构
    - 前4列为晶片信息，后续为测量点位数据
    """
    # 验证文件类型
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="仅支持 .xlsx 格式的Excel文件")
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        tmp_file.write(await file.read())
        tmp_file_path = tmp_file.name
    
    try:
        service = WaferService(db)
        result = service.import_wafers_from_excel(tmp_file_path)
        
        return {
            "success": True,
            "message": result["message"],
            "imported_wafers": result["imported_wafers"],
            "skipped_wafers": result["skipped_wafers"],
            "imported_measurements": result["imported_measurements"]
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
    finally:
        # 清理临时文件
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)


@router.get("/wafers/import-template", summary="下载Excel导入模板")
async def download_import_template():
    """
    下载Excel导入模板
    
    返回一个包含示例数据的Excel模板文件，包含：
    - Sheet1（数据1）：设备1的测量数据模板
    - Sheet2（数据2）：设备2的测量数据模板
    - 统一的列名：晶片号、原始等级、浓度目标、厚度目标
    """
    import tempfile
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        tmp_file_path = tmp_file.name
    
    try:
        service = WaferService(None)  # 不需要数据库连接
        template_path = service.generate_import_template(tmp_file_path)
        
        # 读取文件并返回
        from fastapi.responses import FileResponse
        
        return FileResponse(
            path=template_path,
            filename="晶片数据导入模板.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        # 清理临时文件
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        raise HTTPException(status_code=500, detail=f"生成模板失败: {str(e)}")


@router.post("/wafers/bulk-create", response_model=WaferResponse, status_code=201)
def create_wafer_with_measurements(
    wafer_no: str,
    measurements: List[MeasurementCreate],
    db: Session = Depends(get_db)
):
    """一次性创建晶圆及其所有测量数据"""
    service = WaferService(db)
    
    measurements_data = [m.model_dump() for m in measurements]
    try:
        wafer = service.create_wafer_with_measurements(wafer_no, measurements_data)
        return wafer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/wafers/{wafer_no}")
def delete_wafer(wafer_no: str, db: Session = Depends(get_db)):
    """删除晶圆"""
    wafer_repo = WaferRepository()
    success = wafer_repo.delete_wafer(db, wafer_no)
    if not success:
        raise HTTPException(status_code=404, detail="未找到晶圆")
    return {"message": "晶圆删除成功"}


@router.get("/wafers/{wafer_no}", response_model=WaferWithStats)
def get_wafer(wafer_no: str, db: Session = Depends(get_db)):
    """根据晶片号获取晶圆详情及统计信息"""
    service = WaferService(db)
    stats = service.wafer_repo.get_wafer_with_stats(db, wafer_no)
    if not stats:
        raise HTTPException(status_code=404, detail=f"未找到晶片号: {wafer_no}")
    
    wafer = stats["wafer"]
    return WaferWithStats(
        id=wafer.id,
        wafer_no=wafer.wafer_no,
        original_grade=wafer.original_grade,
        concentration_target=wafer.concentration_target,
        thickness_target=wafer.thickness_target,
        created_at=wafer.created_at,
        updated_at=wafer.updated_at,
        avg_concentration=stats["avg_concentration"],
        avg_thickness=stats["avg_thickness"],
        measurement_count=stats["measurement_count"]
    )


# ==================== 可视化看板 API ====================

@router.get("/dashboard/grade-distribution")
def get_grade_distribution(db: Session = Depends(get_db)):
    """获取等级分布统计数据（用于饼图）
    
    返回:
    - 浓度等级分布: {A: count, B: count, 不合格: count}
    - 厚度等级分布: {A: count, B: count, 不合格: count}
    - 综合等级分布: {A: count, B: count, 不合格: count}
    """
    service = WaferService(db)
    
    # 获取所有晶片的统计信息
    all_wafers, total = service.get_wafers_with_stats(skip=0, limit=10000)
    
    # 初始化计数器
    conc_dist = {"A": 0, "B": 0, "不合格": 0}
    thick_dist = {"A": 0, "B": 0, "不合格": 0}
    overall_dist = {"A": 0, "B": 0, "不合格": 0}
    
    # 统计各等级数量
    for wafer in all_wafers:
        if wafer.conc_grade:
            if wafer.conc_grade in conc_dist:
                conc_dist[wafer.conc_grade] += 1
        
        if wafer.thick_grade:
            if wafer.thick_grade in thick_dist:
                thick_dist[wafer.thick_grade] += 1
        
        if wafer.overall_grade:
            if wafer.overall_grade in overall_dist:
                overall_dist[wafer.overall_grade] += 1
    
    return {
        "conc_grade_distribution": conc_dist,
        "thick_grade_distribution": thick_dist,
        "overall_grade_distribution": overall_dist,
        "total_wafers": len(all_wafers)
    }


@router.get("/dashboard/wafer-details")
def get_wafer_details_for_charts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取晶片详细信息（用于折线图）
    
    参数:
        skip: 跳过记录数（用于分页，每页50个晶片）
        limit: 每页数量（默认50）
    
    返回:
        包含每个晶片的详细测量数据，按点位分组
    """
    from sqlalchemy import text
    
    # 获取所有晶片列表（按创建时间排序）
    wafers_query = db.query(Wafer).order_by(Wafer.created_at.asc())
    total = wafers_query.count()
    wafers = wafers_query.offset(skip).limit(limit).all()
    
    result = []
    
    for wafer in wafers:
        # 获取该晶片的所有测量数据
        measurements = db.query(Measurement).filter(
            Measurement.wafer_no == wafer.wafer_no
        ).order_by(
            Measurement.measurement_equipment.asc(),
            Measurement.measurement_type.asc(),
            Measurement.point_number.asc()
        ).all()
        
        # 组织数据结构
        wafer_data = {
            "wafer_no": wafer.wafer_no,
            "concentration_target": wafer.concentration_target,
            "thickness_target": wafer.thickness_target,
            "measurements": []
        }
        
        for m in measurements:
            wafer_data["measurements"].append({
                "measurement_type": m.measurement_type,
                "point_number": m.point_number,
                "value": m.value,
                "measurement_equipment": m.measurement_equipment
            })
        
        result.append(wafer_data)
    
    return {
        "total": total,
        "current_page": (skip // limit) + 1,
        "total_pages": (total + limit - 1) // limit,
        "items": result
    }


# ==================== 测量数据 API ====================

@router.post("/measurements/", response_model=MeasurementResponse, status_code=201)
def create_measurement(measurement: MeasurementCreate, db: Session = Depends(get_db)):
    """创建测量数据"""
    measurement_repo = MeasurementRepository()
    
    # 验证晶圆是否存在
    wafer_repo = WaferRepository()
    wafer = wafer_repo.get_wafer_by_no(db, measurement.wafer_no)
    if not wafer:
        raise HTTPException(status_code=404, detail="未找到对应的晶圆")
    
    measurement_data = measurement.model_dump()
    return measurement_repo.create_measurement(db, measurement_data)


@router.get("/wafers/{wafer_no}/measurements", response_model=List[MeasurementResponse])
def get_wafer_measurements(wafer_no: str, db: Session = Depends(get_db)):
    """获取指定晶圆的所有测量数据"""
    measurement_repo = MeasurementRepository()
    return measurement_repo.get_measurements_by_wafer(db, wafer_no)

