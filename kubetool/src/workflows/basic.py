"""
LangGraph-based SREAgent: Multi-tool orchestration for Kubernetes operations.
Supports complex multi-step SRE workflows with state management and tool coordination.
"""

from typing import Annotated, TypedDict, Optional
import json

from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from .shared import (
    get_llm_with_tools,
    monitoring_tool,
    logs_tool,
    healing_tool,
    cost_analyzer_tool,
    kubectl_tool,
    ansible_tool,
    helm_tool,
)


# Define SREAgent state
class SREState(TypedDict):
    """State for SRE operations workflow."""
    messages: Annotated[list[BaseMessage], add_messages]
    current_task: Optional[str]
    findings: dict  # Accumulated findings from tools
    remediation_plan: Optional[str]
    tool_calls_count: int
    max_tool_calls: int


# Initialize LLM with shared tool registry
llm_with_tools = get_llm_with_tools()


def should_continue(state: SREState) -> str:
    """Determine next node: continue with tools or end."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If tool calls exceeded, go to end
    if state["tool_calls_count"] >= state["max_tool_calls"]:
        return "end"
    
    # If last message has tool calls, execute them
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # Otherwise, end workflow
    return "end"


def process_query(state: SREState) -> SREState:
    """Process user query and generate initial analysis plan."""
    
    messages = state["messages"]
    current_input = messages[-1].content if messages else ""
    
    # Create system prompt for SRE context
    system_prompt = f"""You are a Kubernetes SRE agent. For the query "{current_input}", use the correct tool:

- "high CPU" or "CPU pods" or "memory" or "metrics" → monitor_metrics
- "logs" or "failing pods" → aggregate_logs with operation="failing_pods_logs"
- "install" or "helm" or "chart" → helm_deploy  
- "get" or "list" or "pods" or "kubectl" → kubectl
- "cost" or "money" or "expensive" → analyze_costs
- "restart" or "heal" → self_healing
- "ansible" → ansible

For "Show me high CPU pods in production" → USE monitor_metrics ONLY
NEVER use analyze_costs for CPU/memory/performance queries!

Tools available:
1. kubectl_tool - Query Kubernetes resources: pods, nodes, services, deployments, etc.
   Use for: "Describe service", "Get pods", "List nodes", "Show deployments", "Get all resources"
   Keywords: describe, get, list, show, status, info, resources, pods, nodes, services, deployments
2. ansible_tool - Execute Ansible playbooks and inventory management
   Use for: "Run playbook", "Check inventory", "Configure nodes"
   Keywords: ansible, playbook, inventory, configure, install, setup
3. helm_tool - Deploy and manage Kubernetes applications using Helm
   Use for: "Add repository", "Install chart", "Upgrade release", "List releases", "Get status"
   Keywords: helm, chart, release, install, upgrade, deploy, repository, add, bitnami
   For repo_add: provide repo_name (e.g., "bitnami"), repo_url auto-completed for common repos
4. monitoring_tool - Query CPU, memory, disk, network metrics and alerts
   Use for: "Show me high CPU pods", "Check cluster metrics", "Alert status"
   Keywords: CPU, memory, metrics, performance, alerts, monitoring, high, usage
5. logs_tool - Retrieve and search pod logs
   Use for: "Show logs from pod X", "Search logs for error", "Get crash logs"
   Keywords: logs, error, crash, debug, troubleshoot, events
6. healing_tool - Restart pods, scale deployments, manage node health
   Use for: "Restart the failing pod", "Scale deployment", "Drain node"
   Keywords: restart, scale, heal, fix, repair, drain, recover
7. cost_analyzer_tool - Analyze cluster costs and optimization opportunities
   Use for: "What are cost drivers?", "Find unused resources", "Optimization tips"
   Keywords: cost, money, expensive, waste, optimize, savings, budget

Tool selection guide:
- KUBECTL: For querying cluster state (nodes, pods, services, resources)
  Examples: "Get all pods", "List services", "Describe deployment", "Show nodes"
- ANSIBLE: For configuration management and automation
- HELM: For application deployment and package management
- MONITORING: For performance metrics and current health
- LOGS: For troubleshooting and historical events
- HEALING: For corrective actions after diagnosis
- COST: For financial and resource optimization ONLY

