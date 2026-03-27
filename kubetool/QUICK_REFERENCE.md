# SREAgent Developer Quick Reference

## Fast Start

```bash
# terminal 1 (backend)
cd /path/to/kubetool
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.api.api_server:app --reload --port 8000

# terminal 2 (frontend)
cd /path/to/kubetool/frontend
npm install
npm run dev
```

UI: http://localhost:3000

## Deployment Scripts

All shell scripts are now under `Deploy_Scripts/`.

```bash
sudo bash Deploy_Scripts/install.sh
sudo bash Deploy_Scripts/deploy.sh
sudo bash Deploy_Scripts/setup-nginx.sh
sudo bash Deploy_Scripts/setup-ssl.sh your-domain.com
sudo bash Deploy_Scripts/manage.sh
```

Alternate path:

```bash
sudo bash Deploy_Scripts/install_tools.sh
sudo bash Deploy_Scripts/deploy_app.sh
```

Note: `deploy.sh` defaults backend to 8000, while `deploy_app.sh` uses 3001.

## Core Imports

```python
# tools
from src.tools.sre.monitoring import monitoring_tool
from src.tools.sre.logs import logs_tool
from src.tools.sre.healing import healing_tool
from src.tools.sre.cost_analyzer import cost_analyzer_tool
from src.tools.infrastructure.kubectl import kubectl_tool
from src.tools.infrastructure.ansible import ansible_tool
from src.tools.infrastructure.helm import helm_tool

# workflows
from src.workflows.basic import run_sre_session
from src.workflows.advanced import run_advanced_workflow

# agents
from src.agents.sre_agent import run_sre_agent
from src.agents.kubectl_agent import agent as kubectl_agent
from src.agents.helm_agent import run_helm_agent
from src.agents.ansible_agent import run_ansible_agent

# api
from src.api.api_server import app
```

## High-Value Files

| Need | Location |
|------|----------|
| API server | `src/api/api_server.py` |
| Basic workflow | `src/workflows/basic.py` |
| Advanced workflow | `src/workflows/advanced.py` |
| Shared workflow wiring | `src/workflows/shared.py` |
| Kubeconfig helper | `src/tools/kubeconfig_utils.py` |
| SRE tools | `src/tools/sre/*.py` |
| Infra tools | `src/tools/infrastructure/*.py` |
| Deployment scripts | `Deploy_Scripts/*.sh` |

## Tests

```bash
pytest tests/ -v
pytest tests/test_sre_tools.py -v
pytest tests/ --cov=src
```

## Docker

```bash
docker-compose build
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## Common Checks

```bash
# backend health (deploy.sh path)
curl -i http://localhost:8000/health

# backend health (deploy_app.sh path)
curl -i http://localhost:3001/health

# nginx config
sudo nginx -t

# services
sudo systemctl status nimbusre-backend nimbusre-frontend
```

## Troubleshooting

### Module import errors

```bash
cd /path/to/kubetool
python -m uvicorn src.api.api_server:app --reload
```

### Frontend cannot reach backend

Check your active backend port and set frontend env accordingly:

- `NEXT_PUBLIC_BACKEND_URL=http://localhost:8000` (deploy.sh)
- `NEXT_PUBLIC_BACKEND_URL=http://localhost:3001` (deploy_app.sh)

### Script location errors

Use the new path:

```bash
sudo bash Deploy_Scripts/<script>.sh
```
