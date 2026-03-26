# SREAgent Frontend + Backend Setup Guide

## Overview

The SREAgent system consists of:
- **Python Backend**: FastAPI server exposing SRE tools as REST API
- **React Frontend**: Next.js chat interface for interacting with SRE tools
- **LangGraph Workflows**: Orchestrated tool execution with approval and rollback

## Project Structure

```
kubetool/
├── api_server.py                 # FastAPI backend server
├── sre_langgraph.py             # Basic workflow (process → tools → synthesize)
├── sre_langgraph_advanced.py    # Advanced workflow (classify → plan → approve → execute → verify)
├── monitoring_tool.py            # Prometheus metrics
├── logs_tool.py                 # Pod log aggregation
├── healing_tool.py              # Self-healing & remediation
├── cost_analyzer_tool.py        # Cost analysis & optimization
├── requirements.txt             # Python dependencies
│
└── frontend/                    # Next.js React application
    ├── app/
    │   ├── page.tsx            # Main chat interface
    │   ├── layout.tsx          # Root layout
    │   ├── globals.css         # Global styles
    │   └── api/sre/route.ts    # Next.js API route
    ├── components/
    │   ├── ChatInterface.tsx    # Main chat component
    │   ├── FindingsPanel.tsx    # Findings display
    │   └── WorkflowStatus.tsx   # Workflow status
    ├── lib/
    │   ├── types.ts            # TypeScript types
    │   └── store.ts            # Zustand state management
    ├── package.json            # Node.js dependencies
    ├── next.config.ts          # Next.js configuration
    ├── tailwind.config.ts      # Tailwind CSS config
    ├── tsconfig.json           # TypeScript config
    └── .env.local              # Environment variables
```

## Prerequisites

### Python Requirements
- Python 3.8+
- pip or conda

### Node.js Requirements
- Node.js 18+
- npm or yarn

### System Dependencies
- kubectl installed and configured
- Access to Kubernetes cluster (minikube, docker-desktop, or cloud cluster)
- Prometheus/Grafana running on cluster (for monitoring_tool)

## Installation & Setup

### 1. Backend Setup

#### Step 1.1: Install Python Dependencies

```bash
cd kubetool
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; import uvicorn; print('✓ FastAPI dependencies installed')"
```

#### Step 1.2: Verify Kubernetes Connection

```bash
# Check kubectl access
kubectl get nodes

# Check cluster info
kubectl cluster-info

# Verify Prometheus (if monitoring enabled)
kubectl get pods -n monitoring | grep prometheus
```

#### Step 1.3: Configure LLM (Ollama)

```bash
# Start Ollama (if not running)
ollama serve

# In another terminal, pull llama2 model
ollama pull llama2

# Verify model is loaded
curl http://localhost:11434/api/tags
```

### 2. Frontend Setup

#### Step 2.1: Install Node.js Dependencies

```bash
cd frontend
npm install
# or
yarn install
```

#### Step 2.2: Configure Environment

Edit `frontend/.env.local`:

```env
# Backend API Configuration
NEXT_PUBLIC_BACKEND_URL=http://localhost:3001

# Feature Flags
NEXT_PUBLIC_ENABLE_ADVANCED_WORKFLOW=true
NEXT_PUBLIC_ENABLE_REAL_TIME_UPDATES=true
```

For production (deployed backend):
```env
NEXT_PUBLIC_BACKEND_URL=https://api.yourdomain.com
```

#### Step 2.3: Build Frontend (Optional)

```bash
npm run build
```

## Running the Application

### Development Mode

#### Terminal 1: Start Python Backend

```bash
cd kubetool
source venv/bin/activate
python api_server.py
```

Output should show:
```
INFO:     Uvicorn running on http://0.0.0.0:3001
```

#### Terminal 2: Start Next.js Frontend

```bash
cd kubetool/frontend
npm run dev
```

Output should show:
```
> next dev
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

#### Terminal 3 (Optional): Monitor Logs

```bash
cd kubetool
source venv/bin/activate
python -c "import monitoring_tool; print(monitoring_tool.__doc__)"
```

### Production Mode

#### Build and Run Frontend

```bash
cd frontend
npm run build
npm run start
```

#### Run Backend with Gunicorn (Production ASGI Server)

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app --bind 0.0.0.0:3001
```

#### Using Docker (Recommended)

