# R1L_RTM 健康檢查 - 快速參考

## 快速檢查命令

```bash
# 運行完整健康檢查
cd /home/sqa_server/apps/R1L_RTM
./health_check.sh

# 查看所有容器狀態
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 查看容器健康狀態（詳細）
docker inspect r1l_rtm_backend | grep -A 10 Health
```

## 健康檢查端點

| 服務 | 端點 | 說明 |
|-----|------|------|
| 後端健康檢查 | `http://localhost:8000/health` (容器內部) | 檢查後端和資料庫連接 |
| 後端就緒檢查 | `http://localhost:8000/readiness` (容器內部) | 檢查後端是否準備就緒 |
| 反向代理 | `http://localhost:5566/healthz` | Nginx 健康檢查 |
| 前端 (通過代理) | `http://localhost:5566/` | 前端頁面 |
| 後端 API (通過代理) | `http://localhost:5566/api/...` | 後端 API |

## 測試命令

```bash
# 測試反向代理
curl http://localhost:5566/healthz

# 測試前端
curl http://localhost:5566/

# 測試後端 API
curl http://localhost:5566/api/cfts/autocomplete/cfts-ids

# 從容器內部測試後端健康檢查
docker exec r1l_rtm_backend curl -s http://localhost:8000/health
```

## 常用操作

### 重啟服務
```bash
# 重啟單個服務
docker restart r1l_rtm_backend

# 重啟所有服務
cd /home/sqa_server/apps/R1L_RTM
docker compose restart
```

### 查看日誌
```bash
# 查看後端日誌
docker logs r1l_rtm_backend --tail 50

# 持續跟蹤日誌
docker logs -f r1l_rtm_backend

# 查看所有容器日誌
docker compose logs -f
```

### 啟動監控
```bash
# 前台運行（60秒間隔）
./monitor.sh

# 背景運行
nohup ./monitor.sh > /dev/null 2>&1 &

# 查看監控日誌
tail -f monitor.log

# 停止監控
pkill -f monitor.sh
```

### 應用新配置
```bash
cd /home/sqa_server/apps/R1L_RTM

# 停止並移除容器
docker compose down

# 重新啟動（應用新的 docker-compose.yml 配置）
docker compose up -d

# 等待服務啟動後檢查
sleep 30
./health_check.sh
```

## 健康檢查機制說明

### 服務啟動順序
```
1. db (資料庫) → 健康後
2. backend (後端) → 健康後
3. frontend (前端) → 健康後
4. reverse-proxy (反向代理)
```

### 健康檢查頻率
- **資料庫**: 每 10 秒檢查一次
- **後端**: 每 30 秒檢查一次，啟動等待 40 秒
- **前端**: 每 30 秒檢查一次，啟動等待 60 秒
- **反向代理**: 每 30 秒檢查一次

### 重試機制
- **資料庫連接**: 最多重試 5 次，間隔 2 秒
- **容器健康檢查**: 失敗 3 次後標記為不健康
- **監控腳本**: 最多重啟 3 次，冷卻時間 300 秒

## 故障排除

### 問題：後端無法連接資料庫
```bash
# 檢查資料庫狀態
docker ps | grep r1l_rtm_db

# 查看資料庫日誌
docker logs r1l_rtm_db --tail 30

# 重啟後端
docker restart r1l_rtm_backend
```

### 問題：前端顯示 502 錯誤
```bash
# 運行健康檢查
./health_check.sh

# 檢查後端狀態
docker logs r1l_rtm_backend --tail 50

# 檢查 Nginx 配置
docker exec r1l_rtm_reverse_proxy nginx -t
```

### 問題：健康檢查一直失敗
```bash
# 查看詳細的健康檢查狀態
docker inspect r1l_rtm_backend --format='{{json .State.Health}}' | python3 -m json.tool

# 手動測試健康檢查
docker exec r1l_rtm_backend curl -v http://localhost:8000/health
```

## 文件位置

- `docker-compose.yml` - Docker Compose 配置（包含健康檢查設定）
- `backend/app/db/database.py` - 資料庫連接重試機制
- `backend/app/main.py` - 健康檢查端點
- `health_check.sh` - 健康檢查腳本
- `monitor.sh` - 持續監控腳本
- `monitor.log` - 監控日誌
- `README_HEALTH_CHECK.md` - 詳細說明文件

## 服務埠號

| 服務 | 內部埠號 | 外部埠號 | 說明 |
|-----|---------|---------|------|
| 資料庫 | 5432 | - | 僅內部訪問 |
| 後端 API | 8000 | - | 僅內部訪問 |
| 前端 | 3000 | - | 僅內部訪問 |
| 反向代理 | 80 | 5566 | 對外服務埠 |

**重要**: 所有對外訪問必須通過反向代理的 5566 埠！

## 健康狀態說明

| 狀態 | 說明 |
|-----|------|
| healthy | 服務運行正常，健康檢查通過 |
| unhealthy | 服務運行但健康檢查失敗 |
| starting | 服務正在啟動，健康檢查尚未完成 |
| (no healthcheck) | 未配置健康檢查 |

## 監控建議

### 開發環境
- 每天運行一次 `health_check.sh`
- 關注容器日誌中的錯誤信息
- 在代碼更新後檢查服務狀態

### 生產環境
- 使用 `monitor.sh` 持續監控
- 設置外部監控系統（Prometheus、Grafana）
- 配置告警通知
- 定期檢查 `monitor.log`
- 定期備份資料庫

## 相關資源

- [Docker Compose 文檔](https://docs.docker.com/compose/)
- [健康檢查詳細說明](README_HEALTH_CHECK.md)
- FastAPI 文檔: https://fastapi.tiangolo.com/
- Vue.js 文檔: https://vuejs.org/
