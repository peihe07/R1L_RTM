# R1L_RTM 健康檢查機制說明文件

## 概述

本系統已實施完整的健康檢查機制，確保所有服務（資料庫、後端API、前端、反向代理）的穩定運行。

## 實施的改進

### 1. 資料庫連接重試機制

**位置**: `backend/app/db/database.py`

**功能**:
- 自動重試資料庫連接（預設5次，間隔2秒）
- 避免因資料庫啟動慢導致後端啟動失敗
- 詳細的日誌記錄

**參數**:
```python
max_retries=5        # 最大重試次數
retry_interval=2     # 重試間隔（秒）
```

### 2. 後端健康檢查端點

**位置**: `backend/app/main.py`

**端點**:

- `GET /health` - 健康檢查
  - 檢查 API 和資料庫連接狀態
  - 返回詳細的健康狀態資訊
  - 狀態碼: 200 (健康) / 503 (不健康)

- `GET /readiness` - 就緒檢查
  - 檢查服務是否準備好接收請求
  - 狀態碼: 200 (就緒) / 503 (未就緒)

**範例回應**:
```json
{
  "status": "healthy",
  "database": "connected",
  "message": "All systems operational"
}
```

### 3. Docker Compose 健康檢查配置

**位置**: `docker-compose.yml`

**配置內容**:

#### 資料庫 (db)
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

#### 後端 (backend)
```yaml
healthcheck:
  test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()\" || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
depends_on:
  db:
    condition: service_healthy
```

#### 前端 (frontend)
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
depends_on:
  backend:
    condition: service_healthy
```

#### 反向代理 (reverse-proxy)
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:80/healthz || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
depends_on:
  frontend:
    condition: service_healthy
  backend:
    condition: service_healthy
```

### 4. 健康檢查腳本

**檔案**: `health_check.sh`

**功能**:
- 檢查所有容器的運行狀態和健康狀態
- 測試 HTTP 端點是否正常回應
- 顯示資源使用情況（CPU、記憶體）
- 顯示各容器的最近日誌
- 生成彩色的健康報告

**使用方式**:
```bash
cd /home/sqa_server/apps/R1L_RTM
./health_check.sh
```

**輸出範例**:
```
================================
  R1L_RTM Health Check Report
  2025-10-20 08:30:00
================================

1. Container Status Check
-------------------------
✓ r1l_rtm_db: running (healthy)
✓ r1l_rtm_backend: running (healthy)
✓ r1l_rtm_frontend: running (health: starting)
✓ r1l_rtm_reverse_proxy: running (no healthcheck)

2. HTTP Endpoint Check
----------------------
✓ Backend Health: http://localhost:8000/health (HTTP 200)
✓ Backend Readiness: http://localhost:8000/readiness (HTTP 200)
✓ Reverse Proxy: http://localhost:80/healthz (HTTP 200)
✓ Frontend (via proxy): http://localhost:80/ (HTTP 200)
✓ Backend API (via proxy): http://localhost:80/api/cfts/autocomplete/cfts-ids (HTTP 200)

================================
Overall Status: HEALTHY ✓
```

### 5. 持續監控腳本

**檔案**: `monitor.sh`

**功能**:
- 持續監控所有服務的健康狀態
- 在檢測到異常時自動重啟容器
- 重試機制（最多3次）
- 日誌記錄到 `monitor.log`
- 避免頻繁重啟（冷卻時間300秒）

**使用方式**:
```bash
# 前台運行（預設60秒間隔）
./monitor.sh

# 自訂間隔（30秒）
./monitor.sh 30

# 背景運行
nohup ./monitor.sh > /dev/null 2>&1 &

# 停止監控
pkill -f monitor.sh
```

**日誌位置**: `monitor.log`

## 服務啟動順序

有了健康檢查機制後，服務啟動順序如下：

```
1. db (資料庫)
   ↓ (等待健康)
2. backend (後端API)
   ↓ (等待健康)
3. frontend (前端)
   ↓ (等待健康)
4. reverse-proxy (反向代理)
```

每個服務只有在其依賴服務健康後才會啟動。

## 手動測試健康檢查

### 測試後端健康檢查
```bash
curl http://localhost:8000/health
curl http://localhost:8000/readiness
```

### 測試反向代理
```bash
curl http://localhost:80/healthz
```

### 測試完整系統
```bash
curl http://localhost:80/
curl http://localhost:80/api/cfts/autocomplete/cfts-ids
```

### 查看容器健康狀態
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### 查看詳細健康資訊
```bash
docker inspect r1l_rtm_backend | jq '.[0].State.Health'
```

## 重啟服務

### 重啟單個服務
```bash
docker restart r1l_rtm_backend
```

### 重啟所有服務
```bash
cd /home/sqa_server/apps/R1L_RTM
docker-compose restart
```

### 完全重建（應用新配置）
```bash
cd /home/sqa_server/apps/R1L_RTM
docker-compose down
docker-compose up -d
```

## 故障排除

### 問題：後端無法連接資料庫

**症狀**: 後端日誌顯示 `connection to server at "db" failed`

**解決方案**:
1. 檢查資料庫是否健康: `docker ps | grep r1l_rtm_db`
2. 等待資料庫完全啟動（約10-20秒）
3. 重啟後端: `docker restart r1l_rtm_backend`

### 問題：健康檢查一直顯示 "starting"

**症狀**: 容器運行但健康狀態持續顯示 "starting"

**解決方案**:
1. 檢查 `start_period` 是否足夠長
2. 查看容器日誌: `docker logs r1l_rtm_backend`
3. 手動測試健康檢查端點

### 問題：前端顯示 502 錯誤

**症狀**: 瀏覽器訪問前端返回 502 Bad Gateway

**解決方案**:
1. 運行健康檢查腳本: `./health_check.sh`
2. 確認後端是否健康
3. 檢查 Nginx 配置: `docker exec r1l_rtm_reverse_proxy nginx -t`

## 監控建議

### 開發環境
- 定期運行 `health_check.sh` 查看系統狀態
- 關注容器日誌中的異常信息

### 生產環境
- 使用 `monitor.sh` 持續監控
- 配置外部監控系統（如 Prometheus + Grafana）
- 設定告警通知（郵件、Slack等）
- 定期檢查 `monitor.log` 日誌

## 進階配置

### 調整健康檢查頻率

編輯 `docker-compose.yml`，修改以下參數：

```yaml
healthcheck:
  interval: 30s      # 檢查間隔
  timeout: 10s       # 超時時間
  retries: 3         # 失敗重試次數
  start_period: 40s  # 啟動等待時間
```

### 增加後端重試次數

編輯 `backend/app/db/database.py`:

```python
engine = create_engine_with_retry(
    DATABASE_URL,
    max_retries=10,      # 增加到10次
    retry_interval=3     # 間隔3秒
)
```

## 相關檔案

- `docker-compose.yml` - Docker Compose 配置
- `backend/app/db/database.py` - 資料庫連接管理
- `backend/app/main.py` - 健康檢查端點
- `health_check.sh` - 健康檢查腳本
- `monitor.sh` - 持續監控腳本
- `monitor.log` - 監控日誌

## 總結

通過實施這套完整的健康檢查機制，R1L_RTM 系統現在具備：

✓ 自動重試資料庫連接
✓ 服務健康狀態監控
✓ 正確的服務啟動順序
✓ 自動故障恢復（通過 restart 策略）
✓ 詳細的健康報告
✓ 持續監控和自動重啟

這將大大提高系統的穩定性和可維護性。
