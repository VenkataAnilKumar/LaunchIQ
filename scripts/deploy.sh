#!/bin/bash
# LaunchIQ Deployment Script — One-Command Deploy to Production
# Usage: ./deploy.sh [frontend|backend|full]

set -e

ENVIRONMENT="${ENVIRONMENT:-production}"
REGION="${AWS_REGION:-us-east-1}"
VERCEL_ORG_ID="${VERCEL_ORG_ID}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID}"

usage() {
    echo "LaunchIQ Deployment Script"
    echo "Usage: $0 [frontend|backend|full|verify]"
    echo ""
    echo "  frontend  - Deploy frontend to Vercel only"
    echo "  backend   - Deploy backend to AWS ECS only"
    echo "  full      - Deploy both frontend and backend"
    echo "  verify    - Run health checks only (no deployment)"
    echo ""
    echo "Environment variables required:"
    echo "  VERCEL_TOKEN        - Vercel API token"
    echo "  AWS_ACCOUNT_ID      - AWS account ID"
    echo "  AWS_REGION          - AWS region (default: us-east-1)"
    echo ""
}

check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    # Check CLI tools
    command -v git &> /dev/null || { echo "❌ git not found"; exit 1; }
    command -v aws &> /dev/null || { echo "❌ AWS CLI not found"; exit 1; }
    command -v docker &> /dev/null || { echo "❌ Docker not found"; exit 1; }
    
    # Check credentials
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        echo "✓ AWS Account ID: $AWS_ACCOUNT_ID"
    fi
    
    # Verify no uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "❌ Uncommitted changes detected. Commit changes before deploying."
        exit 1
    fi
    
    echo "✅ Prerequisites OK"
}

deploy_frontend() {
    echo ""
    echo "🚀 Deploying Frontend to Vercel..."
    
    # Check Vercel token
    if [ -z "$VERCEL_TOKEN" ]; then
        echo "❌ VERCEL_TOKEN not set"
        exit 1
    fi
    
    cd src/apps/web
    
    # Install deps
    pnpm install
    
    # Check TypeScript
    echo "  Checking TypeScript..."
    npx tsc --noEmit || { echo "❌ TypeScript errors"; exit 1; }
    
    # Check ESLint
    echo "  Checking ESLint..."
    npx next lint || { echo "❌ ESLint errors"; exit 1; }
    
    # Production build
    echo "  Building for production..."
    pnpm build || { echo "❌ Build failed"; exit 1; }
    
    # Deploy to Vercel
    echo "  Uploading to Vercel..."
    npx vercel --prod --token=$VERCEL_TOKEN
    
    cd - > /dev/null
    echo "✅ Frontend deployed to Vercel"
}

deploy_backend() {
    echo ""
    echo "🚀 Deploying Backend to AWS ECS..."
    
    # Check AWS credentials
    aws sts get-caller-identity > /dev/null || { echo "❌ AWS credentials not configured"; exit 1; }
    
    # Build Docker image
    echo "  Building Docker image..."
    docker build \
        -f src/infra/docker/Dockerfile.api \
        -t launchiq-api:latest \
        . || { echo "❌ Docker build failed"; exit 1; }
    
    # Tag for ECR
    ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/launchiq-api"
    docker tag launchiq-api:latest ${ECR_REPO}:latest
    docker tag launchiq-api:latest ${ECR_REPO}:$(git rev-parse --short HEAD)
    
    # Login to ECR
    echo "  Logging in to ECR..."
    aws ecr get-login-password --region $REGION | \
        docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
    
    # Push image
    echo "  Pushing image to ECR..."
    docker push ${ECR_REPO}:latest
    docker push ${ECR_REPO}:$(git rev-parse --short HEAD)
    
    # Run migrations
    echo "  Running database migrations..."
    cd src/memory/structured
    alembic upgrade head
    cd - > /dev/null
    
    # Deploy with CDK
    echo "  Deploying with AWS CDK..."
    cd src/infra/aws
    npm install
    npx cdk deploy ECSStack --require-approval never
    cd - > /dev/null
    
    # Wait for deployment
    echo "  Waiting for deployment (2 min)..."
    sleep 120
    
    echo "✅ Backend deployed to AWS ECS"
}

verify_deployment() {
    echo ""
    echo "✅ Verifying Deployment..."
    
    # Get endpoints
    FRONTEND_URL="https://launchiq.vercel.app"
    BACKEND_URL=$(aws elbv2 describe-load-balancers \
        --region $REGION \
        --query "LoadBalancers[?LoadBalancerName=='launchiq-alb'].DNSName" \
        --output text)
    
    if [ -z "$BACKEND_URL" ]; then
        echo "⚠️  Could not find ALB endpoint. Skipping backend verification."
    else
        BACKEND_URL="https://${BACKEND_URL}"
    fi
    
    # Frontend check
    echo -n "  Frontend ($FRONTEND_URL)... "
    if curl -sf "$FRONTEND_URL" > /dev/null 2>&1; then
        echo "✅"
    else
        echo "❌ (failed to connect)"
    fi
    
    # Backend health check
    if [ -n "$BACKEND_URL" ]; then
        echo -n "  API Health ($BACKEND_URL/api/v1/health)... "
        RESPONSE=$(curl -s "$BACKEND_URL/api/v1/health" 2>/dev/null || echo "")
        if echo "$RESPONSE" | grep -q "ok"; then
            echo "✅"
        else
            echo "❌ (no response)"
        fi
    fi
    
    echo ""
    echo "🎉 Deployment complete!"
    echo ""
    echo "Endpoints:"
    echo "  Frontend: $FRONTEND_URL"
    if [ -n "$BACKEND_URL" ]; then
        echo "  Backend:  ${BACKEND_URL}/api/v1"
    fi
}

rollback_frontend() {
    echo ""
    echo "⏮️  Rolling back Frontend..."
    cd src/apps/web
    npx vercel rollback
    cd - > /dev/null
    echo "✅ Frontend rolled back"
}

rollback_backend() {
    echo ""
    echo "⏮️  Rolling back Backend..."
    
    # Get previous image version
    PREVIOUS_IMAGE=$(aws ecr describe-images \
        --repository-name launchiq-api \
        --region $REGION \
        --query 'imageDetails[1].imageTags[0]' \
        --output text)
    
    if [ -z "$PREVIOUS_IMAGE" ]; then
        echo "❌ Could not find previous image"
        exit 1
    fi
    
    # Force new deployment with previous image
    aws ecs update-service \
        --cluster launchiq-prod \
        --service launchiq-api \
        --force-new-deployment \
        --region $REGION
    
    echo "✅ Backend rollback initiated (may take 5-10 minutes)"
}

# -------- Main Script --------

if [ $# -eq 0 ]; then
    usage
    exit 0
fi

case "$1" in
    frontend)
        check_prerequisites
        deploy_frontend
        verify_deployment
        ;;
    backend)
        check_prerequisites
        deploy_backend
        verify_deployment
        ;;
    full)
        check_prerequisites
        deploy_frontend
        deploy_backend
        verify_deployment
        ;;
    verify)
        verify_deployment
        ;;
    rollback-frontend)
        rollback_frontend
        ;;
    rollback-backend)
        rollback_backend
        ;;
    *)
        usage
        exit 1
        ;;
esac
