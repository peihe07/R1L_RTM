from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import requirements, sys2_requirements, testcases
from .db.database import create_tables
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