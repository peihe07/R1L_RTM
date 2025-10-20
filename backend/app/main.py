from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .api import requirements, sys2_requirements, testcases
from .db.database import create_tables, engine
# 導入所有模型以便 create_tables 知道它們
from .models import cfts_db, sys2_requirement, testcase
import os

app = FastAPI(title="Requirement Test Management API")

# 啟動時建立資料庫表
@app.on_event("startup")
async def startup_event():
    create_tables()

# 從環境變數讀取 CORS 設定
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3001")
allowed_origins = cors_origins.split(",") if cors_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(requirements.router)
app.include_router(requirements.req_router)
app.include_router(sys2_requirements.router)
app.include_router(testcases.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Requirement Test Management API"}


@app.get("/health", tags=["Health"])
async def health_check():
    """健康檢查端點 - 檢查 API 和資料庫連接狀態"""
    from sqlalchemy import text
    try:
        # 測試資料庫連接
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "database": "connected",
                "message": "All systems operational"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.get("/readiness", tags=["Health"])
async def readiness_check():
    """就緒檢查端點 - 檢查服務是否準備好接收請求"""
    from sqlalchemy import text
    try:
        # 測試資料庫連接
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ready"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "error": str(e)}
        )