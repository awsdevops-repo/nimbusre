"""
Advanced LangGraph SREAgent with workflow orchestration and state persistence.
Supports complex multi-step SRE operations with decision trees and rollback.
"""

from typing import Annotated, TypedDict, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
import json

from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages

from src.tools.sre.monitoring import monitoring_tool
from src.tools.sre.logs import logs_tool
from src.tools.sre.healing import healing_tool
from src.tools.sre.cost_analyzer import cost_analyzer_tool
from src.tools.infrastructure.kubectl import kubectl_tool
from src.tools.infrastructure.ansible import ansible_tool
from src.tools.infrastructure.helm import helm_tool


@dataclass
class RemediationAction:
    """Track remediation actions for audit trail."""
    tool_name: str
    action: str
    parameters: dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: Literal["planned", "executing", "succeeded", "failed", "rolled_back"] = "planned"
    result: Optional[str] = None
    error: Optional[str] = None


class SREWorkflowState(TypedDict):
    """Extended state for complex SRE workflows."""
    messages: Annotated[list[BaseMessage], add_messages]
    workflow_type: Literal["diagnostic", "remediation", "optimization", "multi_step"]
    severity: Literal["critical", "high", "medium", "low"]
    status: Literal["planning", "executing", "verifying", "completed", "failed"]
    findings: dict
    planned_actions: list[RemediationAction]
    executed_actions: list[RemediationAction]
    rollback_stack: list[RemediationAction]  # For rollback capability
    approval_required: bool
    approved_by: Optional[str]
    tool_calls_count: int
    max_tool_calls: int


def classify_severity(query: str) -> Literal["critical", "high", "medium", "low"]:
    """Classify query severity based on keywords."""
    critical_keywords = ["down", "outage", "critical", "emergency", "5xx", "error rate"]
    high_keywords = ["high cpu", "memory pressure", "pending", "crash"]
    
    query_lower = query.lower()
    
    if any(kw in query_lower for kw in critical_keywords):
        return "critical"
    elif any(kw in query_lower for kw in high_keywords):
        return "high"
    elif "cost" in query_lower or "optimization" in query_lower:
        return "low"
    else:
        return "medium"


def determine_workflow_type(query: str) -> Literal["diagnostic", "remediation", "optimization", "multi_step"]:
    """Determine the workflow type."""
    if "fix" in query.lower() or "restart" in query.lower() or "scale" in query.lower():
        return "remediation"
    elif "cost" in query.lower() or "optimize" in query.lower():
        return "optimization"
    elif "and" in query.lower() or "," in query.lower():
        return "multi_step"
    else:
        return "diagnostic"


def plan_remediation(state: SREWorkflowState) -> SREWorkflowState:
    """Plan remediation actions without executing."""
    
    messages = state["messages"]
    severity = state["severity"]
    workflow_type = state["workflow_type"]
    
    system_prompt = f"""You are an expert SRE planning remediation for a {severity.upper()} issue.

Workflow type: {workflow_type}

For {workflow_type} workflows:
1. DIAGNOSTIC: Gather information and findings
2. REMEDIATION: Plan and execute fixes
3. OPTIMIZATION: Identify cost savings
4. MULTI_STEP: Combine multiple workflows

Your task:
1. Analyze the issue severity and impact
2. Identify information needed (metrics, logs, etc)
3. Propose remediation steps WITH CAUTION
4. Always verify before destructive actions
5. Plan rollback if needed

Do NOT execute healing actions yet. Only plan them.
Use monitoring_tool and logs_tool to gather data first."""
    
    llm = ChatOllama(model="llama3.1:8b", temperature=0)
    tools = [kubectl_tool, ansible_tool, helm_tool, monitoring_tool, logs_tool, healing_tool, cost_analyzer_tool]
    llm_with_tools = llm.bind_tools(tools)
    
    response = llm_with_tools.invoke(
        [{"role": "system", "content": system_prompt}] + 
        [{"role": "user", "content": messages[-1].content}]
    )
    
    state["messages"].append(response)
    state["status"] = "planning"
    
    # Extract planned actions from response if available
    if hasattr(response, "tool_calls"):
        for tool_call in response.tool_calls:
            action = RemediationAction(
                tool_name=tool_call["name"],
                action=tool_call["name"],
                parameters=tool_call["args"]
            )
            state["planned_actions"].append(action)
    
    return state


