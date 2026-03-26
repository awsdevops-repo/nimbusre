# SREAgent - Developer Quick Reference

## 🏗️ New Project Structure (Complete)

Your project has been professionally reorganized! Here's what changed:

### Before → After

```
OLD STRUCTURE              NEW STRUCTURE
─────────────────          ─────────────────
monitoring_tool.py  ──┐    src/
logs_tool.py        ──┼──> tools/
healing_tool.py     ──┤    └── sre/
cost_analyzer_tool.py ┘       ├── monitoring.py
                               ├── logs.py
                               ├── healing.py
                               └── cost_analyzer.py

ansible_tool.py     ──┐    src/
helm_tool.py        ──┼──> tools/
                       └──> └── infrastructure/
                               ├── ansible.py
                               └── helm.py

sre_langgraph.py    ──┐    src/
sre_langgraph_      ──┼──> workflows/
  advanced.py         └──── ├── basic.py
                             └── advanced.py

sre_agent.py        ──┐    src/
helm_agent.py       ──┼──> agents/
ansible_agent.py    └─────  ├── sre_agent.py
                             ├── helm_agent.py
                             └── ansible_agent.py

api_server.py       ────>   src/api/api_server.py

test_*.py           ────>   tests/test_*.py
*.yaml              ────>   config/*.yaml
*.md (docs)         ────>   docs/*.md
```

## 🚀 Quick Start (30 seconds)

### Terminal 1: Start Backend
```bash
cd kubetool
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.api.api_server:app --reload --port 3001
```

### Terminal 2: Start Frontend
```bash
cd kubetool/frontend
npm install
npm run dev
```

### Browser
```
http://localhost:3000
```

## 📦 Module Reference

### Import Tools
```python
# SRE Tools
from src.tools.sre.monitoring import monitoring_tool
from src.tools.sre.logs import logs_tool
from src.tools.sre.healing import healing_tool
from src.tools.sre.cost_analyzer import cost_analyzer_tool

# Infrastructure Tools
from src.tools.infrastructure.ansible import ansible_tool
from src.tools.infrastructure.helm import helm_tool
```

### Import Workflows
```python
from src.workflows.basic import run_sre_session
from src.workflows.advanced import run_advanced_workflow
```

### Import Agents
```python
from src.agents.sre_agent import run_sre_agent
from src.agents.helm_agent import run_helm_agent
from src.agents.ansible_agent import run_ansible_agent
```

## 📂 Where to Find Things

| What | Location |
|------|----------|
| Monitoring code | `src/tools/sre/monitoring.py` |
| Logs code | `src/tools/sre/logs.py` |
| Healing code | `src/tools/sre/healing.py` |
| Cost analysis | `src/tools/sre/cost_analyzer.py` |
| Ansible code | `src/tools/infrastructure/ansible.py` |
| Helm code | `src/tools/infrastructure/helm.py` |
| Basic workflow | `src/workflows/basic.py` |
| Advanced workflow | `src/workflows/advanced.py` |
| API server | `src/api/api_server.py` |
| Tests | `tests/test_*.py` |
| Config files | `config/*.yaml` |
| Documentation | `docs/*.md` |
| React UI | `frontend/app/page.tsx` |

## 🧪 Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_sre_tools.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## 🐳 Docker

```bash
# Build images
docker-compose build

# Run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📋 File Status

### ✅ Moved & Updated
- ✅ All 6 tool files → `src/tools/`
- ✅ All 3 agent files → `src/agents/`
- ✅ All 2 workflow files → `src/workflows/`
- ✅ API server → `src/api/`
- ✅ All tests → `tests/`
- ✅ All docs → `docs/`
- ✅ Config files → `config/`
- ✅ All imports updated
- ✅ All `__init__.py` files created

### ⚠️ To Clean Up (Optional)
Old files in project root that can be deleted:
```bash
# Run after verifying everything works
rm -f monitoring_tool.py logs_tool.py healing_tool.py cost_analyzer_tool.py
rm -f ansible_tool.py helm_tool.py
rm -f sre_agent.py helm_agent.py ansible_agent.py
rm -f sre_langgraph.py sre_langgraph_advanced.py api_server.py
rm -f test_*.py
```

## 📚 Documentation

Start with these in order:
1. **PROJECT_STRUCTURE.md** ← You are here (overview)
2. **docs/QUICK_START.md** ← Quick setup
3. **docs/SRE_TOOLS_README.md** ← Tool reference
4. **docs/LANGGRAPH_INTEGRATION.md** ← Workflow guide

## 🆘 Common Issues

### "ModuleNotFoundError" when running backend
```bash
# Make sure you're in project root
cd /path/to/kubetool

# Run with module syntax
python -m uvicorn src.api.api_server:app --reload
```

### Tests not finding modules
```bash
# Run from project root
cd /path/to/kubetool
pytest tests/ -v
```

### Frontend can't connect to backend
```bash
# Check backend is running
curl http://localhost:3001/health

# Check .env.local in frontend folder
cat frontend/.env.local
# Should show: NEXT_PUBLIC_BACKEND_URL=http://localhost:3001
```

## 🎯 Key Improvements

✨ **Better Organization**
- Tools grouped by category (SRE vs Infrastructure)
- Clear separation of concerns
- Easier to navigate

✨ **Scalability**
- Easy to add new tools
- Clear package structure
- Ready for growth

✨ **Maintainability**
- All imports consistent
- Central `__init__.py` files
- Proper Python package structure

✨ **Documentation**
- Centralized in `docs/` folder
- Clear module organization
- Easy to find references

## 🚀 Next Steps

1. **Verify everything works**:
   ```bash
   python -m uvicorn src.api.api_server:app --reload
   # In another terminal
   pytest tests/test_sre_tools.py -v
   ```

2. **Start using new structure**:
   ```bash
   python -m uvicorn src.api.api_server:app
   cd frontend && npm run dev
   ```

3. **Clean up old files** (when ready):
   ```bash
   # Delete old root-level tool files
   # They're all in src/ now
   ```

## 📞 Need Help?

Check these files in order:
1. This file (quick reference)
2. `docs/QUICK_START.md` (setup)
3. `docs/PROJECT_STRUCTURE.md` (detailed layout)
4. `docs/SRE_TOOLS_README.md` (tool APIs)

---

**You're all set!** The project structure is now professional-grade and ready for scaling. 🎉

**Pro Tip**: Run the API server with:
```bash
python -m uvicorn src.api.api_server:app --reload --port 3001
```

This keeps hot-reload enabled and clearly shows the module path!
