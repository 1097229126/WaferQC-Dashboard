"""
WaferQC-Dashboard API 测试用例 - 适配现有数据库结构
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.core.database import Base, get_db


# 测试数据库配置 - 使用 SQLite 进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_waferqc.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def db_session():
    """为每个测试创建全新的数据库"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_root_endpoint():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_create_wafer(db_session):
    """测试创建晶圆"""
    wafer_data = {
        "wafer_no": "TEST-WAFER-001",
        "original_grade": "A",
        "concentration_target": 1.5e15,
        "thickness_target": 10.0
    }
    
    response = client.post("/api/v1/wafers/", json=wafer_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["wafer_no"] == "TEST-WAFER-001"
    assert "id" in data


def test_get_wafers(db_session):
    """测试获取晶圆列表"""
    # 先创建一个测试晶圆
    wafer_data = {
        "wafer_no": "TEST-WAFER-002",
        "original_grade": "B"
    }
    client.post("/api/v1/wafers/", json=wafer_data)
    
    # 获取所有晶圆
    response = client.get("/api/v1/wafers/")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()


def test_create_measurement(db_session):
    """测试创建测量数据"""
    # 先创建晶圆
    wafer_data = {
        "wafer_no": "TEST-WAFER-003"
    }
    wafer_response = client.post("/api/v1/wafers/", json=wafer_data)
    
    # 创建浓度测量数据
    measurement_data = {
        "wafer_no": "TEST-WAFER-003",
        "measurement_type": 1,  # 浓度
        "value": 1.5e15
    }
    
    response = client.post("/api/v1/measurements/", json=measurement_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["wafer_no"] == "TEST-WAFER-003"
    assert data["measurement_type"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
