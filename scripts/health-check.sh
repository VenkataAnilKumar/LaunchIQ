#!/bin/bash
# LaunchIQ Health Check Script — Verify all systems operational

set -e

FRONTEND_URL="${FRONTEND_URL:-https://launchiq.vercel.app}"
API_URL="${API_URL:-https://api.launchiq.io}"
LANGFUSE_HOST="${LANGFUSE_HOST:-https://cloud.langfuse.com}"

echo "🎯 LaunchIQ Production Health Check"
echo "===================================="
echo ""
echo "Frontend: $FRONTEND_URL"
echo "API: $API_URL"
echo ""

# Counter
PASSED=0
FAILED=0

check_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Checking $name... "
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "$expected_code" ]; then
        echo "✅ ($HTTP_CODE)"
        ((PASSED++))
    else
        echo "❌ (Got $HTTP_CODE, expected $expected_code)"
        ((FAILED++))
    fi
}

check_json_response() {
    local name=$1
    local url=$2
    local field=$3
    
    echo -n "Checking $name... "
    
    RESPONSE=$(curl -s "$url" 2>/dev/null || echo "{}")
    
    if echo "$RESPONSE" | grep -q "$field"; then
        echo "✅"
        ((PASSED++))
    else
        echo "❌ (No $field in response)"
        ((FAILED++))
    fi
}

echo "📡 Frontend Checks"
check_endpoint "Frontend homepage" "$FRONTEND_URL" 200
check_endpoint "Frontend /dashboard redirect" "$FRONTEND_URL/dashboard" 307

echo ""
echo "🔌 Backend API Checks"
check_endpoint "API health endpoint" "$API_URL/api/v1/health" 200
check_json_response "API returns status" "$API_URL/api/v1/health" "status"

echo ""
echo "📊 Observability Checks"
check_endpoint "Langfuse connectivity" "$LANGFUSE_HOST/api/health" 200

echo ""
echo "📈 Database Checks (via API)"
if command -v psql &> /dev/null; then
    echo -n "Checking database from local... "
    if psql -h localhost -U postgres -d launchiq -c "SELECT 1;" &>/dev/null; then
        echo "✅"
        ((PASSED++))
    else
        echo "⚠️  (Can't connect locally, but API might still work)"
    fi
fi

echo ""
echo "===================================="
echo "Summary: $PASSED passed, $FAILED failed"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All systems operational!"
    exit 0
else
    echo "⚠️  Some checks failed. See above for details."
    exit 1
fi
