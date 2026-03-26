# SREAgent: Project Structure Guide

## 📁 New Project Layout

The project has been reorganized for better maintainability and scalability:

```
kubetool/
│
├── src/                           # Main source code
│   ├── __init__.py               # Package init
│   ├── api/                      # FastAPI backend
│   │   ├── __init__.py
│   │   └── api_server.py         # REST API server (port 3001)
│   │
│   ├── tools/                    # All tools organized by category
│   │   ├── __init__.py
│   │   ├── sre/                  # SRE monitoring & operations
│   │   │   ├── __init__.py
│   │   │   ├── monitoring.py     # Prometheus metrics tool
│   │   │   ├── logs.py           # Pod log aggregation tool
│   │   │   ├── healing.py        # Self-remediation tool
│   │   │   └── cost_analyzer.py  # Cost optimization tool
│   │   │
│   │   └── infrastructure/       # Infrastructure management
│   │       ├── __init__.py
│   │       ├── ansible.py        # Host/software management
│   │       └── helm.py           # Kubernetes app deployment
│   │
│   ├── workflows/                # LangGraph orchestration
│   │   ├── __init__.py
│   │   ├── basic.py              # Basic query → tools → response
│   │   └── advanced.py           # Advanced: classify → plan → approve → execute
│   │
│   └── agents/                   # LangChain agents
│       ├── __init__.py
│       ├── sre_agent.py          # SRE tools agent
│       ├── helm_agent.py         # Helm deployment agent
│       └── ansible_agent.py      # Ansible inventory agent
│
├── frontend/                      # React/Next.js UI
│   ├── app/
│   │   ├── page.tsx              # Main chat interface
│   │   ├── layout.tsx            # Root layout
│   │   ├── globals.css           # Global styles
│   │   └── api/sre/route.ts      # Next.js API proxy
│   ├── components/
│   │   ├── ChatInterface.tsx     # Chat component
│   │   ├── FindingsPanel.tsx     # Findings display
│   │   └── WorkflowStatus.tsx    # Status display
│   ├── lib/
│   │   ├── types.ts              # TypeScript types
│   │   └── store.ts              # Zustand state
│   ├── package.json
│   ├── Dockerfile
│   └── tailwind.config.ts
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_sre_tools.py         # SRE tools tests
│   ├── test_helm_tool.py         # Helm tool tests
│   ├── test_ansible_tool.py      # Ansible tool tests
│   └── test_agent.py             # Agent tests
│
├── config/                        # Configuration files
│   ├── __init__.py
│   ├── ansible_inventory.yaml    # Ansible hosts
│   └── helm_deployments.yaml     # Helm chart configs
│
├── docs/                          # Documentation
│   ├── INDEX.md                  # Doc index
│   ├── QUICK_START.md            # 5-minute setup
│   ├── SETUP_AND_DEPLOYMENT.md   # Full guide
│   ├── SRE_TOOLS_README.md       # Tools documentation
│   ├── LANGGRAPH_INTEGRATION.md  # Workflow guide
│   ├── ANSIBLE_README.md         # Ansible tool docs
│   ├── HELM_README.md            # Helm tool docs
│   └── sre_phases.md             # Development phases
│
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Backend container
├── docker-compose.yml            # Multi-container setup
├── README.md                     # Main README
├── .gitignore                    # Git ignore rules
├── pyproject.toml               # Python project config (optional)
└── pytest.ini                   # Test configuration (optional)
```

## 🚀 Running the Application

### Local Development

```bash
# Backend
cd kubetool
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start API server
python -m uvicorn src.api.api_server:app --reload --port 3001
```

```bash
# Frontend (new terminal)
cd kubetool/frontend
npm install
npm run dev
```

### With Docker Compose

```bash
cd kubetool
docker-compose up -d
```

Access at http://localhost:3000

## 📦 Module Organization

### Tools (`src/tools/`)

#### SRE Tools (`src/tools/sre/`)
Kubernetes monitoring and operations:
- **monitoring.py**: Prometheus metrics, pod status, performance
- **logs.py**: Pod log retrieval and searching
- **healing.py**: Self-remediation and health checks
- **cost_analyzer.py**: Cost analysis and optimization

Usage:
```python
from src.tools.sre.monitoring import monitoring_tool
from src.tools.sre.logs import logs_tool
from src.tools.sre.healing import healing_tool
from src.tools.sre.cost_analyzer import cost_analyzer_tool
```

#### Infrastructure Tools (`src/tools/infrastructure/`)
Host and application management:
- **ansible.py**: Software inventory, host management
- **helm.py**: Kubernetes application deployment

Usage:
```python
from src.tools.infrastructure.ansible import ansible_tool
from src.tools.infrastructure.helm import helm_tool
```

### Workflows (`src/workflows/`)

Orchestration layer for tool execution:
- **basic.py**: Fast query processing with tool coordination
- **advanced.py**: Complex workflows with approval and rollback

Usage:
```python
from src.workflows.basic import run_sre_session
from src.workflows.advanced import run_advanced_workflow
```

### Agents (`src/agents/`)

LangChain agents for natural language:
- **sre_agent.py**: Multi-tool SRE agent
- **helm_agent.py**: Helm deployment agent
- **ansible_agent.py**: Ansible inventory agent

### API (`src/api/`)

FastAPI backend exposing workflows:
- **api_server.py**: REST endpoints and CORS configuration

## 🧪 Testing