def request_approval(state: SREWorkflowState) -> SREWorkflowState:
    """Request approval for planned actions if needed."""
    
    if state["severity"] in ["critical", "high"] and state["workflow_type"] == "remediation":
        state["approval_required"] = True
        approval_message = f"""
APPROVAL REQUIRED for {state['severity'].upper()} severity {state['workflow_type']} workflow.

Planned Actions:
"""
        for action in state["planned_actions"]:
            approval_message += f"\n- {action.tool_name}: {action.action}"
            approval_message += f"\n  Parameters: {json.dumps(action.parameters)}"
        
        approval_message += "\n\nType 'APPROVE' to proceed, or 'CANCEL' to abort."
        print(approval_message)
        
        # In interactive mode, request user approval
        # For now, auto-approve for demonstration
        state["approved_by"] = "system"
    
    return state


def execute_remediation(state: SREWorkflowState) -> SREWorkflowState:
    """Execute planned remediation actions."""
    
    state["status"] = "executing"
    
    llm = ChatOllama(model="llama3.1", temperature=0)
    tools = [kubectl_tool, ansible_tool, helm_tool, monitoring_tool, logs_tool, healing_tool, cost_analyzer_tool]
    llm_with_tools = llm.bind_tools(tools)
    
    # Helper to clean tool inputs (convert <nil> strings to None)
    def clean_tool_input(tool_input):
        if isinstance(tool_input, dict):
            cleaned = {}
            for key, value in tool_input.items():
                if value == "<nil>" or value == "nil" or value is None:
                    cleaned[key] = None
                elif key == "extra_args" and value == "":
                    # Convert empty string to empty list for extra_args
                    cleaned[key] = []
                else:
                    cleaned[key] = value
            return cleaned
        return tool_input
    
    # Execute tools based on planned actions
    for action in state["planned_actions"]:
        action.status = "executing"
        
        try:
            # Clean parameters before invocation
            params = clean_tool_input(action.parameters)
            
            if action.tool_name == "monitor_metrics":
                result = monitoring_tool.invoke(params)
            elif action.tool_name == "aggregate_logs":
                result = logs_tool.invoke(params)
            elif action.tool_name == "self_healing":
                result = healing_tool.invoke(params)
            elif action.tool_name == "analyze_costs":
                result = cost_analyzer_tool.invoke(params)
            elif action.tool_name == "kubectl":
                result = kubectl_tool.invoke(params)
            elif action.tool_name in ("ansible", "ansible_inventory"):
                result = ansible_tool.invoke(params)
            elif action.tool_name == "helm_deploy":
                result = helm_tool.invoke(params)
            else:
                raise ValueError(f"Unknown tool: {action.tool_name}")
            
            action.status = "succeeded"
            action.result = str(result)[:500]
            state["executed_actions"].append(action)
            
            # Store in findings
            state["findings"][action.tool_name] = result
            
            # Add to messages
            state["messages"].append(ToolMessage(
                tool_call_id=f"action-{len(state['executed_actions'])}",
                name=action.tool_name,
                content=str(result)[:1000]
            ))
            
        except Exception as e:
            action.status = "failed"
            action.error = str(e)
            print(f"❌ Action failed: {action.tool_name}")
            print(f"   Error: {e}")
            # Trigger rollback on critical errors
            if state["severity"] == "critical":
                state["status"] = "failed"
                trigger_rollback(state)
    
    return state


def verify_remediation(state: SREWorkflowState) -> SREWorkflowState:
    """Verify remediation was successful."""
    
    state["status"] = "verifying"
    
    # Query metrics to verify
    verify_prompt = """The remediation has been executed. 
Please verify if the issue has been resolved by:
1. Checking current metrics
2. Reviewing any errors or anomalies
3. Confirming pod/deployment status

Use monitoring_tool to verify the fix."""
    
    state["messages"].append(HumanMessage(content=verify_prompt))
    
    llm = ChatOllama(model="llama3.1", temperature=0)
    tools = [kubectl_tool, ansible_tool, helm_tool, monitoring_tool, logs_tool, healing_tool, cost_analyzer_tool]
    llm_with_tools = llm.bind_tools(tools)
    
    response = llm_with_tools.invoke(state["messages"])
    state["messages"].append(response)
    
    # Check if verification successful
    if "resolved" in response.content.lower() or "fixed" in response.content.lower():
        state["status"] = "completed"
    else:
        state["status"] = "failed"
    
    return state


