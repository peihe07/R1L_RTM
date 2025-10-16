# CFTS 需求測試管理系統 - 專案配置說明

本文件記錄了專案的所有重要配置設定。

## 目錄
- [環境配置](#環境配置)
- [Docker 部署配置](#docker-部署配置)
- [Git 配置](#git-配置)
- [依賴包說明](#依賴包說明)
- [快速啟動](#快速啟動)
- [常見問題](#常見問題)

---

## 環境配置

### 後端環境變數 (.env)

**位置**: `/backend/.env`

```env
# PostgreSQL Database Configuration
# For local development (without Docker)
# DATABASE_URL=postgresql://postgres:password@localhost:5432/requirement_test_db

# For Docker Compose deployment
DATABASE_URL=postgresql://postgres:password@db:5432/requirement_test_db

# FastAPI Secret Key - IMPORTANT: Change this in production!
SECRET_KEY=your-secret-key-here-please-change-in-production

# Application Settings
DEBUG=True
```

**重要提示**:
- 預設配置為 Docker Compose 部署模式
- 本地開發時請取消註解 localhost 配置行，並註解 Docker 配置行
- 生產環境務必更改 `SECRET_KEY`

### 前端環境變數 (.env)

**位置**: `/frontend/.env`

```env
# API Base URL
# For local development (backend running on localhost:8000)
VITE_API_BASE_URL=http://localhost:8000

# For Docker Compose deployment (uncomment the line below)
# VITE_API_BASE_URL=http://backend:8000
```

**重要提示**:
- 前端透過此變數連接後端 API
- Docker 部署時使用容器內部網路 (backend:8000)
- 本地開發時使用 localhost:8000

---

## Docker 部署配置

### docker-compose.yml 概要

**位置**: `/docker-compose.yml`

#### 服務架構

| 服務 | 映像 | 端口映射 | 說明 |
|------|------|----------|------|
| db | postgres:15 | 5432:5432 | PostgreSQL 資料庫 |
| backend | 自定義構建 | 8000:8000 | FastAPI 後端服務 |
| frontend | node:18-alpine | 3000:3000 | Vue.js 前端服務 |

#### 資料持久化

- `postgres_data`: PostgreSQL 資料卷
- `./data/cfts_excel`: Excel 資料檔案 (唯讀掛載)

#### 健康檢查

資料庫服務配置了健康檢查:
- 每 5 秒檢查一次
- 超時時間 5 秒
- 重試 5 次

後端服務等待資料庫健康後才啟動。

---

## Git 配置

### .gitignore 重點項目

```gitignore
# 環境變數 (已配置,不會提交到版本控制)
.env
.env.local
.env.*.local

# Python 虛擬環境
venv/
.venv/
backend/venv/
backend/.venv/

# Node.js 依賴
node_modules/

# 資料庫文件
*.db
*.sqlite
*.sqlite3

# IDE 配置
.vscode/*
!.vscode/settings.json
.idea/

# 作業系統文件
.DS_Store
```

### Git 倉庫狀態

- Git 倉庫已初始化
- `.gitignore` 已配置完成
- 環境變數文件 (`.env`) 已正確忽略

---

## 依賴包說明

### 後端依賴 (Python)

**位置**: `/backend/requirements.txt`

#### 核心框架
- `fastapi==0.118.0` - 現代 Web 框架
- `uvicorn==0.37.0` - ASGI 伺服器
- `pydantic==2.11.10` - 資料驗證
- `pydantic-settings==2.7.1` - 設定管理

#### 資料庫相關
- `sqlalchemy==2.0.43` - ORM 框架
- `psycopg2-binary==2.9.10` - PostgreSQL 驅動
- `alembic==1.12.1` - 資料庫遷移工具

#### 資料處理
- `pandas==2.3.3` - 資料處理
- `openpyxl==3.1.5` - Excel 讀取

#### 其他工具
- `python-dotenv==1.0.0` - 環境變數管理
- `python-multipart` - 表單資料支援

**安裝命令**:
```bash
cd backend
pip install -r requirements.txt
```

### 前端依賴 (Node.js)

**位置**: `/frontend/package.json`

#### 核心依賴
- `vue@^3.3.8` - Vue.js 3 框架
- `axios@^1.6.2` - HTTP 客戶端

#### 開發依賴
- `@vitejs/plugin-vue@^4.5.0` - Vite 的 Vue 插件
- `vite@^5.0.0` - 前端構建工具

**安裝命令**:
```bash
cd frontend
npm install
```

**依賴狀態**:
- ✅ frontend/node_modules 已存在
- 前端依賴已正確安裝

---

## 快速啟動

### 方式一: Docker Compose (推薦)

```bash
# 使用啟動腳本
./start-docker.sh

# 或手動啟動
docker-compose up --build
```

**訪問地址**:
- 前端界面: http://localhost:3000
- 後端 API: http://localhost:8000
- API 文檔: http://localhost:8000/docs

### 方式二: 本地開發

#### 1. 啟動資料庫
```bash
docker-compose up db -d
```

#### 2. 修改環境變數
**backend/.env**:
```env
# 使用 localhost 而非 db
DATABASE_URL=postgresql://postgres:password@localhost:5432/requirement_test_db
```

**frontend/.env**:
```env
# 使用 localhost
VITE_API_BASE_URL=http://localhost:8000
```

#### 3. 啟動後端
```bash
cd backend
# 首次運行需要載入資料
python load_excel_to_db.py
# 啟動後端服務
uvicorn app.main:app --reload
```

#### 4. 啟動前端
```bash
cd frontend
npm run dev
```

---

## 常見問題

### Q1: Docker 啟動失敗?

**檢查項目**:
1. Docker 是否正在運行
2. 端口 3000, 8000, 5432 是否被佔用
3. Docker Compose 版本是否符合要求

**解決方案**:
```bash
# 停止所有容器
docker-compose down

# 清理並重新構建
docker-compose up --build --force-recreate
```

### Q2: 資料庫連接失敗?

**檢查項目**:
1. `.env` 檔案中的 `DATABASE_URL` 是否正確
2. 資料庫容器是否健康運行
3. 本地開發與 Docker 部署的配置是否對應

**調試命令**:
```bash
# 檢查資料庫容器狀態
docker-compose ps db

# 檢查資料庫日誌
docker-compose logs db

# 進入資料庫容器
docker-compose exec db psql -U postgres -d requirement_test_db
```

### Q3: 前端無法連接後端?

**檢查項目**:
1. 後端服務是否正常運行 (http://localhost:8000/docs)
2. `VITE_API_BASE_URL` 是否設置正確
3. 瀏覽器控制台是否有 CORS 錯誤

**解決方案**:
- Docker 部署: 確保使用 `http://localhost:8000`
- 檢查後端 CORS 設定 (`backend/app/main.py`)

### Q4: 依賴包安裝錯誤?

**Python 依賴**:
```bash
# 使用虛擬環境
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Node.js 依賴**:
```bash
cd frontend
# 清除 npm 快取
npm cache clean --force
# 刪除 node_modules 並重新安裝
rm -rf node_modules package-lock.json
npm install
```

### Q5: Excel 資料未載入?

**檢查項目**:
1. `/data/cfts_excel/` 目錄是否存在且包含 Excel 檔案
2. Excel 檔案格式是否正確

**手動載入資料**:
```bash
# 進入後端目錄
cd backend

# 重建資料表
python recreate_tables.py

# 批次匯入
python batch_import_excel.py

# 或使用載入腳本
python load_excel_to_db.py
```

---

## 專案結構概覽

```
R1L_RTM/
├── backend/
│   ├── .env                 # ✅ 已配置
│   ├── .env.example         # 環境變數範例
│   ├── requirements.txt     # Python 依賴
│   └── app/                 # FastAPI 應用程式
│
├── frontend/
│   ├── .env                 # ✅ 已配置
│   ├── .env.example         # 環境變數範例
│   ├── package.json         # Node.js 依賴
│   └── src/                 # Vue.js 應用程式
│
├── docker/
│   ├── backend/Dockerfile   # ✅ 已驗證
│   └── frontend/Dockerfile  # ✅ 已驗證
│
├── docker-compose.yml       # ✅ 已驗證
├── start-docker.sh          # ✅ 已設置執行權限
├── .gitignore               # ✅ 已配置
└── PROJECT_SETUP.md         # 本文件
```

---

## 配置檢查清單

- [x] 後端 `.env` 文件已創建並配置
- [x] 前端 `.env` 文件已創建並配置
- [x] Docker Compose 配置已驗證
- [x] Docker Dockerfile 配置正確
- [x] Git 倉庫已初始化
- [x] `.gitignore` 已正確配置
- [x] 環境變數文件不會被提交到版本控制
- [x] 前端依賴包已安裝 (node_modules 存在)
- [x] `start-docker.sh` 具有執行權限
- [x] 資料庫連接配置已驗證

---

## 版本資訊

- **Python**: 3.11
- **Node.js**: 18
- **PostgreSQL**: 15
- **FastAPI**: 0.118.0
- **Vue.js**: 3.3.8
- **Vite**: 5.0.0

---

## 更新日誌

### 2025-10-16
- ✅ 初始化專案配置
- ✅ 創建後端和前端環境變數文件
- ✅ 驗證 Docker 配置
- ✅ 初始化 Git 倉庫
- ✅ 配置 .gitignore
- ✅ 創建專案配置說明文件

---

## 聯絡資訊

如有問題,請參考:
- **主要文檔**: README.md
- **開發日誌**: DEVELOPMENT_LOG.md
- **Docker 指南**: DOCKER_GUIDE.md
- **後端文檔**: backend/README.md
- **前端文檔**: frontend/README.md

---

**最後更新**: 2025-10-16
**文件版本**: 1.0
