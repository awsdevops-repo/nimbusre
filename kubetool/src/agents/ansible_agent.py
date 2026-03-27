from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from src.tools.infrastructure.ansible import ansible_tool

llm = ChatOllama(model="llama3.1:8b", temperature=0)
agent = create_react_agent(llm, tools=[ansible_tool])


def run_ansible_agent(query: str) -> str:
    """Run a single Ansible query and return the response."""
    result = agent.invoke({"messages": [("human", query)]})
    return result["messages"][-1].content


if __name__ == "__main__":
    # Example queries for software inventory across hosts
    queries = [
        "List all installed software on all servers",
        "Get the python version on linux_servers",
        "Show OS information for all hosts",
        "What services are running on windows_servers",
        "Check if docker is installed on any host",
    ]

    print("🤖 Ansible Inventory Agent")
    print("=" * 60)

    for query in queries:
        print(f"\n📋 Query: {query}")
        print("-" * 60)
        try:
            response = run_ansible_agent(query)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 60)