Run tests from project root:

```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_sre_tools.py

# With coverage
pytest tests/ --cov=src
```

Test files can import from src:
```python
from src.tools.sre.monitoring import monitoring_tool
from src.workflows.basic import run_sre_session
```

## 📋 Configuration

### Environment Variables

Create `.env` in project root:
```env
# Optional
OLLAMA_MODEL=llama2
OLLAMA_API_BASE=http://localhost:11434
KUBECONFIG=/path/to/kubeconfig
DEBUG=false
LOG_LEVEL=info
```

### Config Files

Located in `config/`:
- `ansible_inventory.yaml`: Define Ansible hosts
- `helm_deployments.yaml`: Helm chart configurations

Access in code:
```python
with open("config/ansible_inventory.yaml") as f:
    inventory = yaml.safe_load(f)
```

## 📚 Documentation

All docs in `docs/` folder:

| File | Purpose |
|------|---------|
| INDEX.md | Documentation index |
| QUICK_START.md | 5-minute setup |
| SETUP_AND_DEPLOYMENT.md | Full installation |
| SRE_TOOLS_README.md | Tools API reference |
| LANGGRAPH_INTEGRATION.md | Workflow details |
| ANSIBLE_README.md | Ansible tool guide |
| HELM_README.md | Helm tool guide |

## 🔄 Import Patterns

### From Root Project

```python
# Tools
from src.tools.sre.monitoring import monitoring_tool
from src.tools.infrastructure.helm import helm_tool

# Workflows
from src.workflows.basic import run_sre_session
from src.workflows.advanced import run_advanced_workflow

# Agents
from src.agents.sre_agent import run_sre_agent

# API
from src.api.api_server import app
```

### From Subdirectories

Within `src/tools/sre/`:
```python
from src.tools.sre.monitoring import monitoring_tool  # Full path
# or
from .monitoring import monitoring_tool  # Relative import
```

## 🐳 Docker Setup

### Build Images

```bash
# Backend
docker build -t sreagent-backend:1.0 .

# Frontend
docker build -t sreagent-frontend:1.0 ./frontend
```

### Run with Compose

```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## 🧩 Adding New Tools

To add a new SRE tool:

1. Create file in `src/tools/sre/my_tool.py`:
```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    param1: str = Field(..., description="First parameter")

@tool("my_tool", args_schema=MyToolInput)
def my_tool(param1: str):
    """Tool description."""
    return {"result": "..."}
```

2. Update `src/tools/sre/__init__.py`:
```python
from .my_tool import my_tool

__all__ = [
    "monitoring_tool",
    "logs_tool",
    "healing_tool",
    "cost_analyzer_tool",
    "my_tool",  # Add here
]
```

3. Add to workflows in `src/workflows/basic.py`:
```python
from src.tools.sre.my_tool import my_tool

tools = [
    monitoring_tool,
    logs_tool,
    healing_tool,
    cost_analyzer_tool,
    my_tool,  # Add here
]
```

## 🧹 Project Cleanup

To remove old files from root (they're now in src/):

```bash
# Verify files are moved
ls -la src/tools/sre/
ls -la src/api/
ls -la src/workflows/

# Remove old files (after verification)
# rm monitoring_tool.py logs_tool.py healing_tool.py cost_analyzer_tool.py
# rm ansible_tool.py helm_tool.py
# rm sre_agent.py helm_agent.py ansible_agent.py
# rm sre_langgraph.py sre_langgraph_advanced.py api_server.py
# rm test_*.py
# rm *.md (except README.md in project root)
```

## ✅ Migration Checklist

- ✅ Directory structure created
- ✅ Files moved to new locations
- ✅ Imports updated in all files
- ✅ `__init__.py` files created
- ✅ Dockerfile updated with new paths
- ✅ Docker Compose configured
- ✅ Documentation moved to docs/
- ✅ Tests in tests/ folder
- ✅ Config files organized

## 🚀 Next Steps

1. **Verify structure works**:
   ```bash
   python -m uvicorn src.api.api_server:app --reload
   ```

2. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

3. **Start full system**:
   ```bash
   docker-compose up -d
   ```

4. **Clean up old files** (after verification):
   ```bash
   # Carefully remove original files from root
   rm -f monitoring_tool.py logs_tool.py healing_tool.py cost_analyzer_tool.py
   rm -f ansible_tool.py helm_tool.py
   rm -f sre_agent.py helm_agent.py ansible_agent.py
   rm -f sre_langgraph.py sre_langgraph_advanced.py api_server.py
   rm -f test_*.py
   ```

## 📝 Notes

- All Python modules are now under `src/` package
- Tests can be run with pytest from any directory
- Documentation is centralized in `docs/`
- Configuration is separate from code in `config/`
- Frontend remains in `frontend/` for clarity
- Docker builds should work without changes

## 🆘 Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`:

```bash
# Ensure you're in project root
cd /path/to/kubetool

# Run with module syntax
python -m src.api.api_server
# or
python -m uvicorn src.api.api_server:app
```

### Relative Import Errors

Make sure all packages have `__init__.py`:
```bash
find src -type d | xargs -I {} touch {}/__init__.py
```

### Docker Build Fails

Clear cache and rebuild:
```bash
docker-compose down
docker system prune
docker-compose up --build
```

---

**Project Structure Complete!** ✨

The project is now organized for scalability and maintainability. All tools, workflows, and agents are properly modularized.
