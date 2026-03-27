from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from src.tools.infrastructure.kubectl import kubectl_tool

llm = ChatOllama(model="llama3.1:8b", temperature=0)
agent = create_react_agent(llm, tools=[kubectl_tool])


if __name__ == "__main__":
    # Example queries for kubectl operations
    queries = [
        "Get all pods in the default namespace",
        "Describe the nginx deployment in the default namespace",
        "Show logs from the nginx pod",
        "Get all services in the kube-system namespace",
        "Describe the api-server pod in the kube-system namespace",
        "Show logs from the metrics-server pod in the kube-system namespace",
        "Get all pods across all namespaces",
        "Describe the coredns deployment in the kube-system namespace",
    ]

    print("🚀 Kubectl Agent")
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
