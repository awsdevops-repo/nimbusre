from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from src.tools.infrastructure.ansible import ansible_tool

llm = ChatOllama(model="llama3.1:8b", temperature=0).bind_tools([ansible_tool])

agent = create_agent(llm, tools=[ansible_tool])

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
        result = agent.invoke({"messages": [("human", query)]})
        print(f"Response: {result['messages'][-1].content}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 60)
