from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from src.tools.infrastructure.helm import helm_tool

llm = ChatOllama(model="llama3.1:8b", temperature=0)
agent = create_react_agent(llm, tools=[helm_tool])


def run_helm_agent(query: str) -> str:
    """Run a single Helm query and return the response."""
    result = agent.invoke({"messages": [("human", query)]})
    return result["messages"][-1].content


if __name__ == "__main__":
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
            response = run_helm_agent(query)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 70)
