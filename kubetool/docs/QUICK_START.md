# SREAgent Quick Start Guide

Get up and running with SREAgent in 10 minutes.

## 🚀 Quick Start (5 mins)

### Prerequisites
- Python 3.8+ installed
- Node.js 18+ installed
- kubectl configured for your cluster
- Ollama running with llama2 model

### 1. Start the Backend (Terminal 1)

```bash
cd kubetool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
python api_server.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:3001
```

### 2. Start the Frontend (Terminal 2)

```bash
cd kubetool/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
> next dev
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

### 3. Open in Browser

Visit: **http://localhost:3000**

You should see the SREAgent chat interface! 🎉

## 💬 First Queries to Try

### 1. Check Cluster Health
```
Show me the overall health of the cluster
```

### 2. Monitor Resource Usage
```
What pods are using the most CPU?
```

### 3. Check for Issues
```
Are there any pods in CrashLoopBackOff?
```

### 4. Cost Analysis
```
Find wasted resources in the cluster
```

### 5. Troubleshooting
```
Get logs from the last failed pod
```

## 🔧 Common Tasks

### Check API Health
```bash
curl http://localhost:3001/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "monitoring": "available",
    "logs": "available",
    "healing": "available",
    "cost_analyzer": "available"
  }
}
```

### View API Documentation
Open: **http://localhost:3001/docs**

### See Available Tools
```bash
curl http://localhost:3001/api/tools
```

### Get Example Queries
```bash
curl http://localhost:3001/api/examples
```

## 🆘 Troubleshooting

### Backend won't start
```bash
# Verify Python dependencies
python -c "import fastapi; import uvicorn; print('✓ OK')"

# If missing, reinstall
pip install fastapi uvicorn pydantic langchain-core langchain-ollama langgraph
```

### Frontend won't start
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Try again
npm run dev
```

### Can't connect to Kubernetes
```bash
# Verify kubectl works
kubectl get nodes

# Check kubeconfig
export KUBECONFIG=$HOME/.kube/config

# Test by running a tool
python -c "from monitoring_tool import *; print('✓ Connected')"
```

### Ollama not responding
```bash
# Start Ollama (if not running)
ollama serve

# In another terminal
ollama pull llama2

# Verify
curl http://localhost:11434/api/tags
```

## 📊 Using the Advanced Workflow

The Advanced workflow adds approval gates and rollback capability:

1. In the frontend header, toggle **Advanced** mode
2. Ask: "Restart the failing pod"
3. The system will:
   - Classify severity
   - Create an action plan
   - Request approval
   - Execute if approved
   - Verify the result

## 🔄 Workflow Types

### Basic Workflow
- Fast query processing
- Direct tool execution
- Good for monitoring and analysis
- No approval gates

### Advanced Workflow
- Includes approval steps
- Rollback capability for critical actions
- Severity classification
- Audit trail of all actions

## 📚 Next Steps

1. **Read Full Setup Guide**: `SETUP_AND_DEPLOYMENT.md`
2. **Learn about Tools**: `SRE_TOOLS_README.md`
3. **LangGraph Integration**: `LANGGRAPH_INTEGRATION.md`
4. **Customize for Your Cluster**: See tool configuration in each file

## 🎯 Key Features

✅ Natural language queries  
✅ Real-time cluster monitoring  
✅ Automated log searching  
✅ Self-healing pod remediation  
✅ Cost analysis and optimization  
✅ Advanced workflows with approval  
✅ Audit trail of all actions  
✅ Dark mode support  

## 💡 Pro Tips

1. **Use Quick Actions**: Click the buttons in the chat for common queries
2. **Check Status Panel**: The right sidebar shows findings and recommendations
3. **Export Results**: Copy any finding or recommendation
4. **Use Advanced Mode**: For risky operations like pod restarts

## 🐛 Report Issues

If something isn't working:

1. Check the terminal where you ran the backend
2. Look for error messages in browser console (F12)
3. Try the troubleshooting steps above
4. Check `SETUP_AND_DEPLOYMENT.md` for more details

## 📞 Support

For detailed help:
- API Documentation: http://localhost:3001/docs
- Tool Documentation: See README files in kubetool/
- LangGraph Docs: Check LANGGRAPH_INTEGRATION.md

---

**That's it!** You're now using SREAgent. Happy monitoring! 🚀
