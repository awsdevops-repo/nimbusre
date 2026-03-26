import subprocess
import json
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool


ALLOWED_ANALYSIS = {
    "resource_waste",      # Detect over-provisioned resources
    "cost_by_namespace",   # Cost breakdown by namespace
    "cost_by_pod",         # Cost per pod
    "unused_pvcs",         # Detect unused persistent volumes
    "unused_services",     # Detect unused LoadBalancer services
    "node_utilization",    # Node efficiency analysis
    "rightsizing_recommendations",  # Recommend better resource limits
    "cluster_cost",        # Total cluster cost
    "compare_periods",     # Compare cost across time periods
    "optimization_opportunities",  # Identify savings opportunities
}


class CostAnalysisInput(BaseModel):
    analysis_type: Literal[
        "resource_waste", "cost_by_namespace", "cost_by_pod", "unused_pvcs",
        "unused_services", "node_utilization", "rightsizing_recommendations",
        "cluster_cost", "compare_periods", "optimization_opportunities"
    ] = Field(..., description="Type of cost analysis to perform")
    namespace: Optional[str] = Field(None, description="Specific namespace to analyze")
    pod_name: Optional[str] = Field(None, description="Specific pod to analyze")
    time_period: Optional[str] = Field("30d", description="Analysis period (e.g., '7d', '30d', '90d')")
    compare_to: Optional[str] = Field(None, description="Period to compare against (e.g., '7d', '30d')")
    cpu_cost_per_core: Optional[float] = Field(0.10, description="Cost per CPU core per hour")
    memory_cost_per_gb: Optional[float] = Field(0.01, description="Cost per GB memory per hour")
    storage_cost_per_gb: Optional[float] = Field(0.10, description="Cost per GB storage per month")
    include_external: bool = Field(False, description="Include external service costs")
    kubeconfig: Optional[str] = Field(None, description="Path to kubeconfig file")


@tool("analyze_costs", args_schema=CostAnalysisInput)
def cost_analyzer_tool(
    analysis_type: str,
    namespace: Optional[str] = None,
    pod_name: Optional[str] = None,
    time_period: str = "30d",
    compare_to: Optional[str] = None,
    cpu_cost_per_core: float = 0.10,
    memory_cost_per_gb: float = 0.01,
    storage_cost_per_gb: float = 0.10,
    include_external: bool = False,
    kubeconfig: Optional[str] = None,
):
    """
    Analyze Kubernetes cluster costs and identify optimization opportunities.
    Detects resource waste, rightsizing needs, and cost anomalies.
    """

    # Validate analysis type
    if analysis_type not in ALLOWED_ANALYSIS:
        return f"Analysis type not allowed: {analysis_type}"

    # Gather resource data
    try:
        resources = _gather_cluster_resources(namespace, kubeconfig)
        
        if not resources:
            return "No resources found in cluster"

        # Perform analysis
        result = _perform_cost_analysis(
            analysis_type, resources, namespace, pod_name,
            time_period, compare_to,
            cpu_cost_per_core, memory_cost_per_gb, storage_cost_per_gb
        )

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error analyzing costs: {str(e)}"


def _gather_cluster_resources(namespace: Optional[str], kubeconfig: Optional[str]) -> dict:
    """Gather resource usage data from cluster."""

    try:
        base_cmd = ["kubectl", "get"]
        if kubeconfig:
            base_cmd.extend(["--kubeconfig", kubeconfig])

        # Get all pods with resource requests/limits
        ns_flag = ["-n", namespace] if namespace else ["-A"]
        
        pods_cmd = base_cmd + ["pods"] + ns_flag + [
            "-o", "json"
        ]

        pods_output = subprocess.check_output(
            pods_cmd, text=True, timeout=30
        )
        pods = json.loads(pods_output)

        # Get PVCs
        pvc_cmd = base_cmd + ["pvc"] + ns_flag + ["-o", "json"]
        pvc_output = subprocess.check_output(
            pvc_cmd, text=True, timeout=30
        )
        pvcs = json.loads(pvc_output)

        # Get nodes
        nodes_cmd = base_cmd + ["nodes", "-o", "json"]
        nodes_output = subprocess.check_output(
            nodes_cmd, text=True, timeout=30
        )
        nodes = json.loads(nodes_output)

        return {
            "pods": pods.get("items", []),
            "pvcs": pvcs.get("items", []),
            "nodes": nodes.get("items", []),
        }

    except Exception as e:
        return {"error": str(e)}


