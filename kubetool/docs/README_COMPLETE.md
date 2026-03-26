# SREAgent: AI-Powered Kubernetes Management System

<div align="center">

![SREAgent](https://img.shields.io/badge/SREAgent-v1.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&style=flat)
![Node.js](https://img.shields.io/badge/Node.js-18+-green?logo=node.js&style=flat)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Latest-blue?logo=kubernetes&style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

**Intelligent Site Reliability Engineering Assistant for Kubernetes**

[Quick Start](#-quick-start) • [Features](#-features) • [Documentation](#-documentation) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

## 🤖 What is SREAgent?

SREAgent is an AI-powered chatbot that understands your Kubernetes cluster's health and helps you:

- 📊 **Monitor** cluster metrics, pod status, and performance
- 🔍 **Troubleshoot** issues with log analysis and diagnostics
- 🛠️ **Heal** problems automatically with self-remediation
- 💰 **Optimize** costs by identifying wasted resources
- 🚀 **Deploy** applications using Helm and Ansible

All through natural language queries to an intelligent LLM agent.

```
User: "Show me high CPU pods"
     ↓
LangGraph Workflow
     ↓
[Monitoring Tool] → Queries Prometheus → Finds CPU > 80% pods
[Logs Tool] → Checks recent pod logs → Detects error patterns
[Cost Analyzer] → Calculates pod costs → Recommends rightsizing
     ↓
Chat Response + Findings Panel + Recommendations
```

## ✨ Key Features

### 🎯 Core Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| **Natural Language Queries** | Ask questions about your cluster in plain English | ✅ |
| **Prometheus Integration** | Real-time metrics from Prometheus | ✅ |
| **Log Aggregation** | Search and analyze pod logs | ✅ |
| **Self-Healing** | Automatic pod restart, scaling, health recovery | ✅ |
| **Cost Analysis** | Identify wasted resources and optimize spending | ✅ |
| **Advanced Workflows** | Approval gates and rollback for critical actions | ✅ |
| **Dark Mode** | Beautiful dark theme UI | ✅ |
| **Mobile Responsive** | Works on desktop, tablet, mobile | ✅ |

### 🛠️ Supported Tools

- **Monitoring Tool**: CPU, memory, network, disk, pod restarts, error rates, alerts
- **Logs Tool**: Pod logs, log search, error pattern detection, label filtering
- **Healing Tool**: Pod restart, deployment scaling, node drain, health checks
- **Cost Analyzer**: Resource waste, cost breakdown, rightsizing recommendations
- **Ansible Tool**: Host software inventory, OS info, service status
- **Helm Tool**: Chart install, upgrade, rollback, values management

## 📋 Quick Start

### Prerequisites
```bash
# Required
- Python 3.8+ (backend)
- Node.js 18+ (frontend)
- kubectl configured
- Ollama running with llama2 model

# Optional (for full features)
- Prometheus (for metrics)
- Kubernetes 1.20+ cluster
```

### 5-Minute Setup

**Terminal 1 - Start Backend:**
```bash
cd kubetool
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.api.api_server:app --reload --port 3001
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Browser:**
```
Open http://localhost:3000
```

### First Query
Try: **"Show me high CPU pods"**

👉 **See [QUICK_START.md](QUICK_START.md) for detailed setup**

## 🏗️ Architecture

```
┌───────────────────────────────────────────────┐
│         React/Next.js Frontend                │
│  (ChatInterface + FindingsPanel + Status)     │
└───────────────────────────────────────────────┘
                      ↓ REST API
┌───────────────────────────────────────────────┐
│        FastAPI Backend Server (port 3001)     │
│  /api/sre → Routes to LangGraph workflows     │
└───────────────────────────────────────────────┘
                      ↓
┌───────────────────────────────────────────────┐
│   LangGraph Workflow Orchestration            │
│  Basic: Process → Tools → Synthesize          │
│  Advanced: Classify → Plan → Approve → Exec   │
└───────────────────────────────────────────────┘
                      ↓
┌───────────────────────────────────────────────┐
│      LangChain Tools + Ollama LLM             │
│  [Monitoring] [Logs] [Healing] [Cost] [etc]  │
└───────────────────────────────────────────────┘
                      ↓
┌───────────────────────────────────────────────┐
│   Kubernetes & External Systems               │
│  kubectl | Prometheus | Logs API | Cost APIs │
└───────────────────────────────────────────────┘
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[INDEX.md](INDEX.md)** | 📖 Complete documentation index |
| **[QUICK_START.md](QUICK_START.md)** | 🚀 5-minute setup guide |
| **[SETUP_AND_DEPLOYMENT.md](SETUP_AND_DEPLOYMENT.md)** | 📦 Full installation & deployment |
| **[SRE_TOOLS_README.md](SRE_TOOLS_README.md)** | 🛠️ Tool documentation & API reference |
| **[LANGGRAPH_INTEGRATION.md](LANGGRAPH_INTEGRATION.md)** | 📊 Workflow orchestration guide |
| **[ANSIBLE_README.md](ANSIBLE_README.md)** | 🔧 Ansible tool documentation |
| **[HELM_README.md](HELM_README.md)** | ⚓ Helm tool documentation |

## 🚀 Usage Examples

### Monitor Your Cluster
```
User: "What's the health of my cluster?"
SREAgent: Queries Prometheus, checks logs, returns overall status
```

### Troubleshoot Issues
```
User: "Get logs from failed pods"
SREAgent: Finds pods in error state, retrieves logs, suggests fixes
```

### Optimize Costs
```
User: "Find wasted resources"
SREAgent: Detects over-provisioned pods, rightsizing recommendations
```

### Auto-Remediate (Advanced Mode)
```
User: "Restart the crashing pod"
SREAgent: 
  1. Classifies as maintenance
  2. Creates remediation plan
  3. Requests approval
  4. Executes restart
  5. Verifies pod health
```

## 🔧 Running the System

### Development Mode
```bash
# Terminal 1: Backend
cd kubetool
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api_server.py

# Terminal 2: Frontend
cd kubetool/frontend
npm run dev

# Terminal 3: Monitor Ollama (if needed)
ollama serve
```

### Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Access at http://localhost:3000
```

### Production Deployment
```bash
# Build and push Docker images
docker build -t sreagent-backend:1.0 .
docker build -t sreagent-frontend:1.0 ./frontend

# Deploy to Kubernetes
kubectl apply -f sreagent-deployment.yaml
```

See [SETUP_AND_DEPLOYMENT.md](SETUP_AND_DEPLOYMENT.md) for detailed instructions.

## 🔌 API Endpoints

### Base URL: `http://localhost:3001`

```bash
# Health check
GET /health

# Main query endpoint
POST /api/sre
{
  "query": "Show me high CPU pods",
  "workflow_type": "basic",
  "max_tools": 5
}

# List available tools
GET /api/tools

# List example queries
GET /api/examples

# API documentation
GET /docs (Swagger UI)
```

## 🎯 Workflow Types

### Basic Workflow
✅ Fast processing  
✅ Good for monitoring and analysis  
✅ No approval gates  
✅ Direct tool execution  

### Advanced Workflow
✅ Includes approval steps  
✅ Rollback capability  
✅ Severity classification  
✅ Audit trail  
✅ Safe for production changes  

Toggle in frontend header: **Basic** ↔️ **Advanced**

## 📊 Features Detail

### Monitoring Tool
- **Operations**: CPU/memory/disk usage, network I/O, pod restarts, error rates, alerts
- **Source**: Prometheus metrics
- **Output**: Metrics, trends, anomalies

### Logs Tool
- **Operations**: Pod logs, log search, error detection, label filtering
- **Source**: Kubernetes logs API
- **Output**: Log snippets, patterns, recommendations

### Healing Tool
- **Operations**: Pod restart, deployment scaling, node drain, health checks
- **Safety**: Protected namespaces, grace periods, rollback support
- **Output**: Action results, verification status

### Cost Analyzer Tool
- **Operations**: Resource waste detection, cost breakdown, rightsizing
- **Calculation**: CPU/memory/storage costs by resource
- **Output**: Recommendations, savings potential

## 🌐 Integration Ready

Pre-built support for:
- ✅ Kubernetes (kubectl)
- ✅ Prometheus
- ✅ Ollama LLM

Ready for integration with:
- 🔲 Slack (notifications)
- 🔲 PagerDuty (incident creation)
- 🔲 Datadog (event logging)
- 🔲 Email alerts
- 🔲 Custom webhooks

See [SETUP_AND_DEPLOYMENT.md](SETUP_AND_DEPLOYMENT.md#integration-with-external-systems) for integration examples.

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python dependencies
python -c "import fastapi; import uvicorn; print('✓ OK')"

# Reinstall if needed
pip install -r requirements.txt
```

### Frontend can't connect
```bash
# Check backend is running
curl http://localhost:3001/health

# Check .env.local
cat kubetool/frontend/.env.local

# Should show: NEXT_PUBLIC_BACKEND_URL=http://localhost:3001
```

### Kubernetes connection issues
```bash
# Verify kubectl
kubectl get nodes

# Check kubeconfig
echo $KUBECONFIG
export KUBECONFIG=$HOME/.kube/config
```

### Ollama not responding
```bash
# Start Ollama
ollama serve

# In another terminal
ollama pull llama2

# Verify
curl http://localhost:11434/api/tags
```

👉 **See [QUICK_START.md](QUICK_START.md#-troubleshooting) for more help**

## 📈 Performance

### Response Times (Basic Workflow)
- Simple query: ~2-5 seconds
- Tool execution: ~1-10 seconds per tool
- Total response: ~5-15 seconds

### Scalability
- Supports clusters with 100+ nodes
- Handles 1000+ pods per query
- Prometheus retention: 15 days by default

### Resource Usage
- Backend: ~256MB RAM, 250m CPU
- Frontend: ~100MB RAM
- Total: ~400MB RAM, 500m CPU

## 🔐 Security

### Best Practices
- ✅ Input validation with Pydantic
- ✅ Protected namespaces for healing operations
- ✅ Approval gates for critical actions
- ✅ Audit trail of all operations
- ✅ RBAC support via kubeconfig
- ✅ Rate limiting ready
- ✅ HTTPS support

### Production Checklist
- [ ] Set KUBECONFIG to limited RBAC role
- [ ] Enable HTTPS
- [ ] Set up authentication
- [ ] Configure rate limiting
- [ ] Enable audit logging
- [ ] Review protected namespaces
- [ ] Set up monitoring for the monitoring system

See [SETUP_AND_DEPLOYMENT.md](SETUP_AND_DEPLOYMENT.md#security-best-practices) for detailed security setup.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional tool integrations
- Dashboard features
- Real-time streaming
- Mobile app
- Better LLM models

## 📄 Project Structure

```
kubetool/
├── api_server.py                 # FastAPI backend
├── sre_langgraph.py             # Basic workflow
├── sre_langgraph_advanced.py    # Advanced workflow
├── monitoring_tool.py            # Tool #1
├── logs_tool.py                 # Tool #2
├── healing_tool.py              # Tool #3
├── cost_analyzer_tool.py        # Tool #4
├── ansible_tool.py              # Infrastructure tool
├── helm_tool.py                 # Deployment tool
├── requirements.txt             # Python deps
├── Dockerfile                   # Backend container
├── docker-compose.yml           # Multi-container setup
│
├── frontend/                    # React/Next.js app
│   ├── app/page.tsx            # Chat interface
│   ├── app/api/sre/route.ts    # API proxy
│   ├── components/             # UI components
│   ├── package.json            # Node deps
│   ├── Dockerfile              # Frontend container
│   └── ...
│
├── README.md                    # This file
├── QUICK_START.md              # 5-min setup
├── SETUP_AND_DEPLOYMENT.md     # Full guide
├── INDEX.md                    # Documentation index
└── ...
```

## 🎓 Learning Resources

### Beginner
1. Read [QUICK_START.md](QUICK_START.md)
2. Try example queries
3. Explore the chat interface

### Intermediate
1. Read [SRE_TOOLS_README.md](SRE_TOOLS_README.md)
2. Understand each tool
3. Experiment with advanced mode

### Advanced
1. Read [LANGGRAPH_INTEGRATION.md](LANGGRAPH_INTEGRATION.md)
2. Customize workflows
3. Deploy to production

## 📞 Support

- **Documentation**: See [INDEX.md](INDEX.md)
- **Quick Help**: See [QUICK_START.md](QUICK_START.md)
- **Detailed Setup**: See [SETUP_AND_DEPLOYMENT.md](SETUP_AND_DEPLOYMENT.md)
- **API Docs**: Visit `/docs` endpoint when running

## 🚀 Getting Started

```bash
# 1. Clone and navigate
cd kubetool

# 2. Start backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python api_server.py

# 3. In new terminal, start frontend
cd frontend && npm install && npm run dev

# 4. Open browser
open http://localhost:3000

# 5. Ask a question!
# "Show me high CPU pods"
```

See [QUICK_START.md](QUICK_START.md) for detailed setup.

## 📜 License

MIT License - See LICENSE file for details

---

<div align="center">

### 🌟 Star us on GitHub if you find this useful!

Made with ❤️ for SREs and Kubernetes enthusiasts

[Documentation](INDEX.md) • [Quick Start](QUICK_START.md) • [Setup Guide](SETUP_AND_DEPLOYMENT.md)

</div>
