# Agentic AI — Platform References 2026
## How Claude / OpenAI / Gemini / AWS / Azure Are Building Agents

**Author:** Venkata Anil Kumar
**Date:** 2026-04-09
**Status:** Reference Document — Work in Progress

---

## 1. Anthropic — Claude

**Philosophy:** Simple, composable patterns over complex frameworks. Start simple, add complexity only when needed.

| Pattern | How Claude Does It |
|---------|-------------------|
| Orchestrator-Workers | Orchestrator dispatches subagents with isolated context windows |
| Tool Use | MCP (Model Context Protocol) as the standard tool connectivity layer |
| Memory | Context engineering — fill the window with exactly the right information |
| HITL | Plan Mode + approval gates before execution |
| Observability | Built-in tracing via Claude Managed Agents (launched April 2026) |
| Deployment | Claude Managed Agents — Anthropic handles sandboxed execution, state, checkpointing |

**Key 2026 Release:** Claude Managed Agents (Public Beta, April 8 2026) — define tasks + tools + guardrails, Anthropic handles everything else.

**Core Patterns:** Prompt Chaining → Routing → Parallelization → Orchestrator-Workers → Evaluator-Optimizer

### References
- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic — Claude Managed Agents Complete Guide 2026](https://www.the-ai-corner.com/p/claude-managed-agents-guide-2026)
- [Anthropic — Claude Code Advanced Patterns: Subagents and MCP](https://www.anthropic.com/webinars/claude-code-advanced-patterns)
- [Agentic Workflows with Claude: Architecture Patterns & Production Patterns](https://medium.com/@reliabledataengineering/agentic-workflows-with-claude-architecture-patterns-design-principles-production-patterns-72bbe4f7e85a)
- [4 Agentic AI Patterns in Claude Code](https://wmedia.es/en/tips/claude-code-agentic-ai-five-patterns)

---

## 2. OpenAI — GPT + Agents SDK

**Philosophy:** Lightweight, few abstractions. Provider-agnostic. Production-ready upgrade of Swarm.

| Component | Description |
|-----------|-------------|
| **Agent** | LLM + instructions + tools + memory + behavior |
| **Runner** | Conductor — handles retries, tool selection, streaming |
| **Handoffs** | Agents delegate to other agents for specialized tasks |
| **Guardrails** | Input + output validation layer |
| **Tracing** | Built-in visualization, debugging, monitoring |
| **Voice Agents** | gpt-realtime-1.5 with interruption detection |

**Key 2026 Feature:** 100+ LLM support — not locked to OpenAI models. Built for multi-agent workflows with minimal code.

### References
- [OpenAI Agents SDK — Official Docs](https://openai.github.io/openai-agents-python/)
- [OpenAI — Agents SDK API Guide](https://developers.openai.com/api/docs/guides/agents-sdk)
- [OpenAI — New Tools for Building Agents](https://openai.com/index/new-tools-for-building-agents/)
- [OpenAI Agents SDK — GitHub Repository](https://github.com/openai/openai-agents-python)
- [Building Production-Ready AI Agents in 2026 using OpenAI Agent SDK](https://medium.com/@sausi/in-2026-building-ai-agents-isnt-about-prompts-it-s-about-architecture-15f5cfc93950)
- [Unpacking OpenAI's Agents SDK: Technical Deep Dive](https://mtugrull.medium.com/unpacking-openais-agents-sdk-a-technical-deep-dive-into-the-future-of-ai-agents-af32dd56e9d1)

---

## 3. Google — Gemini + ADK

**Philosophy:** Agentic models by design. Gemini 2.5/3 are built for tool use natively, not retrofitted.

| Component | Description |
|-----------|-------------|
| **ADK** | Agent Development Kit — Python, TypeScript, Go, Java |
| **Built-in Tools** | Google Search, Maps, Code Execution natively |
| **Function Calling** | Define + connect custom tools and APIs |
| **Thinking Mode** | Enhanced reasoning + planning layer |
| **Long Context** | 1M–2M tokens — agents maintain state over complex tasks |
| **Frameworks** | LangGraph, CrewAI, LlamaIndex, Composio supported |

**Key 2026 Feature:** Gemini 3 — explicitly built as an agentic model. Native tool use, long context, multi-agent orchestration via ADK.

### References
- [Google — Agent Development Kit (ADK) Official Docs](https://google.github.io/adk-docs/)
- [Google — Building Agents with Gemini and Open Source Frameworks](https://developers.googleblog.com/building-agents-google-gemini-open-source-frameworks/)
- [Google — Gemini API Agents Overview](https://ai.google.dev/gemini-api/docs/agents)
- [Google — Building AI Agents with Gemini 3 and Open Source Frameworks](https://developers.googleblog.com/building-ai-agents-with-google-gemini-3-and-open-source-frameworks/)
- [Google Cloud — Agent Designer Overview](https://docs.cloud.google.com/gemini/enterprise/docs/agent-designer)
- [Building Multi-Agent AI System with Gemini 3 and Google Cloud](https://medium.com/google-cloud/build-multi-agent-ai-system-with-gemini-3-1-google-cloud-single-bot-orchestrated-intelligence-dc0c111e30e7)
- [Building Secure, Governed Multi-Agent Systems with Gemini on Google Cloud](https://medium.com/@amiragamalyassin/generative-ai-on-google-cloud-building-secure-governed-and-enterprise-ready-multi-agent-systems-c9bad87f5989)

---

## 4. AWS — Bedrock AgentCore

**Philosophy:** Enterprise-grade, governed, observable agents with policy controls outside the reasoning loop.

| Component | Description |
|-----------|-------------|
| **Knowledge Bases** | Managed RAG — S3 → embeddings → retrieval |
| **Agents** | Managed agentic loop — Lambda tools, conversation history |
| **AgentCore Runtime** | Secure serverless agent deployment |
| **AgentCore Gateway** | Unified tool access layer |
| **AgentCore Memory** | Intelligent context retention across sessions |
| **AgentCore Policy** | Fine-grained action control — verified outside reasoning loop (GA March 2026) |
| **Observability** | OpenTelemetry — CloudWatch, DataDog, LangSmith |

**Cognitive Loop:** Perception → Semantic Understanding → Reasoning & Planning → Execution

**Key 2026 Feature:** AgentCore Policy — enterprise governance layer that verifies agent actions *before* they reach tools or data, outside the agent's own reasoning.

### References
- [AWS — Amazon Bedrock Agents Official Page](https://aws.amazon.com/bedrock/agents/)
- [AWS — Amazon Bedrock Overview](https://aws.amazon.com/bedrock/)
- [AWS — Build AI Agents with AgentCore using CloudFormation](https://aws.amazon.com/blogs/machine-learning/build-ai-agents-with-amazon-bedrock-agentcore-using-aws-cloudformation/)
- [AWS Bedrock in 2026: Build Your First AI Agent](https://dev.to/ajbuilds/aws-bedrock-in-2026-what-it-actually-is-and-how-to-build-your-first-ai-agent-on-it-gf8)
- [Building AI Agents in AWS: Hands-On Bedrock Walkthrough](https://interworks.com/blog/2026/03/06/building-ai-agents-in-aws-a-hands-on-amazon-bedrock-walkthrough/)
- [AI Agents on AWS: Advanced Architecture with Bedrock and RAG](https://medium.com/@sendoamoronta/ai-agents-on-aws-advanced-architecture-with-amazon-bedrock-and-rag-874e089f4dfd)
- [Building AI Agents on AWS in 2025: Bedrock, AgentCore, and Beyond](https://dev.to/aws-builders/building-ai-agents-on-aws-in-2025-a-practitioners-guide-to-bedrock-agentcore-and-beyond-4efn)

---

## 5. Microsoft — Azure AI Foundry + Agent Framework

**Philosophy:** Enterprise-grade, stateful, governed. Direct successor to Semantic Kernel + AutoGen combined.

| Component | Description |
|-----------|-------------|
| **Agent Framework** | Successor to AutoGen + Semantic Kernel — open-source |
| **Threads** | Managed conversation history (stateful) |
| **Runs** | Managed reasoning loop |
| **Tools Tab** | 1,400+ business system integrations — MCP, A2A, SharePoint, Fabric |
| **Memory** | Managed long-term memory — auto extraction + retrieval (Public Preview 2026) |
| **Multi-agent** | Visual workflow builder in Azure Portal |
| **Governance Toolkit** | Released April 2026 — governs autonomous agent actions |

**Key 2026 Feature:** Agent Governance Toolkit (April 2026) — addresses the gap between making agents autonomous and keeping them governed at enterprise scale.

### References
- [Microsoft — AI Agent Orchestration Patterns (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Microsoft — Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/)
- [Microsoft — Azure AI Architecture Design Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/)
- [Architecting Autonomous Agents: Azure AI Foundry Agent Service Deep Dive](https://dev.to/jubinsoni/architecting-autonomous-agents-a-deep-dive-into-azure-ai-foundry-agent-service-4jnk)
- [Microsoft — Agent Governance Toolkit (April 2026)](https://www.helpnetsecurity.com/2026/04/03/microsoft-ai-agent-governance-toolkit/)
- [What's New in Microsoft Foundry — Dec 2025 & Jan 2026](https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-dec-2025-jan-2026/)
- [Microsoft AI Agents: Deep Dive into Frameworks and Platforms](https://www.devoteam.com/expert-view/microsoft-ai-agents/)

---

## Side-by-Side Comparison

| Dimension | Anthropic | OpenAI | Google | AWS | Azure |
|-----------|-----------|--------|--------|-----|-------|
| **Agent SDK** | Claude Agent SDK | Agents SDK | ADK | AgentCore | Agent Framework |
| **Tool Protocol** | MCP | Function Calling | Function Calling | Lambda Tools | MCP + A2A |
| **Memory** | Redis + Qdrant + PG | Thread-based | Long Context (1M+) | AgentCore Memory | Managed Memory |
| **Orchestration** | A2A Protocol | Handoffs | ADK Multi-agent | Multi-agent Bedrock | AutoGen patterns |
| **Governance** | Managed Agents | Guardrails | ADK Policies | AgentCore Policy | Governance Toolkit |
| **Observability** | LangSmith | Built-in Tracing | Cloud Trace | OpenTelemetry | Azure Monitor |
| **Deployment** | Managed (April 2026) | Cloud / Self-host | Vertex AI | Serverless Lambda | Azure Foundry |
| **Differentiator** | Simplicity + Safety | Lightweight + Multi-LLM | Native agentic model | Enterprise policy controls | 1400+ integrations |

---

## Common Patterns Across All 5 in 2026

| Pattern | Description |
|---------|-------------|
| **MCP + A2A** | Becoming the universal standard for tool and agent communication |
| **Managed Execution** | All providers moving toward handling the agent loop for you |
| **Policy / Governance** | Enterprise controls verified *outside* the agent's reasoning loop |
| **Long-term Memory** | All platforms shipping managed memory stores in 2026 |
| **Observability First** | Tracing, evals, and cost tracking are now table stakes |
| **HITL** | Human approval built into the loop, not bolted on after |

---

## Additional General References

- [AI Agent Landscape 2025–2026: Technical Deep Dive](https://tao-hpu.medium.com/ai-agent-landscape-2025-2026-a-technical-deep-dive-abda86db7ae2)
- [Best Open Source AI Agent Frameworks 2026](https://aihaven.com/guides/best-open-source-ai-agent-frameworks-2026/)
- [Agent Design Patterns — Lance Martin](https://rlancemartin.github.io/2026/01/09/agent_design/)
- [Agentic AI Architecture: Building Autonomous AI Systems in 2026](https://calmops.com/architecture/agentic-ai-architecture-autonomous-ai-systems/)
- [AI Agent Architecture for Enterprise: From Chatbot to Autonomous Workflow](https://www.hypertrends.com/2026/04/ai-agent-architecture-enterprise/)
- [AI Agent Architecture Diagram: 2026 Complete Guide](https://a-listware.com/blog/ai-agent-architecture-diagram)

---

*Last updated: 2026-04-09 — References to be expanded with design pattern deep-dives.*
