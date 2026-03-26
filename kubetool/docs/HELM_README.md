# Helm Deployment Agent Tool

A LangChain-based agent tool for managing Kubernetes application deployments using Helm. Deploy, upgrade, monitor, and rollback applications through natural language queries or programmatic APIs.

## Overview

The **Helm Deployment Agent** provides a secure, validated interface to manage Helm releases across Kubernetes clusters. It supports:

- **Installation** - Deploy new charts from repositories
- **Upgrades** - Update existing releases with new values
- **Rollback** - Revert to previous release versions
- **Monitoring** - Check release status and values
- **Search** - Discover available charts
- **Cleanup** - Safely uninstall releases

## Features

✅ **Safe by default** - Protected namespaces, no destructive operations without explicit intent  
✅ **Multi-environment** - Works with any Kubernetes cluster via kubeconfig  
✅ **LangChain integration** - Natural language queries through AI agents  
✅ **Input validation** - Pydantic schemas enforce allowed operations  
✅ **Wait strategies** - Configurable timeouts and ready-state checks  
✅ **Values override** - Set Helm values programmatically or via files  

## Setup

### Prerequisites

```bash
# Install Helm 3
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version  # Should show v3.x.x

# Install LangChain dependencies
pip install langchain-ollama langchain-core

# Verify Kubernetes access
kubectl cluster-info
```

### Configuration

1. **Ensure valid kubeconfig**:
```bash
# Default location
~/.kube/config

# Or set environment variable
export KUBECONFIG=/path/to/kubeconfig

# Test connection
kubectl get nodes
```

2. **Add Helm repositories**:
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

3. **Create namespaces**:
```bash
kubectl create namespace monitoring
kubectl create namespace ingress-nginx
kubectl create namespace databases
```

## Usage

### Direct Tool Usage

```python
from helm_tool import helm_tool

# Install NGINX Ingress Controller
result = helm_tool(
    operation="install",
    release_name="nginx-ingress",
    chart="nginx-community/nginx-ingress",
    namespace="ingress-nginx",
    values={
        "replicaCount": "2",
        "serviceType": "LoadBalancer",
    },
    wait=True,
    timeout="10m",
)
print(result)

# List releases
result = helm_tool(
    operation="list",
    namespace="ingress-nginx",
)
print(result)

# Check status
result = helm_tool(
    operation="status",
    release_name="nginx-ingress",
    namespace="ingress-nginx",
)
print(result)

# Upgrade release
result = helm_tool(
    operation="upgrade",
    release_name="nginx-ingress",
    chart="nginx-community/nginx-ingress",
    namespace="ingress-nginx",
    values={
        "replicaCount": "3",  # Scale up
    },
)
print(result)

# Rollback to previous version
result = helm_tool(
    operation="rollback",
    release_name="nginx-ingress",
    version="1",  # Revision number
    namespace="ingress-nginx",
)
print(result)
```

### With LangChain Agent

```python
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from helm_tool import helm_tool

# Create agent with Helm tool
llm = ChatOllama(model="llama3.1", temperature=0).bind_tools([helm_tool])
agent = create_agent(llm, tools=[helm_tool])

# Query in natural language
result = agent.invoke({
    "messages": [("human", "Install prometheus in the monitoring namespace")]
})
print(result['messages'][-1].content)

# Another example
result = agent.invoke({
    "messages": [("human", "What is the status of the nginx-ingress release?")]
})
print(result['messages'][-1].content)
```

## API Reference

### Operations

| Operation | Description | Required Args |
|-----------|-------------|---|
| `install` | Deploy a new Helm chart | `release_name`, `chart` |
| `upgrade` | Update an existing release | `release_name`, `chart` |
| `uninstall` | Remove a release | `release_name` |
| `list` | List all releases in namespace | — |
| `status` | Check release status | `release_name` |
| `get_values` | Get release configuration | `release_name` |
| `get_notes` | Get release notes/status | `release_name` |
| `rollback` | Revert to previous version | `release_name`, `version` |
| `search` | Search for available charts | `chart` |

### Parameters

- **operation** (str): Helm operation to perform
- **release_name** (str, optional): Name of the Helm release
- **chart** (str, optional): Chart name or repo (e.g., `prometheus-community/kube-prometheus-stack`)
- **namespace** (str, optional): Kubernetes namespace (defaults to `default`)
- **version** (str, optional): Chart or release revision version
- **values** (dict, optional): Helm values to override (e.g., `{"replicaCount": "3"}`)
- **kubeconfig** (str, optional): Path to kubeconfig (defaults to `~/.kube/config`)
- **wait** (bool): Wait for resources to be ready (default: `True`)
- **timeout** (str, optional): Operation timeout (e.g., `10m`, `300s`)

