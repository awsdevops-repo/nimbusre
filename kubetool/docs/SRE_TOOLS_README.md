# SREAgent - Complete Site Reliability Engineering Toolkit

A comprehensive suite of LangChain-based tools for Kubernetes cluster management, monitoring, troubleshooting, and cost optimization. Part of the SREAgent framework.

## Tools Overview

### 1. 🔍 Monitoring Tool (Prometheus/Grafana)
Query cluster metrics and health status in real-time.

**Operations:**
- `cpu_usage` - CPU usage per pod/node
- `memory_usage` - Memory consumption metrics
- `network_io` - Network I/O statistics
- `disk_usage` - Disk usage and pressure alerts
- `pod_restart_count` - Pod restart count (instability indicator)
- `api_latency` - API server latency
- `error_rate` - Service error rates
- `alert_status` - Active Prometheus alerts
- `custom_query` - Custom PromQL queries
- `available_metrics` - List available metrics

**Examples:**
```python
from monitoring_tool import monitoring_tool

# Query CPU usage
result = monitoring_tool(
    query_type="cpu_usage",
    namespace="default",
    time_range="1h"
)

# Check active alerts
result = monitoring_tool(query_type="alert_status")

# Custom PromQL query with anomaly detection
result = monitoring_tool(
    query_type="custom_query",
    custom_promql='rate(http_requests_total[5m])',
    threshold=100  # Flag values > 100
)
```

---

### 2. 📋 Log Aggregation Tool
Search, filter, and aggregate logs across Kubernetes pods.

**Operations:**
- `pod_logs` - Get logs from a specific pod
- `pod_logs_follow` - Stream/follow pod logs
- `previous_logs` - Get crash logs (previous container)
- `search_logs` - Search logs for patterns
- `logs_by_label` - Get logs from pods matching label selector
- `logs_by_node` - Aggregate logs from all pods on a node
- `log_stats` - Get log count and size statistics

**Examples:**
```python
from logs_tool import logs_tool

# Get pod logs
result = logs_tool(
    operation="pod_logs",
    namespace="default",
    pod_name="nginx-1234",
    lines=100
)

# Search for errors
result = logs_tool(
    operation="search_logs",
    namespace="default",
    pod_name="api-server",
    search_pattern="ERROR|FATAL",
    lines=50
)

# Get logs from pods with specific label
result = logs_tool(
    operation="logs_by_label",
    namespace="monitoring",
    label_selector="app=prometheus",
    since="1h"
)
```

---

### 3. 🏥 Self-Healing Tool
Implement automated remediation and health management policies.

**Operations:**
- `restart_pod` - Restart unhealthy pod
- `restart_deployment` - Rollout restart entire deployment
- `scale_deployment` - Scale deployment to handle load
- `drain_node` - Gracefully drain node for maintenance
- `cordon_node` - Mark node unschedulable
- `uncordon_node` - Mark node schedulable again
- `evict_pod` - Evict pod from node
- `check_health` - Check pod readiness and liveness status
- `create_policy` - Create self-healing automation policy

**Examples:**
```python
from healing_tool import healing_tool

# Restart unhealthy pod
result = healing_tool(
    action="restart_pod",
    namespace="default",
    pod_name="crashlooping-app",
    grace_period=30
)

# Scale deployment under high load
result = healing_tool(
    action="scale_deployment",
    namespace="production",
    deployment_name="web-app",
    replicas=5
)

# Check pod health
result = healing_tool(
    action="check_health",
    namespace="default",
    pod_name="my-app"
)

# Drain node for maintenance
result = healing_tool(
    action="drain_node",
    node_name="node-xyz",
    grace_period=60
)
```

---

### 4. 💰 Cost Analysis Tool
Analyze cluster costs and identify optimization opportunities.

**Operations:**
- `resource_waste` - Detect over-provisioned pods
- `cost_by_namespace` - Cost breakdown by namespace
- `cost_by_pod` - Cost per individual pod
- `unused_pvcs` - Identify unattached volumes
- `unused_services` - Find unused LoadBalancer services
- `node_utilization` - Node efficiency analysis
- `rightsizing_recommendations` - Suggest resource limit changes
- `cluster_cost` - Total cluster cost estimation
- `compare_periods` - Compare costs across time periods
- `optimization_opportunities` - List all savings opportunities

**Examples:**
```python
from cost_analyzer_tool import cost_analyzer_tool

# Find resource waste
result = cost_analyzer_tool(
    analysis_type="resource_waste"
)

# Cost breakdown by namespace
result = cost_analyzer_tool(
    analysis_type="cost_by_namespace",
    time_period="30d"
)

# Estimate cluster monthly cost
result = cost_analyzer_tool(
    analysis_type="cluster_cost",
    time_period="30d",
    cpu_cost_per_core=0.10,
    memory_cost_per_gb=0.01,
    storage_cost_per_gb=0.10
)

# Get rightsizing recommendations
result = cost_analyzer_tool(
    analysis_type="rightsizing_recommendations"
)

# Identify optimization opportunities
result = cost_analyzer_tool(
    analysis_type="optimization_opportunities"
)
```

---

## Unified SREAgent Interface

Use all tools together with natural language queries:

```python
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from monitoring_tool import monitoring_tool
from logs_tool import logs_tool
from healing_tool import healing_tool
from cost_analyzer_tool import cost_analyzer_tool

# Create agent with all SRE tools
llm = ChatOllama(model="llama3.1", temperature=0).bind_tools([
    monitoring_tool,
    logs_tool,
    healing_tool,
    cost_analyzer_tool,
])

agent = create_agent(llm, tools=[
    monitoring_tool,
    logs_tool,
    healing_tool,
    cost_analyzer_tool,
])

# Query in natural language
result = agent.invoke({
    "messages": [("human", "Find high CPU pods, check their logs, and suggest cost optimizations")]
})
print(result['messages'][-1].content)
```

