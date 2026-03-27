# Project Structure Visual Guide

## Complete Directory Tree

```
kubetool/
│
├── src/
│   ├── api/
│   │   └── api_server.py
│   ├── agents/
│   │   ├── sre_agent.py
│   │   ├── kubectl_agent.py
│   │   ├── helm_agent.py
│   │   └── ansible_agent.py
│   ├── workflows/
│   │   ├── basic.py
│   │   ├── advanced.py
│   │   └── shared.py
│   └── tools/
│       ├── kubeconfig_utils.py
│       ├── sre/
│       │   ├── monitoring.py
│       │   ├── logs.py
│       │   ├── healing.py
│       │   └── cost_analyzer.py
│       └── infrastructure/
│           ├── kubectl.py
│           ├── ansible.py
│           └── helm.py
│
├── frontend/
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

## Dependency Flow

```
Frontend UI (Next.js)
    frontend/app/page.tsx
                ↓
API Proxy (optional)
    frontend/app/api/sre/route.ts
                ↓
FastAPI Backend
    src/api/api_server.py
                ↓
Workflows
    src/workflows/basic.py
    src/workflows/advanced.py
                ↓
Shared Wiring
    src/workflows/shared.py
                ↓
Tools
    src/tools/sre/*
    src/tools/infrastructure/*
                ↓
External Systems
    Kubernetes / Helm / Ansible / Prometheus / Ollama
```

## Runtime Port Map

- Frontend: `3000`
- Backend (recommended path): `8000` via `Deploy_Scripts/deploy.sh`
- Backend (alternate path): `3001` via `Deploy_Scripts/deploy_app.sh`

## Key Commands

```bash
# Local backend
python -m uvicorn src.api.api_server:app --reload --port 8000

# Frontend
cd frontend && npm run dev

# Recommended deployment flow
sudo bash Deploy_Scripts/install.sh
sudo bash Deploy_Scripts/deploy.sh
sudo bash Deploy_Scripts/setup-nginx.sh
sudo bash Deploy_Scripts/setup-ssl.sh your-domain.com

# Ops menu
sudo bash Deploy_Scripts/manage.sh
```

## Verification Commands

```bash
find src -name "*.py" | wc -l
find src -name "__init__.py" | wc -l
find Deploy_Scripts -maxdepth 1 -name "*.sh" | wc -l
pytest tests/ -v
```

## Reading Order

1. `QUICK_REFERENCE.md`
2. `PROJECT_STRUCTURE.md`
3. `DEPLOYMENT_GUIDE.md`
4. `docs/QUICK_START.md`
5. `docs/SRE_TOOLS_README.md`
