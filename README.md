# R1L Requirement & Test Management System

現代化的需求與測試案例管理系統，支援CFTS、SYS.2需求和TestCase的整合查詢。

## 🚀 快速開始

### 使用Docker（推薦）

```bash
./start-docker.sh
```

訪問：http://localhost:3000

### 手動啟動

#### 後端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### 前端
```bash
cd frontend
npm install
npm run serve
```

## 📊 資料導入

```bash
# 進入backend目錄
cd backend

# CFTS資料
python batch_import_cfts_new.py ../data/CFTS

# SYS.2資料
python batch_import_sys2.py ../data/R1L_SYS.2

# TestCase資料
python batch_import_testcase.py ../data/R1L_TestCase.xlsx
```

## 🎯 功能特色

- ✅ CFTS搜尋與查看
- ✅ 需求ID搜尋
- ✅ Melco ID點擊查看詳細資訊
- ✅ SYS.2需求資料顯示
- ✅ 相關TestCase自動關聯
- ✅ 現代化UI設計

## 🛠️ 技術棧

**後端:**
- FastAPI (Python)
- PostgreSQL
- SQLAlchemy

**前端:**
- Vue.js 3
- Inter字體
- 現代化CSS設計

## 📁 資料結構

```
data/
├── CFTS/                    # CFTS Excel檔案
├── R1L_SYS.2/              # SYS.2需求檔案
└── R1L_TestCase.xlsx       # TestCase資料
```

## 🐳 Docker指令

```bash
# 啟動
./start-docker.sh

# 停止
docker-compose down

# 查看日誌
docker-compose logs -f

# 重建
docker-compose up --build -d

# 刪除所有資料
docker-compose down -v
```

## 📝 API文檔

啟動後訪問：http://localhost:8000/docs

## 💡 開發

- 前端自動熱重載
- 後端自動重啟
- 資料庫資料持久化

## 🎨 UI設計

採用現代化、簡潔的設計風格：
- 清爽的白色背景
- 藍色主題色
- 圓角卡片設計
- 流暢的過渡動畫

---

**資料統計:**
- CFTS: 5,452筆
- SYS.2: 14,683筆  
- TestCase: 34,457筆
