from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from tool import kubectl_tool

llm = ChatOllama(model="llama3.1", temperature=0).bind_tools([kubectl_tool])
agent = create_agent(llm, tools=[kubectl_tool])

queries = [
    "List all pods",
    "Show me the nodes in the cluster",
    "Get services in default namespace",
    "Describe the kubernetes service",
]

for query in queries:
    print(f"\n🤖 Query: {query}")
    result = agent.invoke({"messages": [("human", query)]})
    print(f"📋 Response: {result['messages'][-1].content}")
    print("-" * 50)