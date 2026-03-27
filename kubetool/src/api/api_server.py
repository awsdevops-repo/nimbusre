"""
FastAPI backend to expose SREAgent LangGraph workflow via HTTP API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio

from ..workflows.basic import run_sre_session
from ..workflows.advanced import run_advanced_workflow

app = FastAPI(
    title="SREAgent API",
    description="API for SREAgent Kubernetes management",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    """Request model for SRE queries."""
    query: str
    workflow_type: Optional[str] = None  # "basic" or "advanced"
    max_tools: Optional[int] = 5


class QueryResponse(BaseModel):
    """Response model for SRE queries."""
    status: str
    severity: Optional[str]
    workflow_type: Optional[str]
    findings: Dict[str, Any]
    remediation_plan: Optional[str]
    executed_actions: list
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint redirect."""
    return {"message": "NimbusRE Agent API", "docs": "/docs", "health": "/health"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "monitoring": "available",
            "logs": "available",
            "healing": "available",
            "cost_analyzer": "available",
        }
    }


@app.get("/api/tools")
async def list_tools():
    """List available tools."""
    return {
        "tools": [
            {
                "name": "monitoring_tool",
                "description": "Query Prometheus metrics and cluster health",
                "operations": [
                    "cpu_usage",
                    "memory_usage",
                    "network_io",
                    "pod_restart_count",
                    "error_rate",
                    "alert_status",
                ],
            },
            {
                "name": "logs_tool",
                "description": "Retrieve and search Kubernetes pod logs",
                "operations": [
                    "pod_logs",
                    "search_logs",
                    "previous_logs",
                    "logs_by_label",
                ],
            },
            {
                "name": "healing_tool",
                "description": "Automated pod/deployment remediation",
                "operations": [
                    "restart_pod",
                    "restart_deployment",
                    "scale_deployment",
                    "check_health",
                    "drain_node",
                ],
            },
            {
                "name": "cost_analyzer_tool",
                "description": "Analyze cluster costs and optimization",
                "operations": [
                    "resource_waste",
                    "cost_by_namespace",
                    "rightsizing_recommendations",
                    "optimization_opportunities",
                ],
            },
        ]
    }


@app.post("/api/sre", response_model=QueryResponse)
async def query_sre_agent(request: QueryRequest):
    """
    Main endpoint for SREAgent queries.
    Routes to basic or advanced workflow based on query type.
    """

    workflow_type = request.workflow_type or "basic"

    # If your workflow functions are synchronous:
    def run_workflow():
        if workflow_type == "advanced":
            return run_advanced_workflow(request.query, request.max_tools)
        else:
            return run_sre_session(request.query, request.max_tools)

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(run_workflow),
            timeout=300.0
        )

    # If your workflow functions are async, use this instead:
    # async def run_workflow():
    #     if workflow_type == "advanced":
    #         return await run_advanced_workflow(request.query, request.max_tools)
    #     else:
    #         return await run_sre_session(request.query, request.max_tools)
    # result = await asyncio.wait_for(
    #     run_workflow(),
    #     timeout=300.0
    # )

        # Defensive: ensure result is a dict
        if not isinstance(result, dict):
            return QueryResponse(
                    status="failed",
                    severity="high",
                    workflow_type=workflow_type,
                    findings={"error": {"output": "Internal server error: result is not a dict."}},
                    remediation_plan="Internal error.",
                    executed_actions=[{"tool": "system", "action": "error", "status": "failed"}],
                    error="Internal server error: result is not a dict."
                )

        status = result.get("status", "completed")
        findings = result.get("findings", {})
        remediation_plan = result.get("remediation_plan")
        executed_actions = []
        for action in result.get("executed_actions", []):
            if isinstance(action, dict):
                executed_actions.append({
                    "tool": action.get("tool_name"),
                    "action": action.get("action"),
                    "status": action.get("status"),
                })
            else:
                # RemediationAction dataclass
                executed_actions.append({
                    "tool": getattr(action, "tool_name", None),
                    "action": getattr(action, "action", None),
                    "status": getattr(action, "status", None),
                })

        return QueryResponse(
            status=status,
            severity=result.get("severity"),
            workflow_type=result.get("workflow_type"),
            findings=findings,
            remediation_plan=remediation_plan,
            executed_actions=executed_actions,
        )

    except asyncio.TimeoutError:
        return QueryResponse(
            status="failed",
            severity="high",
            workflow_type="basic",
            findings={"error": {"output": "Workflow timed out after 300 seconds. Check if Ollama is running."}},
            remediation_plan="The LLM workflow timed out. Please ensure Ollama is running and accessible.",
            executed_actions=[{"tool": "system", "action": "timeout", "status": "failed"}],
            error="Workflow timeout - likely Ollama connectivity issue"
        )
    except Exception as e:
        return QueryResponse(
            status="failed",
            severity="high",
            workflow_type="basic",
            findings={"error": {"output": str(e)}},
            remediation_plan=f"Error occurred: {str(e)}",
            executed_actions=[{"tool": "system", "action": "error", "status": "failed"}],
            error=str(e)
        )


@app.get("/api/examples")
async def get_examples():
    """Get example queries for the frontend."""
    return {
        "examples": [
            {
                "category": "Monitoring",
                "queries": [
                    "Show me high CPU pods in production",
                    "Check memory usage across all namespaces",
                    "List pods with high restart counts",
                    "Are there any active alerts?",
                ],
            },
            {
                "category": "Troubleshooting",
                "queries": [
                    "Get logs from the failing pod",
                    "Why is the API gateway down?",
                    "Find pods in CrashLoopBackOff",
                    "Check error rates in the last hour",
                ],
            },
            {
                "category": "Cost Optimization",
                "queries": [
                    "Find wasted resources in the cluster",
                    "What are our biggest cost drivers?",
                    "Show rightsizing recommendations",
                    "Analyze cluster costs for last 30 days",
                ],
            },
            {
                "category": "Remediation",
                "queries": [
                    "Restart the failing pod",
                    "Scale up the web app to handle load",
                    "Drain node for maintenance",
                    "Check pod health and recommend fixes",
                ],
            },
        ]
    }


@app.get("/api/docs")
async def get_documentation():
    """Get tool documentation."""
    return {
        "tools": {
            "monitoring_tool": {
                "description": "Query Prometheus metrics",
                "example_operations": {
                    "cpu_usage": {
                        "description": "Get CPU usage per pod",
                        "params": {
                            "namespace": "default",
                            "pod_name": "optional",
                            "time_range": "1h",
                        }
                    },
                    "alert_status": {
                        "description": "List active alerts",
                        "params": {}
                    },
                }
            },
            "logs_tool": {
                "description": "Retrieve pod logs",
                "example_operations": {
                    "pod_logs": {
                        "description": "Get pod logs",
                        "params": {
                            "namespace": "default",
                            "pod_name": "required",
                            "lines": 100,
                        }
                    },
                }
            },
            "healing_tool": {
                "description": "Automated remediation",
                "example_operations": {
                    "restart_pod": {
                        "description": "Restart a pod",
                        "params": {
                            "namespace": "default",
                            "pod_name": "required",
                            "grace_period": 30,
                        }
                    },
                }
            },
            "cost_analyzer_tool": {
                "description": "Cost analysis",
                "example_operations": {
                    "resource_waste": {
                        "description": "Find wasted resources",
                        "params": {}
                    },
                }
            },
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3001,
        log_level="info",
    )
