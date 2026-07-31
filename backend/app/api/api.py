"""
WaferQC-Dashboard API 路由 - 适配现有数据库表结构
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.schemas import (
    WaferCreate, WaferResponse, WaferWithStats, WaferListResponse,
    MeasurementCreate, MeasurementResponse
)
from app.services.service import WaferService
from app.repositories.repository import WaferRepository, MeasurementRepository

router = APIRouter()


# ==================== 晶圆 API ====================

@router.get("/wafers/", response_model=WaferListResponse)
def get_wafers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """分页获取晶圆列表及其统计信息（平均浓度、平均厚度）"""
    service = WaferService(db)
    wafers, total = service.get_wafers_with_stats(skip, limit)
    return {"total": total, "items": wafers}


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


@router.delete("/wafers/{wafer_no}")
def delete_wafer(wafer_no: str, db: Session = Depends(get_db)):
    """删除晶圆"""
    wafer_repo = WaferRepository()
    success = wafer_repo.delete_wafer(db, wafer_no)
    if not success:
        raise HTTPException(status_code=404, detail="未找到晶圆")
    return {"message": "晶圆删除成功"}


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


# ==================== 批量创建 API ====================

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
