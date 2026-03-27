# SREAgent Project Structure Guide

## Current Layout

```
kubetool/
│
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── api_server.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── sre_agent.py
│   │   ├── helm_agent.py
│   │   ├── ansible_agent.py
│   │   └── kubectl_agent.py
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── basic.py
│   │   ├── advanced.py
│   │   └── shared.py
│   └── tools/
│       ├── __init__.py
│       ├── kubeconfig_utils.py
│       ├── sre/
│       │   ├── __init__.py
│       │   ├── monitoring.py
│       │   ├── logs.py
│       │   ├── healing.py
│       │   └── cost_analyzer.py
│       └── infrastructure/
│           ├── __init__.py
│           ├── kubectl.py
│           ├── ansible.py
│           └── helm.py
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
│
├── tests/
├── config/
├── docs/
├── Deploy_Scripts/
│   ├── install.sh
│   ├── install_tools.sh
│   ├── install_gcc_fix.sh
│   ├── deploy.sh
│   ├── deploy_app.sh
│   ├── setup-nginx.sh
│   ├── setup-ssl.sh
│   ├── manage.sh
│   └── start_backend.sh
│
├── DEPLOYMENT_GUIDE.md
├── PROJECT_STRUCTURE.md
├── QUICK_REFERENCE.md
├── VISUAL_GUIDE.md
├── STRUCTURE_COMPLETE.md
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Key Components

### API

- `src/api/api_server.py`: FastAPI app entrypoint and request routing.

### Tools

- `src/tools/sre/*`: monitoring, logs, healing, cost analysis.
- `src/tools/infrastructure/*`: kubectl, ansible, helm operations.
- `src/tools/kubeconfig_utils.py`: shared kubeconfig resolution helpers.

### Workflows

- `src/workflows/basic.py`: standard query -> tool -> synthesis flow.
- `src/workflows/advanced.py`: classify/plan/approval/execute flow.
- `src/workflows/shared.py`: centralized tool registry + LLM setup.

### Agents

- `src/agents/sre_agent.py`
- `src/agents/kubectl_agent.py`
- `src/agents/helm_agent.py`
- `src/agents/ansible_agent.py`

### Deployment and Ops

- All shell scripts are under `Deploy_Scripts/`.
- Use `DEPLOYMENT_GUIDE.md` for production command paths.

## Runtime Ports

- Recommended deployment path (`Deploy_Scripts/deploy.sh`): backend on `8000`, frontend on `3000`.
- Alternate deployment path (`Deploy_Scripts/deploy_app.sh`): backend on `3001`, frontend on `3000`.

## Typical Development Commands

```bash
# backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.api.api_server:app --reload --port 8000

# frontend
cd frontend
npm install
npm run dev
```

## Script Command Examples

```bash
sudo bash Deploy_Scripts/install.sh
sudo bash Deploy_Scripts/deploy.sh
sudo bash Deploy_Scripts/setup-nginx.sh
sudo bash Deploy_Scripts/setup-ssl.sh your-domain.com
sudo bash Deploy_Scripts/manage.sh
```

## Import Reference

```python
from src.workflows.basic import run_sre_session
from src.workflows.advanced import run_advanced_workflow

from src.tools.sre.monitoring import monitoring_tool
from src.tools.infrastructure.kubectl import kubectl_tool

from src.api.api_server import app
```

## Notes

- `src/` and child folders are Python packages (with `__init__.py`).
- `__pycache__/` folders are generated artifacts and not part of logical structure.
- Keep all future operational scripts inside `Deploy_Scripts/`.