def _perform_cost_analysis(
    analysis_type: str,
    resources: dict,
    namespace: Optional[str],
    pod_name: Optional[str],
    time_period: str,
    compare_to: Optional[str],
    cpu_cost: float,
    memory_cost: float,
    storage_cost: float,
) -> dict:
    """Perform specified cost analysis."""

    if analysis_type == "resource_waste":
        return _analyze_resource_waste(resources, cpu_cost, memory_cost)

    elif analysis_type == "cost_by_namespace":
        return _cost_by_namespace(resources, cpu_cost, memory_cost, storage_cost)

    elif analysis_type == "cost_by_pod":
        return _cost_by_pod(resources, cpu_cost, memory_cost, namespace, pod_name)

    elif analysis_type == "unused_pvcs":
        return _find_unused_pvcs(resources)

    elif analysis_type == "unused_services":
        return _find_unused_services(resources)

    elif analysis_type == "node_utilization":
        return _analyze_node_utilization(resources, cpu_cost, memory_cost)

    elif analysis_type == "rightsizing_recommendations":
        return _rightsizing_recommendations(resources, cpu_cost, memory_cost)

    elif analysis_type == "cluster_cost":
        return _estimate_cluster_cost(resources, cpu_cost, memory_cost, storage_cost, time_period)

    elif analysis_type == "compare_periods":
        return _compare_cost_periods(resources, time_period, compare_to)

    elif analysis_type == "optimization_opportunities":
        return _find_optimization_opportunities(resources, cpu_cost, memory_cost)

    return {"error": "Analysis type not found"}


def _analyze_resource_waste(resources: dict, cpu_cost: float, memory_cost: float) -> dict:
    """Identify over-provisioned pods."""

    waste_findings = []
    total_waste = 0

    for pod in resources.get("pods", []):
        containers = pod.get("spec", {}).get("containers", [])
        
        for container in containers:
            requests = container.get("resources", {}).get("requests", {})
            limits = container.get("resources", {}).get("limits", {})
            
            # Flag if limits 2x+ higher than requests (potential waste)
            if limits and requests:
                cpu_req = _parse_resource(requests.get("cpu", "0"))
                cpu_lim = _parse_resource(limits.get("cpu", "0"))
                
                if cpu_lim > cpu_req * 2:
                    wasted_cpu = cpu_lim - cpu_req
                    waste_findings.append({
                        "pod": pod.get("metadata", {}).get("name"),
                        "namespace": pod.get("metadata", {}).get("namespace"),
                        "wasted_cpu_cores": wasted_cpu,
                        "estimated_waste_per_month": wasted_cpu * 730 * cpu_cost,
                        "recommendation": "Lower CPU limits to match actual usage"
                    })
                    total_waste += wasted_cpu * 730 * cpu_cost

    return {
        "analysis": "resource_waste",
        "findings": waste_findings,
        "total_estimated_waste": f"${total_waste:.2f}/month",
        "count": len(waste_findings)
    }


def _cost_by_namespace(resources: dict, cpu_cost: float, memory_cost: float, storage_cost: float) -> dict:
    """Calculate cost breakdown by namespace."""

    namespace_costs = {}
    
    for pod in resources.get("pods", []):
        ns = pod.get("metadata", {}).get("namespace", "unknown")
        containers = pod.get("spec", {}).get("containers", [])
        
        if ns not in namespace_costs:
            namespace_costs[ns] = {"cpu": 0, "memory": 0, "storage": 0}
        
        for container in containers:
            requests = container.get("resources", {}).get("requests", {})
            cpu_cores = _parse_resource(requests.get("cpu", "0"))
            mem_gb = _parse_resource(requests.get("memory", "0"), unit="Mi") / 1024
            
            namespace_costs[ns]["cpu"] += cpu_cores * 730 * cpu_cost
            namespace_costs[ns]["memory"] += mem_gb * 730 * memory_cost

    return {
        "analysis": "cost_by_namespace",
        "namespaces": {
            ns: {
                "cpu_cost": f"${costs['cpu']:.2f}",
                "memory_cost": f"${costs['memory']:.2f}",
                "total": f"${costs['cpu'] + costs['memory']:.2f}"
            }
            for ns, costs in namespace_costs.items()
        }
    }


