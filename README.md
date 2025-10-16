# CFTS 需求測試管理系統

一個完整的 CFTS (需求規格) 搜索和管理系統，支援雙重搜索功能：CFTS ID 和 Req.ID。

## 功能特色

- **雙重搜索**: 支援 CFTS ID 和 Req.ID 搜索
- **多 CFTS 支援**: 31 個 CFTS 分類，共 9,111 筆需求記錄
- **批次匯入**: 支援從多個 Excel 檔案批次匯入資料
- **智能過濾**: 自動過濾 MD Scope = "Yes" 的記錄
- **自動完成**: CFTS ID 和 Req.ID 搜索欄位支援自動完成
- **中文界面**: 完整中文使用者介面
- **部分匹配**: 支援 CFTS ID 前綴搜索
- **響應式設計**: 支援桌面和移動設備

## 技術架構

- **後端**: FastAPI + SQLAlchemy + PostgreSQL
- **前端**: Vue.js 3 + Vite
- **資料庫**: PostgreSQL
- **容器化**: Docker + Docker Compose

## ⚡ 快速啟動

### 使用 Docker (推薦)

```bash
# 克隆專案
git clone <repository-url>
cd Requirement_Test_Management

# 一鍵啟動所有服務
./start-docker.sh
# 或
docker-compose up --build
```

### 訪問應用

- **前端界面**: http://localhost:3000
- **API 文檔**: http://localhost:8000/docs
- **後端 API**: http://localhost:8000

## 專案結構

```
Requirement_Test_Management/
├── backend/                    # FastAPI 後端
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   └── requirements.py
│   │   ├── db/                # 資料庫操作
│   │   │   ├── database.py
│   │   │   └── crud.py
│   │   └── models/            # 資料模型
│   │       ├── requirement.py
│   │       └── cfts_db.py
│   ├── batch_import_excel.py  # 批次匯入工具
│   ├── check_data.py          # 資料檢查工具
│   ├── recreate_tables.py     # 資料庫重建工具
│   └── requirements.txt
├── frontend/                  # Vue.js 前端
│   ├── src/
│   │   ├── components/
│   │   │   └── SearchInterface.vue
│   │   ├── App.vue
│   │   └── main.js
│   └── package.json
├── data/
│   └── cfts_excel/            # Excel 資料檔案（32 個 CFTS 檔案）
├── docker/                    # Docker 配置
├── docker-compose.yml         # 服務編排
├── start-docker.sh            # 啟動腳本
└── DEVELOPMENT_LOG.md         # 開發日誌
```

## 💾 資料說明

- **總計需求**: 9,111 筆（已過濾 MD Scope = "Yes"）
- **CFTS 分類**: 31 個不同的 CFTS 規格
- **資料來源**: 32 個 Excel 檔案（SYS1_CFTS_XXX_SR26 系列）
- **主要 CFTS**:
  - CFTS019 (Audio Management): 894 筆
  - CFTS084 (SW Security): 732 筆
  - CFTS043 (HVAC Controls): 709 筆
  - CFTS024 (Radio Functions): 598 筆
  - CFTS009 (Power State Charts): 554 筆
  - CFTS044 (Vehicle Controls): 550 筆
  - 等 26 個其他 CFTS...
- **欄位結構**: CFTS ID, Req.ID, Polarian ID, Description, Spec Object Type

## 🛠️ 開發模式

### 後端開發
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端開發
```bash
cd frontend
npm install
npm run dev
```

## 🗄️ 資料庫配置

PostgreSQL 會自動初始化並載入需求數據：
- **主機**: localhost:5432
- **資料庫**: requirement_test_db
- **使用者**: postgres
- **密碼**: password

### 批次匯入資料
```bash
cd backend

# 清除並重建資料庫表格
python3 recreate_tables.py

# 從 Excel 檔案批次匯入（只匯入 MD Scope = "Yes"）
python3 batch_import_excel.py ../data/cfts_excel

# 或匯入所有記錄（不過濾）
python3 batch_import_excel.py ../data/cfts_excel --no-filter

# 檢查匯入的資料
python3 check_data.py
```

## 📝 API 端點

### CFTS 搜索
- `GET /cfts/search?cfts_id={id}` - CFTS ID 搜索（支援部分匹配）
- `GET /cfts/requirement/{req_id}` - 通過 Req.ID 獲取需求
- `GET /cfts/` - 獲取所有需求（分頁支援）
- `GET /cfts/autocomplete/cfts-ids` - 獲取所有 CFTS ID（用於自動完成）

### Req.ID 搜索
- `GET /req/search?req_id={id}` - Req.ID 搜索
- `GET /req/autocomplete/req-ids?query={prefix}` - Req.ID 自動完成（前綴匹配）

### 文檔
- `GET /docs` - Swagger API 文檔
- `GET /redoc` - ReDoc API 文檔

## 🔧 故障排除

1. **確保 Docker Desktop 已啟動**
2. **檢查端口**: 3000, 8000, 5432 未被占用
3. **查看日誌**: `docker-compose logs -f`
4. **重新構建**: `docker-compose up --build`
5. **資料庫問題**: 執行 `python3 recreate_tables.py` 重建資料庫

## 📚 更多資訊

- **開發日誌**: 查看 [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) 了解最新開發進度和問題修復
- **Docker 指南**: 查看 [DOCKER_GUIDE.md](DOCKER_GUIDE.md) 了解 Docker 部署細節

---

🎯 **準備就緒！** 執行 `./start-docker.sh` 即可體驗完整的 CFTS 需求管理系統。