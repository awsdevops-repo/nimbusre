# SREAgent: Complete Documentation Index

Welcome to SREAgent - an AI-powered Site Reliability Engineering toolkit for Kubernetes management.

## 🎯 What is SREAgent?

SREAgent is a comprehensive system that combines:
- **LangChain agents** for natural language understanding
- **LangGraph workflows** for complex multi-step operations
- **Specialized SRE tools** for monitoring, logging, healing, and cost analysis
- **React/Next.js frontend** for user interaction
- **FastAPI backend** for tool orchestration

## 📖 Documentation Map

### Getting Started
1. **[QUICK_START.md](QUICK_START.md)** ⭐ START HERE
   - 5-minute setup guide
   - First queries to try
   - Troubleshooting basics

2. **[SETUP_AND_DEPLOYMENT.md](SETUP_AND_DEPLOYMENT.md)** 
   - Complete installation instructions
   - Production deployment
   - Docker & Kubernetes guides
   - Advanced configuration

### Core Tools Documentation

3. **[SRE_TOOLS_README.md](SRE_TOOLS_README.md)**
   - Monitoring tool (Prometheus metrics)
   - Logs tool (Pod log aggregation)
   - Healing tool (Self-remediation)
   - Cost analyzer tool (Cost optimization)
   - Complete API reference

4. **[ANSIBLE_README.md](ANSIBLE_README.md)**
   - Software inventory management
   - Host-level operations
   - Ansible tool usage guide

5. **[HELM_README.md](HELM_README.md)**
   - Kubernetes application deployment
   - Helm operations
   - Chart management

### Advanced Topics

6. **[LANGGRAPH_INTEGRATION.md](LANGGRAPH_INTEGRATION.md)**
   - Workflow orchestration details
   - Basic vs Advanced workflows
   - State management
   - Error handling
   - Custom workflow patterns

7. **[sre_phases.md](sre_phases.md)**
   - SRE tool development phases
   - Feature roadmap
   - Phase 1-4 planning

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React/Next.js Frontend                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ChatInterface | FindingsPanel | WorkflowStatus      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend Server                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  /api/sre endpoint  →  LangGraph Workflows           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph Orchestration                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Basic Workflow      |  Advanced Workflow            │  │
│  │  (Process → Tools)   |  (Classify → Plan → Approve) │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    LangChain Tools                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Monitoring │ Logs │ Healing │ Cost │ Ansible │ Helm│   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              Kubernetes & External Systems                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ kubectl | Prometheus | Logs | kubectl API | Cost APIs│ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Feature Overview

### Monitoring & Observability
- Real-time Prometheus metrics queries
- Pod and node status monitoring
- Alert status checking
- Performance metrics (CPU, memory, network)
- Error rate and latency tracking

### Troubleshooting & Logging
- Pod log aggregation
- Log searching and filtering
- Label-based log retrieval
- Previous pod logs (for crash analysis)
- Log statistics and summaries

### Self-Healing & Remediation
- Automated pod/deployment restart
- Scaling operations
- Node drain and cordon
- Health checks with recommendations
- Protected namespace enforcement
- Audit trail and rollback

### Cost Analysis & Optimization
- Resource waste detection
- Cost by namespace/pod
- Rightsizing recommendations
- Unused resource cleanup
- Cluster cost tracking
- Period-over-period comparison

### Infrastructure Management
- Helm chart operations
- Kubernetes object management
- Ansible inventory management
- Host-level software management

## 🚀 Quick Feature Matrix

| Feature | Basic Mode | Advanced Mode |
|---------|-----------|---------------|
| Queries | Fast ✓ | Slower (approval) ✓ |
| Read-only operations | ✓ | ✓ |
| Destructive operations | ✗ | ✓ (with approval) |
| Rollback | ✗ | ✓ |
| Audit trail | Basic | Detailed ✓ |
| Severity classification | Auto | Auto ✓ |

## 💻 Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **LLM**: Ollama (local models)
- **Orchestration**: LangGraph
- **Agents**: LangChain
- **Validation**: Pydantic
- **HTTP Server**: Uvicorn

### Frontend
- **Framework**: Next.js 14
- **UI Library**: React 18
- **Styling**: Tailwind CSS
- **State**: Zustand
- **HTTP Client**: Axios
- **Icons**: Lucide React

### Infrastructure
- **Kubernetes**: kubectl API
- **Metrics**: Prometheus
- **Logs**: Kubernetes logs API
- **Config Management**: Helm, Ansible

## 📈 Usage Statistics

### Tools Included
- ✅ 4 SRE tools (monitoring, logs, healing, cost)
- ✅ 1 Ansible tool (host management)
- ✅ 1 Helm tool (app deployment)
- ✅ 60+ individual operations