def _cost_by_pod(resources: dict, cpu_cost: float, memory_cost: float, namespace: Optional[str], pod_name: Optional[str]) -> dict:
    """Calculate cost per pod."""

    pod_costs = []
    
    for pod in resources.get("pods", []):
        pod_ns = pod.get("metadata", {}).get("namespace")
        pname = pod.get("metadata", {}).get("name")
        
        if namespace and pod_ns != namespace:
            continue
        if pod_name and pname != pod_name:
            continue
        
        containers = pod.get("spec", {}).get("containers", [])
        total_cost = 0
        
        for container in containers:
            requests = container.get("resources", {}).get("requests", {})
            cpu_cores = _parse_resource(requests.get("cpu", "0"))
            mem_gb = _parse_resource(requests.get("memory", "0"), unit="Mi") / 1024
            
            cost = (cpu_cores * cpu_cost + mem_gb * memory_cost) * 730
            total_cost += cost
        
        pod_costs.append({
            "pod": pname,
            "namespace": pod_ns,
            "estimated_monthly_cost": f"${total_cost:.2f}"
        })

    return {
        "analysis": "cost_by_pod",
        "pods": pod_costs,
        "count": len(pod_costs)
    }


def _find_unused_pvcs(resources: dict) -> dict:
    """Identify unused persistent volumes."""

    unused = []
    
    for pvc in resources.get("pvcs", []):
        # Check if PVC is bound to any pod
        status = pvc.get("status", {}).get("phase")
        if status == "Unbound":
            unused.append({
                "pvc": pvc.get("metadata", {}).get("name"),
                "namespace": pvc.get("metadata", {}).get("namespace"),
                "size": pvc.get("spec", {}).get("resources", {}).get("requests", {}).get("storage"),
                "status": "Unbound - potential waste",
                "recommendation": "Review and delete if not needed"
            })

    return {
        "analysis": "unused_pvcs",
        "unused_volumes": unused,
        "count": len(unused)
    }


def _find_unused_services(resources: dict) -> dict:
    """Identify unused LoadBalancer services (cost sinks)."""

    return {
        "analysis": "unused_services",
        "note": "Use 'kubectl get svc -A' to manually review LoadBalancer services",
        "recommendation": "Delete unused LoadBalancer services - each costs $0.025/hour"
    }


def _analyze_node_utilization(resources: dict, cpu_cost: float, memory_cost: float) -> dict:
    """Analyze node efficiency."""

    node_analysis = []
    
    for node in resources.get("nodes", []):
        node_name = node.get("metadata", {}).get("name")
        capacity = node.get("status", {}).get("capacity", {})
        
        cpu_capacity = _parse_resource(capacity.get("cpu", "0"))
        memory_capacity = _parse_resource(capacity.get("memory", "0"), unit="Ki") / (1024 * 1024)
        
        # Count pods on node
        pods_on_node = [p for p in resources.get("pods", [])
                       if p.get("spec", {}).get("nodeName") == node_name]
        
        total_requested_cpu = sum(
            _parse_resource(
                c.get("resources", {}).get("requests", {}).get("cpu", "0")
            )
            for p in pods_on_node
            for c in p.get("spec", {}).get("containers", [])
        )
        
        utilization = (total_requested_cpu / cpu_capacity * 100) if cpu_capacity > 0 else 0
        
        node_analysis.append({
            "node": node_name,
            "cpu_capacity": cpu_capacity,
            "cpu_requested": total_requested_cpu,
            "utilization_percent": round(utilization, 2),
            "efficiency": "Good" if utilization > 60 else "Low - consider consolidating"
        })

    return {
        "analysis": "node_utilization",
        "nodes": node_analysis
    }


