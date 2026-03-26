from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from src.tools.sre.monitoring import monitoring_tool
from src.tools.sre.logs import logs_tool
from src.tools.sre.healing import healing_tool
from src.tools.sre.cost_analyzer import cost_analyzer_tool

# Create agent with all 4 SRE tools
llm = ChatOllama(model="llama3.1:8b", temperature=0).bind_tools([
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

# Example SRE queries
queries = [
    # Monitoring queries
    "What is the current CPU usage across all pods?",
    "Are there any active alerts in the cluster?",
    
    # Log queries
    "Show me logs from the nginx pod in the default namespace",
    "Check the health status of all pods",
    
    # Healing queries
    "Restart the problematic pod if it's in CrashLoopBackOff",
    "Scale up the web-app deployment to 3 replicas to handle load",
    
    # Cost queries
    "Which namespaces are costing the most?",
    "Show me resource waste and optimization opportunities",
    "What's the estimated monthly cost of the cluster?",
    
    # Compound queries
    "Check pod health, identify any high CPU pods, and suggest cost optimizations",
    "Find unused resources and provide remediation steps",
]

print("🚀 SREAgent - Multi-Tool Kubernetes Management")
print("=" * 80)

for query in queries:
    print(f"\n📋 Query: {query}")
    print("-" * 80)
    try:
        result = agent.invoke({"messages": [("human", query)]})
        response = result['messages'][-1].content
        print(f"Response: {response[:500]}..." if len(response) > 500 else f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 80)
print("Agent interaction complete!")
print("=" * 80)
