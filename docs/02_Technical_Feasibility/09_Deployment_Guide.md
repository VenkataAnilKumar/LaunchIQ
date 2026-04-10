# LaunchIQ — Deployment Guide

**Status:** Production-Ready  
**Last Updated:** 2026-04-09  
**Audience:** DevOps engineers, deployment engineers, infrastructure team

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [GitHub Secrets Setup](#github-secrets-setup)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup & Migrations](#database-setup--migrations)
5. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
6. [Backend Deployment (AWS CDK)](#backend-deployment-aws-cdk)
7. [Verification & Health Checks](#verification--health-checks)
8. [Troubleshooting](#troubleshooting)
9. [Rollback Procedures](#rollback-procedures)

---

## Pre-Deployment Checklist

Before deploying, confirm:

- [ ] All tests passing locally: `pytest src/ --cov=src`
- [ ] Eval regression gate passing: `python src/evals/regression/run_regression.py --assert-baseline`
- [ ] TypeScript strict mode: `npx tsc --noEmit` (in `src/apps/web`)
- [ ] Next.js builds successfully: `cd src/apps/web && pnpm build`
- [ ] Docker images build: `docker build -f src/infra/docker/Dockerfile.api -t launchiq-api:latest .`
- [ ] No uncommitted changes: `git status`
- [ ] Latest code pulled: `git pull origin main`
- [ ] AWS credentials configured: `aws sts get-caller-identity`
- [ ] Vercel CLI installed: `vercel --version`
- [ ] Database backups created (if upgrading existing DB)

---

## GitHub Secrets Setup

Add these secrets to your GitHub repository at **Settings → Secrets and variables → Actions**.

### Required Secrets

| Secret Name | Value | Source |
|---|---|---|
| `ANTHROPIC_API_KEY` | Your Claude API key | https://console.anthropic.com |
| `INTEGRATION_ENCRYPTION_KEY` | 32-char random string for AES-256 | `openssl rand -hex 16` |
| `OPENAI_API_KEY` | OpenAI embedding model key | https://platform.openai.com |
| `VERCEL_TOKEN` | Vercel API token | https://vercel.com/account/tokens |
| `VERCEL_ORG_ID` | Vercel organization ID | Vercel dashboard |
| `VERCEL_PROJECT_ID` | Vercel project ID for frontend | Vercel project settings |
| `AWS_ACCESS_KEY_ID` | AWS credentials | AWS IAM console |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials | AWS IAM console |
| `AWS_REGION` | Deployment region (e.g., `us-east-1`) | — |
| `ECR_REGISTRY` | AWS ECR registry URL | `<account-id>.dkr.ecr.<region>.amazonaws.com` |
| `ECR_REPOSITORY` | Repository name for API image | `launchiq-api` |
| `SLACK_WEBHOOK_URL` | Slack channel for deployment alerts | https://api.slack.com/messaging/webhooks |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key for eval tracing | https://cloud.langfuse.com |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | https://cloud.langfuse.com |

### How to Add Secrets

**Via GitHub Web UI:**
1. Go to repo **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Enter secret name and value
4. Click **Add secret**

**Via GitHub CLI:**
```bash
gh secret set ANTHROPIC_API_KEY -b "your-key-value"
gh secret set INTEGRATION_ENCRYPTION_KEY -b "your-32-char-key"
# ... repeat for all secrets
```

**Verify secrets were added:**
```bash
gh secret list
```

---

## Environment Configuration

### Local Development (.env file)

Create `.env` in repo root for local development:

```bash
# API Configuration
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/launchiq
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# LLM & AI
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Encryption
INTEGRATION_ENCRYPTION_KEY=... (32-char hex)

# Observability
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
SENTRY_DSN=https://...@sentry.io/...

# Frontend (Next.js)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEV_BEARER_TOKEN=... (dev-only token)

# Environment
ENVIRONMENT=development
DEBUG=true
```

### Production Configuration (.env.production)

```bash
# API Configuration
DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@${DB_HOST}:5432/launchiq
REDIS_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:6379/0
QDRANT_URL=https://${QDRANT_HOST}
QDRANT_API_KEY=${QDRANT_API_KEY}

# LLM & AI
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
TAVILY_API_KEY=${TAVILY_API_KEY}

# Encryption
INTEGRATION_ENCRYPTION_KEY=${INTEGRATION_ENCRYPTION_KEY}

# Observability
LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
SENTRY_DSN=${SENTRY_DSN}

# Frontend (Next.js)
NEXT_PUBLIC_API_URL=https://api.launchiq.io
CLERK_PUBLISHABLE_KEY=${CLERK_PUBLISHABLE_KEY}
CLERK_SECRET_KEY=${CLERK_SECRET_KEY}

# Environment
ENVIRONMENT=production
DEBUG=false
```

---

## Database Setup & Migrations

### Prerequisites

- PostgreSQL 14+ installed and running
- `alembic` CLI available: `pip install alembic`

### Step 1: Create Database

```bash
# Local development
psql -U postgres -c "CREATE DATABASE launchiq;"

# Production: Use managed database (AWS RDS recommended)
# Connection string: postgresql://user:password@host:5432/launchiq
```

### Step 2: Run Alembic Migrations

```bash
# Navigate to migration directory
cd src/memory/structured

# Check current migration status
alembic current

# Upgrade to latest version
alembic upgrade head

# Verify schema was created
psql -d launchiq -c "\dt"  # List tables (should see: launches, agent_runs, hitl_checkpoints, users)
```

### Step 3: Seed Demo Data (Optional)

```bash
# From repo root
python src/data/seed.py --demo

# Verify data was seeded
python -c "
from sqlalchemy import create_engine, text
engine = create_engine('postgresql://postgres:password@localhost:5432/launchiq')
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM launches;'))
    print(f'Launches in DB: {result.scalar()}')
"
```

---

## Frontend Deployment (Vercel)

### Step 1: Connect GitHub to Vercel

1. Go to https://vercel.com/new
2. Click **Import Git Repository**
3. Select GitHub organization and `LaunchIQ` repo
4. Click **Import**

### Step 2: Configure Environment Variables

In Vercel project **Settings** → **Environment Variables**, add:

```
NEXT_PUBLIC_API_URL=https://api.launchiq.io
CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...
```

### Step 3: Deploy Frontend

**Automatic (recommended):**
- Push to `main` branch → Vercel auto-deploys
- Production deployments go to https://launchiq.vercel.app

**Manual deployment:**
```bash
cd src/apps/web
vercel --prod
```

### Step 4: Verify Frontend

```bash
curl -I https://launchiq.vercel.app
# Expected: HTTP/1.1 200 OK

# Check API connectivity
curl https://launchiq.vercel.app/api/health
# Expected: {"status": "ok"}
```

---

## Backend Deployment (AWS CDK)

### Step 1: Initialize AWS CDK Stack

```bash
cd src/infra/aws

# Install CDK dependencies
npm install

# Bootstrap CDK (one-time only per AWS account)
cdk bootstrap aws://${AWS_ACCOUNT_ID}/${AWS_REGION}
```

### Step 2: Deploy Database (RDS)

```bash
# Deploy RDS PostgreSQL cluster
cdk deploy RDSStack --require-approval never

# Extract connection endpoint
aws rds describe-db-clusters \
  --db-cluster-identifier launchiq-db \
  --query 'DBClusters[0].Endpoint' \
  --output text
```

### Step 3: Deploy Cache (ElastiCache)

```bash
# Deploy Redis cluster
cdk deploy CacheStack --require-approval never

# Extract endpoint
aws elasticache describe-cache-clusters \
  --cache-cluster-id launchiq-redis \
  --show-cache-node-info \
  --query 'CacheClusters[0].CacheNodes[0].Endpoint'
```

### Step 4: Build & Push Docker Image

```bash
# Build API image
docker build \
  -f src/infra/docker/Dockerfile.api \
  -t launchiq-api:latest \
  .

# Tag for ECR
docker tag launchiq-api:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/launchiq-api:latest

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Push image
docker push \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/launchiq-api:latest
```

### Step 5: Deploy ECS Service

```bash
# Deploy ECS cluster + Fargate service
cdk deploy ECSStack --require-approval never

# Watch deployment progress
aws ecs describe-services \
  --cluster launchiq-prod \
  --services launchiq-api \
  --query 'services[0].{Status: status, DesiredCount: deployments[0].desiredCount}'
```

### Step 6: Run Database Migrations on Production

```bash
# Get RDS endpoint
RDS_ENDPOINT=$(aws rds describe-db-clusters \
  --db-cluster-identifier launchiq-db \
  --query 'DBClusters[0].Endpoint' \
  --output text)

# Run Alembic against production DB
cd src/memory/structured
DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@${RDS_ENDPOINT}:5432/launchiq \
  alembic upgrade head
```

### Step 7: Verify Backend

```bash
# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names launchiq-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

# Health check
curl https://${ALB_DNS}/api/v1/health
# Expected: {"status": "ok"}

# Database connectivity
curl -H "Authorization: Bearer ${DEV_BEARER_TOKEN}" \
  https://${ALB_DNS}/api/v1/launches
# Expected: {"launches": [...]}
```

---

## Verification & Health Checks

### Frontend Verification

```bash
# 1. Homepage loads
curl -I https://launchiq.vercel.app
echo "✅ Frontend responds"

# 2. Clerk auth is configured
curl -s https://launchiq.vercel.app | grep -q "clerk"
echo "✅ Clerk auth on page"

# 3. API proxy configured
curl -s https://launchiq.vercel.app/api/health
echo "✅ API proxy works"
```

### Backend Verification

```bash
# 1. API health
curl https://api.launchiq.io/api/v1/health
# Response: {"status": "ok", "version": "0.1.0"}

# 2. Database connectivity
curl -H "Authorization: Bearer ${DEV_TOKEN}" \
  https://api.launchiq.io/api/v1/launches
# Response: {"launches": [...]}

# 3. Redis connectivity (via Celery)
curl -H "Authorization: Bearer ${DEV_TOKEN}" \
  https://api.launchiq.io/api/v1/agents/status
# Response: {"agents": [...]}

# 4. Check logs for errors
aws logs tail /ecs/launchiq-api --follow
```

### Full E2E Health Check Script

```bash
#!/bin/bash
set -e

echo "🎯 LaunchIQ Production Health Check"
echo "=================================="

echo -n "Frontend... "
curl -sf https://launchiq.vercel.app > /dev/null && echo "✅" || echo "❌"

echo -n "API health... "
curl -sf https://api.launchiq.io/api/v1/health > /dev/null && echo "✅" || echo "❌"

echo -n "Database... "
curl -sf -H "Authorization: Bearer ${DEV_TOKEN}" \
  https://api.launchiq.io/api/v1/launches > /dev/null && echo "✅" || echo "❌"

echo -n "Observability... "
curl -sf https://cloud.langfuse.com/api/health > /dev/null && echo "✅" || echo "❌"

echo ""
echo "✅ All systems operational"
```

---

## Troubleshooting

### Frontend Issues

**Vercel build fails:**
```bash
# Check build logs
vercel logs https://launchiq.vercel.app --follow

# Common causes:
# - Missing env vars: check Vercel project Settings → Environment Variables
# - TypeScript errors: run `npx tsc --noEmit` locally
# - Dependencies: check pnpm.lock is committed

# Fix: Rebuild
vercel --prod --force
```

**API connectivity error:**
```bash
# Check NEXT_PUBLIC_API_URL is set correctly
echo $NEXT_PUBLIC_API_URL

# Verify API endpoint is accessible
curl -I https://api.launchiq.io/api/v1/health

# Check CORS headers
curl -I -H "Origin: https://launchiq.vercel.app" \
  https://api.launchiq.io/api/v1/health
```

### Backend Issues

**ECS task failing to start:**
```bash
# Check task logs
aws logs tail /ecs/launchiq-api --follow

# Common causes:
# - Database connection failed: check RDS security group inbound rules
# - Environment variables not set: check ECS task definition
# - Image not found in ECR: check image tag matches

# Restart service
aws ecs update-service \
  --cluster launchiq-prod \
  --service launchiq-api \
  --force-new-deployment
```

**Database migration failed:**
```bash
# Check Alembic status
cd src/memory/structured
alembic current  # Shows current revision
alembic history  # Shows all revisions

# Rollback to previous version
alembic downgrade -1

# Try upgrading again with verbose output
alembic upgrade head -v
```

**API returning 502 (Bad Gateway):**
```bash
# Check ECS service health
aws ecs describe-services \
  --cluster launchiq-prod \
  --services launchiq-api \
  --query 'services[0].[runningCount,desiredCount,status]'

# Check task issues
aws ecs describe-tasks \
  --cluster launchiq-prod \
  --tasks $(aws ecs list-tasks \
    --cluster launchiq-prod \
    --query 'taskArns[0]' \
    --output text) \
  --query 'tasks[0].containers[0].lastStatus'

# Restart service
aws ecs update-service \
  --cluster launchiq-prod \
  --service launchiq-api \
  --force-new-deployment
```

---

## Rollback Procedures

### Frontend Rollback (Vercel)

```bash
# List recent deployments
vercel deployments --prod

# Rollback to previous stable version
vercel rollback launchiq.vercel.app

# Verify rollback
curl https://launchiq.vercel.app
```

### Backend Rollback (AWS ECS)

```bash
# Get previous image revision
aws ecr describe-images \
  --repository-name launchiq-api \
  --query 'imageDetails[].{Tag:imageTags[0],Pushed:imagePushedAt}' \
  --sort-by imagePushedAt

# Update ECS task definition to use previous image
aws ecs update-service \
  --cluster launchiq-prod \
  --service launchiq-api \
  --force-new-deployment

# Verify rollback
curl https://api.launchiq.io/api/v1/health
```

### Database Rollback (Alembic)

```bash
# Check current revision
cd src/memory/structured
alembic current

# Rollback one migration
alembic downgrade -1

# Or rollback to specific revision
alembic downgrade 001_initial_schema

# Verify
psql -d launchiq -c "\dt"  # Check tables
```

---

## Monitoring & Alerting

### CloudWatch Dashboards

```bash
# View API error rate
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=launchiq-api \
  --start-time 2026-04-09T00:00:00Z \
  --end-time 2026-04-10T00:00:00Z \
  --period 300 \
  --statistics Average
```

### Slack Alerts

Configured in Vercel + CloudWatch to notify `#launchiq-alerts`:
- Build failures
- Deploy status
- API errors (>1% error rate)
- Database connectivity issues

---

## Deployment Checklist (Final)

Before marking as "Live":

- [ ] Frontend loads without errors
- [ ] API health endpoint responds
- [ ] Database schema migrated successfully
- [ ] User signup/login works (Clerk)
- [ ] Create launch endpoint works
- [ ] Agent pipeline starts and streams
- [ ] HITL checkpoint works
- [ ] Brief/personas/strategy/content display correctly
- [ ] Integrations (HubSpot/Slack/GA4) configurable
- [ ] Error logging to Sentry functional
- [ ] Eval tracing to Langfuse functional
- [ ] SSL certificate valid (HTTPS)
- [ ] DNS records pointing to ALB (backend) and Vercel (frontend)
- [ ] Monitoring/alerting active
- [ ] Backups configured (RDS automated backups enabled)

---

**Deployment Support:** Issues? Contact DevOps team or check logs:

```bash
# All logs in one place
aws logs tail /ecs/launchiq-api /aws/rds/cluster/launchiq --follow
```