## Testing

```bash
# Run basic tests
python test_helm_tool.py

# Test with real Kubernetes cluster
python -c "
from helm_tool import helm_tool
result = helm_tool(operation='list', namespace='kube-system')
print(result)
"
```

## Examples

### Example 1: Install Prometheus Monitoring Stack

```python
result = helm_tool(
    operation="install",
    release_name="prometheus",
    chart="prometheus-community/kube-prometheus-stack",
    namespace="monitoring",
    values={
        "prometheus.prometheusSpec.retention": "15d",
        "grafana.adminPassword": "changeme",
        "grafana.replicas": "2",
    },
    wait=True,
    timeout="15m",
)
print(result)
```

### Example 2: Upgrade Release with New Configuration

```python
result = helm_tool(
    operation="upgrade",
    release_name="nginx-ingress",
    chart="nginx-community/nginx-ingress",
    namespace="ingress-nginx",
    values={
        "replicaCount": "3",
        "controller.resources.limits.cpu": "1000m",
        "controller.resources.limits.memory": "1Gi",
    },
    wait=True,
    timeout="5m",
)
print(result)
```

### Example 3: Check and Rollback on Issues

```python
# Check current status
status = helm_tool(
    operation="status",
    release_name="myapp",
    namespace="production",
)
print(f"Status: {status}")

# If there are issues, rollback
rollback = helm_tool(
    operation="rollback",
    release_name="myapp",
    version="2",  # Previous stable revision
    namespace="production",
    wait=True,
)
print(f"Rollback result: {rollback}")
```

### Example 4: Search and Install PostgreSQL Database

```python
# Search for PostgreSQL charts
search = helm_tool(
    operation="search",
    chart="postgres",
)
print(f"Available charts: {search}")

# Install
result = helm_tool(
    operation="install",
    release_name="postgres",
    chart="bitnami/postgresql",
    namespace="databases",
    values={
        "global.postgresql.password": "secure-db-password",
        "primary.persistence.size": "100Gi",
        "replica.replicaCount": "2",
    },
    wait=True,
    timeout="10m",
)
print(result)
```

## Security Considerations

⚠️ **Protected Namespaces**
- Cannot install/upgrade/uninstall in: `kube-system`, `kube-public`, `kube-node-lease`
- These system namespaces are protected from accidental changes

✅ **Best Practices**
- Use separate kubeconfigs with limited RBAC roles
- Store sensitive values (passwords, secrets) in Kubernetes Secrets, not in values
- Always use `--wait` and `--timeout` for production deployments
- Test upgrades in staging before production
- Keep release history: `helm list --max=10` to review past revisions
- Use version constraints in values to prevent unexpected chart updates

## Troubleshooting

### "helm not found"
```bash
# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
helm version
```

### "Kubeconfig not found"
```bash
# Check kubeconfig path
echo $KUBECONFIG
ls ~/.kube/config

# Set correct path
export KUBECONFIG=~/.kube/config
```

### "Release not found"
```bash
# List available releases
helm list -n <namespace>

# Check if release exists in different namespace
helm list -A
```

### "Timed out waiting for resources"
```bash
# Increase timeout
helm upgrade myapp chart --timeout 15m

# Check pod status
kubectl get pods -n <namespace>
kubectl describe pod <pod-name> -n <namespace>
```

### "Chart not found"
```bash
# Update repositories
helm repo update

# Search for charts
helm search repo <chart-name>

# List added repositories
helm repo list
```

## Integration with SREAgent

This tool is part of the **SREAgent** project for:
- ✅ Kubernetes deployment and management
- ✅ Application lifecycle operations
- ✅ Multi-environment deployment coordination

Combined with [kubectl tool](tool.py) and [Ansible inventory tool](ansible_tool.py) for complete infrastructure management.

## Common Commands Reference

```bash
# Repository management
helm repo add <name> <url>
helm repo update
helm search repo <keyword>

# Release management
helm install <release> <chart>
helm upgrade <release> <chart>
helm uninstall <release>
helm list -A

# Inspection
helm status <release> -n <namespace>
helm get values <release> -n <namespace>
helm history <release> -n <namespace>
helm template <release> <chart>

# Rollback
helm rollback <release> <revision> -n <namespace>

# Cleanup
helm delete <release> --namespace <ns> --wait
```

## Resources

- [Official Helm Documentation](https://helm.sh/docs/)
- [Helm Chart Hub](https://artifacthub.io/)
- [Bitnami Helm Charts](https://github.com/bitnami/charts)
- [Kubernetes Package Manager Best Practices](https://helm.sh/docs/chart_best_practices/)
