#!/bin/bash

# R1L_RTM Continuous Monitor Script
# 持續監控服務狀態，並在異常時自動重啟

INTERVAL=${1:-60}  # 檢查間隔（秒），預設 60 秒
MAX_RETRIES=3
RESTART_COOLDOWN=300  # 重啟冷卻時間（秒），避免頻繁重啟

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 紀錄檔
LOG_FILE="/home/sqa_server/apps/R1L_RTM/monitor.log"

# 函數：記錄日誌
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# 函數：檢查容器健康狀態
check_container_health() {
    local container_name=$1
    local status=$(docker inspect -f '{{.State.Status}}' $container_name 2>/dev/null)
    local health=$(docker inspect -f '{{.State.Health.Status}}' $container_name 2>/dev/null)

    if [ -z "$status" ]; then
        return 2  # 容器不存在
    fi

    if [ "$status" != "running" ]; then
        return 1  # 容器未運行
    fi

    if [ "$health" == "unhealthy" ]; then
        return 1  # 健康檢查失敗
    fi

    return 0  # 正常
}

# 函數：重啟容器
restart_container() {
    local container_name=$1
    log "WARN" "Restarting container: $container_name"
    docker restart $container_name
    sleep 10  # 等待容器啟動
}

# 函數：檢查 HTTP 端點
check_http() {
    local url=$1
    local expected_code=${2:-200}
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    [ "$response" == "$expected_code" ]
}

# 主監控循環
log "INFO" "Starting R1L_RTM monitor (interval: ${INTERVAL}s)"

declare -A retry_count

while true; do
    all_healthy=true

    # 檢查各個容器
    for container in r1l_rtm_db r1l_rtm_backend r1l_rtm_frontend r1l_rtm_reverse_proxy; do
        if ! check_container_health "$container"; then
            log "ERROR" "Container $container is unhealthy"
            all_healthy=false

            # 增加重試計數
            retry_count[$container]=$((${retry_count[$container]:-0} + 1))

            # 如果重試次數未達上限，嘗試重啟
            if [ ${retry_count[$container]} -le $MAX_RETRIES ]; then
                restart_container "$container"
            else
                log "ERROR" "Container $container exceeded max retries, manual intervention required"
            fi
        else
            # 重置重試計數
            retry_count[$container]=0
        fi
    done

    # 檢查 HTTP 端點（使用反向代理的正確埠號）
    if ! check_http "http://localhost:5566/healthz"; then
        log "ERROR" "Reverse proxy health check failed"
        all_healthy=false
    fi

    # 檢查後端 API（通過反向代理）
    if ! check_http "http://localhost:5566/api/cfts/autocomplete/cfts-ids"; then
        log "ERROR" "Backend API check failed"
        all_healthy=false
    fi

    if [ "$all_healthy" = true ]; then
        log "INFO" "All services healthy"
    fi

    sleep $INTERVAL
done