### API Endpoints
- ✅ 5 main endpoints
- ✅ Swagger documentation
- ✅ Health checks
- ✅ Example queries

### Frontend Components
- ✅ Chat interface with message history
- ✅ Real-time status panel
- ✅ Findings aggregation
- ✅ Quick action buttons
- ✅ Dark mode support
- ✅ Responsive design

## 🎓 Learning Path

### Beginner
1. Read QUICK_START.md
2. Try the example queries
3. Explore the chat interface
4. Check findings and recommendations

### Intermediate
1. Read SRE_TOOLS_README.md
2. Understand each tool's capabilities
3. Try advanced workflow mode
4. Experiment with different query types

### Advanced
1. Read LANGGRAPH_INTEGRATION.md
2. Understand workflow orchestration
3. Customize workflows
4. Integrate external systems
5. Deploy to production

## 🔧 Common Tasks

### Monitor Your Cluster
```
User: "Show me high CPU pods"
→ monitoring_tool queries Prometheus
→ Returns pods with CPU > threshold
→ Displays in findings panel
```

### Troubleshoot Issues
```
User: "Get logs from the failing pod"
→ logs_tool fetches pod logs
→ Searches for error patterns
→ Suggests remediation
```

### Optimize Costs
```
User: "Find wasted resources"
→ cost_analyzer queries cluster
→ Detects over-provisioned pods
→ Recommends rightsizing
```

### Auto-Remediate
```
User: "Restart the failing pod" (Advanced mode)
→ Classify as maintenance (medium severity)
→ Create remediation plan
→ Request approval
→ Execute restart
→ Verify pod health
```

## 🌐 Integration Points

### Supported Platforms
- ✅ Kubernetes (any distribution)
- ✅ Prometheus (for metrics)
- ✅ Ollama (for LLM)
- ✅ kubectl (CLI)

### Ready for Integration
- 🔲 Slack (notifications)
- 🔲 PagerDuty (incident creation)
- 🔲 Datadog (event logging)
- 🔲 Email (alerts)
- 🔲 Webhooks (custom integrations)

See SETUP_AND_DEPLOYMENT.md for integration examples.

## 📋 File Structure

```
kubetool/
├── README.md                          # Main project readme
├── QUICK_START.md                     # 5-minute setup ⭐
├── SETUP_AND_DEPLOYMENT.md            # Complete guide
├── LANGGRAPH_INTEGRATION.md           # Workflow docs
├── SRE_TOOLS_README.md               # Tools documentation
├── ANSIBLE_README.md                 # Ansible tool guide
├── HELM_README.md                    # Helm tool guide
├── sre_phases.md                     # Development phases
│
├── api_server.py                     # FastAPI backend
├── sre_langgraph.py                  # Basic workflow
├── sre_langgraph_advanced.py         # Advanced workflow
│
├── monitoring_tool.py                # SRE tool #1
├── logs_tool.py                      # SRE tool #2
├── healing_tool.py                   # SRE tool #3
├── cost_analyzer_tool.py             # SRE tool #4
├── ansible_tool.py                   # Infrastructure tool
├── helm_tool.py                      # App deployment tool
│
├── requirements.txt                  # Python deps
├── frontend/                         # React/Next.js app
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── package.json
│   └── ...
└── test_*.py                         # Test files
```

## 🎯 Getting Help

### For Setup Issues
→ See QUICK_START.md Troubleshooting section

### For Tool-Specific Questions
→ Check SRE_TOOLS_README.md or individual tool docs

### For Workflow Questions
→ Read LANGGRAPH_INTEGRATION.md

### For Production Deployment
→ Follow SETUP_AND_DEPLOYMENT.md

### For API Questions
→ Visit http://localhost:3001/docs (Swagger UI)

## 🚦 Status & Roadmap

### ✅ Implemented (Phase 1-3)
- Monitoring tool with Prometheus integration
- Log aggregation and searching
- Self-healing and remediation
- Cost analysis and optimization
- Ansible tool for host management
- Helm tool for app deployment
- LangGraph basic and advanced workflows
- React/Next.js frontend with chat interface
- FastAPI backend with REST API

### 🔲 Planned (Phase 4+)
- Dashboard with historical metrics
- Real-time WebSocket streaming
- Slack/Teams integration
- PagerDuty automation
- Multi-user support with RBAC
- Workflow templates and marketplace
- Mobile app

## 📞 Support

- **Issue Tracker**: File issues in the project repository
- **Documentation**: Check the README files
- **Examples**: See test files for usage examples
- **API Docs**: Visit /docs endpoint when running backend

## 📄 License

This project is provided as-is. Modify and deploy as needed for your use case.

---

## 🎉 You're All Set!

Start with [QUICK_START.md](QUICK_START.md) to get up and running in minutes. Happy monitoring! 🚀