EXAMPLES:
- "Get all pods in default namespace" → kubectl_tool
- "List all services" → kubectl_tool
- "Describe kubernetes service" → kubectl_tool
- "Add the bitnami Helm repository" → helm_deploy
- "Install nginx chart" → helm_deploy
- "List Helm releases" → helm_deploy
- "Show me cluster costs" → cost_analyzer_tool
- "Find expensive resources" → cost_analyzer_tool

For complex issues:
- Start with kubectl to understand cluster structure
- Use monitoring to see current state
- Get logs to identify root cause
- Plan and execute healing if needed
- Analyze cost impact

Always be methodical and explain your reasoning."""
    
    # Get LLM response
    response = llm_with_tools.invoke(
        [{"role": "system", "content": system_prompt}] + 
        [{"role": "user", "content": current_input}]
    )
    
    # Update state
    state["messages"].append(response)
    state["tool_calls_count"] = 0
    
    return state


def execute_tools(state: SREState) -> SREState:
    """Execute tool calls from LLM response."""
    
    messages = state["messages"]
    last_message = messages[-1]
    
    if not hasattr(last_message, "tool_calls"):
        return state
    
    tool_calls = last_message.tool_calls
    
    # Helper to clean tool inputs (convert <nil> strings to None)
    def clean_tool_input(tool_input):
        cleaned = {}
        for key, value in tool_input.items():
            if value == "<nil>" or value == "nil" or value is None:
                cleaned[key] = None
            elif key == "extra_args":
                # Ensure extra_args is always a list
                if isinstance(value, str):
                    # Split string arguments properly and fix common mistakes
                    if value.strip():
                        # Fix common kubectl argument mistakes
                        if '--all-namespaces=' in value:
                            # Split --all-namespaces=default into --all-namespaces and ignore the value
                            cleaned[key] = ['--all-namespaces']
                        elif ' ' in value:
                            cleaned[key] = value.split()
                        elif ',' in value:
                            cleaned[key] = [arg.strip() for arg in value.split(',')]
                        else:
                            cleaned[key] = [value]
                    else:
                        cleaned[key] = []
                elif isinstance(value, list):
                    cleaned[key] = value
                else:
                    cleaned[key] = []
            else:
                cleaned[key] = value
        return cleaned
    
    # Execute each tool call
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_input = clean_tool_input(tool_call["args"])
        
        print(f"  📌 Executing: {tool_name}")
        
        try:
            # Execute appropriate tool
            if tool_name == "monitor_metrics":
                result = monitoring_tool.invoke(tool_input)
            elif tool_name == "aggregate_logs":
                result = logs_tool.invoke(tool_input)
            elif tool_name == "self_healing":
                result = healing_tool.invoke(tool_input)
            elif tool_name == "analyze_costs":
                result = cost_analyzer_tool.invoke(tool_input)
            elif tool_name == "kubectl":
                result = kubectl_tool.invoke(tool_input)
            elif tool_name in ("ansible", "ansible_inventory"):
                result = ansible_tool.invoke(tool_input)
            elif tool_name == "helm_deploy":
                result = helm_tool.invoke(tool_input)
            else:
                result = f"Unknown tool: {tool_name}"
            
            # Store finding
            state["findings"][tool_name] = {
                "input": tool_input,
                "output": result,
                "timestamp": str(__import__('time').time())
            }
            
            # Add tool result to messages
            state["messages"].append(ToolMessage(
                tool_call_id=tool_call["id"],
                name=tool_name,
                content=str(result)[:1000]  # Limit output size
            ))
            
        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            state["findings"][tool_name] = {"error": error_msg}
            state["messages"].append(ToolMessage(
                tool_call_id=tool_call["id"],
                name=tool_name,
                content=error_msg
            ))
        
        state["tool_calls_count"] += 1
    
    # Get LLM response to tool results
    response = llm_with_tools.invoke(state["messages"])
    state["messages"].append(response)
    
    return state


def synthesize_findings(state: SREState) -> SREState:
    """Synthesize findings and create remediation plan."""
    
    findings_text = json.dumps(state["findings"], indent=2)
    
    synthesis_prompt = f"""Based on the gathered findings, provide:
