from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from src.tools.infrastructure.helm import helm_tool

llm = ChatOllama(model="llama3.1:8b", temperature=0).bind_tools([helm_tool])

agent = create_agent(llm, tools=[helm_tool])

# Example queries for Helm deployments
queries = [
    "List all Helm releases in the default namespace",
    "What version of nginx is available?",
    "Install the latest version of prometheus in the monitoring namespace",
    "What is the current status of the nginx-ingress release?",
    "Show me the values for the prometheus release",
    "Upgrade the prometheus release to use 3 replicas",
    "Search for available elasticsearch charts",
    "Rollback the nginx-ingress release to the previous version",
]

print("🚀 Helm Deployment Agent")
print("=" * 70)

for query in queries:
    print(f"\n📋 Query: {query}")
    print("-" * 70)
    try:
        result = agent.invoke({"messages": [("human", query)]})
        print(f"Response: {result['messages'][-1].content}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 70)
