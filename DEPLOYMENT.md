# LaunchIQ Deployment Quick Start

**Status:** Production-Ready  
**Last Updated:** 2026-04-09

---

## 🚀 30-Minute Deployment

### Prerequisites (5 min)

- [ ] GitHub account with admin access to repo
- [ ] AWS account with IAM credentials
- [ ] Vercel account linked to GitHub
- [ ] Docker installed locally
- [ ] AWS CLI v2 configured: `aws sts get-caller-identity`

### Phase 1: Setup Secrets (5 min)

```bash
# 1. Generate encryption key
ENCRYPTION_KEY=$(openssl rand -hex 16)
echo "Save this: $ENCRYPTION_KEY"

# 2. Add to GitHub Secrets
# Go to: Repo Settings → Secrets and variables → Actions
# Add these secrets:
#   ANTHROPIC_API_KEY: (from https://console.anthropic.com)
#   INTEGRATION_ENCRYPTION_KEY: $ENCRYPTION_KEY
#   OPENAI_API_KEY: (from https://platform.openai.com)
#   VERCEL_TOKEN: (from https://vercel.com/account/tokens)
#   AWS_ACCESS_KEY_ID: (from AWS IAM)
#   AWS_SECRET_ACCESS_KEY: (from AWS IAM)
```

### Phase 2: Verify Readiness (5 min)

```bash
# Run pre-deployment checks
chmod +x scripts/pre-deploy-check.sh
./scripts/pre-deploy-check.sh

# Expected output: ✅ All checks passed — Ready to deploy! 🚀
```

### Phase 3: Deploy Frontend (5 min)

```bash
# Deploy to Vercel
export VERCEL_TOKEN="your-vercel-token"
chmod +x scripts/deploy.sh
./scripts/deploy.sh frontend

# Verify
curl https://launchiq.vercel.app
```

### Phase 4: Deploy Backend (15 min)

```bash
# Deploy to AWS
export AWS_ACCOUNT_ID="your-account-id"
export AWS_REGION="us-east-1"
./scripts/deploy.sh backend

# Monitor logs
aws logs tail /ecs/launchiq-api --follow
```

### Phase 5: Verify Health (5 min)

```bash
# Run health checks
chmod +x scripts/health-check.sh
./scripts/health-check.sh

# Expected output: 🎉 All systems operational!
```

---

## 📋 Detailed Deployment Resources

| Resource | Purpose | Time |
|---|---|---|
| **[Deployment Guide](../docs/02_Technical_Feasibility/09_Deployment_Guide.md)** | Complete step-by-step instructions with troubleshooting | 30 min read |
| **[deploy.sh](../scripts/deploy.sh)** | One-command deployment script (frontend/backend/full) | Run once |
| **[pre-deploy-check.sh](../scripts/pre-deploy-check.sh)** | Pre-deployment validation checklist | 2 min run |
| **[health-check.sh](../scripts/health-check.sh)** | Production health verification | 1 min run |

---

## 🔐 GitHub Secrets Needed

**Run this to add all secrets at once:**

```bash
# Set your values first
export ANTHROPIC_API_KEY="sk-ant-..."
export INTEGRATION_ENCRYPTION_KEY="32-char-hex-key"
export OPENAI_API_KEY="sk-..."
export VERCEL_TOKEN="your-token"
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
export LANGFUSE_PUBLIC_KEY="pk-..."
export LANGFUSE_SECRET_KEY="sk-..."

# Add secrets via GitHub CLI
gh secret set ANTHROPIC_API_KEY -b "$ANTHROPIC_API_KEY"
gh secret set INTEGRATION_ENCRYPTION_KEY -b "$INTEGRATION_ENCRYPTION_KEY"
gh secret set OPENAI_API_KEY -b "$OPENAI_API_KEY"
gh secret set VERCEL_TOKEN -b "$VERCEL_TOKEN"
gh secret set AWS_ACCESS_KEY_ID -b "$AWS_ACCESS_KEY_ID"
gh secret set AWS_SECRET_ACCESS_KEY -b "$AWS_SECRET_ACCESS_KEY"
gh secret set AWS_REGION -b "$AWS_REGION"
gh secret set LANGFUSE_PUBLIC_KEY -b "$LANGFUSE_PUBLIC_KEY"
gh secret set LANGFUSE_SECRET_KEY -b "$LANGFUSE_SECRET_KEY"

# Verify
gh secret list
```

