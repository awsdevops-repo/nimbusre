# LangGraph Integration for SREAgent

Complete guide to integrating SREAgent tools into LangGraph workflows for orchestrated Kubernetes management.

## Overview

Two integration approaches provided:

1. **Basic SREAgent** (`sre_langgraph.py`) - Simplified multi-tool orchestration
2. **Advanced SREAgent** (`sre_langgraph_advanced.py`) - Complex workflows with approval, rollback, and state management

## Basic Integration: `sre_langgraph.py`

### Architecture

```
START
  ↓
process_query (LLM analyzes issue)
  ↓
should_continue? 
  ├─ YES → tools (Execute monitoring, logs, healing, cost tools)
  │          ↓
  │     should_continue?
  │          ├─ YES → tools (loop for multi-step)
  │          └─ NO → synthesize
  │
  └─ NO → synthesize (Generate recommendations)
            ↓
          END
```

### Key Components

**SREState:**
```python
messages: list of conversational messages
current_task: Current operation being performed
findings: Dictionary of tool results
remediation_plan: Final recommendations
tool_calls_count: Track tool usage
max_tool_calls: Limit iterations
```

**Nodes:**
- `process_query`: Initial LLM analysis
- `tools`: Execute selected tools
- `synthesize`: Generate final recommendations

### Usage Example

```python
from sre_langgraph import run_sre_session

# Single query with automatic tool orchestration
result = run_sre_session(
    "Find high CPU pods and suggest scaling",
    max_tools=5
)

print(result["remediation_plan"])
print(result["findings"])
```

### Interactive Mode

```python
from sre_langgraph import run_sre_conversation

# Multi-turn conversation
run_sre_conversation()
```

## Advanced Integration: `sre_langgraph_advanced.py`

### Architecture

```
START
  ↓
classify (Determine severity & workflow type)
  ↓
plan (Plan actions without executing)
  ↓
request_approval (Check if approval needed)
  ↓
should_execute?
  ├─ YES → execute (Run planned actions with rollback capability)
  │          ↓
  │      verify (Confirm remediation worked)
  │          ↓
  │        END
  │
  └─ NO → END (Wait for approval)
```

### Workflow Types

**1. Diagnostic** - Gather information only
```python
"Check CPU usage across the cluster"
```

**2. Remediation** - Fix issues (requires approval for critical/high)
```python
"Restart the failing pod and verify it works"
```

**3. Optimization** - Cost or performance improvements (low risk)
```python
"Find wasted resources and recommend optimization"
```

**4. Multi-step** - Complex operations (diagnostic + remediation)
```python
"Check logs, find the error, restart the pod, and verify the fix"
```

### Severity Levels

- **CRITICAL** - Outages, service down (requires approval)
- **HIGH** - High CPU, memory pressure (requires approval)
- **MEDIUM** - Default for unknown issues
- **LOW** - Cost optimization, non-critical changes

### Advanced Features

#### 1. Action Planning & Approval

```python
from sre_langgraph_advanced import run_advanced_workflow

result = run_advanced_workflow(
    "Restart the problematic pod"
)

# Shows:
# - Planned actions
# - Approval requirement
# - Execution status
# - Verification results
```

#### 2. Rollback Capability

```python
RemediationAction tracks:
- tool_name: Which tool was used
- action: What was done
- parameters: Arguments passed
- status: planned → executing → succeeded/failed → rolled_back
- result: Output or error message
```

Automatically triggers on critical failures:
```python
if state["severity"] == "critical":
    if action.status == "failed":
        trigger_rollback(state)  # Reverse all changes
```

#### 3. Audit Trail

```python
state["executed_actions"]  # What was done
state["rollback_stack"]    # What was rolled back
state["findings"]          # All gathered data
state["messages"]          # Full conversation history
```

#### 4. State Persistence

```python
from dataclasses import dataclass

@dataclass
class RemediationAction:
    tool_name: str
    action: str
    parameters: dict
    timestamp: str
    status: Literal["planned", "executing", "succeeded", "failed", "rolled_back"]
    result: Optional[str]
    error: Optional[str]
```

## Comparison

| Feature | Basic | Advanced |
|---------|-------|----------|
| Multi-tool orchestration | ✅ | ✅ |
| Message history | ✅ | ✅ |
| Findings aggregation | ✅ | ✅ |
| Approval workflows | ❌ | ✅ |
| Rollback support | ❌ | ✅ |
| Severity classification | ❌ | ✅ |
| Workflow type detection | ❌ | ✅ |
| Action tracking | Basic | Advanced |
| Interactive mode | ✅ | ❌ |

## Usage Patterns

### Pattern 1: Quick Diagnostic

```python
from sre_langgraph import run_sre_session

# Simple query, automatic tool selection
result = run_sre_session(
    "Why is CPU high in production?",
    max_tools=3
)
```

### Pattern 2: Production Remediation

```python
from sre_langgraph_advanced import run_advanced_workflow

# High-risk operation with approval and rollback
result = run_advanced_workflow(
    "Pod keeps crashing. Restart and verify the fix."
)

# Shows all actions, requires approval for critical issues
```

### Pattern 3: Cost Optimization Initiative

```python
from sre_langgraph import run_sre_session

# Multi-step cost analysis
queries = [
    "What are our biggest cost drivers?",
    "Show me resource waste by namespace",
    "Give me rightsizing recommendations",
]

for query in queries:
    result = run_sre_session(query, max_tools=2)
    print(result["remediation_plan"])
```

### Pattern 4: Incident Response