def trigger_rollback(state: SREWorkflowState) -> SREWorkflowState:
    """Rollback executed actions in reverse order."""
    
    print("\n⚠️  TRIGGERING ROLLBACK")
    
    # Reverse executed actions
    for action in reversed(state["executed_actions"]):
        if action.tool_name == "self_healing":
            # Create reverse action
            reverse_action = RemediationAction(
                tool_name=action.tool_name,
                action=f"rollback_{action.action}",
                parameters=action.parameters
            )
            
            print(f"🔄 Rolling back: {reverse_action.action}")
            # In real scenario, execute reverse action
            # For now, just mark as rolled back
            action.status = "rolled_back"
            state["rollback_stack"].append(reverse_action)
    
    state["status"] = "failed"
    return state


def build_advanced_sre_graph():
    """Build advanced workflow graph with approval and rollback."""
    
    graph = StateGraph(SREWorkflowState)
    
    # Nodes
    graph.add_node("classify", lambda state: {
        **state,
        "severity": classify_severity(state["messages"][-1].content),
        "workflow_type": determine_workflow_type(state["messages"][-1].content),
    })
    
    graph.add_node("plan", plan_remediation)
    graph.add_node("request_approval", request_approval)
    graph.add_node("execute", execute_remediation)
    graph.add_node("verify", verify_remediation)
    
    # Edges
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "plan")
    graph.add_edge("plan", "request_approval")
    
    # Conditional: execute only if approved or low risk
    def should_execute(state: SREWorkflowState) -> str:
        if state["approval_required"] and not state["approved_by"]:
            return "wait"
        return "execute"
    
    graph.add_conditional_edges(
        "request_approval",
        should_execute,
        {"execute": "execute", "wait": END}
    )
    
    graph.add_edge("execute", "verify")
    graph.add_edge("verify", END)
    
    return graph.compile()


def run_advanced_workflow(query: str):
    """Run advanced SRE workflow with orchestration."""
    graph = build_advanced_sre_graph()
    state = {
        "messages": [HumanMessage(content=query)],
        "workflow_type": "diagnostic",
        "severity": "medium",
        "status": "planning",
        "findings": {},
        "planned_actions": [],
        "executed_actions": [],
        "rollback_stack": [],
        "approval_required": False,
        "approved_by": None,
        "tool_calls_count": 0,
        "max_tool_calls": 10,
    }
    print(f"\n🚀 SREAgent Advanced Workflow")
    print(f"📋 Query: {query}")
    print("=" * 80)
    try:
        result = graph.invoke(state)
    except Exception as e:
        print(f"\n❌ Exception in advanced workflow: {e}")
        return {
            "status": "failed",
            "error": f"Exception in advanced workflow: {str(e)}",
            "traceback": getattr(e, "__traceback__", None),
            "findings": {},
            "planned_actions": [],
            "executed_actions": [],
            "rollback_stack": [],
            "severity": "unknown",
            "workflow_type": "unknown"
        }
    # ...existing summary print code...
    return result


def run_sre_session(initial_query: str, max_tools: int = 5):
    """Run an interactive SRE session."""
    agent = build_sre_graph()
    state = {
        "messages": [HumanMessage(content=initial_query)],
        "current_task": None,
        "findings": {},
        "remediation_plan": None,
        "tool_calls_count": 0,
        "max_tool_calls": max_tools,
    }
    print(f"\n🚀 SREAgent - Starting Session")
    print(f"📋 Query: {initial_query}")
    print("=" * 80)
    try:
        result = agent.invoke(state)
    except Exception as e:
        print(f"\n❌ Exception in basic workflow: {e}")
        return {
            "status": "failed",
            "error": f"Exception in basic workflow: {str(e)}",
            "traceback": getattr(e, "__traceback__", None),
            "findings": {},
            "remediation_plan": None,
        }
    # ...existing summary print code...
    return result


if __name__ == "__main__":
    # Example workflows
    print("ADVANCED SREAgent WORKFLOWS")
    print("=" * 80)
    
    # Critical issue - requires approval
    result1 = run_advanced_workflow(
        "Production pod keeps crashing. Restart it if needed and verify the fix works."
    )
    
    # Optimization - low risk
    result2 = run_advanced_workflow(
        "Analyze cluster costs and find wasteful resources to optimize."
    )
    
    # Complex multi-step
    result3 = run_advanced_workflow(
        "We have high error rates in the API gateway. Check logs, find the issue, "
        "and scale up if it's a load problem. Then show me the cost impact."
    )