---

## Setup

### Prerequisites

```bash
# Kubernetes access
kubectl cluster-info
echo $KUBECONFIG

# Prometheus (for monitoring)
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring

# LangChain
pip install langchain-ollama langchain-core

# Local Ollama with llama3.1
ollama pull llama3.1
ollama serve
```

### Configuration

1. **Ensure kubectl access**:
```bash
kubectl get nodes
kubectl get pods -A
```

2. **Configure Prometheus endpoint** (if not localhost:9090):
```bash
kubectl port-forward -n monitoring prometheus-0 9090:9090
```

3. **Set cost model** (customize per your cloud provider):
```python
cost_analyzer_tool(
    analysis_type="cluster_cost",
    cpu_cost_per_core=0.10,      # AWS: ~$0.10/core/hour
    memory_cost_per_gb=0.01,      # AWS: ~$0.01/GB/hour
    storage_cost_per_gb=0.10,     # AWS: ~$0.10/GB/month
)
```

---

## Common Workflows

### SRE Response to High CPU Alert

```python
# 1. Check current metrics
monitoring_tool(query_type="cpu_usage", threshold=80)

# 2. Identify problematic pods
logs_tool(operation="logs_by_label", label_selector="env=prod")

# 3. Get logs for context
logs_tool(operation="pod_logs", pod_name="high-cpu-pod")

# 4. Remediate: scale or restart
healing_tool(action="scale_deployment", deployment_name="app", replicas=5)

# 5. Analyze impact on costs
cost_analyzer_tool(analysis_type="cost_by_pod")
```

### Cost Optimization Initiative

```python
# 1. Find waste
cost_analyzer_tool(analysis_type="resource_waste")

# 2. Get recommendations
cost_analyzer_tool(analysis_type="rightsizing_recommendations")

# 3. Check node efficiency
cost_analyzer_tool(analysis_type="node_utilization")

# 4. Identify unused resources
cost_analyzer_tool(analysis_type="unused_pvcs")
cost_analyzer_tool(analysis_type="unused_services")

# 5. Estimate savings
cost_analyzer_tool(analysis_type="optimization_opportunities")
```

### Pod Troubleshooting

```python
# 1. Check health
healing_tool(action="check_health", pod_name="failing-pod")

# 2. Get previous crash logs
logs_tool(operation="previous_logs", pod_name="failing-pod")

# 3. Check recent logs
logs_tool(operation="pod_logs", pod_name="failing-pod", lines=200)

# 4. Look for error patterns
logs_tool(operation="search_logs", pod_name="failing-pod", search_pattern="ERROR|Exception")

# 5. Remediate
healing_tool(action="restart_pod", pod_name="failing-pod")

# 6. Monitor recovery
monitoring_tool(query_type="pod_restart_count", pod_name="failing-pod")
```

---

## Testing

```bash
# Run all tests
python test_sre_tools.py

# Interactive agent
python sre_agent.py
```

---

## Security Considerations

✅ **Built-in Safeguards:**
- Protected namespaces (kube-system, kube-public, kube-node-lease)
- Read-only Prometheus queries
- No destructive log operations
- Critical deployment protection
- Grace period enforcement on pod deletion

⚠️ **Best Practices:**
- Use RBAC to limit agent service account permissions
- Audit all remediation actions
- Set up alerts for scaling events
- Review cost recommendations before implementation
- Test healing policies in non-prod first

---

## Integration Points

Works seamlessly with other SREAgent tools:
- [kubectl tool](tool.py) - Direct Kubernetes operations
- [Ansible tool](ansible_tool.py) - Multi-host management
- [Helm tool](helm_tool.py) - Application deployment
- **SRE Tools** (this package) - Monitoring, logs, healing, costs

---

## Performance Notes

- Prometheus queries: ~1-5 seconds
- Log aggregation: ~2-10 seconds depending on volume
- Cost analysis: ~5-30 seconds (runs comprehensive resource scan)
- Healing actions: ~10-60 seconds (depends on grace periods)

---

## Troubleshooting

### "Prometheus not found"
```bash
# Check if Prometheus is running
kubectl get svc -n monitoring | grep prometheus

# Port forward if needed
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
```

### "kubectl logs not found"
```bash
# Ensure pod exists
kubectl get pods -n <namespace>

# Check pod is not being initialized
kubectl describe pod <pod-name> -n <namespace>
```

### "High cost estimate"
Validate against cloud provider:
```bash
# AWS
aws ce get-cost-and-usage --time-period ... --metrics BlendedCost

# GCP
gcloud billing accounts list
```

---

## Future Enhancements

- Multi-cluster support
- Machine learning anomaly detection
- Automated canary analysis
- Integration with PagerDuty/Slack
- Predictive scaling policies
- Financial chargeback models

---

## SREAgent Complete Suite

| Component | Status | Purpose |
|-----------|--------|---------|
| kubectl tool | ✅ Ready | Direct K8s operations |
| Ansible tool | ✅ Ready | Multi-host management |
| Helm tool | ✅ Ready | Application deployment |
| **Monitoring** | ✅ Ready | Prometheus/Grafana queries |
| **Logs** | ✅ Ready | Pod log aggregation |
| **Healing** | ✅ Ready | Auto-remediation policies |
| **Cost Analysis** | ✅ Ready | Resource optimization |