```python
from sre_langgraph_advanced import run_advanced_workflow

# Critical issue workflow
result = run_advanced_workflow(
    "Service is down. Check metrics, get logs, "
    "restart pods if needed, and confirm recovery."
)

# Tracks: planned actions, approval, execution, verification
print(result["status"])  # completed or failed
print(result["executed_actions"])  # Full audit trail
```

### Pattern 5: Interactive Troubleshooting

```python
from sre_langgraph import run_sre_conversation

# Multi-turn investigation
# User: "Show me high error rate pods"
# Agent: [queries monitoring, shows results]
# User: "Get logs from the top pod"
# Agent: [queries logs, displays output]
```

## Tool Integration Details

### How Tools Are Called

```python
# LLM determines which tools to use
llm_with_tools = llm.bind_tools([
    monitoring_tool,
    logs_tool,
    healing_tool,
    cost_analyzer_tool,
])

# LLM generates tool calls based on query
response = llm_with_tools.invoke(messages)

# Graph executes selected tools
for tool_call in response.tool_calls:
    if tool_call["name"] == "monitor_metrics":
        result = monitoring_tool(**tool_call["args"])
```

### Tool Execution Flow

```
LLM decides tools needed
         ↓
Graph executes tools in sequence
         ↓
Results stored in findings
         ↓
Results added to message history
         ↓
LLM analyzes results
         ↓
LLM decides next steps
```

## Error Handling

### Basic Graph

```python
try:
    result = tool(**tool_input)
except Exception as e:
    state["findings"][tool_name] = {"error": str(e)}
    state["messages"].append(ToolMessage(
        tool_call_id=tool_call["id"],
        name=tool_name,
        content=error_msg
    ))
```

### Advanced Graph

```python
action.status = "executing"
try:
    result = execute_tool()
    action.status = "succeeded"
except Exception as e:
    action.status = "failed"
    action.error = str(e)
    if state["severity"] == "critical":
        trigger_rollback(state)
```

## State Management

### Saving State

```python
import json

def save_state(state: SREWorkflowState, filename: str):
    """Persist workflow state."""
    state_copy = {
        "workflow_type": state["workflow_type"],
        "severity": state["severity"],
        "status": state["status"],
        "findings": state["findings"],
        "executed_actions": [
            {
                "tool_name": a.tool_name,
                "action": a.action,
                "status": a.status,
                "timestamp": a.timestamp,
            }
            for a in state["executed_actions"]
        ],
    }
    with open(filename, "w") as f:
        json.dump(state_copy, f, indent=2)
```

### Resuming State

```python
def load_state(filename: str) -> dict:
    """Load previous workflow state."""
    with open(filename, "r") as f:
        return json.load(f)
```

## Performance Optimization

### Parallel Tool Execution

```python
# Current: Sequential execution
for tool_call in response.tool_calls:
    execute(tool_call)

# Future: Can parallelize independent tools
import asyncio

async def execute_parallel(tool_calls):
    tasks = [execute_async(tc) for tc in tool_calls]
    return await asyncio.gather(*tasks)
```

### Caching Results

```python
# Cache metrics to avoid redundant queries
cache = {}

def monitoring_tool_cached(**kwargs):
    cache_key = json.dumps(kwargs, sort_keys=True)
    if cache_key in cache:
        return cache[cache_key]
    result = monitoring_tool(**kwargs)
    cache[cache_key] = result
    return result
```

## Integration with External Systems

### Slack Notifications

```python
def notify_slack(message: str, channel: str):
    """Send updates to Slack."""
    from slack_sdk import WebClient
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    client.chat_postMessage(channel=channel, text=message)

# In graph:
if action.status == "failed":
    notify_slack(f"❌ {action.action} failed", "#incidents")
```

### PagerDuty Escalation

```python
def create_incident(severity: str, title: str):
    """Escalate to PagerDuty."""
    from pdpyras import APISession
    session = APISession(token=os.environ["PD_TOKEN"])
    incident = session.post(
        "/incidents",
        json={"incident": {
            "title": title,
            "urgency": severity,
            ...
        }}
    )
    return incident
```

### Datadog Event Logging

```python
def log_to_datadog(event: str, tags: list):
    """Log actions to Datadog."""
    from datadog import initialize, api
    initialize(**options)
    api.Event.create(title="SREAgent Action", text=event, tags=tags)
```

## Best Practices

1. **Always verify before destructive actions** - Use healing_tool with caution
2. **Set appropriate max_tool_calls** - Prevent infinite loops (5-10 is reasonable)
3. **Use severity classification** - High/critical issues need approval
4. **Keep message history** - Full audit trail for troubleshooting
5. **Test in non-prod first** - Validate workflows before production use
6. **Monitor tool_calls_count** - Catch inefficient LLM decisions
7. **Use timeouts** - Prevent hanging operations
8. **Log everything** - Store findings and actions for analysis

## Troubleshooting

### "Tool call stuck in loop"
- Set `max_tool_calls` lower (default 10)
- Check if LLM is misinterpreting the task
- Add explicit "STOP" instruction to LLM system prompt

### "State too large"
- Remove verbose message history
- Summarize findings periodically
- Use database for long-term state

### "Tool execution slow"
- Check network connectivity to Kubernetes
- Verify Prometheus is responsive
- Use caching for repeated queries

## Next Steps

1. Integrate with your incident management system
2. Add webhooks for Slack/Teams notifications
3. Implement persistent state storage
4. Build dashboard for workflow metrics
5. Create custom tools for your specific needs
6. Add cost alerts and budgets
7. Implement ML for anomaly detection