Create `Dockerfile` in kubetool directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3001
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "3001"]
```

Build and run:
```bash
docker build -t sreagent-backend .
docker run -p 3001:3001 -v ~/.kube/config:/root/.kube/config sreagent-backend
```

## API Endpoints

### Base URL
```
http://localhost:3001
```

### Endpoints

#### 1. Health Check
```
GET /health
Response: { status: "healthy", version: "1.0.0", components: {...} }
```

#### 2. Main SRE Query
```
POST /api/sre
Content-Type: application/json

Request:
{
  "query": "Show me high CPU pods",
  "workflow_type": "basic",  # or "advanced"
  "max_tools": 5
}

Response:
{
  "status": "completed",
  "severity": "high",
  "workflow_type": "basic",
  "findings": {
    "monitoring_tool": [...]
  },
  "remediation_plan": "...",
  "executed_actions": [...]
}
```

#### 3. List Available Tools
```
GET /api/tools
Response: { tools: [...] }
```

#### 4. List Example Queries
```
GET /api/examples
Response: { examples: [...] }
```

## Usage Examples

### Example 1: Monitor Cluster Health

**Query:** "Show me the overall health of the cluster"

**Flow:**
1. Frontend sends query to `/api/sre`
2. Backend calls `run_sre_session()` with query
3. LangGraph workflow:
   - Process query
   - Call monitoring_tool (get cluster metrics)
   - Call logs_tool (check error logs)
   - Synthesize findings
4. Returns findings and recommendations
5. Frontend displays results in chat with sidebar panels

### Example 2: Troubleshoot High CPU

**Query:** "Why are my pods using high CPU?"

**Expected Response:**
- Severity: HIGH
- Findings from monitoring_tool (CPU > threshold)
- Findings from logs_tool (error patterns)
- Recommendations for scaling or optimization

### Example 3: Advanced Cost Optimization

**Query:** "Find ways to reduce our cluster costs" (with Advanced workflow)

**Flow:**
1. Classify: Cost optimization task (high severity)
2. Plan: Use cost_analyzer_tool
3. Request approval (if critical recommendation)
4. Execute: Provide remediation steps
5. Verify: Check impact

## Configuration

### Customize Tool Behavior

#### Monitor Specific Namespaces

Edit `monitoring_tool.py`:
```python
MONITORED_NAMESPACES = ["default", "production", "staging"]
```

#### Restrict Healing Operations

Edit `healing_tool.py`:
```python
PROTECTED_NAMESPACES = ["kube-system", "kube-public", "default"]
HEALING_OPERATIONS = ["restart_pod", "check_health"]  # Exclude scale_deployment
```

#### Adjust Cost Calculation

Edit `cost_analyzer_tool.py`:
```python
HOURLY_RATES = {
    "cpu": 0.025,      # $ per CPU per hour
    "memory": 0.005,   # $ per GB per hour
    "storage": 0.001,  # $ per GB per month
}
```

### Environment Variables

```bash
# Optional: Override Ollama model
export OLLAMA_MODEL=mistral
export OLLAMA_API_BASE=http://ollama:11434

# Optional: Override Kubernetes config
export KUBECONFIG=/path/to/kubeconfig

# Optional: Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend can't connect to backend

**Error:** `Error: Cannot connect to backend`

**Solution:**
1. Verify backend is running: `curl http://localhost:3001/health`
2. Check NEXT_PUBLIC_BACKEND_URL in `.env.local`
3. Check CORS headers (should allow origin from frontend)

### Kubernetes connection issues

**Error:** `Unable to connect to Kubernetes cluster`

**Solution:**
```bash
# Verify kubectl
kubectl get nodes

# Check kubeconfig
export KUBECONFIG=$HOME/.kube/config

# Restart tools
python -c "from monitoring_tool import *; print('✓ Connected')"
```

### Ollama not responding

**Error:** `Connection refused to localhost:11434`

**Solution:**
```bash
# Start Ollama
ollama serve

# Verify model
ollama list

# Ensure model is pulled
ollama pull llama2
```

## Advanced Features

### Real-time Streaming Responses

To enable server-sent events (SSE) for streaming tool execution:

Edit `api_server.py`:
```python
from fastapi.responses import StreamingResponse

@app.post("/api/sre/stream")
async def query_sre_agent_stream(request: QueryRequest):
    async def generate():
        for chunk in run_advanced_workflow_streaming(request.query):
            yield f"data: {json.dumps(chunk)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

Update frontend to handle SSE:
```typescript
const source = new EventSource('/api/sre/stream');
source.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Update UI with streaming data
};
```

### Integration with External Systems

#### Slack Notifications

Add to `api_server.py`:
```python
from slack_sdk import WebClient

slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

async def notify_slack(message: str, severity: str):
    color = {"critical": "danger", "high": "warning", "low": "good"}.get(severity)
    slack_client.chat_postMessage(
        channel="#sre-alerts",
        attachments=[{
            "color": color,
            "text": message
        }]
    )
```

#### PagerDuty Escalation

```python
import pdpyras

pagerduty_api = pdpyras.APISession(
    token=os.getenv("PAGERDUTY_API_KEY")
)

def create_incident(title: str, severity: str):
    pagerduty_api.post("/incidents", json={
        "title": title,
        "service_id": os.getenv("PAGERDUTY_SERVICE_ID"),
        "urgency": "high" if severity == "critical" else "low",
    })
```

## Performance Optimization

### Caching Tool Results

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cluster_metrics():
    # Cache metrics for 5 minutes
    return monitoring_tool.get_metrics()
```

### Parallel Tool Execution

```python
import asyncio

async def run_tools_parallel(query: str):
    results = await asyncio.gather(
        asyncio.to_thread(monitoring_tool.run, query),
        asyncio.to_thread(logs_tool.run, query),
        asyncio.to_thread(cost_analyzer_tool.run, query),
    )
    return results
```

### Database for Conversation History

```bash
pip install sqlalchemy
```

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///sre_history.db")
Session = sessionmaker(bind=engine)

# Store conversations for audit trail
```

## Security Best Practices

1. **API Authentication**
   ```python
   from fastapi.security import HTTPBearer
   security = HTTPBearer()
   ```

2. **HTTPS in Production**
   ```bash
   # Use Let's Encrypt
   certbot certonly --standalone -d api.yourdomain.com
   ```

3. **Input Validation**
   - Already implemented with Pydantic
   - Custom validators for queries

4. **RBAC for Kubernetes**
   - Create service account with limited permissions
   - Use KUBECONFIG with restricted role

5. **Rate Limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/api/sre")
   @limiter.limit("10/minute")
   async def query_sre_agent(request: QueryRequest):
       ...
   ```

## Monitoring & Logging

### Application Logs

```bash
# View backend logs
docker logs sreagent-backend

# Or in terminal
tail -f /var/log/sreagent.log
```

### Prometheus Metrics

The backend exposes metrics at `/metrics`:
```
GET http://localhost:3001/metrics
```

Configure Prometheus scrape config:
```yaml
scrape_configs:
  - job_name: 'sreagent'
    static_configs:
      - targets: ['localhost:3001']
```

## Deployment

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "3001:3001"
    environment:
      - KUBECONFIG=/root/.kube/config
    volumes:
      - ~/.kube/config:/root/.kube/config

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://backend:3001
    depends_on:
      - backend
```

Run:
```bash
docker-compose up -d
```

### Kubernetes Deployment

Create `sreagent-deployment.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: sreagent

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sreagent-backend
  namespace: sreagent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sreagent-backend
  template:
    metadata:
      labels:
        app: sreagent-backend
    spec:
      serviceAccountName: sreagent
      containers:
      - name: backend
        image: sreagent-backend:latest
        ports:
        - containerPort: 3001
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: sreagent-backend
  namespace: sreagent
spec:
  type: LoadBalancer
  ports:
  - port: 3001
    targetPort: 3001
  selector:
    app: sreagent-backend
```

Deploy:
```bash
kubectl apply -f sreagent-deployment.yaml
```

## Support & Documentation

- **API Docs**: http://localhost:3001/docs (Swagger UI)
- **LangGraph Integration**: See `LANGGRAPH_INTEGRATION.md`
- **SRE Tools**: See `SRE_TOOLS_README.md`
- **Ansible Tool**: See `ANSIBLE_README.md`
- **Helm Tool**: See `HELM_README.md`

## Next Steps

1. **Enable Real-time Monitoring**: Implement WebSocket for live updates
2. **Add Dashboard**: Create analytics and metrics visualization
3. **Integrate PagerDuty**: Automatic incident creation for critical alerts
4. **Multi-tenant Support**: Add user/organization isolation
5. **Conversation History**: Persist chat history to database

## License

This project is part of the SREAgent toolkit. See LICENSE file for details.
