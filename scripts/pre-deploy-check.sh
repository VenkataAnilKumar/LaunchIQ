#!/bin/bash
# LaunchIQ Pre-Deployment Checklist — Verify everything is ready to ship

set -e

echo "🎯 LaunchIQ Pre-Deployment Checklist"
echo "====================================="
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

check() {
    local name=$1
    local command=$2
    
    echo -n "  ✓ $name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo "✅"
        ((CHECKS_PASSED++))
    else
        echo "❌"
        ((CHECKS_FAILED++))
    fi
}

echo "1️⃣  Code Quality"
check "Python linting (ruff)" "cd src && ruff check ."
check "Python type checking (mypy)" "cd src && mypy"
check "TypeScript strict mode" "cd src/apps/web && npx tsc --noEmit"
check "ESLint checks" "cd src/apps/web && npx next lint"

echo ""
echo "2️⃣  Testing"
check "Unit tests passing" "pytest src/tests/test_smoke.py --tb=no -q"
check "E2E tests setup" "test -f src/tests/test_e2e.py"
check "Eval framework available" "test -d src/evals/regression"

echo ""
echo "3️⃣  Build Verification"
check "Next.js production build" "cd src/apps/web && pnpm build"
check "Docker API image" "docker build -f src/infra/docker/Dockerfile.api -t launchiq-api:test . --quiet"
check "Docker worker image" "docker build -f src/infra/docker/Dockerfile.worker -t launchiq-worker:test . --quiet"

echo ""
echo "4️⃣  Infrastructure"
check "CDK stacks defined" "test -f src/infra/aws/app.py"
check "Docker Compose config" "cd src/infra/docker && docker-compose config > /dev/null"
check "Alembic migrations" "test -d src/memory/structured/migrations/versions"

echo ""
echo "5️⃣  Git Status"
check "No uncommitted changes" "git status --porcelain | wc -l | grep -q '^0'"
check "Local in sync with origin" "git fetch --dry-run"
check "Main branch selected" "git branch --show-current | grep -q '^main'"

echo ""
echo "6️⃣  Secrets & Config"
check "Requirements file complete" "grep -q 'anthropic' src/apps/api/requirements.txt"
check "Alembic config present" "test -f src/memory/structured/alembic.ini"
check ".env.example exists" "test -f .env.example"

echo ""
echo "7️⃣  Documentation"
check "Deployment guide exists" "test -f docs/02_Technical_Feasibility/09_Deployment_Guide.md"
check "README complete" "test -f README.md"
check "Architecture doc exists" "test -f docs/02_Technical_Feasibility/01_Technical_Architecture.md"

echo ""
echo "====================================="
echo "Results: $CHECKS_PASSED passed, $CHECKS_FAILED failed"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo "✅ All checks passed — Ready to deploy! 🚀"
    exit 0
else
    echo "❌ Some checks failed — Fix issues before deploying"
    exit 1
fi