1. Root cause analysis
2. Remediation plan (if applicable)
3. Cost optimization opportunities
4. Recommended next steps

Findings:
{findings_text}"""
    
    response = llm_with_tools.invoke(
        state["messages"] + [HumanMessage(content=synthesis_prompt)]
    )
    
    state["messages"].append(response)
    state["remediation_plan"] = response.content
    
    return state


def build_sre_graph():
    """Build the SREAgent LangGraph workflow."""
    
    graph = StateGraph(SREState)
    
    # Define nodes
    graph.add_node("process_query", process_query)
    graph.add_node("tools", execute_tools)
    graph.add_node("synthesize", synthesize_findings)
    
    # Define edges
    graph.add_edge(START, "process_query")
    graph.add_conditional_edges(
        "process_query",
        should_continue,
        {
            "tools": "tools",
            "end": "synthesize"
        }
    )
    graph.add_conditional_edges(
        "tools",
        should_continue,
        {
            "tools": "tools",
            "end": "synthesize"
        }
    )
    graph.add_edge("synthesize", END)
    
    return graph.compile()


# Interactive session interface
def run_sre_session(initial_query: str, max_tools: int = 5):
    """Run an interactive SRE session."""
    
    agent = build_sre_graph()
    
    # Initialize state
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
    
    # Execute graph
    result = agent.invoke(state)
    
    print("\n" + "=" * 80)
    print("📊 FINAL FINDINGS")
    print("=" * 80)
    for tool_name, finding in result["findings"].items():
        print(f"\n🔧 {tool_name}:")
        if "error" in finding:
            print(f"  ❌ {finding['error']}")
        else:
            print(f"  ✅ Input: {finding['input']}")
            print(f"  📤 Output: {str(finding['output'])[:200]}...")
    
    print("\n" + "=" * 80)
    print("🎯 REMEDIATION PLAN")
    print("=" * 80)
    if result["remediation_plan"]:
        print(result["remediation_plan"])
    
    return result


# Multi-turn conversation support
def run_sre_conversation():
    """Run multi-turn SRE conversation."""
    
    agent = build_sre_graph()
    
    state = {
        "messages": [],
        "current_task": None,
        "findings": {},
        "remediation_plan": None,
        "tool_calls_count": 0,
        "max_tool_calls": 5,
    }
    
    print("🚀 SREAgent - Interactive Mode")
    print("Type your queries below. Press Ctrl+C to exit.")
    print("=" * 80)
    
    while True:
        try:
            user_input = input("\n📋 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break
            
            # Add user message
            state["messages"].append(HumanMessage(content=user_input))
            state["findings"] = {}  # Reset findings for new query
            state["tool_calls_count"] = 0
            
            print("\n🤖 SREAgent: Analyzing...")
            
            # Execute graph
            result = agent.invoke(state)
            
            # Display findings
            if result["findings"]:
                print("\n📊 Findings:")
                for tool_name, finding in result["findings"].items():
                    if "error" not in finding:
                        print(f"  ✅ {tool_name}: Found data")
            
            # Display response
            if result["remediation_plan"]:
                print(f"\n🎯 Analysis:\n{result['remediation_plan'][:500]}...")
            
            # Update state for next iteration
            state = result
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


if __name__ == "__main__":
    # Example 1: Single query with multi-tool orchestration
    print("\n" + "=" * 80)
    print("EXAMPLE 1: High CPU Investigation")
    print("=" * 80)
    
    result = run_sre_session(
        "We have a high CPU alert in the production namespace. "
        "Find the problematic pods, check their logs, and recommend scaling if needed. "
        "Also show me if this impacts cluster costs.",
        max_tools=5
    )
    
    # Example 2: Cost optimization workflow
    print("\n\n" + "=" * 80)
    print("EXAMPLE 2: Cost Optimization Initiative")
    print("=" * 80)
    
    result = run_sre_session(
        "Analyze our cluster costs for the last 30 days. "
        "Find wasted resources and provide optimization recommendations.",
        max_tools=4
    )
    
    # Uncomment to run interactive mode
    # print("\n\nStarting interactive session...")
    # run_sre_conversation()
