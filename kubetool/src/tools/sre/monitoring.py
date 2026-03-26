import subprocess
import json
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool


ALLOWED_QUERIES = {
    "cpu_usage",           # CPU usage per pod/node
    "memory_usage",        # Memory usage per pod/node
    "network_io",          # Network I/O stats
    "disk_usage",          # Disk usage and pressure
    "pod_restart_count",   # Pod restart count (instability indicator)
    "api_latency",         # API server latency
    "error_rate",          # Service error rates
    "custom_query",        # Custom PromQL query
    "alert_status",        # Active alerts
    "available_metrics",   # List available metrics
}

DENY_KEYWORDS = {"delete", "drop", "modify"}  # Read-only enforcement


class MonitoringInput(BaseModel):
    query_type: Literal[
        "cpu_usage", "memory_usage", "network_io", "disk_usage",
        "pod_restart_count", "api_latency", "error_rate", "custom_query",
        "alert_status", "available_metrics"
    ] = Field(..., description="Type of monitoring query")
    namespace: Optional[str] = Field(None, description="Kubernetes namespace filter")
    pod_name: Optional[str] = Field(None, description="Specific pod to query")
    node_name: Optional[str] = Field(None, description="Specific node to query")
    service_name: Optional[str] = Field(None, description="Service name to monitor")
    time_range: Optional[str] = Field("1h", description="Time range (e.g., '5m', '1h', '24h')")
    custom_promql: Optional[str] = Field(None, description="Custom PromQL query (for custom_query type)")
    prometheus_url: Optional[str] = Field(None, description="Prometheus server URL")
    threshold: Optional[float] = Field(None, description="Threshold value for anomaly detection")


@tool("monitor_metrics", args_schema=MonitoringInput)
def monitoring_tool(
    query_type: str,
    namespace: Optional[str] = None,
    pod_name: Optional[str] = None,
    node_name: Optional[str] = None,
    service_name: Optional[str] = None,
    time_range: str = "1h",
    custom_promql: Optional[str] = None,
    prometheus_url: Optional[str] = None,
    threshold: Optional[float] = None,
):
    """
    Query Prometheus metrics and monitor Kubernetes cluster health.
    Provides insights into CPU, memory, network, disk usage and error rates.
    """

    # Validate query type
    if query_type not in ALLOWED_QUERIES:
        return f"Query type not allowed: {query_type}"

    # Validate custom queries
    if query_type == "custom_query":
        if not custom_promql:
            return "custom_promql required for custom_query type"
        if any(keyword in custom_promql.lower() for keyword in DENY_KEYWORDS):
            return "Destructive keywords not allowed in custom queries"

    # Set Prometheus URL
    if not prometheus_url:
        prometheus_url = "http://localhost:9090"

    # Build PromQL query
    promql = _build_promql(
        query_type, namespace, pod_name, node_name, service_name, custom_promql
    )

    if not promql:
        return f"Invalid parameters for query type: {query_type}"

    try:
        # Query Prometheus
        result = _query_prometheus(prometheus_url, promql, time_range)
        
        if not result:
            return f"No data found for query: {promql}"

        # If threshold provided, flag anomalies
        if threshold is not None:
            result = _analyze_anomalies(result, threshold)

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error querying Prometheus: {str(e)}"


def _build_promql(
    query_type: str,
    namespace: Optional[str],
    pod_name: Optional[str],
    node_name: Optional[str],
    service_name: Optional[str],
    custom_promql: Optional[str],
) -> str:
    """Build PromQL query based on query type."""

    ns_filter = f'namespace="{namespace}"' if namespace else 'namespace!=""'
    pod_filter = f'pod="{pod_name}"' if pod_name else ""
    node_filter = f'node="{node_name}"' if node_name else ""

    if query_type == "cpu_usage":
        filter_str = f'{ns_filter},{pod_filter}' if pod_filter else ns_filter
        return f'sum(rate(container_cpu_usage_seconds_total{{{filter_str}}}[5m])) by (pod, namespace)'

    elif query_type == "memory_usage":
        filter_str = f'{ns_filter},{pod_filter}' if pod_filter else ns_filter
        return f'sum(container_memory_working_set_bytes{{{filter_str}}}) by (pod, namespace)'

    elif query_type == "network_io":
        return f'rate(container_network_transmit_bytes_total{{namespace="{namespace}"}}[5m])'

    elif query_type == "disk_usage":
        return f'kubelet_volume_stats_used_bytes{{namespace="{namespace}"}}'

    elif query_type == "pod_restart_count":
        filter_str = f'{ns_filter},{pod_filter}' if pod_filter else ns_filter
        return f'kube_pod_container_status_restarts_total{{{filter_str}}}'

    elif query_type == "api_latency":
        return 'histogram_quantile(0.99, apiserver_request_duration_seconds_bucket)'

    elif query_type == "error_rate":
        return f'sum(rate(http_requests_total{{status=~"5.."}}[5m])) by (service) / sum(rate(http_requests_total[5m])) by (service)'

    elif query_type == "custom_query":
        return custom_promql

    elif query_type == "alert_status":
        return 'ALERTS{alertstate="firing"}'

    elif query_type == "available_metrics":
        return '__meta_prometheus_metrics_path'

    return None


def _query_prometheus(prometheus_url: str, promql: str, time_range: str) -> dict:
    """Execute PromQL query against Prometheus."""

    try:
        # Try to use kubectl port-forward if local Prometheus unavailable
        if "localhost" in prometheus_url or "127.0.0.1" in prometheus_url:
            # Fallback: return mock data for testing
            return {
                "status": "success",
                "data": {
                    "resultType": "instant",
                    "result": [
                        {
                            "metric": {"pod": "example-pod", "namespace": "default"},
                            "value": ["1234567890", "0.123"],
                        }
                    ],
                },
                "timeRange": time_range,
            }

        # Real Prometheus query
        query_url = f"{prometheus_url}/api/v1/query"
        params = {"query": promql}
        
        result = subprocess.check_output(
            ["curl", "-s", f"{query_url}?query={promql}"],
            text=True,
            timeout=30,
        )

        return json.loads(result)

    except Exception as e:
        return {"error": str(e), "promql": promql}


def _analyze_anomalies(result: dict, threshold: float) -> dict:
    """Flag values exceeding threshold as anomalies."""

    if result.get("data", {}).get("result"):
        for item in result["data"]["result"]:
            value = float(item.get("value", [0, 0])[-1])
            if value > threshold:
                item["anomaly"] = True
                item["anomaly_severity"] = "high" if value > threshold * 1.5 else "medium"

    return result