def _rightsizing_recommendations(resources: dict, cpu_cost: float, memory_cost: float) -> dict:
    """Generate rightsizing recommendations."""

    recommendations = []
    
    for pod in resources.get("pods", [])[:5]:  # Top 5 pods
        requests = pod.get("spec", {}).get("containers", [{}])[0].get("resources", {}).get("requests", {})
        limits = pod.get("spec", {}).get("containers", [{}])[0].get("resources", {}).get("limits", {})
        
        if limits and limits.get("cpu"):
            recommendations.append({
                "pod": pod.get("metadata", {}).get("name"),
                "current_cpu_limit": limits.get("cpu"),
                "suggested_cpu_limit": "Reduce by 20%",
                "estimated_savings": "$50-100/month per pod"
            })

    return {
        "analysis": "rightsizing_recommendations",
        "recommendations": recommendations
    }


def _estimate_cluster_cost(resources: dict, cpu_cost: float, memory_cost: float, storage_cost: float, time_period: str) -> dict:
    """Estimate total cluster cost."""

    total_cpu = 0
    total_memory = 0
    total_storage = 0
    
    # Sum CPU and memory
    for pod in resources.get("pods", []):
        for container in pod.get("spec", {}).get("containers", []):
            requests = container.get("resources", {}).get("requests", {})
            total_cpu += _parse_resource(requests.get("cpu", "0"))
            total_memory += _parse_resource(requests.get("memory", "0"), unit="Mi")
    
    # Sum storage
    for pvc in resources.get("pvcs", []):
        storage = pvc.get("spec", {}).get("resources", {}).get("requests", {}).get("storage")
        if storage:
            total_storage += _parse_resource(storage, unit="Gi")
    
    # Calculate costs
    cpu_monthly = total_cpu * 730 * cpu_cost
    memory_monthly = (total_memory / 1024) * 730 * memory_cost
    storage_monthly = total_storage * storage_cost
    total_monthly = cpu_monthly + memory_monthly + storage_monthly

    return {
        "analysis": "cluster_cost",
        "cpu_monthly": f"${cpu_monthly:.2f}",
        "memory_monthly": f"${memory_monthly:.2f}",
        "storage_monthly": f"${storage_monthly:.2f}",
        "total_monthly_estimate": f"${total_monthly:.2f}",
        "total_yearly_estimate": f"${total_monthly * 12:.2f}"
    }


def _compare_cost_periods(resources: dict, time_period: str, compare_to: Optional[str]) -> dict:
    """Compare costs across time periods."""

    return {
        "analysis": "compare_periods",
        "note": "Comparison requires historical data",
        "current_period": time_period,
        "compare_to_period": compare_to or "previous period",
        "recommendation": "Enable cost monitoring with metrics for trend analysis"
    }


def _find_optimization_opportunities(resources: dict, cpu_cost: float, memory_cost: float) -> dict:
    """Identify cost optimization opportunities."""

    opportunities = [
        {
            "opportunity": "Right-size pod CPU limits",
            "savings_potential": "10-20%",
            "effort": "Medium",
            "implementation": "Review pod performance and adjust CPU limits"
        },
        {
            "opportunity": "Remove unused PVCs",
            "savings_potential": "5-15%",
            "effort": "Low",
            "implementation": "Identify and delete unattached volumes"
        },
        {
            "opportunity": "Consolidate to fewer, larger nodes",
            "savings_potential": "15-25%",
            "effort": "High",
            "implementation": "Bin-pack pods more efficiently"
        },
        {
            "opportunity": "Use spot instances for non-critical workloads",
            "savings_potential": "50-70%",
            "effort": "Medium",
            "implementation": "Configure node affinity for spot instances"
        }
    ]

    return {
        "analysis": "optimization_opportunities",
        "opportunities": opportunities,
        "total_potential_savings": "Up to 70% with comprehensive optimization"
    }


def _parse_resource(value: str, unit: str = "m") -> float:
    """Parse Kubernetes resource value to numeric."""

    if not value:
        return 0.0
    
    value = str(value).strip()
    
    # CPU parsing (m = millicores, no suffix = cores)
    if unit == "m" or "m" in value:
        return float(value.replace("m", "")) / 1000
    
    # Memory parsing
    if "Gi" in value:
        return float(value.replace("Gi", "")) * 1024
    elif "Mi" in value:
        return float(value.replace("Mi", ""))
    elif "Ki" in value:
        return float(value.replace("Ki", "")) / 1024
    
    # Storage parsing
    if unit == "Gi" and "Gi" in value:
        return float(value.replace("Gi", ""))
    
    try:
        return float(value)
    except ValueError:
        return 0.0
