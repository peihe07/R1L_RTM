#!/bin/bash

# R1L_RTM Health Check Script
# 檢查所有服務的健康狀態

set -e

COMPOSE_FILE="/home/sqa_server/apps/R1L_RTM/docker-compose.yml"
PROJECT_NAME="r1l_rtm"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數：打印標題
print_header() {
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  R1L_RTM Health Check Report${NC}"
    echo -e "${BLUE}  $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

# 函數：檢查容器狀態
check_container_status() {
    local container_name=$1
    local status=$(docker inspect -f '{{.State.Status}}' $container_name 2>/dev/null)
    local health=$(docker inspect -f '{{.State.Health.Status}}' $container_name 2>/dev/null)

    if [ -z "$status" ]; then
        echo -e "${RED}✗${NC} $container_name: NOT FOUND"
        return 1
    fi

    if [ "$status" != "running" ]; then
        echo -e "${RED}✗${NC} $container_name: $status"
        return 1
    fi

    if [ "$health" == "healthy" ]; then
        echo -e "${GREEN}✓${NC} $container_name: running (healthy)"
    elif [ "$health" == "unhealthy" ]; then
        echo -e "${RED}✗${NC} $container_name: running (unhealthy)"
        return 1
    elif [ "$health" == "starting" ]; then
        echo -e "${YELLOW}⚠${NC} $container_name: running (health: starting)"
    elif [ "$health" == "<no value>" ]; then
        echo -e "${GREEN}✓${NC} $container_name: running (no healthcheck)"
    else
        echo -e "${YELLOW}⚠${NC} $container_name: running (health: $health)"
    fi

    return 0
}

# 函數：測試 HTTP 端點
check_http_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)

    if [ "$response" == "$expected_code" ]; then
        echo -e "${GREEN}✓${NC} $name: $url (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗${NC} $name: $url (HTTP $response, expected $expected_code)"
        return 1
    fi
}

# 主程序開始
print_header

echo "1. Container Status Check"
echo "-------------------------"
all_healthy=true

check_container_status "r1l_rtm_db" || all_healthy=false
check_container_status "r1l_rtm_backend" || all_healthy=false
check_container_status "r1l_rtm_frontend" || all_healthy=false
check_container_status "r1l_rtm_reverse_proxy" || all_healthy=false

echo ""
echo "2. HTTP Endpoint Check"
echo "----------------------"

# 注意：後端和前端服務不對外開放，只能從反向代理訪問
check_http_endpoint "Reverse Proxy Health" "http://localhost:5566/healthz" || all_healthy=false
check_http_endpoint "Frontend (via proxy)" "http://localhost:5566/" || all_healthy=false
check_http_endpoint "Backend API (via proxy)" "http://localhost:5566/api/cfts/autocomplete/cfts-ids" || all_healthy=false

# 從容器內部測試後端健康檢查
echo -n "Backend Health (internal): "
if docker exec r1l_rtm_backend python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} http://localhost:8000/health (HTTP 200)"
else
    echo -e "${RED}✗${NC} http://localhost:8000/health (Failed)"
    all_healthy=false
fi

echo ""
echo "3. Resource Usage"
echo "-----------------"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
    r1l_rtm_db r1l_rtm_backend r1l_rtm_frontend r1l_rtm_reverse_proxy 2>/dev/null || true

echo ""
echo "4. Recent Logs (Last 5 lines)"
echo "------------------------------"
for container in r1l_rtm_db r1l_rtm_backend r1l_rtm_frontend r1l_rtm_reverse_proxy; do
    echo ""
    echo -e "${BLUE}[$container]${NC}"
    docker logs --tail 5 $container 2>&1 | sed 's/^/  /'
done

echo ""
echo "================================"
if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}Overall Status: HEALTHY ✓${NC}"
    exit 0
else
    echo -e "${RED}Overall Status: UNHEALTHY ✗${NC}"
    exit 1
fi
