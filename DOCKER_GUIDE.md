# 🐳 CFTS 系統 Docker 部署指南

## 🚀 一鍵啟動

### 方法 1: 使用啟動腳本 (推薦)
```bash
./start-docker.sh
```

### 方法 2: 手動啟動
```bash
docker-compose up --build
```

## 🏗️ 服務架構

| 服務 | 端口 | 說明 |
|------|------|------|
| **PostgreSQL** | 5432 | 資料庫服務，自動載入 524 條需求數據 |
| **Backend API** | 8000 | FastAPI 後端，提供 CFTS 搜索 API |
| **Frontend** | 3000 | Vue.js 前端界面，中文搜索介面 |

## 🌐 訪問地址

- **🔍 搜索界面**: http://localhost:3000
- **📖 API 文檔**: http://localhost:8000/docs
- **⚡ API 端點**: http://localhost:8000
- **🗄️ 資料庫**: localhost:5432

## 🎯 快速測試

### CFTS 搜索測試
- **部分匹配**: `CFTS016` → 找到 523 條結果
- **精確搜索**: `CFTS016-58` → 找到特定需求
- **模式搜索**: `CFTS016-7` → 找到所有 7 開頭的需求

### Req.ID 搜索測試
- **範例**: `4921596`, `4921624`, `4921625`

## 🛠️ Docker 命令參考

```bash
# 🚀 啟動服務
docker-compose up --build          # 前台啟動並重新構建
docker-compose up -d --build       # 後台啟動並重新構建

# 📊 監控服務
docker-compose ps                  # 查看服務狀態
docker-compose logs -f             # 實時查看日誌
docker-compose logs backend        # 查看後端日誌
docker-compose logs frontend       # 查看前端日誌

# 🔄 服務管理
docker-compose restart             # 重啟所有服務
docker-compose restart backend     # 重啟後端服務
docker-compose stop               # 停止服務
docker-compose down               # 停止並移除容器

# 🧹 清理資源
docker-compose down -v            # 停止服務並移除 volumes
docker system prune -f            # 清理未使用的 Docker 資源
```

## 🔧 故障排除

### 常見問題
1. **端口衝突**: 確保 3000, 8000, 5432 端口未被占用
2. **Docker 未啟動**: 確保 Docker Desktop 正在運行
3. **資料載入失敗**: 檢查 `extracted_data.json` 是否存在

### 診斷命令
```bash
# 檢查容器狀態
docker-compose ps

# 查看詳細錯誤
docker-compose logs --tail=50

# 檢查網路連接
docker-compose exec backend curl http://db:5432
```

### 重置環境
```bash
# 完全重置 (會清除資料庫數據)
docker-compose down -v
docker-compose up --build
```

```bash
# 查看資源使用
docker stats

# 檢查記憶體使用
docker-compose exec backend ps aux
```