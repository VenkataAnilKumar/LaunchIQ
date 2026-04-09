# Security & Compliance Overview
## LaunchIQ — AI-Powered Product Launch Intelligence Platform

**Version:** 1.0
**Author:** Venkata Anil Kumar
**Date:** 2026-04-09

---

## 1. Security Philosophy

LaunchIQ is designed with **security-by-default** — particularly critical for a B2B SaaS platform that handles proprietary product strategies, marketing plans, and competitive intelligence belonging to our customers.

Core principles:
- **Zero trust:** Every request authenticated and authorized, no implicit trust
- **Least privilege:** Each agent and service has only the permissions it needs
- **Data isolation:** Strict tenant separation — no cross-user data leakage
- **Transparency:** Full audit trail of all agent actions
- **Defense in depth:** Multiple security layers, no single point of failure

---

## 2. Authentication & Authorization

| Layer | Implementation | Details |
|-------|---------------|---------|
| User auth | Clerk (JWT) | OAuth2 (Google, GitHub) + magic links |
| API auth | JWT validation | Bearer token on every API request |
| Row-level security | Supabase RLS | Database-level tenant isolation |
| Service-to-service | API keys (env vars) | Internal services use secret rotation |
| Agent authorization | Scoped permissions | Each agent has read/write scope per resource |

**Session Management:**
- JWT expiry: 1 hour (access token), 7 days (refresh token)
- Session state in Redis with 24-hour TTL
- Automatic logout on suspicious activity

---

## 3. Data Security

### Encryption
- **In transit:** TLS 1.3 on all connections (HTTPS enforced, HSTS headers)
- **At rest:** AES-256 encryption on all database volumes (Supabase managed)
- **Secrets:** AWS Secrets Manager for all API keys (never in code or env files in production)
- **Backups:** Encrypted daily backups with 30-day retention

### Data Isolation (Multi-tenancy)
- PostgreSQL Row Level Security (RLS) policies per user/org
- Qdrant namespace separation per tenant
- Redis key prefixing per user session
- All queries include `user_id` or `org_id` filter — enforced at ORM layer

### PII Handling
- User emails and names stored in Clerk (not duplicated in our DB)
- Only anonymized user IDs stored in analytics events (PostHog)
- Product descriptions and strategies stored encrypted
- No PII passed to Claude API (product descriptions sanitized)

---

## 4. Application Security

### OWASP Top 10 Coverage

| Vulnerability | Mitigation |
|---------------|-----------|
| Injection (SQL/Command) | SQLAlchemy parameterized queries, no raw SQL |
| Broken Auth | Clerk handles auth; JWT validation on all routes |
| Sensitive Data Exposure | Encryption at rest + in transit; secrets in AWS SM |
| XXE | JSON-only APIs; no XML parsing |
| Broken Access Control | RLS + route-level auth checks |
| Security Misconfiguration | Security headers (CORS, CSP, HSTS) enforced |
| XSS | React escaping by default; CSP headers; agent output sanitized |
| Insecure Deserialization | Pydantic validation on all inputs; no pickle |
| Vulnerable Components | Dependabot alerts; monthly dependency updates |
| Insufficient Logging | Full audit logs in PostgreSQL + Sentry |

### AI-Specific Security

| Threat | Mitigation |
|--------|-----------|
| Prompt injection | User inputs sanitized and wrapped in system-level context before passing to agents |
| Jailbreaking | Anthropic's built-in safety filters + output validation layer |
| Data poisoning | Research data from Tavily validated for source credibility |
| Model output hallucination | Citations required; structured output schema validation |
| Sensitive data leakage in prompts | No customer PII included in agent prompts |
| Unauthorized tool use | MCP tool permissions scoped per agent; no cross-agent tool access |

---

## 5. Infrastructure Security

| Component | Security Measure |
|-----------|----------------|
| Vercel (frontend) | Automatic HTTPS, DDoS protection, edge firewall |
| AWS Lambda | VPC isolation, IAM least-privilege roles |
| Supabase | Managed security, RLS, SOC 2 Type II compliant provider |
| Redis | Auth enabled, no public exposure, VPC-internal only |
| Qdrant | API key auth, no public endpoint |
| GitHub | Branch protection, required reviews, Dependabot, secret scanning |

---

## 6. API Security

- **Rate limiting:** 100 req/min per user; 10 agent runs/hour on free tier
- **Input validation:** Pydantic schemas validate all request bodies
- **CORS:** Allowlist of trusted origins only
- **Security headers:** HSTS, X-Frame-Options, X-Content-Type-Options, CSP
- **API versioning:** `/api/v1/` — breaking changes require new version
- **Request size limits:** 10MB max payload to prevent DoS

---

## 7. Compliance Posture

### GDPR (General Data Protection Regulation)
| Requirement | Status |
|-------------|--------|
| Lawful basis for processing | Consent (signup) + Contractual necessity |
| Right to access | Data export API endpoint (planned MVP) |
| Right to erasure | Account deletion removes all user data |
| Data portability | JSON export of all user-generated content |
| Privacy policy | Published at launch |
| Data processing agreement | Available for business customers |
| Data residency | EU region available (Supabase EU) |

### CCPA (California Consumer Privacy Act)
| Requirement | Status |
|-------------|--------|
| Right to know | In-app data visibility page |
| Right to delete | Account deletion flow |
| Do not sell | No data sold; explicit in privacy policy |
| Opt-out of analytics | PostHog opt-out via cookie consent |

### SOC 2 Readiness (Future)
- Audit logging in place from day one
- Access control policies documented
- Change management via GitHub PRs with required reviews
- Incident response plan documented
- Target: SOC 2 Type I within 12 months of public launch

---

## 8. Incident Response Plan

### Severity Levels
| Level | Definition | Response Time |
|-------|-----------|--------------|
| P0 | Data breach, service down | 15 minutes |
| P1 | Security vulnerability discovered | 1 hour |
| P2 | Degraded service, non-critical bug | 4 hours |
| P3 | Minor issue, no user impact | 24 hours |

### Response Steps (P0/P1)
1. **Detect:** Sentry alert or user report
2. **Contain:** Disable affected endpoint or user account
3. **Assess:** Determine scope and data exposure
4. **Notify:** Inform affected users within 72 hours (GDPR requirement)
5. **Remediate:** Deploy fix, rotate secrets if needed
6. **Post-mortem:** Document root cause and prevention measures

---

## 9. Anthropic API Usage Policy Compliance

- No customer data used for model training (confirmed with Anthropic commercial terms)
- Agent outputs do not include harmful, misleading, or illegal content (built-in safety filters)
- Rate limits respected and monitored
- API key rotation policy: every 90 days
- Usage monitored for unexpected cost spikes (LangSmith + CloudWatch alerts)