---

## 🎯 Deployment Checklist

Before deploying, confirm:

```bash
# 1. Code quality
pytest src/ --cov=src                    # Unit tests pass
cd src/apps/web && pnpm build            # Frontend builds
cd src/infra/aws && npx cdk synth        # CDK synthesizes

# 2. No uncommitted changes
git status --porcelain | wc -l            # Should output: 0

# 3. All secrets added
gh secret list | wc -l                    # Should be >= 9

# 4. Credentials configured
aws sts get-caller-identity                # AWS credentials work
vercel whoami                              # Vercel token works
```

---

## 📍 Endpoints After Deployment

| Service | URL | Purpose |
|---|---|---|
| **Frontend** | https://launchiq.vercel.app | Web application |
| **API** | https://api.launchiq.io/api/v1 | REST API |
| **Health** | https://api.launchiq.io/api/v1/health | Status check |
| **Docs** | https://api.launchiq.io/docs | API documentation |

---

## 🔄 Common Operations

### Check Deployment Status
```bash
# Frontend (Vercel)
vercel status

# Backend (AWS ECS)
aws ecs describe-services \
  --cluster launchiq-prod \
  --services launchiq-api \
  --query 'services[0].[runningCount,desiredCount,status]'
```

### View Logs
```bash
# Frontend build logs
vercel logs https://launchiq.vercel.app --follow

# Backend application logs
aws logs tail /ecs/launchiq-api --follow

# Database migration logs
cd src/memory/structured && alembic current
```

### Rollback Deployment
```bash
# Frontend rollback (5 seconds)
vercel rollback launchiq.vercel.app

# Backend rollback (5-10 minutes)
aws ecs update-service \
  --cluster launchiq-prod \
  --service launchiq-api \
  --force-new-deployment
```

---

## ⚠️ Troubleshooting

**Frontend build fails:**
```bash
cd src/apps/web && npx tsc --noEmit  # Check TypeScript
pnpm build                            # Full build
```

**API won't start:**
```bash
aws logs tail /ecs/launchiq-api --follow  # Check logs
aws ecs describe-task-definition \
  --task-definition launchiq-api          # Check task definition
```

**Database connection error:**
```bash
# Verify RDS is accessible
psql -h ${RDS_ENDPOINT} -U postgres -d launchiq -c "SELECT 1;"

# Check security group inbound rules
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=launchiq-db"
```

---

## 📞 Support

For issues during deployment:
1. Run `./scripts/health-check.sh` to identify failures
2. Check [Deployment Guide](../docs/02_Technical_Feasibility/09_Deployment_Guide.md) troubleshooting section
3. Review logs: `aws logs tail /ecs/launchiq-api --follow`
4. Rollback if needed: `./scripts/deploy.sh rollback-backend`

---

## ✅ Success Criteria

Deployment is complete when:

- ✅ `./scripts/pre-deploy-check.sh` passes
- ✅ `./scripts/health-check.sh` shows all green
- ✅ https://launchiq.vercel.app loads without errors
- ✅ https://api.launchiq.io/api/v1/health returns `{"status": "ok"}`
- ✅ User can sign in with Clerk
- ✅ Can create a launch and see agents streaming
- ✅ Can approve/reject HITL checkpoints
- ✅ Final brief generates and displays correctly

---

**Ready to ship? 🚀**

```bash
./scripts/deploy.sh full && ./scripts/health-check.sh
```
