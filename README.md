<div align="center">

# ☁️ NimbusRE

### **Your AI-Powered Kubernetes SRE Copilot**

> *Stop firefighting your cluster. Start having a conversation with it.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-FF6B35?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)](https://terraform.io)
[![Ollama](https://img.shields.io/badge/Ollama-llama3.1-black?style=for-the-badge)](https://ollama.com)

<br/>

[🚀 Quick Start](#-quick-start) &nbsp;•&nbsp; [✨ Features](#-features) &nbsp;•&nbsp; [🏗️ Architecture](#️-architecture) &nbsp;•&nbsp; [🎬 Demo](#-hackathon-demo-script) &nbsp;•&nbsp; [📦 Deploy](#-deployment)

</div>

---

## 🔥 The Problem

Every Kubernetes incident today looks like this:

```
Alert fires → Open 5 tabs → kubectl get pods → kubectl describe → grep logs
    → Google error → Slack escalate → Maybe fix it 40 minutes later
```

**This is broken.** SRE teams waste hours every week on repetitive cluster interrogation, context-switching between tools, and manual remediation commands.

---

## 💡 The Solution

NimbusRE gives your cluster a voice — and gives you an AI partner who already knows every `kubectl` command, every Helm chart operation, and every Ansible playbook you need.

```
You: "Why are pods crashing in production?"

NimbusRE: Checking pod status... analyzing logs... correlating with metrics...

  ⚠️  3 pods in CrashLoopBackOff  (ImagePullBackOff: registry auth expired)
  📋  Last 50 log lines show: "unauthorized: authentication required"
  ✅  Recommended fix: rotate imagePullSecret and restart deployment

  Shall I apply the fix? [yes / no]
```

One conversation. Zero tab-switching. Real answers.

---

## ✨ Features

### 🤖 Intelligent AI Workflows

| Mode | When to Use | What It Does |
|------|-------------|--------------|
| **Basic** | Quick diagnosis | Query → Tool loop → Instant findings |
| **Advanced** | Critical operations | Classify severity → Plan → **Human approval gate** → Execute → Verify |

### 🛠️ Tool-Augmented Operations

| Tool | Capability |
|------|-----------|
| 🔭 **Monitoring** | CPU, memory, restarts, error rates, alert status |
| 📜 **Logs** | Real-time aggregation, pattern search, error detection |
| 🩺 **Self-Healing** | Pod restart, deployment scaling, node drain, health recovery |
| 💰 **Cost Analyzer** | Waste identification, rightsizing recommendations, cost breakdown |
| ☸️ **kubectl** | Governed read/describe/logs with kubeconfig safety |
| ⛵ **Helm** | Install, upgrade, rollback, values management |
| 📡 **Ansible** | Host inventory, OS info, service status |

### 🖥️ Full-Stack Product Experience

- **Chat UI** — Next.js real-time chat with findings panel and recommendation cards
- **REST API** — FastAPI backend with OpenAPI docs at `/docs`
- **Streaming** — Live status updates as the agent works
- **Safety gates** — Advanced workflow requires explicit approval before destructive actions

### 🏗️ Infrastructure as Code

Terraform blueprints included for the full platform:

- **EKS cluster** with networking, node groups, IRSA roles
- **EC2 Ansible host** for configuration management
- **EC2 Ubuntu tool server** with pre-installed SRE tooling
- **GitHub Actions CI** for automated Terraform deployment

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Chat Interface                          │
│                  Next.js  ·  TypeScript                      │
└──────────────────────────┬──────────────────────────────────┘
                           │  REST / HTTP
┌──────────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend                            │
│              api_server.py  ·  port 8000                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
┌─────────▼──────────┐           ┌─────────▼──────────┐
│   Basic Workflow   │           │  Advanced Workflow  │
│  Quick diagnostics │           │  Approval-gated ops │
└─────────┬──────────┘           └─────────┬──────────┘
          └────────────────┬────────────────┘
                           │  LangGraph Agent Loop
          ┌────────────────▼────────────────────────┐
          │              Tool Registry               │
          │  kubectl · helm · monitoring · logs      │
          │  healing · cost-analyzer · ansible       │
          └────────────────┬────────────────────────┘
                           │
          ┌────────────────▼────────────────────────┐
          │          Ollama  (llama3.1:8b)           │
          │        Local LLM · No cloud keys         │
          └─────────────────────────────────────────┘
```

---

## 📁 Repo Structure

```text
nimbusre/
├── kubetool/                    ← 🤖 AI SRE App (main product)
│   ├── src/
│   │   ├── api/                 ← FastAPI entrypoint
│   │   ├── workflows/           ← LangGraph Basic + Advanced + Shared
│   │   ├── agents/              ← SRE agent + kubectl agent
│   │   └── tools/               ← All 7 tool integrations
│   ├── frontend/                ← Next.js chat UI
│   ├── Deploy_Scripts/          ← 9 operational shell scripts
│   └── docs/                    ← Full documentation
├── eks/                         ← ☸️  Terraform: EKS cluster
├── ec2-ansible-host/            ← 🖥️  Terraform: Ansible EC2 host
├── ec2-ubuntu-tool-server/      ← 🛠️  Terraform: Ubuntu tool server
└── .github/workflows/           ← 🔄 CI/CD: Terraform automation
```

---

## 🚀 Quick Start

> Get the full AI SRE experience running locally in under 5 minutes.

**Prerequisites:** Python 3.11+, Node.js 18+, [Ollama](https://ollama.com), `kubectl` configured

```bash
# 1. Pull the LLM model (one-time, ~5GB)
ollama pull llama3.1:8b

# 2. Start the backend
cd nimbusre/kubetool
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.api.api_server:app --reload --port 8000
```

```bash
# 3. Start the frontend (new terminal)
cd nimbusre/kubetool/frontend
npm install && npm run dev
```

| Service | URL |
|---------|-----|
| 🖥️ Chat UI | http://localhost:3000 |
| 📖 API Docs | http://localhost:8000/docs |

---

## 🎬 Hackathon Demo Script

Run these prompts live to tell the full story:

```
1. "What's the health of my cluster right now?"
   → Shows pod counts, node status, recent alerts

2. "Why are pods crashing in the default namespace?"
   → Runs kubectl describe + log analysis → Root cause

3. "Search for OOMKilled errors in the last hour"
   → Log aggregation → Pattern detection → Memory insights

4. "Scale the web deployment to 3 replicas"
   → Advanced workflow: shows approval gate before executing

5. "Find wasted resources and cost savings opportunities"
   → Cost analyzer → Rightsizing table → Dollar estimates
```

---

## 📦 Deployment

**One-command scripted deployment:**

```bash
cd nimbusre/kubetool

sudo bash Deploy_Scripts/install.sh       # Install Python 3.11 + deps
sudo bash Deploy_Scripts/deploy.sh        # Start backend service on :8000
sudo bash Deploy_Scripts/setup-nginx.sh  # Reverse proxy + domain routing
sudo bash Deploy_Scripts/setup-ssl.sh your-domain.com  # HTTPS (optional)
```

**Operations menu:**

```bash
sudo bash Deploy_Scripts/manage.sh        # Start / Stop / Restart / Logs
```

---

## 🌟 Why NimbusRE Wins

| Criteria | NimbusRE |
|----------|---------|
| **Innovation** | LLM-driven SRE with approval-gated autonomous remediation |
| **Completeness** | Frontend + Backend + IaC + CI/CD — full production stack |
| **Practicality** | Real tools, real clusters, real cost savings — not a toy |
| **Extensibility** | Drop-in new tools, swap LLMs, plug in any kubeconfig |
| **Safety** | Read-only kubectl guards + human-in-the-loop for mutations |
| **Local-first** | Runs on Ollama — no API keys, no data leaves your machine |

---

## 🔮 What's Next

- 🔐 RBAC-aware action approvals per team/role
- 🌐 Multi-cluster context switching from the UI
- 📊 Grafana / CloudWatch / Datadog observability adapters
- 🤖 Policy-based auto-remediation with configurable guardrails
- 📈 Cost anomaly alerting and spend trend dashboards
- 🗣️ Voice interface for hands-free cluster operations

---

## 📄 License

MIT — build on it, hack it, ship it.

---

<div align="center">

**Built with ☁️ + 🤖 + ☸️ for the hackathon**

*NimbusRE — because your cluster deserves better than 2 AM grep sessions*

</div>
